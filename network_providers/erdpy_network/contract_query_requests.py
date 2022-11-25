from typing import Dict, Any
from erdpy_network.interface import IContractQuery


class ContractQueryRequest:
    def __init__(self, query: IContractQuery):
        self.query = query

    def to_http_request(self) -> Dict[str, Any]:
        request = {'scAddress': self.query.get_address().bech32(),
                   'funcName': self.query.get_function(),
                   'value': str(self.query.get_value()),
                   'args': self.query.get_encoded_arguments()
                   }

        if self.query.get_caller() is not None:
            request['caller'] = self.query.get_caller().bech32()

        return request
