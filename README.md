# Condominio Compliant (MVP locale, zero costi)

MVP locale per amministratori condominiali:
- anagrafica amministratori e condomini
- generazione automatica scadenze normative
- dashboard con stati `ok`, `in_scadenza`, `scaduto`
- job notifiche simulato (log locale, nessun costo API)

## Stack
- Python 3.11+
- FastAPI + Jinja2
- SQLite locale (file `condominio.db`)
- Pytest

## Struttura
- `app/main.py` → server web + endpoint
- `app/models.py` → tabelle (`administrators`, `buildings`, `deadline_types`, `building_deadlines`)
- `app/db.py` → init DB + seed scadenze italiane
- `app/services.py` → onboarding, calcolo stati, utility date
- `scripts/run_notifications.sh` → trigger notifiche
- `tests/` → test unitari

## Avvio locale
```bash
cd ~/.openclaw/workspace-developer/business-ideas/condominio-compliant
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Apri: `http://127.0.0.1:8000`

## Flusso rapido demo
1. Vai su `/onboarding`
2. Inserisci amministratore + condominio
3. Seleziona tipologie impianto
4. Apri `/dashboard` per vedere le scadenze
5. Esegui notifiche da `/api/notifications/run` oppure:
   ```bash
   ./scripts/run_notifications.sh
   ```

Le notifiche vengono salvate in `notifications.log` (simulazione email/WhatsApp senza costi).

## Test
```bash
cd ~/.openclaw/workspace-developer/business-ideas/condominio-compliant
source .venv/bin/activate
pytest -q
```

## Note zero-costi
- Nessun servizio cloud obbligatorio
- Nessuna API a pagamento
- Tutto gira in locale con SQLite

## Possibili estensioni future
- invio email SMTP reale
- integrazione WhatsApp Cloud API
- autenticazione utenti e multi-tenant avanzato
