# Passkey-Vault für Tasker

Dieser Flask-Dienst speichert Zugangsdaten verschlüsselt und gibt sie erst nach
einer erfolgreichen WebAuthn-Authentifizierung zurück. Er lauscht standardmäßig
auf `0.0.0.0:4099`.

> **Wichtige Plattformgrenze:** Eine reine Tasker-HTTP-Aktion kann kein
> Fingerabdruck-/PIN-/FIDO-Fenster öffnen. WebAuthn darf nur in einem sicheren
> Browser-Kontext (HTTPS; `localhost` ist die einzige HTTP-Ausnahme) oder in
> einer Android-App mit Credential Manager ausgeführt werden. Der mitgelieferte
> Web-Client öffnet nur die WebAuthn-Oberfläche; für wirklich browserlosen
> Betrieb muss eine kleine Android-/Tasker-Plugin-App die JSON-Endpunkte aufrufen
> und die erhaltenen Optionen an Android Credential Manager übergeben.

## Installation und Start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export VAULT_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export RP_ID=example.local
export ORIGIN=https://example.local:4099
python app.py
```

Im Netzwerk muss vor Flask ein HTTPS-Reverse-Proxy stehen. `RP_ID` ist nur der
Hostname, `ORIGIN` enthält Schema und gegebenenfalls Port. Ohne dauerhaftes
`VAULT_KEY` können gespeicherte Passwörter nach einem Neustart nicht mehr
entschlüsselt werden.

## Aufrufe

* Registrierung (kompatibel zur gewünschten URL):
  `https://example.local:4099/register?username=max&password=geheim&create-passkey&type=fido`
* Plattform-Passkey (Fingerabdruck/PIN): `type=fingerprint`
* Abruf: `https://example.local:4099/get?username=max`

Passwörter in URLs landen häufig in Verlauf und Proxy-Logs. Deshalb ist
`POST /api/register/options` mit JSON (`username`, `password`, `type`) die
empfohlene Schnittstelle. Die HTML-Seite ist nur ein Referenz-Client.

## API-Ablauf für Android/Tasker-Plugin

1. `POST /api/register/options`, WebAuthn-Credential erstellen, dann dessen JSON
   an `POST /api/register/verify` senden.
2. `POST /api/authenticate/options` mit `username`, Assertion erzeugen, dann an
   `POST /api/authenticate/verify` senden.
3. Die zweite Antwort enthält bei Erfolg `username` und `password`.

Challenges liegen kurzlebig in der Flask-Session. Cookies müssen deshalb bei
beiden Requests eines Ablaufs erhalten bleiben.

## Entwicklung

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
```
