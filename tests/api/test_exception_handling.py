from fastapi.testclient import TestClient

from packages.api.app import app


@app.get("/test-unhandled-error")
async def unhandled_error_endpoint() -> None:
    raise RuntimeError("Unexpected failure")


def test_unhandled_exception_returns_standard_error() -> None:
    client = TestClient(
        app,
        raise_server_exceptions=False,
    )

    response = client.get("/test-unhandled-error")

    assert response.status_code == 500

    payload = response.json()

    assert payload["error"]["code"] == "internal_server_error"
    assert "correlation_id" in payload["error"]
