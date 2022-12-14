from erdpy_core.address import Address
from erdpy_core.code_metadata import CodeMetadata
from erdpy_core.transaction_payload_builders import (ContractDeployBuilder,
                                                     ContractUpgradeBuilder,
                                                     FunctionCallBuilder)


def test_function_call_builder():
    alice_address = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")

    # Using the constructor only
    data = FunctionCallBuilder("foo", [42, "test", alice_address]).build().data
    assert data == b"foo@2a@74657374@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"

    # Using the constructor, then populating "arguments"
    builder = FunctionCallBuilder("foo")
    builder.arguments.append(42)
    builder.arguments.append("test")
    builder.arguments.append(alice_address)
    data = builder.build().data
    assert data == b"foo@2a@74657374@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"


def test_contract_deploy_builder():
    metadata = CodeMetadata(upgradeable=True, readable=True, payable=True, payable_by_contract=True)
    builder = ContractDeployBuilder(bytes([0xAA, 0xBB, 0xCC, 0xDD]), metadata)
    builder.arguments.append(42)
    builder.arguments.append("test")
    data = builder.build().data
    print(data)
    assert data == b"aabbccdd@0500@0506@2a@74657374"


def test_contract_upgrade_builder():
    metadata = CodeMetadata(upgradeable=True, readable=True, payable=True, payable_by_contract=True)
    builder = ContractUpgradeBuilder(bytes([0xAA, 0xBB, 0xCC, 0xDD]), metadata)
    builder.arguments.append(42)
    builder.arguments.append("test")
    data = builder.build().data
    print(data)
    assert data == b"upgradeContract@aabbccdd@0506@2a@74657374"
