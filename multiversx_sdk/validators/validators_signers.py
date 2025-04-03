from pathlib import Path

from multiversx_sdk.wallet.validator_keys import ValidatorPublicKey
from multiversx_sdk.wallet.validator_pem import ValidatorPEM
from multiversx_sdk.wallet.validator_signer import ValidatorSigner


class ValidatorsSigners:
    def __init__(self, validator_signers: list[ValidatorSigner]):
        self.signers = validator_signers

    @staticmethod
    def new_from_pem(file: Path) -> "ValidatorsSigners":
        validator_pem_files = ValidatorPEM.from_file_all(file)
        signers = [ValidatorSigner(pem.secret_key) for pem in validator_pem_files]
        return ValidatorsSigners(signers)

    def get_num_of_nodes(self) -> int:
        return len(self.signers)

    def get_signers(self) -> list[ValidatorSigner]:
        return self.signers

    def get_public_keys(self) -> list[ValidatorPublicKey]:
        return [signer.get_pubkey() for signer in self.signers]
