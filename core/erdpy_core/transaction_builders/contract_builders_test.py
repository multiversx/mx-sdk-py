from typing import List

from erdpy_core.address import Address
from erdpy_core.code_metadata import CodeMetadata
from erdpy_core.interfaces import ITokenPayment
from erdpy_core.token_payment import TokenPayment
from erdpy_core.transaction_builders.contract_builders import (
    ContractCallBuilder, ContractDeploymentBuilder, ContractUpgradeBuilder)
from erdpy_core.transaction_builders.default_configuration import \
    DefaultTransactionBuildersConfiguration

dummyConfig = DefaultTransactionBuildersConfiguration(chain_id="D")


def test_contract_deployment_builder():
    owner = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    metadata = CodeMetadata(upgradeable=True, readable=True, payable=True, payable_by_contract=True)

    builder = ContractDeploymentBuilder(
        dummyConfig,
        owner=owner,
        deploy_arguments=[42, "test"],
        code_metadata=metadata,
        code=bytes([0xAA, 0xBB, 0xCC, 0xDD]),
        gas_limit=10000000
    )

    payload = builder.build_payload()
    tx = builder.build()

    assert payload.data == b"aabbccdd@0500@0506@2a@74657374"
    assert tx.chainID == "D"
    assert tx.sender == owner
    assert tx.receiver.bech32() == "erd1qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq6gq4hu"
    assert tx.gas_limit == 10000000
    assert tx.gas_price == 1000000000
    assert tx.data.encoded() == payload.encoded()


def test_contract_upgrade_builder():
    contract = Address.from_bech32("erd1qqqqqqqqqqqqqpgquzmh78klkqwt0p4rjys0qtp3la07gz4d396qn50nnm")
    owner = Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")
    metadata = CodeMetadata(upgradeable=True, readable=True, payable=True, payable_by_contract=True)

    builder = ContractUpgradeBuilder(
        dummyConfig,
        contract=contract,
        owner=owner,
        upgrade_arguments=[42, "test"],
        code_metadata=metadata,
        code=bytes([0xAA, 0xBB, 0xCC, 0xDD]),
        gas_limit=10000000
    )

    payload = builder.build_payload()
    tx = builder.build()

    assert payload.data == b"upgradeContract@aabbccdd@0506@2a@74657374"
    assert tx.chainID == "D"
    assert tx.sender == owner
    assert tx.receiver == contract
    assert tx.gas_limit == 10000000
    assert tx.gas_price == 1000000000
    assert tx.data.encoded() == payload.encoded()


def test_contract_call_builder():
    contract = Address.from_bech32("erd1qqqqqqqqqqqqqpgquzmh78klkqwt0p4rjys0qtp3la07gz4d396qn50nnm")
    caller = Address.from_bech32("erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8")

    builder = ContractCallBuilder(
        dummyConfig,
        contract=contract,
        function_name="foo",
        caller=caller,
        call_arguments=[42, "test", Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")],
        gas_limit=10000000
    )

    payload = builder.build_payload()
    tx = builder.build()

    assert payload.data == b"foo@2a@74657374@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"
    assert tx.sender == caller
    assert tx.receiver == contract
    assert tx.gas_limit == 10000000
    assert tx.data.encoded() == payload.encoded()


def test_contract_call_builder_with_esdt_transfer():
    contract = Address.from_bech32("erd1qqqqqqqqqqqqqpgquzmh78klkqwt0p4rjys0qtp3la07gz4d396qn50nnm")
    caller = Address.from_bech32("erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8")

    transfers: List[ITokenPayment] = [
        TokenPayment.fungible_from_amount("COUNTER-8b028f", "100.00", 2)
    ]

    builder = ContractCallBuilder(
        dummyConfig,
        contract=contract,
        function_name="hello",
        caller=caller,
        call_arguments=[42, "test", Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")],
        gas_limit=10000000,
        esdt_transfers=transfers
    )

    payload = builder.build_payload()
    tx = builder.build()

    assert payload.data == b"ESDTTransfer@434f554e5445522d386230323866@2710@68656c6c6f@2a@74657374@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"
    assert tx.sender == caller
    assert tx.receiver == contract
    assert tx.data.encoded() == payload.encoded()


def test_contract_call_builder_with_esdt_nft_transfer():
    contract = Address.from_bech32("erd1qqqqqqqqqqqqqpgquzmh78klkqwt0p4rjys0qtp3la07gz4d396qn50nnm")
    caller = Address.from_bech32("erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8")

    transfers: List[ITokenPayment] = [
        TokenPayment.non_fungible("ERDPY-38f249", 1)
    ]

    builder = ContractCallBuilder(
        dummyConfig,
        contract=contract,
        function_name="hello",
        caller=caller,
        call_arguments=[42, "test", Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")],
        gas_limit=10000000,
        esdt_transfers=transfers
    )

    payload = builder.build_payload()
    tx = builder.build()

    assert payload.data == b"ESDTNFTTransfer@45524450592d333866323439@01@01@00000000000000000500e0b77f1edfb01cb786a39120f02c31ff5fe40aad8974@68656c6c6f@2a@74657374@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"
    assert tx.sender == caller
    assert tx.receiver == caller
    assert tx.data.encoded() == payload.encoded()


def test_contract_call_builder_with_multi_esdt_nft_transfer():
    contract = Address.from_bech32("erd1qqqqqqqqqqqqqpgquzmh78klkqwt0p4rjys0qtp3la07gz4d396qn50nnm")
    caller = Address.from_bech32("erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8")

    transfers = [
        TokenPayment.non_fungible("ERDPY-38f249", 1),
        TokenPayment.fungible_from_amount("BAR-c80d29", "10.00", 18)
    ]

    builder = ContractCallBuilder(
        dummyConfig,
        contract=contract,
        function_name="hello",
        caller=caller,
        call_arguments=[42, "test", Address.from_bech32("erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th")],
        gas_limit=10000000,
        esdt_transfers=transfers
    )

    payload = builder.build_payload()
    tx = builder.build()

    assert payload.data == b"MultiESDTNFTTransfer@00000000000000000500e0b77f1edfb01cb786a39120f02c31ff5fe40aad8974@02@45524450592d333866323439@01@01@4241522d633830643239@@8ac7230489e80000@68656c6c6f@2a@74657374@0139472eff6886771a982f3083da5d421f24c29181e63888228dc81ca60d69e1"
    assert tx.sender == caller
    assert tx.receiver == caller
    assert tx.data.encoded() == payload.encoded()
