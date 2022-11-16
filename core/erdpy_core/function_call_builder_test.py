from erdpy_core.function_call_builder import FunctionCallBuilder


def test_function_call_builder():
    data = FunctionCallBuilder().set_function("foo").set_arguments([42, "test"]).build().data
    assert data == b"foo@2a@74657374"
