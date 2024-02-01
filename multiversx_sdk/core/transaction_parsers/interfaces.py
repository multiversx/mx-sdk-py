from typing import Protocol, Sequence

from multiversx_sdk.core.interfaces import IAddress


class ITransactionOnNetwork(Protocol):
    @property
    def contract_results(self) -> 'IContractResults': ...
    @property
    def logs(self) -> 'ITransactionLogs': ...


class IContractResults(Protocol):
    @property
    def items(self) -> Sequence['IContractResultItem']: ...


class IContractResultItem(Protocol):
    @property
    def logs(self) -> 'ITransactionLogs': ...


class ITransactionLogs(Protocol):
    @property
    def events(self) -> Sequence['ITransactionEvent']: ...


class ITransactionEvent(Protocol):
    @property
    def address(self) -> IAddress: ...

    @property
    def identifier(self) -> str: ...

    @property
    def topics(self) -> Sequence['ITransactionEventTopic']: ...

    @property
    def data(self) -> str: ...


class ITransactionEventTopic(Protocol):
    @property
    def raw(self) -> bytes: ...
