import re
from copy import deepcopy
from typing import Any, Optional

import pytest
import requests

from multiversx_sdk.native_auth.config import NativeAuthServerConfig
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
from multiversx_sdk.native_auth.native_auth_server import NativeAuthServer


def mock(mocker: Any, code: int, response: Any, text_response: str = ""):
    mock_response = mocker.Mock()
    mock_response.status_code = code
    mock_response.json.return_value = response
    mock_response.text = text_response
    mocker.patch("requests.get", return_value=mock_response)


def mock_side_effect(mocker: Any, responses: list[Any]):
    def side_effect(*args: Any, **kwargs: Any):
        response = responses.pop(0)

        if "exception" in response:
            raise response["exception"]

        mock_response = mocker.Mock()
        mock_response.status_code = response["code"]
        mock_response.json.return_value = response["response"]
        mock_response.text = response.get("text", "")
        return mock_response

    mocker.patch("requests.get", side_effect=side_effect)


class TestNativeAuthServer:
    ADDRESS = "erd1qnk2vmuqywfqtdnkmauvpm8ls0xh00k8xeupuaf6cm6cd4rx89qqz0ppgl"
    SIGNATURE = "906e79d54e69e688680abee54ec0c49ce2561eb5abfd01865b31cb3ed738272c7cfc4fc8cc1c3590dd5757e622639b01a510945d7f7c9d1ceda20a50a817080d"
    BLOCK_HASH = "ab459013b27fdc6fe98eed567bd0c1754e0628a4cc16883bf0170a29da37ad46"
    TTL = 86400
    TOKEN = f"aHR0cHM6Ly9hcGkubXVsdGl2ZXJzeC5jb20.{BLOCK_HASH}.{TTL}.e30"
    ACCESS_TOKEN = "ZXJkMXFuazJ2bXVxeXdmcXRkbmttYXV2cG04bHMweGgwMGs4eGV1cHVhZjZjbTZjZDRyeDg5cXF6MHBwZ2w.YUhSMGNITTZMeTloY0drdWJYVnNkR2wyWlhKemVDNWpiMjAuYWI0NTkwMTNiMjdmZGM2ZmU5OGVlZDU2N2JkMGMxNzU0ZTA2MjhhNGNjMTY4ODNiZjAxNzBhMjlkYTM3YWQ0Ni44NjQwMC5lMzA.906e79d54e69e688680abee54ec0c49ce2561eb5abfd01865b31cb3ed738272c7cfc4fc8cc1c3590dd5757e622639b01a510945d7f7c9d1ceda20a50a817080d"
    BLOCK_TIMESTAMP = 1671009408
    ORIGIN = "https://api.multiversx.com"

    MULTISIG_ACCESS_TOKEN = "ZXJkMXFuazJ2bXVxeXdmcXRkbmttYXV2cG04bHMweGgwMGs4eGV1cHVhZjZjbTZjZDRyeDg5cXF6MHBwZ2w.YUhSMGNITTZMeTloY0drdWJYVnNkR2wyWlhKemVDNWpiMjAuYWI0NTkwMTNiMjdmZGM2ZmU5OGVlZDU2N2JkMGMxNzU0ZTA2MjhhNGNjMTY4ODNiZjAxNzBhMjlkYTM3YWQ0Ni44NjQwMC5leUp0ZFd4MGFYTnBaeUk2SW1WeVpERnhjWEZ4Y1hGeGNYRnhjWEZ4Y0dkeE9UUTBhRGRvTm0xamEzYzJjVEJrTTJjeU1qTmphbm8wZVhSMmEyVnVPRFoxTURCemVqZGpZWEozSW4w.b38b3766de5fcc9f66b1bb65662404238b1eddad18436bea39a694db591dc27bc2a66c62c4dfec3ce09021de83d324cd5f4e49a329833c67baafdd71ab2f750b"
    IMPERSONATE_ACCESS_TOKEN = "ZXJkMXFuazJ2bXVxeXdmcXRkbmttYXV2cG04bHMweGgwMGs4eGV1cHVhZjZjbTZjZDRyeDg5cXF6MHBwZ2w.YUhSMGNITTZMeTloY0drdWJYVnNkR2wyWlhKemVDNWpiMjAuYWI0NTkwMTNiMjdmZGM2ZmU5OGVlZDU2N2JkMGMxNzU0ZTA2MjhhNGNjMTY4ODNiZjAxNzBhMjlkYTM3YWQ0Ni44NjQwMC5leUpwYlhCbGNuTnZibUYwWlNJNkltVnlaREZ4Y1hGeGNYRnhjWEZ4Y1hGeGNHZHhPVFEwYURkb05tMWphM2MyY1RCa00yY3lNak5qYW5vMGVYUjJhMlZ1T0RaMU1EQnplamRqWVhKM0luMA.91c5ee2f4020f0c1f098331760c6963b6b300dc3002d9caa9479d8d1509edf4c44ee518d8f19506830232d76b5baeee5ab6f442354dac69a35e69c290b638d04"
    MULTISIG_ADDRESS = "erd1qqqqqqqqqqqqqpgq944h7h6mckw6q0d3g223cjz4ytvken86u00sz7carw"

    default_config = NativeAuthServerConfig(
        api_url="https://api.multiversx.com",
        accepted_origins=["https://api.multiversx.com"],
        max_expiry_seconds=86400,
        validate_impersonate_url="https://extras-api.multiversx.com/impersonate/allowed",
    )

    def test_simple_decode(self, mocker: Any):
        mock(mocker, 200, self.BLOCK_TIMESTAMP)
        mock(mocker, 200, [{"timestamp": self.BLOCK_TIMESTAMP}])

        server = NativeAuthServer(self.default_config)
        result = server.decode(self.ACCESS_TOKEN)

        assert result.address.to_bech32() == self.ADDRESS
        assert result.origin == self.ORIGIN
        assert result.ttl == self.TTL
        assert result.block_hash == self.BLOCK_HASH
        assert result.signature == bytes.fromhex(self.SIGNATURE)
        assert result.body == self.TOKEN

    def test_invalid_config_ttl(self):
        config = deepcopy(self.default_config)

        with pytest.raises(
            NativeAuthInvalidConfigError,
            match="Invalid `max_expiry_seconds`. Must be greater than 0 and less than or equal to 86400.",
        ):
            config.max_expiry_seconds = 86401
            NativeAuthServer(config)

        with pytest.raises(
            NativeAuthInvalidConfigError,
            match="Invalid `max_expiry_seconds`. Must be greater than 0 and less than or equal to 86400.",
        ):
            config.max_expiry_seconds = 0
            NativeAuthServer(config)

        with pytest.raises(
            NativeAuthInvalidConfigError,
            match="Invalid `max_expiry_seconds`. Must be greater than 0 and less than or equal to 86400.",
        ):
            config.max_expiry_seconds = -1
            NativeAuthServer(config)

        with pytest.raises(TypeError):
            config.max_expiry_seconds = "asd"  # type: ignore
            NativeAuthServer(config)

    def test_invalid_config_origin(self):
        config = deepcopy(self.default_config)

        with pytest.raises(
            NativeAuthInvalidConfigError,
            match=re.escape("`accepted_origins` must be a non-empty list of strings."),
        ):
            config.accepted_origins = []
            NativeAuthServer(config)

        with pytest.raises(
            NativeAuthInvalidConfigError,
            match=re.escape("`accepted_origins` must be a non-empty list of strings."),
        ):
            config.accepted_origins = "hello world"  # type: ignore
            NativeAuthServer(config)

    def test_invalid_token(self):
        server = NativeAuthServer(self.default_config)

        with pytest.raises(NativeAuthInvalidTokenError, match="The provided token in not a NativeAuth token."):
            server.decode("invalid token")

    def test_simple_validation_for_current_timestamp(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        server = NativeAuthServer(self.default_config)
        result = server.validate(self.ACCESS_TOKEN)

        assert result.address.to_bech32() == self.ADDRESS
        assert result.signer_address.to_bech32() == self.ADDRESS
        assert result.origin == self.ORIGIN
        assert result.issued == self.BLOCK_TIMESTAMP
        assert result.expires == self.BLOCK_TIMESTAMP + self.TTL

    def test_latest_possible_timestamp_validation(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP + self.TTL}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP + self.TTL}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        server = NativeAuthServer(self.default_config)
        result = server.validate(self.ACCESS_TOKEN)

        assert result.address.to_bech32() == self.ADDRESS
        assert result.signer_address.to_bech32() == self.ADDRESS
        assert result.origin == self.ORIGIN
        assert result.issued == self.BLOCK_TIMESTAMP
        assert result.expires == self.BLOCK_TIMESTAMP + self.TTL

    def test_origin_should_be_accepted(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP + self.TTL}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP + self.TTL}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        server = NativeAuthServer(self.default_config)
        result = server.validate(self.ACCESS_TOKEN)

        assert result.address.to_bech32() == self.ADDRESS
        assert result.signer_address.to_bech32() == self.ADDRESS
        assert result.origin == self.ORIGIN
        assert result.issued == self.BLOCK_TIMESTAMP
        assert result.expires == self.BLOCK_TIMESTAMP + self.TTL
        assert result.origin == self.ORIGIN

    def test_origin_should_not_be_accepted(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP + self.TTL}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP + self.TTL}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        config = deepcopy(self.default_config)
        config.accepted_origins = ["other-origin"]

        with pytest.raises(
            NativeAuthOriginNotAcceptedError, match=re.escape("The origin: https://api.multiversx.com is not accepted.")
        ):
            server = NativeAuthServer(config)
            server.validate(self.ACCESS_TOKEN)

    def test_block_hash_not_found(self, mocker: Any):
        mock(mocker, 404, None)

        with pytest.raises(
            NativeAuthInvalidBlockHashError,
            match=re.escape("Invalid block hash: ab459013b27fdc6fe98eed567bd0c1754e0628a4cc16883bf0170a29da37ad46"),
        ):
            server = NativeAuthServer(self.default_config)
            server.validate(self.ACCESS_TOKEN)

    def test_block_hash_unexpected_error(self, mocker: Any):
        mock(mocker, 500, requests.exceptions.RequestException("Internal Server error"), "Internal Server Error")

        with pytest.raises(Exception, match="Internal Server Error"):
            server = NativeAuthServer(self.default_config)
            server.validate(self.ACCESS_TOKEN)

    def test_expired_token(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP + self.TTL + 1}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP + self.TTL + 1}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        with pytest.raises(NativeAuthTokenExpiredError, match="The provided token has expired."):
            server = NativeAuthServer(self.default_config)
            server.validate(self.ACCESS_TOKEN)

    def test_invalid_signature(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        with pytest.raises(NativeAuthInvalidSignatureError, match="The provided signature is invalid."):
            server = NativeAuthServer(self.default_config)
            server.validate(self.ACCESS_TOKEN + "abbbbbbbbb")

    def test_greater_ttl_than_max_expiry_seconds(self):
        config = deepcopy(self.default_config)
        config.max_expiry_seconds = 80000
        server = NativeAuthServer(config)

        with pytest.raises(
            NativeAuthInvalidTokenTtlError,
            match="The provided TTL: 86400 is larger than the maximum allowed TTL: 80000.",
        ):
            server.validate(self.ACCESS_TOKEN)

    def test_cache_hit(self):
        block_hash = self.BLOCK_HASH
        block_timestamp = self.BLOCK_TIMESTAMP

        class NativeAuthCache:
            def get(self, key: str) -> Optional[str]:
                if key == f"block:timestamp:{block_hash}":
                    return str(block_timestamp)
                if key == "block:timestamp:latest":
                    return str(block_timestamp)
                raise Exception(f"Key {key} not found")

            def set(self, key: str, value: int, ttl: int) -> None:
                pass

        server = NativeAuthServer(self.default_config, NativeAuthCache())
        result = server.validate(self.ACCESS_TOKEN)

        assert result.address.to_bech32() == self.ADDRESS
        assert result.signer_address.to_bech32() == self.ADDRESS
        assert result.origin == self.ORIGIN
        assert result.issued == self.BLOCK_TIMESTAMP
        assert result.expires == self.BLOCK_TIMESTAMP + self.TTL

    def test_cache_miss(self, mocker: Any):
        class NativeAuthCache:
            def get(self, key: str) -> Optional[str]:
                return None

            def set(self, key: str, value: int, ttl: int) -> None:
                pass

        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        server = NativeAuthServer(self.default_config, NativeAuthCache())
        result = server.validate(self.ACCESS_TOKEN)

        assert result.address.to_bech32() == self.ADDRESS
        assert result.signer_address.to_bech32() == self.ADDRESS
        assert result.origin == self.ORIGIN
        assert result.issued == self.BLOCK_TIMESTAMP
        assert result.expires == self.BLOCK_TIMESTAMP + self.TTL

    def test_wildacard_is_accepted(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        config = deepcopy(self.default_config)
        config.accepted_origins = ["*"]
        server = NativeAuthServer(config)
        result = server.validate(self.ACCESS_TOKEN)

        assert result.address.to_bech32() == self.ADDRESS
        assert result.signer_address.to_bech32() == self.ADDRESS
        assert result.origin == self.ORIGIN
        assert result.issued == self.BLOCK_TIMESTAMP
        assert result.expires == self.BLOCK_TIMESTAMP + self.TTL

    def test_wildacard_origin_is_accepted(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        config = deepcopy(self.default_config)
        config.accepted_origins = ["*.multiversx.com"]
        server = NativeAuthServer(config)
        result = server.validate(self.ACCESS_TOKEN)

        assert result.address.to_bech32() == self.ADDRESS
        assert result.signer_address.to_bech32() == self.ADDRESS
        assert result.origin == self.ORIGIN
        assert result.issued == self.BLOCK_TIMESTAMP
        assert result.expires == self.BLOCK_TIMESTAMP + self.TTL

    def test_two_wildacards_not_accepted(self):
        config = deepcopy(self.default_config)
        config.accepted_origins = ["*.multiversx*.com"]

        with pytest.raises(
            NativeAuthInvalidWildcardOriginError, match=re.escape("Invalid wildcard origin: *.multiversx*.com")
        ):
            server = NativeAuthServer(config)
            server.validate(self.ACCESS_TOKEN)

    def test_wildacard_validation_protocol_not_accepted(self):
        config = deepcopy(self.default_config)
        config.accepted_origins = ["www.*.multiversx.com"]

        with pytest.raises(
            NativeAuthInvalidWildcardOriginError, match=re.escape("Invalid wildcard origin: www.*.multiversx.com")
        ):
            server = NativeAuthServer(config)
            server.validate(self.ACCESS_TOKEN)

    def test_wildacard_origin_not_accepted(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        config = deepcopy(self.default_config)
        config.accepted_origins = ["*.test.com"]

        with pytest.raises(
            NativeAuthOriginNotAcceptedError, match=re.escape("The origin: https://api.multiversx.com is not accepted.")
        ):
            server = NativeAuthServer(config)
            server.validate(self.ACCESS_TOKEN)

    def test_https_wildacard_origin_is_accepted(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        config = deepcopy(self.default_config)
        config.accepted_origins = ["https://*.multiversx.com"]

        server = NativeAuthServer(config)
        result = server.validate(self.ACCESS_TOKEN)

        assert result.address.to_bech32() == self.ADDRESS
        assert result.signer_address.to_bech32() == self.ADDRESS
        assert result.origin == self.ORIGIN
        assert result.issued == self.BLOCK_TIMESTAMP
        assert result.expires == self.BLOCK_TIMESTAMP + self.TTL

    def test_http_wildacard_origin_is_accepted(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        config = deepcopy(self.default_config)
        config.accepted_origins = ["http://*.multiversx.com"]

        with pytest.raises(
            NativeAuthOriginNotAcceptedError, match=re.escape("The origin: https://api.multiversx.com is not accepted.")
        ):
            server = NativeAuthServer(config)
            server.validate(self.ACCESS_TOKEN)

    def test_origin_is_accepted_with_custom_validation(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        config = deepcopy(self.default_config)
        config.accepted_origins = ["other-origin"]
        config.is_origin_accepted = lambda origin: origin == self.ORIGIN

        server = NativeAuthServer(config)
        result = server.validate(self.ACCESS_TOKEN)

        assert result.address.to_bech32() == self.ADDRESS
        assert result.signer_address.to_bech32() == self.ADDRESS
        assert result.origin == self.ORIGIN
        assert result.issued == self.BLOCK_TIMESTAMP
        assert result.expires == self.BLOCK_TIMESTAMP + self.TTL

    def test_origin_is_not_accepted_with_custom_validation(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        config = deepcopy(self.default_config)
        config.accepted_origins = ["other-origin"]
        config.is_origin_accepted = lambda origin: origin != self.ORIGIN

        with pytest.raises(
            NativeAuthOriginNotAcceptedError, match="The origin: https://api.multiversx.com is not accepted."
        ):
            server = NativeAuthServer(config)
            server.validate(self.ACCESS_TOKEN)

    def test_validation_for_multisign_key_via_api(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP}}}]',
            },
            {
                "code": 200,
                "response": True,
            },
        ]
        mock_side_effect(mocker, responses)

        server = NativeAuthServer(self.default_config)
        result = server.validate(self.MULTISIG_ACCESS_TOKEN)

        assert result.address.to_bech32() == self.MULTISIG_ADDRESS
        assert result.signer_address.to_bech32() == self.ADDRESS
        assert result.origin == self.ORIGIN
        assert result.issued == self.BLOCK_TIMESTAMP
        assert result.expires == self.BLOCK_TIMESTAMP + self.TTL
        assert result.extra_info == {"multisig": self.MULTISIG_ADDRESS}

    def test_validation_for_impersonate_key_via_api(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP}}}]',
            },
            {
                "code": 200,
                "response": True,
            },
        ]
        mock_side_effect(mocker, responses)

        server = NativeAuthServer(self.default_config)
        result = server.validate(self.IMPERSONATE_ACCESS_TOKEN)

        assert result.address.to_bech32() == self.MULTISIG_ADDRESS
        assert result.signer_address.to_bech32() == self.ADDRESS
        assert result.origin == self.ORIGIN
        assert result.issued == self.BLOCK_TIMESTAMP
        assert result.expires == self.BLOCK_TIMESTAMP + self.TTL
        assert result.extra_info == {"impersonate": self.MULTISIG_ADDRESS}

    def test_validation_for_impersonate_key_via_callback(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        config = deepcopy(self.default_config)
        config.validate_impersonate_callback = lambda address, impersonate: True
        server = NativeAuthServer(config)
        result = server.validate(self.IMPERSONATE_ACCESS_TOKEN)

        assert result.address.to_bech32() == self.MULTISIG_ADDRESS
        assert result.signer_address.to_bech32() == self.ADDRESS
        assert result.origin == self.ORIGIN
        assert result.issued == self.BLOCK_TIMESTAMP
        assert result.expires == self.BLOCK_TIMESTAMP + self.TTL
        assert result.extra_info == {"impersonate": self.MULTISIG_ADDRESS}

    def test_impersonate_request_fails(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP}}}]',
            },
            {
                "exception": requests.exceptions.RequestException("Forbidden"),
            },
        ]
        mock_side_effect(mocker, responses)

        with pytest.raises(NativeAuthInvalidImpersonateError):
            server = NativeAuthServer(self.default_config)
            server.validate(self.MULTISIG_ACCESS_TOKEN)

    def test_impersonate_cache_hit(self):
        address = self.ADDRESS
        multisig_address = self.MULTISIG_ADDRESS
        block_hash = self.BLOCK_HASH
        block_timestamp = self.BLOCK_TIMESTAMP

        class NativeAuthCache:
            def get(self, key: str) -> Optional[str]:
                if key == f"impersonate:{address}:{multisig_address}":
                    return str(1)
                if key == f"block:timestamp:{block_hash}":
                    return str(block_timestamp)
                if key == "block:timestamp:latest":
                    return str(block_timestamp)
                raise Exception(f"Key {key} not found")

            def set(self, key: str, value: int, ttl: int) -> None:
                pass

        server = NativeAuthServer(self.default_config, NativeAuthCache())
        result = server.validate(self.IMPERSONATE_ACCESS_TOKEN)

        assert result.address.to_bech32() == self.MULTISIG_ADDRESS
        assert result.signer_address.to_bech32() == self.ADDRESS
        assert result.origin == self.ORIGIN
        assert result.issued == self.BLOCK_TIMESTAMP
        assert result.expires == self.BLOCK_TIMESTAMP + self.TTL
        assert result.extra_info == {"impersonate": self.MULTISIG_ADDRESS}

    def test_impersonate_cache_miss(self, mocker: Any):
        address = self.ADDRESS
        multisig_address = self.MULTISIG_ADDRESS
        block_hash = self.BLOCK_HASH
        block_timestamp = self.BLOCK_TIMESTAMP

        class NativeAuthCache:
            def get(self, key: str) -> Optional[str]:
                if key == f"impersonate:{address}:{multisig_address}":
                    return None
                if key == f"block:timestamp:{block_hash}":
                    return str(block_timestamp)
                if key == "block:timestamp:latest":
                    return str(block_timestamp)
                raise Exception(f"Key {key} not found")

            def set(self, key: str, value: int, ttl: int) -> None:
                pass

        mock(mocker, 200, True)

        server = NativeAuthServer(self.default_config, NativeAuthCache())
        result = server.validate(self.IMPERSONATE_ACCESS_TOKEN)

        assert result.address.to_bech32() == self.MULTISIG_ADDRESS
        assert result.signer_address.to_bech32() == self.ADDRESS
        assert result.origin == self.ORIGIN
        assert result.issued == self.BLOCK_TIMESTAMP
        assert result.expires == self.BLOCK_TIMESTAMP + self.TTL
        assert result.extra_info == {"impersonate": self.MULTISIG_ADDRESS}

    def test_is_valid(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP + self.TTL}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP + self.TTL}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        server = NativeAuthServer(self.default_config)
        is_valid = server.is_valid(self.ACCESS_TOKEN)
        assert is_valid

    def test_is_not_valid(self, mocker: Any):
        responses = [
            {
                "code": 200,
                "response": self.BLOCK_TIMESTAMP,
                "text": str(self.BLOCK_TIMESTAMP),
            },
            {
                "code": 200,
                "response": [{"timestamp": self.BLOCK_TIMESTAMP}],
                "text": f'[{{"timestamp": {self.BLOCK_TIMESTAMP}}}]',
            },
        ]
        mock_side_effect(mocker, responses)

        config = deepcopy(self.default_config)
        config.accepted_origins = ["http://*.multiversx.com"]

        server = NativeAuthServer(config)
        is_valid = server.is_valid(self.ACCESS_TOKEN)
        assert not is_valid
