import pytest
from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route("/api/v1/auth/jit", methods=["POST"])
def jit_request():
    return jsonify({"status": "auto-grant", "req_id": "test_123"}), 200

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_jit_route_success(client):
    res = client.post("/api/v1/auth/jit", json={"user_id": "u1", "reason": "emergency"})
    assert res.status_code == 200
    assert res.get_json()["status"] == "auto-grant"
