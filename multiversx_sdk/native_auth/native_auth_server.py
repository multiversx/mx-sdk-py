import base64
import json
from http.client import NOT_FOUND, OK
from typing import Optional, Union

import requests

from multiversx_sdk.core.address import Address
from multiversx_sdk.core.message import Message, MessageComputer
from multiversx_sdk.native_auth.config import (
    NativeAuthCacheInterface,
    NativeAuthServerConfig,
)
from multiversx_sdk.native_auth.constants import (
    ACCESS_TOKEN_COMPONENTS_SEPARATOR,
    CACHE_VALUE_IMPERSONATED,
    CACHE_VALUE_NOT_IMPERSONATED,
    MAX_ACCEPTED_WILDCARD_ORIGINS,
    MAX_EXPIRY_SECONDS,
    ONE_HOUR_IN_SECONDS,
    ONE_ROUND_IN_SECONDS,
)
from multiversx_sdk.native_auth.errors import (
    NativeAuthInvalidBlockHashError,
    NativeAuthInvalidConfigError,
    NativeAuthInvalidImpersonateError,
    NativeAuthInvalidSignatureError,
    NativeAuthInvalidTokenError,
    NativeAuthInvalidTokenTtlError,
    NativeAuthInvalidWildcardOriginError,
    NativeAuthOriginNotAcceptedError,
    NativeAuthTokenExpiredError,
)
from multiversx_sdk.native_auth.resources import (
    NativeAuthDecoded,
    NativeAuthValidateResult,
    WildcardOrigin,
)
from multiversx_sdk.wallet.user_keys import UserPublicKey


class NativeAuthServer:
    def __init__(self, config: NativeAuthServerConfig, cache: Optional[NativeAuthCacheInterface] = None) -> None:
        if not (0 < config.max_expiry_seconds <= MAX_EXPIRY_SECONDS):
            raise NativeAuthInvalidConfigError(
                f"Invalid `max_expiry_seconds`. Must be greater than 0 and less than or equal to {MAX_EXPIRY_SECONDS}."
            )

        if not isinstance(config.accepted_origins, list) or not config.accepted_origins:
            raise NativeAuthInvalidConfigError("`accepted_origins` must be a non-empty list of strings.")

        self.accepted_wildcard_origins: list[str] = []
        self.config = config
        self.cache = cache
        self.wildcard_origins = self._get_wildcard_origins()

    def decode(self, access_token: str) -> NativeAuthDecoded:
        token_components = access_token.split(ACCESS_TOKEN_COMPONENTS_SEPARATOR)
        if len(token_components) != 3:
            raise NativeAuthInvalidTokenError()

        address, body, signature = token_components
        parsed_address = Address.new_from_bech32(self._decode_value(address))
        parsed_body = self._decode_value(body)
        body_components = parsed_body.split(".")

        if len(body_components) != 4:
            raise NativeAuthInvalidTokenError()

        origin, block_hash, ttl, extra_info = body_components

        parsed_origin = self._decode_value(origin)

        try:
            parsed_extra_info = json.loads(self._decode_value(extra_info))
        except Exception:
            raise NativeAuthInvalidTokenError()

        return NativeAuthDecoded(
            ttl=int(ttl),
            origin=parsed_origin,
            address=parsed_address,
            signature=bytes.fromhex(signature),
            block_hash=block_hash,
            body=parsed_body,
            extra_info=parsed_extra_info if parsed_extra_info != "e30" else {},  # empty object ('e30' = encoded '{}')
        )

    def is_valid(self, access_token: str) -> bool:
        try:
            self.validate(access_token)
            return True
        except Exception:
            return False

    def validate(self, access_token: str) -> NativeAuthValidateResult:
        decoded = self.decode(access_token)

        if decoded.ttl > self.config.max_expiry_seconds:
            raise NativeAuthInvalidTokenTtlError(decoded.ttl, self.config.max_expiry_seconds)

        if not self._is_origin_accepted(decoded.origin):
            raise NativeAuthOriginNotAcceptedError(decoded.origin)

        block_timestamp, expires = self._verify_token_age_and_get_issue_and_expiry(decoded_token=decoded)

        signed_message = f"{decoded.address.to_bech32()}{decoded.body}"
        valid = self._verify_signature(decoded.address, signed_message, decoded.signature)

        if not valid and not self.config.skip_legacy_validation:
            signed_message = f"{decoded.address.to_bech32()}{decoded.body}{{}}"
            valid = self._verify_signature(decoded.address, signed_message, decoded.signature)

        if not valid:
            raise NativeAuthInvalidSignatureError()

        impersonate_address = self._validate_impersonate_address(decoded)
        impersonate_address = Address.new_from_bech32(impersonate_address) if impersonate_address else None

        return NativeAuthValidateResult(
            issued=block_timestamp,
            expires=expires,
            origin=decoded.origin,
            address=impersonate_address or decoded.address,
            extra_info=decoded.extra_info,
            signer_address=decoded.address,
        )

    def _verify_token_age_and_get_issue_and_expiry(self, decoded_token: NativeAuthDecoded) -> tuple[int, int]:
        block_timestamp = self._get_block_timestamp(decoded_token.block_hash)
        if not block_timestamp:
            raise NativeAuthInvalidBlockHashError(decoded_token.block_hash)

        current_block_timestamp = self._get_current_block_timestamp()
        expires = block_timestamp + decoded_token.ttl

        if expires < current_block_timestamp:
            raise NativeAuthTokenExpiredError()

        return block_timestamp, expires

    def _validate_impersonate_address(self, decoded: NativeAuthDecoded) -> Union[str, None]:
        impersonate_address: str = decoded.extra_info.get("multisig", None) or decoded.extra_info.get(
            "impersonate", None
        )
        if not impersonate_address:
            return None

        if self.config.validate_impersonate_callback:
            is_valid = self.config.validate_impersonate_callback(decoded.address.to_bech32(), impersonate_address)
            if is_valid:
                return impersonate_address

        if self.config.validate_impersonate_url:
            is_valid = self._validate_impersonate_address_from_url(decoded.address.to_bech32(), impersonate_address)
            if is_valid:
                return impersonate_address

        return None

    def _validate_impersonate_address_from_url(self, address: str, impersonate_address: str) -> str:
        cache_key = f"impersonate:{address}:{impersonate_address}"

        if self.cache:
            cached_value = self.cache.get(cache_key)
            if cached_value == CACHE_VALUE_IMPERSONATED:
                return impersonate_address

        url = f"{self.config.validate_impersonate_url}/{address}/{impersonate_address}"

        try:
            requests.get(url)

            if self.cache:
                self.cache.set(cache_key, CACHE_VALUE_IMPERSONATED, ONE_HOUR_IN_SECONDS)

            return impersonate_address
        except requests.exceptions.RequestException as ex:
            if ex.response and ex.response.status_code != OK:
                if self.cache:
                    self.cache.set(cache_key, CACHE_VALUE_NOT_IMPERSONATED, ONE_HOUR_IN_SECONDS)

            raise NativeAuthInvalidImpersonateError()
        except Exception as ex:
            raise ex

    def _verify_signature(self, address: Address, message: str, signature: bytes) -> bool:
        if self.config.verify_signature:
            return self.config.verify_signature(address.to_bech32(), message, signature)

        signed_message = Message(message.encode())
        message_computer = MessageComputer()
        serialized_message = message_computer.compute_bytes_for_verifying(signed_message)

        user_pubkey = UserPublicKey(address.get_public_key())
        return user_pubkey.verify(serialized_message, signature)

    def _get_current_block_timestamp(self) -> int:
        if self.cache:
            timestamp = self.cache.get("block:timestamp:latest")
            if timestamp:
                return int(timestamp)

        response = requests.get(f"{self.config.api_url}/blocks?size=1&fields=timestamp")
        timestamp = int(response.json()[0]["timestamp"])

        if self.cache:
            self.cache.set("block:timestamp:latest", timestamp, ONE_ROUND_IN_SECONDS)

        return timestamp

    def _get_block_timestamp(self, hash: str) -> Union[int, None]:
        if self.cache:
            timestamp = self.cache.get(f"block:timestamp:{hash}")
            if timestamp:
                return int(timestamp)

        try:
            timestamp = requests.get(f"{self.config.api_url}/blocks/{hash}?extract=timestamp")

            if timestamp.status_code == NOT_FOUND:
                return None

            timestamp = timestamp.text
            if self.cache:
                self.cache.set(f"block:timestamp:{hash}", int(timestamp), self.config.max_expiry_seconds)

            return int(timestamp)
        except Exception as ex:
            raise ex

    def _is_origin_accepted(self, origin: str) -> bool:
        if self._is_wildcard_origin_accepted(origin):
            return True

        is_accepted = origin in self.config.accepted_origins or f"https://{origin}" in self.config.accepted_origins
        if is_accepted:
            return True

        if self.config.is_origin_accepted:
            return self.config.is_origin_accepted(origin)

        return False

    def _is_wildcard_origin_accepted(self, origin: str) -> bool:
        if origin in self.accepted_wildcard_origins:
            return True

        if not len(self.wildcard_origins):
            return False

        wildcard_origin = [
            wildcard
            for wildcard in self.wildcard_origins
            if origin.startswith(wildcard.protocol) and origin.endswith(wildcard.domain)
        ]

        if not wildcard_origin:
            return False

        # append new origin to the end of the list
        self.accepted_wildcard_origins.append(origin)

        if len(self.accepted_wildcard_origins) > MAX_ACCEPTED_WILDCARD_ORIGINS:
            # remove the first element of the list which is the oldest
            self.accepted_wildcard_origins.pop(0)

        return True

    def _decode_value(self, value: str) -> str:
        return base64.urlsafe_b64decode(self._ensure_correct_base64_padding(value)).decode("utf-8")

    def _ensure_correct_base64_padding(self, value: str) -> str:
        missing_padding = len(value) % 4
        if missing_padding:
            value += "=" * (4 - missing_padding)
        return value

    def _get_wildcard_origins(self) -> list[WildcardOrigin]:
        origins_with_wildcard = [origin for origin in self.config.accepted_origins if origin.find("*") != -1]
        if len(origins_with_wildcard) == 0:
            return []
        # protocol is what comes before the first '*'
        # domain is what comes after the first '*' and before the first slash
        wildcard_origins: list[WildcardOrigin] = []
        for origin in origins_with_wildcard:
            components = origin.split("*")
            if len(components) != 2:
                raise NativeAuthInvalidWildcardOriginError(origin)

            protocol, domain = components
            if protocol != "" and protocol not in ["http://", "https://"]:
                raise NativeAuthInvalidWildcardOriginError(origin)

            wildcard_origins.append(WildcardOrigin(protocol, domain))

        return wildcard_origins
