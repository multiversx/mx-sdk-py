from typing import Any

from multiversx_sdk.abi.type_formula import TypeFormula


class TypeFormulaParser:
    BEGIN_TYPE_PARAMETERS = "<"
    END_TYPE_PARAMETERS = ">"
    COMMA = ","
    PUNCTUATION = [COMMA, BEGIN_TYPE_PARAMETERS, END_TYPE_PARAMETERS]

    def parse_expression(self, expression: str) -> TypeFormula:
        expression = expression.strip()
        tokens = [token for token in self.tokenize_expression(expression) if token != self.COMMA]
        stack: list[Any] = []

        for token in tokens:
            if self.is_punctuation(token):
                if self.is_end_of_type_parameters(token):
                    type_formula = self.acquire_type_with_parameters(stack)
                    stack.append(type_formula)
                elif self.is_beginning_of_type_parameters(token):
                    # This symbol is pushed as a simple string.
                    stack.append(token)
                else:
                    raise ValueError(f"unexpected token (punctuation): {token}")
            else:
                # It's a type name. We push it as a simple string.
                stack.append(token)

        if len(stack) != 1:
            raise ValueError(f"unexpected stack length at end of parsing: {len(stack)}")
        if stack[0] in self.PUNCTUATION:
            raise ValueError("unexpected root element")

        item = stack[0]

        if isinstance(item, TypeFormula):
            return item
        elif isinstance(item, str):
            # Expression contained a simple, non-generic type.
            return TypeFormula(item, [])
        else:
            raise ValueError(f"Unexpected item on stack: {item}")

    def tokenize_expression(self, expression: str) -> list[str]:
        tokens: list[str] = []
        current_token = ""

        for character in expression:
            if self.is_punctuation(character):
                if current_token:
                    # Retain current token
                    tokens.append(current_token.strip())
                    # Reset current token
                    current_token = ""
                # Punctuation character
                tokens.append(character)
            else:
                current_token += character

        if current_token:
            # Retain the last token (if any).
            tokens.append(current_token.strip())

        return tokens

    def acquire_type_with_parameters(self, stack: list[Any]) -> TypeFormula:
        type_parameters = self.acquire_type_parameters(stack)
        type_name = stack.pop()
        type_formula = TypeFormula(type_name, type_parameters[::-1])
        return type_formula

    def acquire_type_parameters(self, stack: list[Any]) -> list[TypeFormula]:
        type_parameters: list[TypeFormula] = []

        while True:
            item = stack.pop()

            if item is None:
                raise ValueError("badly specified type parameters")

            if self.is_beginning_of_type_parameters(item):
                # We've acquired all type parameters.
                break

            if isinstance(item, TypeFormula):
                # Type parameter is a previously-acquired type.
                type_parameters.append(item)
            elif isinstance(item, str):
                # Type parameter is a simple, non-generic type.
                type_parameters.append(TypeFormula(item, []))
            else:
                raise ValueError(f"unexpected type parameter object in stack: {item}")

        return type_parameters

    def is_punctuation(self, token: str) -> bool:
        return token in self.PUNCTUATION

    def is_end_of_type_parameters(self, token: str) -> bool:
        return token == self.END_TYPE_PARAMETERS

    def is_beginning_of_type_parameters(self, token: str) -> bool:
        return token == self.BEGIN_TYPE_PARAMETERS
