from erdpy_core.address import Address
from erdpy_core.code_metadata import CodeMetadata
from erdpy_core.token_payment import TokenPayment
from erdpy_core.transaction_payload_builders import (
    ContractDeployBuilder, ContractUpgradeBuilder, ESDTNFTTransferBuilder,
    ESDTTransferBuilder, FunctionCallBuilder, MultiESDTNFTTransferBuilder)


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
    assert data == b"aabbccdd@0500@0506@2a@74657374"


def test_contract_upgrade_builder():
    metadata = CodeMetadata(upgradeable=True, readable=True, payable=True, payable_by_contract=True)
    builder = ContractUpgradeBuilder(bytes([0xAA, 0xBB, 0xCC, 0xDD]), metadata)
    builder.arguments.append(42)
    builder.arguments.append("test")
    data = builder.build().data
    assert data == b"upgradeContract@aabbccdd@0506@2a@74657374"


def test_esdt_transfer_builder():
    payment = TokenPayment.fungible_from_amount("COUNTER-8b028f", "100.00", 2)
    data = ESDTTransferBuilder(payment).build().data
    assert data == b"ESDTTransfer@434f554e5445522d386230323866@2710"


def test_esdt_nft_transfer_builder():
    # NFT
    payment = TokenPayment.non_fungible("ERDPY-38f249", 1)
    destination = Address.from_bech32("erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx")
    data = ESDTNFTTransferBuilder(payment, destination).build().data
    assert data == b"ESDTNFTTransfer@45524450592d333866323439@01@01@8049d639e5a6980d1cd2392abcce41029cda74a1563523a202f09641cc2618f8"

    # SFT
    payment = TokenPayment.semi_fungible("SEMI-9efd0f", 1, 5)
    destination = Address.from_bech32("erd1testnlersh4z0wsv8kjx39me4rmnvjkwu8dsaea7ukdvvc9z396qykv7z7")
    data = ESDTNFTTransferBuilder(payment, destination).build().data
    assert data == b"ESDTNFTTransfer@53454d492d396566643066@01@05@5e60b9ff2385ea27ba0c3da4689779a8f7364acee1db0ee7bee59ac660a28974"


def test_multi_esdt_nft_transfer_builder():
    payment_one = TokenPayment.non_fungible("ERDPY-38f249", 1)
    payment_two = TokenPayment.fungible_from_amount("BAR-c80d29", "10.00", 18)
    destination = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    data = MultiESDTNFTTransferBuilder([payment_one, payment_two], destination).build().data
    assert data == b"MultiESDTNFTTransfer@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1@02@45524450592d333866323439@01@01@4241522d633830643239@@8ac7230489e80000"
