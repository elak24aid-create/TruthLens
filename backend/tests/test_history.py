from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_history_crud_flow():
    # 1. Add item
    payload = {
        "text_snippet": "World leaders gather for international climate conference in Geneva.",
        "verdict": "Likely Genuine",
        "confidence": 82,
        "summary": "Verified through established transparent sources.",
        "input_type": "text",
    }
    create_res = client.post("/api/history", json=payload)
    assert create_res.status_code == 201
    created = create_res.json()
    assert "id" in created
    item_id = created["id"]

    # 2. Get history list
    list_res = client.get("/api/history")
    assert list_res.status_code == 200
    items = list_res.json()
    assert any(i["id"] == item_id for i in items)

    # 3. Delete item
    del_res = client.delete(f"/api/history/{item_id}")
    assert del_res.status_code == 200

    # 4. Verify deleted
    list_res_after = client.get("/api/history")
    items_after = list_res_after.json()
    assert not any(i["id"] == item_id for i in items_after)
