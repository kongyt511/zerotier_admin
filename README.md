# ZeroTier Admin

A web-based admin UI for self-hosted ZeroTier controllers.

**Stack:** Vue 3 + Naive UI (frontend) · FastAPI + uvicorn (backend)

## Requirements

- Python 3.10+
- Node.js 18+

## Build & Deploy

### 1. Build the frontend

```bash
cd frontend
npm install
npm run build
```

This generates `frontend/dist/`, which the backend serves automatically.

### 2. Install backend dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Start the server

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

Open `http://<host>:8000` in your browser.

## Configuration

On first visit, go to the Settings page and enter:

- **ZeroTier URL** — controller API address, default `http://localhost:9993`
- **API Token** — found in `/var/lib/zerotier-one/authtoken.secret`

Settings are saved to `backend/config.json`.

## Development

Start both servers separately:

```bash
# Terminal 1 — backend
cd backend
uvicorn main:app --reload

# Terminal 2 — frontend
cd frontend
npm run dev
```

Frontend dev server runs on `http://localhost:5173` and proxies API calls to the backend.

## Run as a System Service (Linux)

Create `/etc/systemd/system/zerotier-admin.service`:

```ini
[Unit]
Description=ZeroTier Admin
After=network.target

[Service]
WorkingDirectory=/opt/zerotier_admin/backend
ExecStart=/usr/local/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Then enable and start:

```bash
sudo systemctl enable --now zerotier-admin
```
