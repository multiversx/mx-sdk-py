from multiversx_sdk.core import codec

test_vectors_1 = [
    [-1, 0Xff],
    [1, 0X01],
    [2, 0X02],
    [-2, 0Xfe],
    [3, 0X03],
    [-3, 0Xfd],
    [4, 0X04],
    [-4, 0Xfc],
]

test_vectors_2 = [
    [-1, 0Xff],
    [1, 0X01],
    [2, 0X02],
    [-2, 0Xfe],
    [3, 0X03],
    [-3, 0Xfd],
    [4, 0X04],
    [-4, 0Xfc],
    [5, 0X05],
    [-5, 0Xfb],
    [6, 0X06],
    [-6, 0Xfa],
]

test_vectors_3 = [
    [125, 0X7d],
    [-125, 0X83],
    [126, 0X7e],
    [-126, 0X82],
    [127, 0X7f],
    [-127, 0X81],
    [-128, 0X80],
]

test_vectors_4 = [
    [128, [0x00, 0x80]],
    [129, [0x00, 0x81]],
    [-129, [0xff, 0x7f]],
    [130, [0x00, 0x82]],
    [-130, [0xff, 0x7e]],
    [253, [0x00, 0xfd]],
    [256, [0x01, 0x00]],
    [-256, [0xff, 0x00]],
    [-257, [0xfe, 0xff]],
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
