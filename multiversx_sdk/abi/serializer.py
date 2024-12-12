from typing import Any, Sequence

from multiversx_sdk.abi.codec import Codec
from multiversx_sdk.abi.counted_variadic_values import CountedVariadicValues
from multiversx_sdk.abi.interface import ISingleValue
from multiversx_sdk.abi.multi_value import MultiValue
from multiversx_sdk.abi.optional_value import OptionalValue
from multiversx_sdk.abi.parts import PartsHolder
from multiversx_sdk.abi.small_int_values import U32Value
from multiversx_sdk.abi.variadic_values import VariadicValues
from multiversx_sdk.core.constants import ARGS_SEPARATOR


class Serializer:
    """
    The serializer follows the rules of the MultiversX Serialization format:
    https://docs.multiversx.com/developers/data/serialization-overview
    """

    def __init__(self, parts_separator: str = ARGS_SEPARATOR):
        if not parts_separator:
            raise ValueError("cannot create serializer: parts separator must not be empty")

        self.parts_separator = parts_separator
        self.codec = Codec()

    def serialize(self, input_values: Sequence[Any]) -> str:
        parts = self.serialize_to_parts(input_values)
        return self._encode_parts(parts)

    def serialize_to_parts(self, input_values: Sequence[Any]) -> list[bytes]:
        parts_holder = PartsHolder([])
        self._do_serialize(parts_holder, input_values)
        return parts_holder.get_parts()

    def _do_serialize(self, parts_holder: PartsHolder, input_values: Sequence[Any]):
        for i, value in enumerate(input_values):
            if value is None:
                raise ValueError("cannot serialize null value")

            if isinstance(value, OptionalValue):
                if i != len(input_values) - 1:
                    # Usage of multiple optional values is not recommended:
                    # https://docs.multiversx.com/developers/data/multi-values
                    # Thus, here, we disallow them.
                    raise ValueError("an optional value must be last among input values")

                if value.value is not None:
                    self._do_serialize(parts_holder, [value.value])
            elif isinstance(value, MultiValue):
                self._do_serialize(parts_holder, value.items)
            elif isinstance(value, VariadicValues):
                if i != len(input_values) - 1:
                    raise ValueError("variadic values must be last among input values")

                self._do_serialize(parts_holder, value.items)
            elif isinstance(value, CountedVariadicValues):
                length = U32Value(value.length)
                self._do_serialize(parts_holder, [length])
                self._do_serialize(parts_holder, value.items)
            elif isinstance(value, ISingleValue):
                parts_holder.append_empty_part()
                self._serialize_single_value(parts_holder, value)
            else:
                raise ValueError(f"cannot serialize value of type: {type(value).__name__}")

    def _serialize_single_value(self, parts_holder: PartsHolder, value: ISingleValue):
        data = self.codec.encode_top_level(value)
        parts_holder.append_to_last_part(data)

    def deserialize(self, data: str, output_values: Sequence[Any]):
        parts = self._decode_into_parts(data)
        self.deserialize_parts(parts, output_values)

    def deserialize_parts(self, parts: Sequence[bytes], output_values: Sequence[Any]):
        parts_holder = PartsHolder(parts)
        self._do_deserialize(parts_holder, output_values)

        if not parts_holder.is_focused_beyond_last_part():
            raise Exception("not all parts have been deserialized")

    def _do_deserialize(self, parts_holder: PartsHolder, output_values: Sequence[Any]):
        for i, value in enumerate(output_values):
            if value is None:
                raise ValueError("cannot deserialize into null value")

            if isinstance(value, OptionalValue):
                if i != len(output_values) - 1:
                    # Usage of multiple optional values is not recommended:
                    # https://docs.multiversx.com/developers/data/multi-values
                    # Thus, here, we disallow them.
                    raise ValueError("an optional value must be last among output values")

                if parts_holder.is_focused_beyond_last_part():
                    value.value = None
                else:
                    self._do_deserialize(parts_holder, [value.value])
            elif isinstance(value, MultiValue):
                self._do_deserialize(parts_holder, value.items)
            elif isinstance(value, VariadicValues):
                if i != len(output_values) - 1:
                    raise ValueError("variadic values must be last among output values")

                self._deserialize_variadic_values(parts_holder, value)
            elif isinstance(value, CountedVariadicValues):
                self._deserialize_counted_variadic_values(parts_holder, value)
            elif isinstance(value, ISingleValue):
                self._deserialize_single_value(parts_holder, value)
            else:
                raise ValueError(f"cannot deserialize value of type: {type(value).__name__}")

    def _deserialize_variadic_values(self, parts_holder: PartsHolder, value: VariadicValues):
        if value.item_creator is None:
            raise Exception("cannot decode list: item creator is None")

        while not parts_holder.is_focused_beyond_last_part():
            new_item = value.item_creator()

            self._do_deserialize(parts_holder, [new_item])

            value.items.append(new_item)

    def _deserialize_counted_variadic_values(self, parts_holder: PartsHolder, value: CountedVariadicValues):
        if value.item_creator is None:
            raise Exception("cannot decode list: item creator is None")

        length = U32Value()
        self._deserialize_single_value(parts_holder, length)

        for _ in range(int(length)):
            new_item = value.item_creator()

            self._do_deserialize(parts_holder, [new_item])

            value.items.append(new_item)
            value.length += 1

    def _deserialize_single_value(self, parts_holder: PartsHolder, value: ISingleValue):
        part = parts_holder.read_whole_focused_part()
        self.codec.decode_top_level(part, value)
        parts_holder.focus_on_next_part()

    def _encode_parts(self, parts: list[bytes]) -> str:
        parts_hex = [part.hex() for part in parts]
        return self.parts_separator.join(parts_hex)

    def _decode_into_parts(self, encoded: str) -> list[bytes]:
        parts_hex = encoded.split(self.parts_separator)
        parts = [bytes.fromhex(part_hex) for part_hex in parts_hex]
        return parts
