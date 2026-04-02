<template>
  <div>
    <n-page-header title="网络管理">
      <template #extra>
        <n-space>
          <n-button @click="triggerImport">导入网络</n-button>
          <n-button type="primary" @click="showCreate = true">+ 创建网络</n-button>
        </n-space>
      </template>
    </n-page-header>

    <n-alert v-if="error" type="error" :title="error" style="margin-top: 16px" />

    <n-input
      v-model:value="search"
      placeholder="搜索网络 ID 或名称..."
      clearable
      style="margin-top: 16px; max-width: 340px"
    />

    <n-data-table
      style="margin-top: 12px"
      :columns="columns"
      :data="filtered"
      :loading="loading"
      :row-props="rowProps"
    />

    <!-- Create Network Modal -->
    <n-modal v-model:show="showCreate" preset="card" title="创建新网络" style="width: 500px">
      <n-form :model="form" label-placement="left" label-width="100">
        <n-form-item label="网络名称">
          <n-input v-model:value="form.name" placeholder="可选" />
        </n-form-item>
        <n-form-item label="私有网络">
          <n-switch v-model:value="form.private" />
        </n-form-item>
        <n-form-item label="IP 地址池">
          <n-input-group>
            <n-input v-model:value="form.ipStart" placeholder="起始 IP，如 10.147.17.1" />
            <n-input-group-label>—</n-input-group-label>
            <n-input v-model:value="form.ipEnd" placeholder="结束 IP，如 10.147.17.254" />
          </n-input-group>
        </n-form-item>
        <n-form-item label="路由网段">
          <n-input v-model:value="form.route" placeholder="如 10.147.17.0/24" />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showCreate = false">取消</n-button>
          <n-button type="primary" :loading="creating" @click="createNetwork">创建</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- Import Modal -->
    <n-modal v-model:show="showImport" preset="card" title="导入网络配置" style="width: 560px">
      <n-form label-placement="left" label-width="100">
        <n-form-item label="目标网络 ID">
          <n-input v-model:value="importNwid" placeholder="留空则创建新网络（暂不支持）" />
        </n-form-item>
        <n-form-item label="JSON 数据">
          <n-input
            v-model:value="importJson"
            type="textarea"
            :rows="10"
            placeholder="粘贴从「导出」获得的 JSON..."
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showImport = false">取消</n-button>
          <n-button type="primary" :loading="importing" @click="doImport">导入</n-button>
        </n-space>
      </template>
    </n-modal>

    <!-- hidden file input for JSON import -->
    <input ref="fileInput" type="file" accept=".json" style="display:none" @change="onFileChange" />
  </div>
</template>

<script setup>
import { ref, computed, h, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  NPageHeader, NButton, NAlert, NDataTable, NModal, NForm, NFormItem,
  NInput, NInputGroup, NInputGroupLabel, NSwitch, NText, NSpace, NTag,
} from 'naive-ui'
import { networksApi } from '../api/index.js'

const router = useRouter()
const message = useMessage()
const networks = ref([])
const loading = ref(false)
const error = ref('')
const search = ref('')
const showCreate = ref(false)
const creating = ref(false)
const form = ref({ name: '', private: true, ipStart: '', ipEnd: '', route: '' })

const showImport = ref(false)
const importNwid = ref('')
const importJson = ref('')
const importing = ref(false)
const fileInput = ref(null)

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return networks.value
  return networks.value.filter(n =>
    n.id?.toLowerCase().includes(q) || n.name?.toLowerCase().includes(q)
  )
})

const columns = [
  { title: '网络 ID', key: 'id', render: (row) => h('code', row.id) },
  { title: '名称', key: 'name', render: (row) => row.name || h(NText, { depth: 3 }, () => '未命名') },
  {
    title: '类型',
    key: 'private',
    render: (row) => h(NTag, { type: row.private ? 'warning' : 'info', size: 'small' }, () => row.private ? '私有' : '公开'),
  },
  {
    title: 'IP 分配',
    key: 'v4AssignMode',
    render: (row) => row.v4AssignMode?.zt ? '自动' : '手动',
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) => h(NSpace, {}, () => [
      h(NButton, {
        size: 'small',
        onClick: (e) => { e.stopPropagation(); exportNetwork(row.id) },
      }, () => '导出'),
      h(NButton, {
        size: 'small',
        type: 'error',
        onClick: (e) => { e.stopPropagation(); handleDelete(row.id) },
      }, () => '删除'),
    ]),
  },
]

function rowProps(row) {
  return {
    style: 'cursor: pointer',
    onClick: () => router.push(`/networks/${row.id}`),
  }
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const r = await networksApi.list()
    networks.value = r.data
  } catch (e) {
    error.value = e.response?.data?.detail ?? e.message
  } finally {
    loading.value = false
  }
}

async function createNetwork() {
  creating.value = true
  try {
    const body = { name: form.value.name || undefined, private: form.value.private }
    if (form.value.ipStart && form.value.ipEnd) {
      body.ipAssignmentPools = [{ ipRangeStart: form.value.ipStart, ipRangeEnd: form.value.ipEnd }]
      body.v4AssignMode = { zt: true }
    }
    if (form.value.route) body.routes = [{ target: form.value.route }]
    await networksApi.create(body)
    message.success('网络创建成功')
    showCreate.value = false
    form.value = { name: '', private: true, ipStart: '', ipEnd: '', route: '' }
    await load()
  } catch (e) {
    message.error(e.response?.data?.detail ?? e.message)
  } finally {
    creating.value = false
  }
}

async function handleDelete(nwid) {
  if (!confirm(`确认删除网络 ${nwid}？`)) return
  try {
    await networksApi.remove(nwid)
    message.success('已删除')
    await load()
  } catch (e) {
    message.error(e.response?.data?.detail ?? e.message)
  }
}

async function exportNetwork(nwid) {
  try {
    const r = await networksApi.export(nwid)
    const blob = new Blob([JSON.stringify(r.data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `zerotier-network-${nwid}.json`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    message.error(e.response?.data?.detail ?? e.message)
  }
}

function triggerImport() {
  showImport.value = true
  importJson.value = ''
  importNwid.value = ''
}

function onFileChange(e) {
  const file = e.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (ev) => { importJson.value = ev.target.result }
  reader.readAsText(file)
}

async function doImport() {
  importing.value = true
  try {
    const data = JSON.parse(importJson.value)
    const nwid = importNwid.value || data.network?.id
    if (!nwid) throw new Error('无法确定目标网络 ID，请手动填写')
    const r = await networksApi.import(nwid, data)
    message.success(`导入成功，恢复了 ${r.data.members_restored} 个成员`)
    showImport.value = false
    await load()
  } catch (e) {
    message.error(e.response?.data?.detail ?? e.message)
  } finally {
    importing.value = false
  }
}

onMounted(load)
</script>
