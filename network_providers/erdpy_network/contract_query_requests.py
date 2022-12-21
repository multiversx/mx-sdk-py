from typing import Any, Dict

from erdpy_network.interface import IContractQuery


class ContractQueryRequest:
    def __init__(self, query: IContractQuery):
        self.query = query

    def to_http_request(self) -> Dict[str, Any]:
        request: Dict[str, Any] = {'scAddress': self.query.contract.bech32(),
                                   'funcName': self.query.function,
                                   'value': str(self.query.value),
                                   'args': self.query.encoded_arguments
                                   }
        caller = self.query.caller

        if caller:
            request['caller'] = caller.bech32()

        return request
