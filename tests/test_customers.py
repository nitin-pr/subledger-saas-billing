from tests.factories import make_customer


def test_create_customer_success(client):
    customer = make_customer(client, email="alice@example.com")
    assert customer["email"] == "alice@example.com"
    assert customer["status"] == "active"


def test_create_customer_with_duplicate_email_rejected(client):
    make_customer(client, email="alice@example.com")
    resp = client.post("/customers", json={"name": "Alice Two", "email": "alice@example.com"})
    assert resp.status_code == 400


def test_get_customer_not_found_returns_404(client):
    resp = client.get("/customers/999")
    assert resp.status_code == 404


def test_list_customers_returns_all_created(client):
    make_customer(client, email="a@example.com")
    make_customer(client, email="b@example.com")
    resp = client.get("/customers")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
