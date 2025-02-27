import json
from pathlib import Path

from multiversx_sdk.validators.errors import (
    CannotReadValidatorsDataError,
    ValidatorsFileNotFoundError,
)
from multiversx_sdk.wallet.validator_keys import ValidatorPublicKey
from multiversx_sdk.wallet.validator_pem import ValidatorPEM
from multiversx_sdk.wallet.validator_signer import ValidatorSigner


class ValidatorsFile:
    def __init__(self, validators_file_path: Path):
        self.validators_file_path = validators_file_path
        self._validators_data = self._read_json_file_validators()

    def get_num_of_nodes(self) -> int:
        return len(self._validators_data.get("validators", []))

    def get_validators_list(self):
        return self._validators_data.get("validators", [])

    def load_signers(self) -> list[ValidatorSigner]:
        signers: list[ValidatorSigner] = []
        for validator in self.get_validators_list():
            pem_file = self._load_validator_pem(validator)
            validator_signer = ValidatorSigner(pem_file.secret_key)
            signers.append(validator_signer)

        return signers

    def load_public_keys(self) -> list[ValidatorPublicKey]:
        public_keys: list[ValidatorPublicKey] = []

        for validator in self.get_validators_list():
            pem_file = self._load_validator_pem(validator)
            public_keys.append(pem_file.secret_key.generate_public_key())

        return public_keys

    def _load_validator_pem(self, validator: dict[str, str]) -> ValidatorPEM:
        # Get path of "pemFile", make it absolute
        validator_pem = Path(validator.get("pemFile", "")).expanduser()
        validator_pem = (
            validator_pem if validator_pem.is_absolute() else self.validators_file_path.parent / validator_pem
        )

        return ValidatorPEM.from_file(validator_pem)

    def _read_json_file_validators(self):
        val_file = self.validators_file_path.expanduser()

        if not val_file.is_file():
            raise ValidatorsFileNotFoundError(str(val_file))

        with open(val_file, "r") as json_file:
            try:
                data = json.load(json_file)
            except Exception:
                raise CannotReadValidatorsDataError(str(val_file))
            return data
