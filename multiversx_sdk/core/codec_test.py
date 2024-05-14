from typing import Any

from multiversx_sdk.core import codec

test_vectors_1 = [
    [-1, 0xFF],
    [1, 0x01],
    [2, 0x02],
    [-2, 0xFE],
    [3, 0x03],
    [-3, 0xFD],
    [4, 0x04],
    [-4, 0xFC],
]

test_vectors_2 = [
    [-1, 0xFF],
    [1, 0x01],
    [2, 0x02],
    [-2, 0xFE],
    [3, 0x03],
    [-3, 0xFD],
    [4, 0x04],
    [-4, 0xFC],
    [5, 0x05],
    [-5, 0xFB],
    [6, 0x06],
    [-6, 0xFA],
]

test_vectors_3 = [
    [125, 0x7D],
    [-125, 0x83],
    [126, 0x7E],
    [-126, 0x82],
    [127, 0x7F],
    [-127, 0x81],
    [-128, 0x80],
]

test_vectors_4: Any = [
    [128, [0x00, 0x80]],
    [129, [0x00, 0x81]],
    [-129, [0xFF, 0x7F]],
    [130, [0x00, 0x82]],
    [-130, [0xFF, 0x7E]],
    [253, [0x00, 0xFD]],
    [256, [0x01, 0x00]],
    [-256, [0xFF, 0x00]],
    [-257, [0xFE, 0xFF]],
    [258, [0x01, 0x02]],
]


def test_encode_signed_number():
    assert codec.encode_signed_number(-256) == bytes([0xFF, 0x00])
    assert codec.encode_signed_number(-0x11) == bytes([0xEF])
    assert codec.encode_signed_number(-128) == bytes([0x80])
    assert codec.encode_signed_number(-1) == bytes([0xFF])
    assert codec.encode_signed_number(0) == bytes([])
    assert codec.encode_signed_number(1) == bytes([0x01])
    assert codec.encode_signed_number(256) == bytes([0x01, 0x00])
    assert codec.encode_signed_number(127) == bytes([0x7F])
    assert codec.encode_signed_number(0x11) == bytes([0x11])
    assert codec.encode_signed_number(255) == bytes([0x00, 0xFF])

    for [input_data, expected_data] in test_vectors_1:
        assert codec.encode_signed_number(input_data) == bytes([expected_data])

    for [input_data, expected_data] in test_vectors_2:
        assert codec.encode_signed_number(input_data) == bytes([expected_data])

    for [input_data, expected_data] in test_vectors_3:
        assert codec.encode_signed_number(input_data) == bytes([expected_data])

    for [input_data, [expected_data_1, expected_data_2]] in test_vectors_4:
        assert codec.encode_signed_number(input_data) == bytes([expected_data_1, expected_data_2])
