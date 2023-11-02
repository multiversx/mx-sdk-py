from multiversx_sdk_core.message import Message, MessageComputer


def test_message_v1_serialize_for_signing():
    message = Message("test message".encode())
    message_computer = MessageComputer()
    serialized = message_computer.compute_bytes_for_signing(message)
    assert serialized.hex() == "2162d6271208429e6d3e664139e98ba7c5f1870906fb113e8903b1d3f531004d"
