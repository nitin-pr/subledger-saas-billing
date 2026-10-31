from tests.factories import make_customer, make_plan, make_subscription


def test_generate_invoice_amount_due_matches_plan_price(client):
    plan = make_plan(client, price="49.99")
    customer = make_customer(client)
    subscription = make_subscription(client, customer["id"], plan["id"])

    resp = client.post("/invoices/generate", json={"subscription_id": subscription["id"]})
    assert resp.status_code == 201
    data = resp.json()
    assert data["amount_due"] == "49.99"
    assert float(data["amount_paid"]) == 0
    assert data["status"] == "issued"


def test_already_generated_invoice_is_unaffected_by_a_later_plan_price_change(client):
    # amount_due is taken from the plan price *at generation time* — each
    # new invoice reflects the current price, but an already-created
    # invoice must never retroactively change when the plan price moves.
    plan = make_plan(client, price="49.99")
    customer = make_customer(client)
    subscription = make_subscription(client, customer["id"], plan["id"])

    first_invoice = client.post(
        "/invoices/generate", json={"subscription_id": subscription["id"]}
    ).json()
    assert first_invoice["amount_due"] == "49.99"

    client.patch(f"/plans/{plan['id']}", json={"price": "99.99"})

    # The first invoice, already persisted, must be untouched.
    refetched = client.get(f"/invoices/{first_invoice['id']}").json()
    assert refetched["amount_due"] == "49.99"

    # A newly generated invoice picks up the new price.
    second_invoice = client.post(
        "/invoices/generate", json={"subscription_id": subscription["id"]}
    ).json()
    assert second_invoice["amount_due"] == "99.99"


def test_generate_invoice_for_unknown_subscription_returns_404(client):
    resp = client.post("/invoices/generate", json={"subscription_id": 999})
    assert resp.status_code == 404


def test_generate_invoice_for_cancelled_subscription_is_rejected(client):
    plan = make_plan(client)
    customer = make_customer(client)
    subscription = make_subscription(client, customer["id"], plan["id"])
    client.patch(f"/subscriptions/{subscription['id']}/cancel")

    resp = client.post("/invoices/generate", json={"subscription_id": subscription["id"]})
    assert resp.status_code == 400


def test_generate_invoice_writes_invoice_created_ledger_entry(client):
    plan = make_plan(client)
    customer = make_customer(client)
    subscription = make_subscription(client, customer["id"], plan["id"])
    client.post("/invoices/generate", json={"subscription_id": subscription["id"]})

    ledger = client.get(f"/customers/{customer['id']}/ledger").json()
    assert len(ledger) == 1
    assert ledger[0]["entry_type"] == "invoice_created"


def test_get_invoice_not_found_returns_404(client):
    resp = client.get("/invoices/999")
    assert resp.status_code == 404
