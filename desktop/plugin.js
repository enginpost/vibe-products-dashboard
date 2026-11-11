import { jsx, jsxs } from 'react/jsx-runtime'
import { useEffect, useState, useMemo } from 'react'
import { Button, Input, useValue, host } from '@hermes/plugin-sdk'

const DEFAULT_BASE = 'C:\\Users\\mchoy\\OneDrive\\_projects\\_Gen_AI\\OpenCode\\Vibe Products\\Source\\Data\\Vibe Products'
const STORAGE_KEY = 'basePath'
const HIDDEN_KEY = 'hiddenProjects'

function useStored(key, fallback) {
  const [val, setVal] = useState(() => {
    try { return JSON.parse(localStorage.getItem(key) || 'null') ?? fallback } catch { return fallback }
  })
  useEffect(() => {
    const unsub = () => {}
    return unsub
  }, [])
  return [val, setVal]
}

function VibePane({ ctx }) {
  const [basePath, setBasePath] = useState(DEFAULT_BASE)
  const [projects, setProjects] = useState([])
  const [hidden, setHidden] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const load = async () => {
    setLoading(true); setError('')
    try {
      const saved = await ctx.rest('/config').catch(() => null)
      if (saved?.basePath) setBasePath(saved.basePath)
      const data = await ctx.rest('/projects')
      setProjects(data.projects || [])
      setHidden(data.hidden || [])
    } catch (e) {
      setError('Failed to load projects')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const visible = useMemo(() => projects.filter(p => !hidden.includes(p.name)), [projects, hidden])

  const toggleHide = async (name) => {
    try {
      await ctx.rest('/hide', { method: 'POST', body: { project: name } })
      load()
    } catch {}
  }

  const openLog = async (p) => {
    try {
      const res = await ctx.rest('/read-file', { method: 'POST', body: { name: p.name } })
      if (res?.ok && res.content) {
        host.newChat()
        // Use 'new' address for the fresh draft and wait a tick for the composer to mount
        const wait = (ms) => new Promise(r => setTimeout(r, ms))
        await wait(350)
        const text = `Log for ${p.name}:\n\n${res.content}`
        const ok = await host.composer.setDraft('new', text)
        if (ok) {
          host.composer.focus('new')
          host.notify({ kind: 'info', message: `Log for ${p.name} loaded into new chat` })
        } else {
          // fallback to active composer
          const ok2 = await host.composer.setDraft(null, text)
          if (ok2) host.notify({ kind: 'info', message: `Log for ${p.name} loaded` })
          else host.notifyError('Could not open composer for log')
        }
      } else {
        host.notifyError('Could not read log file')
      }
    } catch {
      host.notifyError('Failed to open log')
    }
  }

  if (loading) return jsx('div', { className: 'p-3 text-sm', children: 'Loading...' })
  if (error) return jsx('div', { className: 'p-3 text-sm text-red-500', children: error })

  return jsxs('div', {
    className: 'h-full min-h-0 w-full flex flex-col',
    children: [
      jsxs('div', {
        className: 'flex items-center justify-between px-3 py-2 border-b border-(--ui-stroke-secondary)',
        children: [
          jsx('div', { className: 'text-sm font-medium', children: 'Vibe Products' }),
          jsx(Button, { onClick: load, children: 'Refresh' })
        ]
      }),
      jsx('div', {
        className: 'flex-1 overflow-auto p-3 space-y-3',
        children: visible.length === 0
          ? jsx('div', { className: 'text-sm text-(--ui-text-tertiary)', children: '(there are no active products to show)' })
          : visible.map(p => jsxs('div', {
              className: 'rounded border border-(--ui-stroke-secondary) p-3 bg-(--ui-bg-secondary)',
              children: [
                jsxs('div', { className: 'flex items-start justify-between', children: [
                  jsxs('div', { className: 'font-medium text-sm flex items-center gap-2', children: [
                    jsx('span', { children: '📁' }),
                    p.name
                  ]}),
                  jsx('div', { className: 'text-xs text-(--ui-text-tertiary)', children: `Status: ${p.status || '—'}` })
                ]}),
                jsx('div', { className: 'text-xs text-(--ui-text-tertiary) mt-1', children: `Started: ${p.start || '—'} • End: ${p.end || '—'}` }),
                jsx('div', { className: 'mt-2 space-y-1', children: [
                  metric('Product Vision Management Readiness (%)', p.vision),
                  metric('Product Iterations Ready for Execution (%)', p.iter_ready),
                  metric('Product Iterations Executing (%)', p.iter_exec),
                ]}),
                jsx('div', { className: 'text-xs text-(--ui-text-tertiary) mt-2', children: `Last log: ${p.log || '—'}` }),
                jsxs('div', { className: 'flex gap-2 mt-2', children: [
                  jsx(Button, { onClick: () => openLog(p), children: 'All Logs' }),
                  jsx(Button, { onClick: () => toggleHide(p.name), children: hidden.includes(p.name) ? 'Show' : 'Hide' })
                ]})
              ]
            }, p.name))
      })
    ]
  })
}

function metric(label, value) {
  const v = Number(value) || 0
  return jsxs('div', {
    children: [
      jsx('div', { className: 'text-[11px] text-(--ui-text-tertiary)', children: label }),
      jsxs('div', { className: 'flex items-center gap-2', children: [
        jsx('div', { className: 'flex-1 h-2 rounded bg-(--ui-bg-tertiary) overflow-hidden', children: jsx('div', { className: 'h-full bg-(--ui-accent)', style: { width: `${v}%` } }) }),
        jsx('div', { className: 'text-[11px] w-10 text-right text-(--ui-text-tertiary)', children: `${v}%` })
      ]})
    ]
  })
}

function SettingsPage({ ctx }) {
  const [base, setBase] = useState(DEFAULT_BASE)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    ctx.rest('/config').then(r => { if (r?.basePath) setBase(r.basePath) }).catch(()=>{})
  }, [])

  const save = async () => {
    await ctx.rest('/config', { method: 'POST', body: { basePath: base } })
    setSaved(true)
    setTimeout(()=>setSaved(false), 1500)
  }

  return jsxs('div', {
    className: 'p-4 space-y-3 max-w-xl',
    children: [
      jsx('div', { className: 'text-sm font-medium', children: 'Vibe Products Base Path' }),
      jsx(Input, { value: base, onChange: e => setBase(e.target.value), placeholder: 'Path to Vibe Products folder' }),
      jsx(Button, { onClick: save, children: 'Save' }),
      saved && jsx('div', { className: 'text-xs text-(--ui-text-tertiary)', children: 'Saved' })
    ]
  })
}

export default {
  id: 'vibe-products-dashboard',
  name: 'Vibe Products Dashboard',
  defaultEnabled: true,
  register(ctx) {
    ctx.register({
      id: 'dashboard-pane',
      area: 'panes',
      title: 'Vibe Products',
      data: { placement: 'right', dock: { pane: 'workspace', pos: 'right' }, width: '45%' },
      render: () => jsx(VibePane, { ctx })
    })
    ctx.registerSettingsPage({
      id: 'vibe-products',
      title: 'Vibe Products Dashboard',
      render: () => jsx(SettingsPage, { ctx })
    })
  }
}
