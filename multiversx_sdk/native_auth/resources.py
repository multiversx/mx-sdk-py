from dataclasses import dataclass
from typing import Any

from multiversx_sdk.core.address import Address


@dataclass
class WildcardOrigin:
    protocol: str = ""
    domain: str = ""


@dataclass
class NativeAuthDecoded:
    ttl: int = 0
    origin: str = ""
    address: Address = Address.empty()
    signature: bytes = b""
    black_hash: str = ""
    body: str = ""
    extra_info: Any = None


@dataclass
class NativeAuthValidateResult:
    issued: int = 0
    expires: int = 0
    address: Address = Address.empty()
    signer_address: Address = Address.empty()
    origin: str = ""
    extra_info: dict[str, str] = {}
