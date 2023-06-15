
from typing import Protocol

from multiversx_sdk_core.interfaces import IAddress


class ITransactionOnNetwork(Protocol):
    hash: str
    contract_results: 'IContractResults'
    logs: 'ITransactionLogs'


class IContractResults(Protocol):
    items: 'IContractResultItem'


class IContractResultItem(Protocol):
    logs: 'ITransactionLogs'


class ITransactionLogs(Protocol):
    events: 'ITransactionEvent'


class ITransactionEvent(Protocol):
    address: IAddress
    identifier: str
    topics: 'ITransactionEventTopic'
    data: str


class ITransactionEventTopic(Protocol):
    pass
