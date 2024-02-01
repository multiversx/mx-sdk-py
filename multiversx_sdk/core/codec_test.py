from multiversx_sdk.core import codec

def test_encode_signed_number():
    assert codec.encode_signed_number(-256) == bytes([0xFF, 0x00])
    assert codec.encode_signed_number(-0x11) == bytes([0xEF])
    assert codec.encode_signed_number(-128) == bytes([0x80])
    assert codec.encode_signed_number(-1) == bytes([0xFF])
    assert codec.encode_signed_number(0) == bytes([])
    assert codec.encode_signed_number(1) == bytes([0x01])
