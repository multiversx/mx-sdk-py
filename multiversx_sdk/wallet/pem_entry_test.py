from pathlib import Path

import pytest

from multiversx_sdk.wallet.constants import USER_SEED_LENGTH
from multiversx_sdk.wallet.errors import InvalidPemError
from multiversx_sdk.wallet.pem_entry import PemEntry

testwallets = Path(__file__).parent.parent / "testutils" / "testwallets"


def test_from_text_all():
    text = (testwallets / "alice.pem").read_text()
    entries = PemEntry.from_text_all(text)
    entry = entries[0]
    assert len(entries) == 1
    assert entry.label == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert entry.message[0:USER_SEED_LENGTH].hex() == "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"

    text = (testwallets / "multipleUserKeys.pem").read_text()
    entries = PemEntry.from_text_all(text)
    entry = entries[0]
    assert len(entries) == 3
    assert entry.label == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"
    assert entry.message[0:USER_SEED_LENGTH].hex() == "413f42575f7f26fad3317a778771212fdb80245850981e48b58a4f25e344e8f9"

    entry = entries[1]
    assert entry.label == "erd1spyavw0956vq68xj8y4tenjpq2wd5a9p2c6j8gsz7ztyrnpxrruqzu66jx"
    assert entry.message[0:USER_SEED_LENGTH].hex() == "b8ca6f8203fb4b545a8e83c5384da033c415db155b53fb5b8eba7ff5a039d639"

    entry = entries[2]
    assert entry.label == "erd1k2s324ww2g0yj38qn2ch2jwctdy8mnfxep94q9arncc6xecg3xaq6mjse8"
    assert entry.message[0:USER_SEED_LENGTH].hex() == "e253a571ca153dc2aee845819f74bcc9773b0586edead15a94cb7235a5027436"


def test_from_text_all_for_validators():
    text = (testwallets / "validatorKey00.pem").read_text()
    entry = PemEntry.from_text_all(text)[0]
    assert (
        entry.label
        == "e7beaa95b3877f47348df4dd1cb578a4f7cabf7a20bfeefe5cdd263878ff132b765e04fef6f40c93512b666c47ed7719b8902f6c922c04247989b7137e837cc81a62e54712471c97a2ddab75aa9c2f58f813ed4c0fa722bde0ab718bff382208"
    )
    assert entry.message.hex() == "7cff99bd671502db7d15bc8abc0c9a804fb925406fbdd50f1e4c17a4cd774247"

    text = (testwallets / "multipleValidatorKeys.pem").read_text()
    entries = PemEntry.from_text_all(text)

    entry = entries[0]
    assert (
        entry.label
        == "f8910e47cf9464777c912e6390758bb39715fffcb861b184017920e4a807b42553f2f21e7f3914b81bcf58b66a72ab16d97013ae1cff807cefc977ef8cbf116258534b9e46d19528042d16ef8374404a89b184e0a4ee18c77c49e454d04eae8d"
    )
    assert entry.message.hex() == "7c19bf3a0c57cdd1fb08e4607cebaa3647d6b9261b4693f61e96e54b218d442a"

    entry = entries[1]
    assert (
        entry.label
        == "1b4e60e6d100cdf234d3427494dac55fbac49856cadc86bcb13a01b9bb05a0d9143e86c186c948e7ae9e52427c9523102efe9019a2a9c06db02993f2e3e6756576ae5a3ec7c235d548bc79de1a6990e1120ae435cb48f7fc436c9f9098b92a0d"
    )
    assert entry.message.hex() == "3034b1d58628a842984da0c70da0b5a251ebb2aebf51afc5b586e2839b5e5263"

    entry = entries[2]
    assert (
        entry.label
        == "e5dc552b4b170cdec4405ff8f9af20313bf0e2756d06c35877b6fbcfa6b354a7b3e2d439ea87999befb09a8fa1b3f014e57ec747bf738c4199338fcd4a87b373dd62f5c8329f1f5f245956bbb06685596a2e83dc38befa63e4a2b5c4ce408506"
    )
    assert entry.message.hex() == "de7e1b385edbb0e1e8f9fc25d91bd8eed71a1da7caab732e6b47a48042d8523d"

    entry = entries[3]
    assert (
        entry.label
        == "12773304cb718250edd89770cedcbf675ccdb7fe2b30bd3185ca65ffa0d516879768ed03f92e41a6e5bc5340b78a9d02655e3b727c79730ead791fb68eaa02b84e1be92a816a9604a1ab9a6d3874b638487e2145239438a4bafac3889348d405"
    )
    assert entry.message.hex() == "8ebeb07d296ad2529400b40687a741a135f8357f79f39fcb2894a6f9703a5816"


def test_to_text():
    text = (testwallets / "alice.pem").read_text()
    assert PemEntry.from_text_all(text)[0].to_text() == text.strip()

    text = (testwallets / "validatorKey00.pem").read_text()
    assert PemEntry.from_text_all(text)[0].to_text() == text.strip()

    text = (testwallets / "multipleUserKeys.pem").read_text()
    entries = PemEntry.from_text_all(text)
    text_actual = "\n".join([entry.to_text() for entry in entries])
    assert text_actual == text.strip()

    text = (testwallets / "multipleValidatorKeys.pem").read_text()
    entries = PemEntry.from_text_all(text)
    text_actual = "\n".join([entry.to_text() for entry in entries])
    assert text_actual == text.strip()


ALICE_PEM = (testwallets / "alice.pem").read_text().strip()
BOB_PEM = (testwallets / "bob.pem").read_text().strip()
ALICE_HEADER, ALICE_FOOTER = ALICE_PEM.splitlines()[0], ALICE_PEM.splitlines()[-1]


def test_from_text_all_with_entry_without_content():
    # Previously, the labels were shifted: Bob's key was returned under Alice's label.
    text = "\n".join([ALICE_HEADER, ALICE_FOOTER, BOB_PEM])

    with pytest.raises(InvalidPemError, match="an entry has no content"):
        PemEntry.from_text_all(text)


@pytest.mark.parametrize(
    "text, error",
    [
        ("\n".join(ALICE_PEM.splitlines()[:-1]), "missing END line"),
        ("\n".join(ALICE_PEM.splitlines()[:-1] + [BOB_PEM]), "missing END line"),
        ("\n".join(ALICE_PEM.splitlines()[1:]), "unexpected line outside of an entry"),
        ("\n".join([ALICE_FOOTER]), "missing BEGIN line"),
        ("\n".join(["Some comment", ALICE_PEM]), "unexpected line outside of an entry"),
        ("\n".join(BOB_PEM.splitlines()[:-1] + [ALICE_FOOTER]), "the END line does not match the BEGIN line"),
        ("-----BEGIN PRIVATE KEY-----\nYWJj\n-----END PRIVATE KEY-----", "unexpected line outside of an entry"),
    ],
    ids=[
        "no-end",
        "no-end-then-entry",
        "no-begin",
        "footer-only",
        "comment",
        "footer-of-another-entry",
        "generic-header",
    ],
)
def test_from_text_all_with_malformed_structure(text: str, error: str):
    with pytest.raises(InvalidPemError, match=error):
        PemEntry.from_text_all(text)


@pytest.mark.parametrize(
    "content",
    [
        "NDEzZjQyNTc1ZjdmMjZmYWQzMzE3YTc3ODc3MTIxMmZk*#@",  # characters outside of the base64 alphabet
        "NDEzZjQyNTc1ZjdmMjZmYWQzMzE3YTc3ODc3MTIxMmZk=",  # bad padding
        "aGVsbG8gd29ybGQ=",  # base64 of "hello world" (not hex)
        "//79",  # base64 of non-UTF-8 bytes
    ],
    ids=["non-base64-characters", "bad-padding", "not-hex", "not-utf8"],
)
def test_from_text_all_with_badly_encoded_content(content: str):
    text = "\n".join([ALICE_HEADER, content, ALICE_FOOTER])

    with pytest.raises(InvalidPemError, match="the content of an entry is not properly encoded"):
        PemEntry.from_text_all(text)

    # For backwards compatibility, the error is a "ValueError" (as before).
    with pytest.raises(ValueError):
        PemEntry.from_text_all(text)


def test_from_text_all_keeps_dashes_within_label():
    entry = PemEntry("my-key-label", bytes(32))
    entries = PemEntry.from_text_all(entry.to_text())

    assert entries[0].label == "my-key-label"
    assert entries[0].message == bytes(32)


def test_from_text_all_with_shorter_trailing_delimiter():
    # Such files exist in the wild (e.g. "testKeys/walletKeys.pem" in mx-chain-go), and they were loaded before.
    text = ALICE_PEM.removesuffix("-----") + "---"
    entries = PemEntry.from_text_all(text)

    assert len(entries) == 1
    assert entries[0].label == "erd1qyu5wthldzr8wx5c9ucg8kjagg0jfs53s8nr3zpz3hypefsdd8ssycr6th"


@pytest.mark.parametrize("label", ["foo\nbar", "foo\r\n", "foo-----bar", "foo\u2028bar"])
def test_to_text_with_label_breaking_the_structure(label: str):
    with pytest.raises(InvalidPemError, match="the label must not contain line breaks"):
        PemEntry(label, bytes(32)).to_text()


@pytest.mark.parametrize("label", ["my-key-", "foo---", "foo -", " foo", "foo ", " foo ", "foo\t", "\u00a0foo"])
def test_to_text_with_label_not_surviving_a_save_and_load_cycle(label: str):
    # When parsing, the trailing dashes and the surrounding whitespace are dropped, so such labels would be altered on reload.
    with pytest.raises(InvalidPemError, match="the label must not start or end with whitespace, nor end with '-'"):
        PemEntry(label, bytes(32)).to_text()


@pytest.mark.parametrize("label", ["", "foo", "-foo", "my-key-label", "foo bar", "foo - bar", "foo--bar"])
def test_to_text_then_from_text_all_preserves_label(label: str):
    entries = PemEntry.from_text_all(PemEntry(label, bytes(32)).to_text())

    assert len(entries) == 1
    assert entries[0].label == label
    assert entries[0].message == bytes(32)
