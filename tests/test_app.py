from cryptography.fernet import Fernet

from app import create_app


def configured_app(tmp_path):
    return create_app(
        {
            "TESTING": True,
            "DATABASE": tmp_path / "test.db",
            "VAULT_KEY": Fernet.generate_key(),
        }
    )


def test_health(tmp_path):
    app = configured_app(tmp_path)
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_registration_rejects_invalid_type(tmp_path):
    app = configured_app(tmp_path)
    response = app.test_client().post(
        "/api/register/options",
        json={"username": "max", "password": "secret", "type": "magic"},
    )
    assert response.status_code == 400
    assert "type=fido|fingerprint" in response.json["error"]


def test_authentication_unknown_user(tmp_path):
    app = configured_app(tmp_path)
    response = app.test_client().post("/api/authenticate/options", json={"username": "nobody"})
    assert response.status_code == 400
    assert response.json == {"error": "Unbekannter Benutzer"}
