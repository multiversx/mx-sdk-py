from enum import Enum
from typing import Optional, Union

from multiversx_sdk.abi.abi import Abi
from multiversx_sdk.core import (
    Address,
    SmartContractResult,
    TransactionEvent,
    TransactionOnNetwork,
    find_events_by_identifier,
)
from multiversx_sdk.core.constants import ARGS_SEPARATOR
from multiversx_sdk.smart_contracts.smart_contract_transactions_outcome_parser_types import (
    DeployedSmartContract,
    ParsedSmartContractCallOutcome,
    SmartContractDeployOutcome,
)


class Events(Enum):
    SCDeploy = "SCDeploy"
    SignalError = "signalError"
    WriteLog = "writeLog"


class SmartContractCallOutcome:
    """**For internal use only.**"""

    def __init__(
        self,
        function: str = "",
        return_data_parts: list[bytes] = [],
        return_message: str = "",
        return_code: str = "",
    ) -> None:
        self.function = function
        self.return_data_parts = return_data_parts
        self.return_message = return_message
        self.return_code = return_code


class SmartContractTransactionsOutcomeParser:
    def __init__(self, abi: Optional[Abi] = None) -> None:
        self.abi = abi

    def parse_deploy(self, transaction: TransactionOnNetwork) -> SmartContractDeployOutcome:
        direct_call_outcome = self._find_direct_smart_contract_call_outcome(transaction)
        events = find_events_by_identifier(transaction, Events.SCDeploy.value)
        contracts = [self._parse_sc_deploy_event(event) for event in events]

        return SmartContractDeployOutcome(
            direct_call_outcome.return_code,
            direct_call_outcome.return_message,
            contracts,
        )

    def parse_execute(
        self, transaction: TransactionOnNetwork, function: Optional[str] = None
    ) -> ParsedSmartContractCallOutcome:
        direct_call_outcome = self._find_direct_smart_contract_call_outcome(transaction)

        if self.abi is None:
            return ParsedSmartContractCallOutcome(
                values=direct_call_outcome.return_data_parts,
                return_code=direct_call_outcome.return_code,
                return_message=direct_call_outcome.return_message,
            )

        function_name = function or direct_call_outcome.function
        if not function_name:
            raise Exception(
                'Function name is not available in the transaction, thus endpoint definition (ABI) cannot be picked (for parsing). Please provide the "function" parameter explicitly.'
            )

        values = self.abi.decode_endpoint_output_parameters(function_name, direct_call_outcome.return_data_parts)
        return ParsedSmartContractCallOutcome(
            values=values,
            return_code=direct_call_outcome.return_code,
            return_message=direct_call_outcome.return_message,
        )

    def _find_direct_smart_contract_call_outcome(self, transaction: TransactionOnNetwork) -> SmartContractCallOutcome:
        outcome = self._find_direct_sc_call_outcome_within_sc_results(transaction)
        if outcome:
            return outcome

        outcome = self._find_direct_sc_call_outcome_if_error(transaction)
        if outcome:
            return outcome

        outcome = self._find_direct_sc_call_outcome_within_write_log_events(transaction)
        if outcome:
            return outcome

        return SmartContractCallOutcome(function=transaction.function)

    def _find_direct_sc_call_outcome_within_sc_results(
        self, transaction: TransactionOnNetwork
    ) -> Union[SmartContractCallOutcome, None]:
        eligible_results: list[SmartContractResult] = []

        for result in transaction.smart_contract_results:
            matches_criteria_on_data = result.data.decode().startswith(ARGS_SEPARATOR)
            matches_criteria_on_receiver = result.receiver == transaction.sender
            matches_criteria_on_previous_hash = result

            matches_criteria = (
                matches_criteria_on_data and matches_criteria_on_receiver and matches_criteria_on_previous_hash
            )

            if matches_criteria:
                eligible_results.append(result)

        if len(eligible_results) == 0:
            return None

        if len(eligible_results) > 1:
            raise Exception(
                f"More than one smart contract result (holding the return data) found for transaction: {transaction.hash.hex()}"
            )

        result = eligible_results[0]
        _, return_code, *return_data_parts = self._string_to_bytes_list(result.data.decode())
        return_code = return_code.decode() if return_code else ""

        return SmartContractCallOutcome(
            function=transaction.function,
            return_code=return_code,
            return_message=result.raw.get("returnMessage") or return_code,
            return_data_parts=return_data_parts,
        )

    def _find_direct_sc_call_outcome_if_error(
        self, transaction: TransactionOnNetwork
    ) -> Union[SmartContractCallOutcome, None]:
        event_identifier = Events.SignalError.value
        eligible_events: list[TransactionEvent] = []

        # first, we search the logs
        eligible_events = [event for event in transaction.logs.events if event.identifier == event_identifier]

        # then, we search in the logs of contract_results
        for result in transaction.smart_contract_results:
            if result.raw.get("prevTxHash", "") != transaction.hash:
                continue

            for event in result.logs.events:
                if event.identifier == event_identifier:
                    eligible_events.append(event)

        if len(eligible_events) == 0:
            return None

        if len(eligible_events) > 1:
            raise Exception(f'More than one "{event_identifier}" event found for transaction: {transaction.hash.hex()}')

        event = eligible_events[0]
        data = event.data.decode()
        last_topic = event.topics[-1] if event.topics else None
        parts = self._string_to_bytes_list(data)
        # Assumption: the last part is the return code.
        return_code = parts[-1] if parts else None

        return_message = event_identifier
        if return_code:
            return_message = return_code.decode()

        if last_topic:
            return_message = last_topic.decode(errors="replace")

        return SmartContractCallOutcome(
            function=transaction.function,
            return_code=return_code.decode() if return_code else event_identifier,
            return_message=return_message,
        )

    def _find_direct_sc_call_outcome_within_write_log_events(
        self, transaction: TransactionOnNetwork
    ) -> Union[SmartContractCallOutcome, None]:
        event_identifier = Events.WriteLog.value
        eligible_events: list[TransactionEvent] = []

        # first, we search the logs
        eligible_events = [event for event in transaction.logs.events if event.identifier == event_identifier]

        # then, we search in the logs of contract_results
        for restult in transaction.smart_contract_results:
            if restult.raw.get("prevTxHash", "") != transaction.hash.hex():
                continue

            for event in restult.logs.events:
                if event.identifier == event_identifier:
                    eligible_events.append(event)

        if len(eligible_events) == 0:
            return None

        if len(eligible_events) > 1:
            raise Exception(f'More than one "{event_identifier}" event found for transaction: {transaction.hash.hex()}')

        event = eligible_events[0]
        data = event.data.decode()
        _, return_code, *return_data_parts = self._string_to_bytes_list(data)
        return_code = return_code.decode() if return_code else ""

        return SmartContractCallOutcome(
            function=transaction.function,
            return_code=return_code,
            return_message=return_code,
            return_data_parts=return_data_parts,
        )

    def _parse_sc_deploy_event(self, event: TransactionEvent) -> DeployedSmartContract:
        if not event.topics[0]:
            raise Exception("No topic found for contract address")
        contract_address_topic = event.topics[0]

        if not event.topics[1]:
            raise Exception("No topic found for owner address")
        owner_address_topic = event.topics[1]

        code_hash_topic = event.topics[2] if event.topics[2] else b""

        contract_address = Address(contract_address_topic)
        owner_address = Address(owner_address_topic)
        code_hash = code_hash_topic

        return DeployedSmartContract(contract_address, owner_address, code_hash)

    def _string_to_bytes_list(self, joined_string: str) -> list[bytes]:
        """Returns raw bytes from an arguments string (e.g. aa@bb@@cc)."""
        # We also keep the zero-length bytes (they could encode missing options, Option<T>).
        parts = joined_string.split(ARGS_SEPARATOR)
        output: list[bytes] = []

        for part in parts:
            try:
                output.append(bytes.fromhex(part))
            except:
                output.append(b"")

        return output
