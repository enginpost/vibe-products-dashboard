import os
import re
import html
from fastapi import APIRouter
from typing import Dict, List

router = APIRouter()

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(PLUGIN_ROOT, 'config.json')
HIDDEN_PATH = os.path.join(PLUGIN_ROOT, 'hidden.json')

DEFAULT_BASE = r'C:\Users\mchoy\OneDrive\_projects\_Gen_AI\OpenCode\Vibe Products\Source\Data\Vibe Products'

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            import json
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('basePath', DEFAULT_BASE)
        except Exception:
            pass
    return DEFAULT_BASE

def save_config(base_path: str):
    import json
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump({'basePath': base_path}, f)
    except Exception:
        pass

def load_hidden():
    if os.path.exists(HIDDEN_PATH):
        try:
            import json
            with open(HIDDEN_PATH, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()

def save_hidden(hidden_set):
    import json
    try:
        with open(HIDDEN_PATH, 'w', encoding='utf-8') as f:
            json.dump(list(hidden_set), f)
    except Exception:
        pass

def parse_meta(path):
    meta = {}
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            txt = f.read()
        # Support both bold **Key:** Value and plain Key: Value with - or • bullet
        # Value is optional -> .* to allow empty values
        patterns = [
            r'[-•]\s*\*\*(.+?):\*\*\s*(.*)',
            r'[-•]\s*(.+?):\s*(.*)',
        ]
        for pat in patterns:
            for m in re.finditer(pat, txt):
                key = m.group(1).strip()
                val = m.group(2).strip()
                if key.lower() in ('name','status','start date','end date','opencode project','dashboard','priority','repo path'):
                    # Only set if we haven't already got a non-empty value, or allow empty to override
                    if key not in meta or meta[key] != '':
                        meta[key] = val
    except Exception:
        pass
    return meta

def parse_sdlc(path):
    data = {}
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            txt = f.read()
        vm = re.search(r'\*\*Vision Management % Ready:\*\*\s*(\d+)%', txt) or re.search(r'Vision Management % Ready:\s*(\d+)%', txt)
        ie = re.search(r'\*\*Product Iteration executing %:\*\*\s*(\d+)%', txt) or re.search(r'Product Iteration executing %:\s*(\d+)%', txt)
        ir = re.search(r'\*\*Product Iterations Ready %:\*\*\s*(\d+)%', txt) or re.search(r'Product Iterations Ready %:\s*(\d+)%', txt)
        data['vision'] = int(vm.group(1)) if vm else 0
        data['iter_exec'] = int(ie.group(1)) if ie else 0
        data['iter_ready'] = int(ir.group(1)) if ir else 0
    except Exception:
        pass
    return data

def parse_log(log_path):
    entry = ''
    try:
        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        rows = []
        in_table = False
        for line in lines:
            if line.startswith('| Log Entry |'):
                in_table = True
                continue
            if in_table and line.startswith('|---'):
                continue
            if in_table and line.startswith('|'):
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 2:
                    rows.append(parts)
        if rows:
            first = rows[0]
            entry = f"{first[0]} ({first[1]})"
    except Exception:
        pass
    return entry

@router.get('/config')
async def get_config():
    return {'basePath': load_config()}

@router.post('/config')
async def set_config(body: dict):
    base = body.get('basePath') or body.get('base_path')
    if base:
        save_config(str(base))
    return {'ok': True, 'basePath': load_config()}

@router.get('/projects')
async def get_projects():
    base = load_config()
    hidden = load_hidden()
    projects = []
    if os.path.isdir(base):
        for name in os.listdir(base):
            proj_dir = os.path.join(base, name)
            if not os.path.isdir(proj_dir) or name in ('Templates', 'README.md', 'Projects_Index.md'):
                continue
            meta = parse_meta(os.path.join(proj_dir, 'PROJECT_META.md'))
            if meta.get('Dashboard', '').lower() != 'render':
                continue
            sdlc = parse_sdlc(os.path.join(proj_dir, 'SDLC.md'))
            log_entry = parse_log(os.path.join(proj_dir, 'log.md'))
            projects.append({
                'name': meta.get('Name', name),
                'status': meta.get('Status', ''),
                'start': meta.get('Start Date', ''),
                'end': meta.get('End Date', ''),
                'openCodeProject': meta.get('OpenCode Project', ''),
                'vision': sdlc.get('vision', 0),
                'iter_exec': sdlc.get('iter_exec', 0),
                'iter_ready': sdlc.get('iter_ready', 0),
                'log': log_entry,
                'logPath': os.path.join(proj_dir, 'log.md')
            })
    # sort by name
    projects.sort(key=lambda p: p['name'].lower())
    return {'projects': projects, 'hidden': list(hidden)}

@router.post('/hide')
async def toggle_hide(body: dict):
    project = body.get('project')
    if not project:
        return {'ok': False}
    hidden = load_hidden()
    if project in hidden:
        hidden.discard(project)
    else:
        hidden.add(project)
    save_hidden(hidden)
    return {'ok': True, 'hidden': list(hidden)}

@router.post('/open-log')
async def open_log(body: dict):
    name = body.get('name')
    if not name:
        return {'ok': False}
    base = load_config()
    # find project dir by name match
    proj_path = None
    for entry in os.listdir(base):
        proj_dir = os.path.join(base, entry)
        if os.path.isdir(proj_dir):
            meta = parse_meta(os.path.join(proj_dir, 'PROJECT_META.md'))
            if meta.get('Name', entry) == name or entry == name:
                proj_path = os.path.join(proj_dir, 'log.md')
                break
    if proj_path and os.path.exists(proj_path):
        return {'ok': True, 'path': proj_path}
    return {'ok': False}

@router.post('/read-file')
async def read_file(body: dict):
    name = body.get('name')
    if not name:
        return {'ok': False, 'content': ''}
    base = load_config()
    proj_path = None
    for entry in os.listdir(base):
        proj_dir = os.path.join(base, entry)
        if os.path.isdir(proj_dir):
            meta = parse_meta(os.path.join(proj_dir, 'PROJECT_META.md'))
            if meta.get('Name', entry) == name or entry == name:
                proj_path = os.path.join(proj_dir, 'log.md')
                break
    if proj_path and os.path.exists(proj_path):
        try:
            with open(proj_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return {'ok': True, 'content': content, 'path': proj_path}
        except Exception as e:
            return {'ok': False, 'content': '', 'error': str(e)}
    return {'ok': False, 'content': ''}
