class TypeFormula:
    def __init__(self, name: str, type_parameters: list["TypeFormula"]) -> None:
        self.name: str = name
        self.type_parameters: list[TypeFormula] = type_parameters

    def __str__(self) -> str:
        if self.type_parameters:
            type_parameters = ", ".join([str(type_parameter) for type_parameter in self.type_parameters])
            return f"{self.name}<{type_parameters}>"
        else:
            return self.name
