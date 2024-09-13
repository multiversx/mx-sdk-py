from typing import Any, Dict

from multiversx_sdk.core.smart_contract_query import SmartContractQuery


class SmartContractQueryConverter:
    def __init__(self) -> None:
        pass

    def smart_contract_query_to_dictionary(self, query: SmartContractQuery) -> Dict[str, Any]:
        request: Dict[str, Any] = {
            'scAddress': query.contract,
            'funcName': query.function,
            'value': str(query.value if query.value else 0),
            'args': [arg.hex() for arg in query.arguments]
        }
        caller = query.caller

        if caller:
            request['caller'] = caller

        return request
