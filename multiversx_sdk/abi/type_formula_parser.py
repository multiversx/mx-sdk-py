
from typing import Any, List

from multiversx_sdk.abi.type_formula import TypeFormula

# TODO: apply simplifications from JS


class TypeFormulaParser:
    BEGIN_TYPE_PARAMETERS = "<"
    END_TYPE_PARAMETERS = ">"
    COMMA = ","
    PUNCTUATION = [COMMA, BEGIN_TYPE_PARAMETERS, END_TYPE_PARAMETERS]

    def parse_expression(self, expression: str) -> TypeFormula:
        expression = expression.strip()

        tokens = self._tokenize_expression(expression)
        tokens = [token for token in tokens if token != TypeFormulaParser.COMMA]

        stack: List[Any] = []

        for token in tokens:
            if token in TypeFormulaParser.PUNCTUATION:
                if token == TypeFormulaParser.END_TYPE_PARAMETERS:
                    type_parameters: List[TypeFormula] = []

                    while True:
                        if not stack:
                            raise Exception("Badly specified type parameters.")

                        if stack[-1] == TypeFormulaParser.BEGIN_TYPE_PARAMETERS:
                            break

                        item = stack.pop()
                        if isinstance(item, TypeFormula):
                            type_formula = item
                        else:
                            type_formula = TypeFormula(item, [])

                        type_parameters.append(type_formula)

                    stack.pop()  # pop "<" symbol
                    type_name = stack.pop()
                    type_formula = TypeFormula(type_name, list(reversed(type_parameters)))
                    stack.append(type_formula)
                elif token == TypeFormulaParser.BEGIN_TYPE_PARAMETERS:
                    # The symbol is pushed as a simple string,
                    # as it will never be interpreted, anyway.
                    stack.append(token)
                elif token == TypeFormulaParser.COMMA:
                    # We simply ignore commas
                    pass
                else:
                    raise Exception(f"Unexpected token (punctuation): {token}.")
            else:
                # It's a type name. We push it as a simple string.
                stack.append(token)

        if len(stack) != 1:
            raise Exception(f"Unexpected stack length at end of parsing: {len(stack)}.")
        if stack[0] in TypeFormulaParser.PUNCTUATION:
            raise Exception(f"Unexpected root element.")

        if isinstance(stack[0], str):
            # Expression contained a simple, non-generic type
            return TypeFormula(stack[0], [])
        elif isinstance(stack[0], TypeFormula):
            return stack[0]
        else:
            raise Exception(f"Unexpected item on stack: {stack[0]}")

    def _tokenize_expression(self, expression: str) -> List[str]:
        tokens: List[str] = []
        current_token = ""

        for i in range(len(expression)):
            character = expression[i]

            if character not in TypeFormulaParser.PUNCTUATION:
                # Non-punctuation character
                current_token += character
            else:
                if current_token:
                    tokens.append(current_token.strip())
                    current_token = ""
                # Punctuation character
                tokens.append(character)

        if current_token:
            tokens.append(current_token.strip())

        return tokens
