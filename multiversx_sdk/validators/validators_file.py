import json
from pathlib import Path
from typing import Any

from multiversx_sdk.validators.errors import (
    CannotReadValidatorsDataError,
    ValidatorsFileNotFoundError,
)
from multiversx_sdk.wallet.validator_keys import ValidatorPublicKey
from multiversx_sdk.wallet.validator_pem import ValidatorPEM
from multiversx_sdk.wallet.validator_signer import ValidatorSigner


class ValidatorsFile:
    def __init__(self, validator_signers: list[ValidatorSigner]):
        self.signers = validator_signers

    @staticmethod
    def new_from_validators_file(path: Path):
        validators_data = _read_json_file_validators(path)
        validators_list: Any = validators_data.get("validators", [])
        signers = _load_signers(validators_list)
        return ValidatorsFile(signers)

    @staticmethod
    def new_from_pem(file: Path) -> "ValidatorsFile":
        validator_pem_files = ValidatorPEM.from_file_all(file)
        signers = [ValidatorSigner(pem.secret_key) for pem in validator_pem_files]
        return ValidatorsFile(signers)

    def get_num_of_nodes(self) -> int:
        return len(self.signers)

    def get_signers(self) -> list[ValidatorSigner]:
        return self.signers

    def get_public_keys(self) -> list[ValidatorPublicKey]:
        return [signer.get_pubkey() for signer in self.signers]


def _load_signers(validators: list[dict[str, str]]) -> list[ValidatorSigner]:
    signers: list[ValidatorSigner] = []
    for validator in validators:
        pem_file = _load_validator_pem(validator)
        validator_signer = ValidatorSigner(pem_file.secret_key)
        signers.append(validator_signer)

    return signers


def _load_validator_pem(validator: dict[str, str]) -> ValidatorPEM:
    # Get path of "pemFile", make it absolute
    validator_pem = Path(validator.get("pemFile", "")).expanduser().resolve()
    return ValidatorPEM.from_file(validator_pem)


def _read_json_file_validators(validators_file: Path) -> dict[str, str]:
    val_file = validators_file.expanduser()

    if not val_file.is_file():
        raise ValidatorsFileNotFoundError(str(val_file))

    with open(val_file, "r") as json_file:
        try:
            data = json.load(json_file)
        except Exception:
            raise CannotReadValidatorsDataError(str(val_file))
        return data
