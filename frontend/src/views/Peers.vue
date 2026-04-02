<template>
  <div>
    <n-page-header title="Peers 对等节点">
      <template #extra>
        <n-space align="center">
          <n-text depth="3" style="font-size: 13px">自动刷新</n-text>
          <n-switch v-model:value="autoRefresh" @update:value="toggleAutoRefresh" />
          <n-button @click="load" :loading="loading">刷新</n-button>
        </n-space>
      </template>
    </n-page-header>

    <n-alert v-if="error" type="error" :title="error" style="margin-top: 16px" />

    <n-input
      v-model:value="search"
      placeholder="搜索节点地址..."
      clearable
      style="margin-top: 16px; max-width: 340px"
    />

    <n-data-table
      style="margin-top: 12px"
      :columns="columns"
      :data="filtered"
      :loading="loading"
      :pagination="{ pageSize: 20 }"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import {
  NPageHeader, NButton, NAlert, NDataTable, NTag, NText, NSwitch, NSpace, NInput,
  NProgress,
} from 'naive-ui'
import { peersApi } from '../api/index.js'

const peers = ref([])
const loading = ref(false)
const error = ref('')
const search = ref('')
const autoRefresh = ref(false)
let timer = null

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return peers.value
  return peers.value.filter(p => p.address?.toLowerCase().includes(q))
})

function roleTag(role) {
  const map = { PLANET: 'info', MOON: 'warning', LEAF: 'default' }
  return h(NTag, { type: map[role] ?? 'default', size: 'small' }, () => role)
}

function latencyBar(ms) {
  if (!ms || ms < 0) return h(NText, { depth: 3 }, () => '—')
  const pct = Math.min(ms / 500 * 100, 100)
  const status = ms < 50 ? 'success' : ms < 150 ? 'warning' : 'error'
  return h('div', { style: 'display:flex; align-items:center; gap:8px' }, [
    h(NProgress, {
      type: 'line',
      percentage: pct,
      status,
      showIndicator: false,
      style: 'width:80px',
      height: 6,
    }),
    h(NText, { style: 'font-size:12px' }, () => `${ms}ms`),
  ])
}

const columns = [
  { title: '节点地址', key: 'address', render: (row) => h('code', row.address) },
  { title: '版本', key: 'version', render: (row) => row.version || '—' },
  { title: '角色', key: 'role', render: (row) => roleTag(row.role) },
  { title: '延迟', key: 'latency', render: (row) => latencyBar(row.latency) },
  {
    title: '路径数',
    key: 'paths',
    render: (row) => (row.paths || []).length,
  },
  {
    title: '直连',
    key: 'isMoon',
    render: (row) => {
      const direct = (row.paths || []).some(p => p.active)
      return h(NTag, { type: direct ? 'success' : 'default', size: 'small' }, () => direct ? '直连' : '中继')
    },
  },
  {
    title: '路径详情',
    key: 'pathDetail',
    render: (row) => {
      const active = (row.paths || []).find(p => p.active)
      return active ? h('code', { style: 'font-size:12px' }, active.address) : '—'
    },
  },
]

async function load() {
  loading.value = true
  error.value = ''
  try {
    const r = await peersApi.list()
    peers.value = r.data
  } catch (e) {
    error.value = e.response?.data?.detail ?? e.message
  } finally {
    loading.value = false
  }
}

function toggleAutoRefresh(val) {
  clearInterval(timer)
  if (val) timer = setInterval(load, 5000)
}

onMounted(load)
onUnmounted(() => clearInterval(timer))
</script>
