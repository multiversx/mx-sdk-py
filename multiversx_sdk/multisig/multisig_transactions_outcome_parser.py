from typing import Optional

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.core.address import Address
from multiversx_sdk.core.config import LibraryConfig
from multiversx_sdk.core.transaction_on_network import TransactionOnNetwork
from multiversx_sdk.smart_contracts.smart_contract_transactions_outcome_parser import (
    SmartContractTransactionsOutcomeParser,
)
from multiversx_sdk.smart_contracts.smart_contract_transactions_outcome_parser_types import (
    ParsedSmartContractCallOutcome,
    SmartContractDeployOutcome,
)


class MultisigTransactionsOutcomeParser:
    def __init__(self, abi: Abi) -> None:
        self._parser = SmartContractTransactionsOutcomeParser(abi)

    def parse_deploy(self, transaction_on_network: TransactionOnNetwork) -> SmartContractDeployOutcome:
        return self._parser.parse_deploy(transaction_on_network)

    def parse_propose_action(self, transaction_on_network: TransactionOnNetwork) -> int:
        outcome = self._parser.parse_execute(transaction_on_network)
        self._raise_for_return_code_in_outcome(outcome)
        [value] = outcome.values
        return value

    def parse_perform_action(self, transaction_on_network: TransactionOnNetwork) -> Optional[Address]:
        outcome = self._parser.parse_execute(transaction_on_network)
        self._raise_for_return_code_in_outcome(outcome)
        [value] = outcome.values
        return Address(value, LibraryConfig.default_address_hrp) if value else None

    def _raise_for_return_code_in_outcome(self, outcome: ParsedSmartContractCallOutcome):
        is_ok = outcome.return_code == "ok"
        if not is_ok:
            raise Exception(outcome.return_code, outcome.return_message)
