# Vibe Products Dashboard – Hermes Desktop Plugin

Self-contained Hermes Desktop plugin that renders your Vibe Projects dashboard natively.

## Install

### Windows / local Hermes Desktop
1. Open Hermes Desktop → Settings → Plugins → Install from Git
2. Paste the repo URL:
   ```
   https://github.com/enginpost/vibe-products-dashboard.git
   ```
3. The plugin will be installed to `%LOCALAPPDATA%\hermes\desktop-plugins\vibe-products-dashboard\`
4. Reload desktop plugins in Hermes Desktop.

### Remote Hermes Agent
If you are running a remote Hermes Agent (e.g., Ubuntu gateway), install the plugin on the agent host via SSH:

```bash
ssh user@your-hermes-host
HERMES_HOME=/mnt/data/hermes hermes plugins install https://github.com/enginpost/vibe-products-dashboard.git
HERMES_HOME=/mnt/data/hermes hermes plugins enable vibe-products-dashboard
HERMES_HOME=/mnt/data/hermes hermes gateway restart -y
```

The desktop UI is installed on your Windows machine, and the backend `dashboard/plugin_api.py` runs on the remote agent where the Vibe Products data lives.

## Structure
```
vibe-products-dashboard/
  desktop/plugin.js        # Desktop UI, pane + settings page
  dashboard/plugin_api.py  # Backend API: /config /projects /hide /open-log
  config.json              # Base path for Vibe Projects data
  plugin.yaml              # Plugin manifest
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
