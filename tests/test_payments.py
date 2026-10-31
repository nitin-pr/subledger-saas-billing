from tests.factories import make_invoice_for_new_subscription


def test_full_payment_marks_invoice_paid(client):
    _, invoice = make_invoice_for_new_subscription(client, price="100.00")

    resp = client.post(
        "/payments/record", json={"invoice_id": invoice["id"], "amount": "100.00", "status": "success"}
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["invoice"]["status"] == "paid"
    assert data["invoice"]["amount_paid"] == "100.00"
    assert data["payment_attempt"]["status"] == "success"


def test_partial_payment_marks_invoice_partially_paid(client):
    _, invoice = make_invoice_for_new_subscription(client, price="100.00")

    resp = client.post(
        "/payments/record", json={"invoice_id": invoice["id"], "amount": "40.00", "status": "success"}
    )
    assert resp.status_code == 201
    assert resp.json()["invoice"]["status"] == "partially_paid"
    assert resp.json()["invoice"]["amount_paid"] == "40.00"


def test_payment_exceeding_remaining_unpaid_amount_is_rejected(client):
    _, invoice = make_invoice_for_new_subscription(client, price="100.00")

    resp = client.post(
        "/payments/record", json={"invoice_id": invoice["id"], "amount": "150.00", "status": "success"}
    )
    assert resp.status_code == 400
    # Invoice must be untouched.
    get_resp = client.get(f"/invoices/{invoice['id']}")
    assert get_resp.json()["amount_paid"] == "0.00"
    assert get_resp.json()["status"] == "issued"


def test_failed_payment_does_not_increase_amount_paid(client):
    _, invoice = make_invoice_for_new_subscription(client, price="100.00")

    resp = client.post(
        "/payments/record",
        json={
            "invoice_id": invoice["id"],
            "amount": "50.00",
            "status": "failed",
            "failure_reason": "card_declined",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["invoice"]["amount_paid"] == "0.00"
    assert data["invoice"]["status"] == "issued"
    assert data["payment_attempt"]["failure_reason"] == "card_declined"


def test_two_partial_payments_can_fully_pay_an_invoice(client):
    _, invoice = make_invoice_for_new_subscription(client, price="100.00")

    client.post(
        "/payments/record", json={"invoice_id": invoice["id"], "amount": "60.00", "status": "success"}
    )
    resp = client.post(
        "/payments/record", json={"invoice_id": invoice["id"], "amount": "40.00", "status": "success"}
    )
    assert resp.json()["invoice"]["status"] == "paid"
    assert resp.json()["invoice"]["amount_paid"] == "100.00"


def test_payment_for_unknown_invoice_returns_404(client):
    resp = client.post(
        "/payments/record", json={"invoice_id": 999, "amount": "10.00", "status": "success"}
    )
    assert resp.status_code == 404


def test_successful_payment_creates_payment_success_ledger_entry(client):
    customer, invoice = make_invoice_for_new_subscription(client, price="100.00")
    client.post(
        "/payments/record", json={"invoice_id": invoice["id"], "amount": "100.00", "status": "success"}
    )

    ledger = client.get(f"/customers/{customer['id']}/ledger").json()
    entry_types = [entry["entry_type"] for entry in ledger]
    assert "invoice_created" in entry_types
    assert "payment_success" in entry_types


def test_failed_payment_creates_payment_failure_ledger_entry(client):
    customer, invoice = make_invoice_for_new_subscription(client, price="100.00")
    client.post(
        "/payments/record",
        json={"invoice_id": invoice["id"], "amount": "50.00", "status": "failed"},
    )

    ledger = client.get(f"/customers/{customer['id']}/ledger").json()
    entry_types = [entry["entry_type"] for entry in ledger]
    assert "payment_failure" in entry_types
