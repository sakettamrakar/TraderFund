# Dashboard Frontend

The dashboard frontend reads its preferred port from the repository `.env` file and its live cross-service targets from `.runtime/service_ports.json`.

Startup flow:

1. `npm run dev` runs `scripts/prepare_dashboard_frontend.py`
2. The port manager reserves a free port inside TraderFund's `21000-21050` range
3. Vite starts on that assigned port
4. The `/api` proxy resolves the current dashboard API target from the shared runtime assignment file

Useful commands:

```bash
npm run dev
npm run preview
```

To inspect current assignments:

```bash
python -m utils.port_manager show
```
