
from typing import List, Protocol

from multiversx_sdk_core.interfaces import IAddress


class ITransactionOnNetwork(Protocol):
    hash: str
    contract_results: 'IContractResults'
    logs: 'ITransactionLogs'


class IContractResults(Protocol):
    items: List['IContractResultItem']


class IContractResultItem(Protocol):
    logs: 'ITransactionLogs'


class ITransactionLogs(Protocol):
    events: List['ITransactionEvent']


class ITransactionEvent(Protocol):
    address: IAddress
    identifier: str
    topics: List['ITransactionEventTopic']
    data: str


class ITransactionEventTopic(Protocol):
    raw: bytes
