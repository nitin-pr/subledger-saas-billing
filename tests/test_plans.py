from tests.factories import make_plan


def test_create_plan_success(client):
    plan = make_plan(client, name="Pro Monthly", price="29.99")
    assert plan["status"] == "active"
    assert plan["price"] == "29.99"


def test_create_plan_with_zero_price_is_rejected(client):
    resp = client.post("/plans", json={"name": "Free", "billing_cycle": "monthly", "price": "0"})
    assert resp.status_code == 422


def test_create_plan_with_negative_price_is_rejected(client):
    resp = client.post(
        "/plans", json={"name": "Negative", "billing_cycle": "monthly", "price": "-5"}
    )
    assert resp.status_code == 422


def test_patch_plan_can_deactivate(client):
    plan = make_plan(client)
    resp = client.patch(f"/plans/{plan['id']}", json={"status": "inactive"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "inactive"


def test_patch_unknown_plan_returns_404(client):
    resp = client.patch("/plans/999", json={"status": "inactive"})
    assert resp.status_code == 404


def test_list_plans_returns_all_created(client):
    make_plan(client, name="A")
    make_plan(client, name="B", billing_cycle="yearly", price="100")
    resp = client.get("/plans")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
