from typing import Dict, Any
from erdpy_network.interface import IContractQuery


class ContractQueryRequest:
    query: IContractQuery

    def __init__(self, query: IContractQuery):
        self.query = query

    def to_http_request(self) -> Dict[str, Any]:
        request = {'scAddress': self.query.address.bech32(),
                   'funcName': self.query.function,
                   'value': self.query.value,
                   'args': self.query.get_encoded_arguments()
                   }

        if self.query.caller is not None:
            request['caller'] = self.query.caller.bech32()

        return request
