from multiversx_sdk.abi.abi_definition import AbiDefinition


class Abi:
    def __init__(self, definition: AbiDefinition) -> None:
        self.definition = definition
