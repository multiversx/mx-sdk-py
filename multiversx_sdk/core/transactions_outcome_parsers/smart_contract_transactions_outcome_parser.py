from multiversx_sdk.core.address import Address
from multiversx_sdk.core.transaction_on_network import (
    SmartContractCallOutcome, TransactionEvent, TransactionOnNetwork,
    find_events_by_identifier)
from multiversx_sdk.core.transactions_outcome_parsers.smart_contract_transactions_outcome_parser_types import (
    DeployedSmartContract, SmartContractDeployOutcome)
from multiversx_sdk.network_providers.constants import DEFAULT_ADDRESS_HRP


class SmartContractTransactionsOutcomeParser:
    def __init__(self) -> None:
        pass

    def get_direct_sc_call(self, transaction: TransactionOnNetwork) -> SmartContractCallOutcome:
        # will copy the logic from js, the "neural" network, to convert to a sc call outcome
        ...

    def parse_deploy(self, transaction: TransactionOnNetwork) -> SmartContractDeployOutcome:
        direct_call_outcome = self.get_direct_sc_call(transaction)
        events = find_events_by_identifier(transaction, "SCDeploy")
        contracts = [self._parse_sc_deploy_event(event) for event in events]

        return SmartContractDeployOutcome(direct_call_outcome.return_code, direct_call_outcome.return_message, contracts)

    def _parse_sc_deploy_event(self, event: TransactionEvent) -> DeployedSmartContract:
        contract_address_topic = event.topics[0] if event.topics[0] else b''
        owner_address_topic = event.topics[1] if event.topics[1] else b''
        code_hash_topic = event.topics[2] if event.topics[2] else b''

        contract_address = Address(contract_address_topic, DEFAULT_ADDRESS_HRP).to_bech32() if len(contract_address_topic) else ""
        owner_address = Address(owner_address_topic, DEFAULT_ADDRESS_HRP).to_bech32() if len(owner_address_topic) else ""
        code_hash = code_hash_topic

        return DeployedSmartContract(contract_address, owner_address, code_hash)
