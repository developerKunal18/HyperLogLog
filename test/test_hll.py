import pytest
import app as app_module


@pytest.fixture()
def client():
    app_module.hll = app_module.HyperLogLog(8)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as client:
        yield client


def test_empty_count_is_zero():
    assert app_module.HyperLogLog(8).count() == 0


def test_unique_items_are_estimated_reasonably():
    hll = app_module.HyperLogLog(10)
    for i in range(1000):
        hll.add(f"user-{i}")
    assert 800 <= hll.count() <= 1250


def test_duplicates_do_not_grow_cardinality():
    hll = app_module.HyperLogLog(10)
    for _ in range(100):
        hll.add("same-user")
    assert hll.count() <= 2


def test_batch_api(client):
    response = client.post("/api/items/batch", json={"values": [f"u-{i}" for i in range(100)]})
    assert response.status_code == 201
    assert 70 <= response.get_json()["estimated_unique"] <= 140


def test_invalid_value(client):
    assert client.post("/api/items", json={"value": ""}).status_code == 400


def test_stats(client):
    client.post("/api/items", json={"value": "a"})
    data = client.get("/api/stats").get_json()
    assert data["precision"] == 8
    assert data["registers"] == 256
    assert data["non_zero_registers"] > 0


def test_precision_validation():
    with pytest.raises(ValueError):
        app_module.HyperLogLog(3)
    with pytest.raises(ValueError):
        app_module.HyperLogLog(17)
