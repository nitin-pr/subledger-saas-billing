from tests.factories import make_invoice_for_new_subscription


def test_ledger_has_no_update_or_delete_route(client):
    # The API exposes no PATCH/PUT/DELETE for ledger entries anywhere —
    # ledger entries are append-only by construction (no such route exists).
    resp = client.patch("/customers/1/ledger", json={})
    assert resp.status_code == 405  # method not allowed on an existing GET-only path


def test_ledger_entries_are_traceable_via_reference_id(client):
    customer, invoice = make_invoice_for_new_subscription(client, price="100.00")
    client.post(
        "/payments/record", json={"invoice_id": invoice["id"], "amount": "100.00", "status": "success"}
    )

    ledger = client.get(f"/customers/{customer['id']}/ledger").json()
    invoice_entry = next(e for e in ledger if e["entry_type"] == "invoice_created")
    payment_entry = next(e for e in ledger if e["entry_type"] == "payment_success")

    assert invoice_entry["reference_id"] == f"invoice:{invoice['id']}"
    assert payment_entry["reference_id"].startswith("payment:")


def test_ledger_for_unknown_customer_returns_404(client):
    resp = client.get("/customers/999/ledger")
    assert resp.status_code == 404


def test_ledger_entries_ordered_chronologically(client):
    customer, invoice = make_invoice_for_new_subscription(client, price="100.00")
    client.post(
        "/payments/record", json={"invoice_id": invoice["id"], "amount": "100.00", "status": "success"}
    )

    ledger = client.get(f"/customers/{customer['id']}/ledger").json()
    assert [e["entry_type"] for e in ledger] == ["invoice_created", "payment_success"]
