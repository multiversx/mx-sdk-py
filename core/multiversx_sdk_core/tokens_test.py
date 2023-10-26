from multiversx_sdk_core.tokens import Token, TokenComputer


def test_token_is_fungible():
    fungible_token = Token("TEST-123456")
    non_fungible_token = Token("NFT-987654", 7)
    token_computer = TokenComputer()

    assert token_computer.is_fungible(fungible_token)
    assert not token_computer.is_fungible(non_fungible_token)


def test_extract_nonce_from_extended_identifier():
    extended_nft_identifier = "TEST-123456-0a"
    extended_fungible_identifier = "FNG-123456"
    token_computer = TokenComputer()

    assert token_computer.extract_nonce_from_extended_identifier(extended_nft_identifier) == 10
    assert token_computer.extract_nonce_from_extended_identifier(extended_fungible_identifier) == 0


def test_extract_identifier_from_extended_identifier():
    extended_nft_identifier = "TEST-123456-0a"
    extended_fungible_identifier = "FNG-123456"
    token_computer = TokenComputer()

    assert token_computer.extract_identifier_from_extended_identifier(extended_nft_identifier) == "TEST-123456"
    assert token_computer.extract_identifier_from_extended_identifier(extended_fungible_identifier) == "FNG-123456"
