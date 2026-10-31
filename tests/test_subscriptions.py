from tests.factories import make_customer, make_plan, make_subscription


def test_create_subscription_success(client):
    plan = make_plan(client)
    customer = make_customer(client)
    subscription = make_subscription(client, customer["id"], plan["id"])
    assert subscription["status"] == "active"
    assert subscription["customer_id"] == customer["id"]
    assert subscription["plan_id"] == plan["id"]


def test_subscription_to_inactive_plan_is_rejected(client):
    plan = make_plan(client)
    client.patch(f"/plans/{plan['id']}", json={"status": "inactive"})
    customer = make_customer(client)

    resp = client.post(
        "/subscriptions", json={"customer_id": customer["id"], "plan_id": plan["id"]}
    )
    assert resp.status_code == 400


def test_duplicate_active_subscription_to_same_plan_is_rejected(client):
    plan = make_plan(client)
    customer = make_customer(client)
    make_subscription(client, customer["id"], plan["id"])

    resp = client.post(
        "/subscriptions", json={"customer_id": customer["id"], "plan_id": plan["id"]}
    )
    assert resp.status_code == 400


def test_subscription_for_unknown_customer_returns_404(client):
    plan = make_plan(client)
    resp = client.post("/subscriptions", json={"customer_id": 999, "plan_id": plan["id"]})
    assert resp.status_code == 404


def test_cancel_subscription_sets_status_cancelled(client):
    plan = make_plan(client)
    customer = make_customer(client)
    subscription = make_subscription(client, customer["id"], plan["id"])

    resp = client.patch(f"/subscriptions/{subscription['id']}/cancel")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"
    assert resp.json()["cancelled_at"] is not None


def test_resubscribing_after_cancellation_is_allowed(client):
    plan = make_plan(client)
    customer = make_customer(client)
    subscription = make_subscription(client, customer["id"], plan["id"])
    client.patch(f"/subscriptions/{subscription['id']}/cancel")

    resp = client.post(
        "/subscriptions", json={"customer_id": customer["id"], "plan_id": plan["id"]}
    )
    assert resp.status_code == 201
