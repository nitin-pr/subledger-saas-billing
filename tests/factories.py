def make_plan(client, **overrides):
    payload = {"name": "Pro", "billing_cycle": "monthly", "price": "20.00"}
    payload.update(overrides)
    resp = client.post("/plans", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


def make_customer(client, email="cust@example.com", **overrides):
    payload = {"name": "Cust", "email": email}
    payload.update(overrides)
    resp = client.post("/customers", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


def make_subscription(client, customer_id, plan_id, **overrides):
    payload = {"customer_id": customer_id, "plan_id": plan_id}
    payload.update(overrides)
    resp = client.post("/subscriptions", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


def make_invoice_for_new_subscription(client, price="100.00"):
    """Creates a plan + customer + active subscription + generated invoice
    in one call, returning (customer, invoice)."""
    plan = make_plan(client, price=price)
    customer = make_customer(client)
    subscription = make_subscription(client, customer["id"], plan["id"])
    resp = client.post("/invoices/generate", json={"subscription_id": subscription["id"]})
    assert resp.status_code == 201, resp.text
    return customer, resp.json()
