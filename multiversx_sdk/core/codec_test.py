from multiversx_sdk.core import codec
from multiversx_sdk.core.constants import (testVectors1, testVectors2,
                                           testVectors3, testVectors4)


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
    for [inputData, expectedData] in testVectors1:
        assert codec.encode_signed_number(inputData) == bytes([expectedData])
    for [inputData, expectedData] in testVectors2:
        assert codec.encode_signed_number(inputData) == bytes([expectedData])
    for [inputData, expectedData] in testVectors3:
        assert codec.encode_signed_number(inputData) == bytes([expectedData])
    for [inputData, [expectedData1, expectedData2]] in testVectors4:
        assert codec.encode_signed_number(inputData) == bytes([expectedData1, expectedData2])
