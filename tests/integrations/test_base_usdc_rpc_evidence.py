"""Deterministic no-network tests of Base RPC receipt validation.

Fixtures are entirely synthetic and must never be represented as real tx hashes.
"""

from copy import deepcopy
from urllib.error import HTTPError, URLError
from dataclasses import replace

import pytest

from integrations.base_usdc.matcher import USDC_CONTRACTS, Invoice
from integrations.base_usdc import rpc_evidence as rpc_module
from integrations.base_usdc.rpc_evidence import (
    BASE_RPC_URLS,
    TRANSFER_TOPIC,
    BasePublicRpc,
    RpcUnavailableError,
    _NoRedirect,
    inspect_invoice,
    inspect_invoices,
)

TX = "0x" + "1" * 64
BLOCK_HASH = "0x" + "2" * 64
ADDRESS = "0x" + "a" * 40
OTHER = "0x" + "b" * 40
CHAIN = 84532
BLOCK = 100


def invoice(**changes):
    original = Invoice("INV-01", CHAIN, ADDRESS, "12.345678", TX, 2)
    return replace(original, **changes)


def log(**changes):
    entry = {
        "transactionHash": TX,
        "blockHash": BLOCK_HASH,
        "blockNumber": hex(BLOCK),
        "logIndex": "0x2",
        "address": USDC_CONTRACTS[CHAIN],
        "removed": False,
        "topics": [
            TRANSFER_TOPIC,
            "0x" + "0" * 24 + "c" * 40,
            "0x" + "0" * 24 + "a" * 40,
        ],
        "data": "0x" + f"{12_345_678:064x}",
    }
    entry.update(changes)
    return entry


def responses(**changes):
    response = {
        "eth_chainId": hex(CHAIN),
        "eth_getTransactionReceipt": {
            "transactionHash": TX,
            "status": "0x1",
            "blockNumber": hex(BLOCK),
            "blockHash": BLOCK_HASH,
            "logs": [log()],
        },
        "eth_getBlockByNumber": {"number": hex(BLOCK), "hash": BLOCK_HASH},
        "eth_blockNumber": hex(BLOCK + 5),
    }
    response.update(changes)
    return response


class FakeRpc:
    def __init__(self, data=None):
        self.data = deepcopy(data if data is not None else responses())
        self.calls = []

    def call(self, method, params):
        self.calls.append((method, params))
        return self.data[method]


def test_canonical_successful_receipt_and_exact_usdc_event():
    rpc = FakeRpc()
    result = inspect_invoice(invoice(), rpc)
    assert result.status == "rpc_observed_match"
    assert result.rpc_observed
    assert result.chain_id == CHAIN
    assert result.block_number == BLOCK
    assert result.block_hash == BLOCK_HASH
    assert result.confirmations == 6
    assert result.log_index == 2
    assert [method for method, _ in rpc.calls] == [
        "eth_chainId", "eth_getTransactionReceipt",
        "eth_getBlockByNumber", "eth_blockNumber",
    ]
    assert rpc.calls[1][1] == [TX]
    assert "not a cryptographic proof" in result.explanation


def test_missing_reference_never_queries_network():
    rpc = FakeRpc()
    result = inspect_invoice(invoice(tx_hash=None, log_index=None), rpc)
    assert result.status == "missing_reference"
    assert not rpc.calls
    assert not result.rpc_observed


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("eth_chainId", hex(8453), "wrong_chain"),
        ("eth_getTransactionReceipt", None, "pending_or_missing"),
    ],
)
def test_wrong_chain_and_absent_receipt(field, value, expected):
    rpc = FakeRpc(responses(**{field: value}))
    result = inspect_invoice(invoice(), rpc)
    assert result.status == expected
    assert not result.rpc_observed


def test_failed_transaction_is_not_a_payment():
    receipt = responses()["eth_getTransactionReceipt"]
    receipt["status"] = "0x0"
    result = inspect_invoice(invoice(), FakeRpc(responses(eth_getTransactionReceipt=receipt)))
    assert result.status == "failed_transaction"


def test_canonical_block_mismatch_prevents_claiming_transfer():
    block = {"number": hex(BLOCK), "hash": "0x" + "3" * 64}
    result = inspect_invoice(invoice(), FakeRpc(responses(eth_getBlockByNumber=block)))
    assert result.status == "noncanonical_block"
    assert not result.rpc_observed


def test_insufficient_confirmations_are_explicit():
    result = inspect_invoice(invoice(), FakeRpc(responses(eth_blockNumber=hex(BLOCK + 2))))
    assert result.status == "insufficient_confirmations"
    assert result.confirmations == 3
    assert not result.rpc_observed


def test_policy_must_be_positive():
    with pytest.raises(ValueError):
        inspect_invoice(invoice(), FakeRpc(), min_confirmations=0)
    with pytest.raises(ValueError):
        inspect_invoice(invoice(), FakeRpc(), min_confirmations=True)


@pytest.mark.parametrize(
    ("modified_log", "status"),
    [
        ({"address": OTHER}, "wrong_token"),
        ({"topics": [
            TRANSFER_TOPIC,
            "0x" + "0" * 24 + "c" * 40,
            "0x" + "0" * 24 + "b" * 40,
        ]}, "wrong_address"),
        ({"data": "0x" + f"{12_345_677:064x}"}, "partial"),
        ({"data": "0x" + f"{12_345_679:064x}"}, "amount_mismatch"),
        ({"topics": ["0x" + "5" * 64]}, "missing_transfer"),
        ({"logIndex": "0x3"}, "missing_transfer"),
        ({"removed": True}, "invalid_evidence"),
        ({"blockHash": "0x" + "4" * 64}, "invalid_evidence"),
        ({"transactionHash": "0x" + "4" * 64}, "invalid_evidence"),
        ({"data": "0x01"}, "invalid_evidence"),
    ],
)
def test_invalid_event_is_never_reported_as_matched(modified_log, status):
    data = responses()
    data["eth_getTransactionReceipt"]["logs"] = [log(**modified_log)]
    result = inspect_invoice(invoice(), FakeRpc(data))
    assert result.status == status
    assert not result.rpc_observed


def test_wrong_token_on_matching_chain_is_explicit():
    receipt = responses()["eth_getTransactionReceipt"]
    receipt["logs"] = [log(address=USDC_CONTRACTS[8453])]
    result = inspect_invoice(invoice(), FakeRpc(responses(eth_getTransactionReceipt=receipt)))
    assert result.status == "wrong_token"


def test_multiple_logs_in_one_tx_require_explicit_event_index():
    receipt = responses()["eth_getTransactionReceipt"]
    receipt["logs"] = [log(), log(logIndex="0x3")]
    rpc = FakeRpc(responses(eth_getTransactionReceipt=receipt))
    assert inspect_invoice(invoice(log_index=None), rpc).status == "ambiguous_transfer"
    assert inspect_invoice(invoice(log_index=3), rpc).status == "rpc_observed_match"


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("transactionHash", "0x" + "3" * 64),
        ("status", None),
        ("blockNumber", "0x00"),
        ("logs", "invalid"),
    ],
)
def test_corrupted_receipt_fails_closed(key, value):
    receipt = responses()["eth_getTransactionReceipt"]
    receipt[key] = value
    result = inspect_invoice(invoice(), FakeRpc(responses(eth_getTransactionReceipt=receipt)))
    assert result.status == "invalid_evidence"
    assert not result.rpc_observed


def test_corrupted_rpc_head_and_block_data_fail_closed():
    bad_head = inspect_invoice(invoice(), FakeRpc(responses(eth_blockNumber="0xZZ")))
    assert bad_head.status == "invalid_evidence"
    bad_block = inspect_invoice(invoice(), FakeRpc(responses(eth_getBlockByNumber=None)))
    assert bad_block.status == "invalid_evidence"


def test_unexpected_rpc_exception_has_no_fabricated_success():
    class BrokenRpc:
        def call(self, method, params):
            raise RuntimeError("a private token that must never leak")

    result = inspect_invoice(invoice(), BrokenRpc())
    assert result.status == "rpc_unavailable"
    assert "private token" not in result.explanation


def test_allowlisted_public_endpoints_only():
    assert BASE_RPC_URLS[8453] == "https://mainnet.base.org"
    assert BASE_RPC_URLS[84532] == "https://sepolia.base.org"
    for unsupported in [1, 137, True]:
        with pytest.raises(ValueError):
            BasePublicRpc(unsupported)
    transport = BasePublicRpc(CHAIN)
    with pytest.raises(ValueError):
        transport.call("eth_sendRawTransaction", ["0xDEAD"])
    with pytest.raises(ValueError):
        BasePublicRpc(CHAIN, timeout_seconds=0)


def test_batch_duplicate_claims_reject_both_even_after_valid_receipts():
    same_event = inspect_invoices([
        invoice(invoice_id="INV-A"), invoice(invoice_id="INV-B"),
    ], FakeRpc())
    assert [r.status for r in same_event] == ["duplicate_claim", "duplicate_claim"]
    assert all(not r.rpc_observed for r in same_event)


def test_batch_distinct_events_do_not_block_each_other():
    data = responses()
    data["eth_getTransactionReceipt"]["logs"] = [log(), log(logIndex="0x3")]
    results = inspect_invoices([
        invoice(invoice_id="INV-A"),
        invoice(invoice_id="INV-B", log_index=3),
    ], FakeRpc(data))
    assert [r.status for r in results] == ["rpc_observed_match", "rpc_observed_match"]


def test_public_rpc_batch_size_is_bounded():
    with pytest.raises(ValueError, match="At most 20"):
        inspect_invoices([invoice()] * 21, FakeRpc())

def test_rpc_redirects_cannot_escape_preselected_base_host():
    # No network request; the handler must refuse even an HTTPS redirect.
    handler = _NoRedirect()
    assert handler.redirect_request(
        None, None, 302, "Found", {}, "https://example.net/redirect-target"
    ) is None


@pytest.mark.parametrize(
    ("upstream", "expected_category"),
    [
        (HTTPError("https://sepolia.base.org", 429, "secret rate token", {}, None),
         "rate_limited"),
        (HTTPError("https://sepolia.base.org", 403, "secret vendor data", {}, None),
         "access_denied"),
        (HTTPError("https://sepolia.base.org", 500, "secret provider failure", {}, None),
         "http_error"),
        (URLError("secret internal hostname"), "network_error"),
    ],
)
def test_transport_classifies_failure_without_exposing_provider_text(
    monkeypatch, upstream, expected_category,
):
    class FakeOpener:
        def open(self, req, timeout):
            raise upstream

    monkeypatch.setattr(
        rpc_module.request, "build_opener",
        lambda *handlers: FakeOpener(),
    )
    transport = BasePublicRpc(CHAIN)
    with pytest.raises(RpcUnavailableError) as captured:
        transport.call("eth_chainId", [])
    assert captured.value.category == expected_category
    assert "secret" not in str(captured.value)

    # The public observation remains a failed, unauthenticated claim.
    observation = inspect_invoice(invoice(), transport)
    assert observation.status == "rpc_unavailable"
    assert not observation.rpc_observed
    assert expected_category in observation.explanation
    assert "secret" not in observation.explanation


@pytest.mark.parametrize(
    ("rpc_data", "expected_category"),
    [
        (b"definitely not JSON", "invalid_response"),
        (b'{"jsonrpc":"2.0","id":1,"error":{"message":"secret vendor error"}}',
         "rpc_error"),
        (b'{"jsonrpc":"2.0","id":1,"result":null}', "invalid_response"),
    ],
)
def test_transport_rejects_malformed_rpc_responses_without_logging_body(
    monkeypatch, rpc_data, expected_category,
):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self, count):
            return rpc_data

    class FakeOpener:
        def open(self, req, timeout):
            return FakeResponse()

    monkeypatch.setattr(
        rpc_module.request, "build_opener",
        lambda *handlers: FakeOpener(),
    )
    with pytest.raises(RpcUnavailableError) as captured:
        BasePublicRpc(CHAIN).call("eth_chainId", [])
    assert captured.value.category == expected_category
    assert "secret" not in str(captured.value)


def test_transport_rejects_valid_rpc_error_envelope_without_exposing_it(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return False

        def read(self, count):
            return b'{"jsonrpc":"2.0","id":1,"error":{"message":"secret vendor error"}}'

    class FakeOpener:
        def open(self, req, timeout):
            return FakeResponse()

    monkeypatch.setattr(
        rpc_module.request, "build_opener",
        lambda *handlers: FakeOpener(),
    )
    with pytest.raises(RpcUnavailableError) as captured:
        BasePublicRpc(CHAIN).call("eth_chainId", [])
    assert captured.value.category == "rpc_error"
    assert "secret" not in str(captured.value)
