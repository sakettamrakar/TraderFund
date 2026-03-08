import fs from 'node:fs'
import path from 'node:path'

import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

const repoRoot = path.resolve(__dirname, '../../..')
const runtimeStatePath = path.join(repoRoot, '.runtime', 'service_ports.json')

function readRuntimeState() {
  if (!fs.existsSync(runtimeStatePath)) {
    return { services: {} }
  }

  try {
    return JSON.parse(fs.readFileSync(runtimeStatePath, 'utf-8'))
  } catch {
    return { services: {} }
  }
}

function readAssignedPort(serviceKey, fallbackPort) {
  const runtimeState = readRuntimeState()
  const assigned = runtimeState.services?.[serviceKey]?.port
  const port = Number(assigned ?? fallbackPort)
  return Number.isFinite(port) ? port : Number(fallbackPort)
}

function readAssignedUrl(serviceKey, fallbackHost, fallbackPort) {
  const runtimeState = readRuntimeState()
  const service = runtimeState.services?.[serviceKey]
  const host = service?.public_host ?? fallbackHost
  const port = readAssignedPort(serviceKey, fallbackPort)
  return `http://${host}:${port}`
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, repoRoot, '')
  const frontendPort = readAssignedPort('dashboard_frontend', env.FRONTEND_PORT || 21011)
  const apiHost = env.API_PUBLIC_HOST || '127.0.0.1'
  const apiPort = env.API_PORT || 21010
  const frontendHost = env.FRONTEND_BIND_HOST || '0.0.0.0'

  return {
    envDir: repoRoot,
    plugins: [react()],
    server: {
      host: frontendHost,
      port: frontendPort,
      proxy: {
        '/api': {
          target: readAssignedUrl('dashboard_api', apiHost, apiPort),
          changeOrigin: true,
          secure: false,
          router: () => readAssignedUrl('dashboard_api', apiHost, apiPort),
        },
      },
    },
    preview: {
      host: frontendHost,
      port: Number(env.FRONTEND_PREVIEW_PORT || frontendPort + 20),
    },
  }
})
