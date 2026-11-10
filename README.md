# Vibe Products Dashboard – Hermes Desktop Plugin

Self-contained Hermes Desktop plugin that renders your Vibe Projects dashboard natively.

## Install via Git in Hermes Desktop

Hermes Desktop can install desktop plugins from a git repo.

1. Create a new GitHub repo, e.g. `vibe-products-dashboard`
2. Push this repo:
```bash
git remote add origin https://github.com/<your-user>/vibe-products-dashboard.git
git branch -M main
git push -u origin main
```
3. In Hermes Desktop: Settings → Plugins → Install from Git → paste the repo URL
   - The plugin id is `vibe-products-dashboard` and must match the folder name.

## Structure
```
vibe-products-dashboard/
  plugin.js        # Desktop UI, pane + settings page
  plugin_api.py    # Backend API: /config /projects /hide /open-log
  config.json      # Base path for Vibe Projects data
  hidden.json      # Persisted hidden projects
```

## Configuration
Open Settings → Plugins → Vibe Products Dashboard to set the `Vibe Projects Base Path`. Default:
`C:\Users\mchoy\OneDrive\_projects\_Gen_AI\OpenCode\Vibe Products\Source\Data\Vibe Products`

Backend must be enabled in `config.yaml`:
```yaml
plugins:
  enabled:
    - vibe-products-dashboard
```
Restart the gateway after enabling.

## Development
Edit files, commit & push. Hermes Desktop will pull updates on next plugin refresh or when you use "Update from Git".
