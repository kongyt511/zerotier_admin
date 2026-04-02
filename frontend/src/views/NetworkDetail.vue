<template>
  <div>
    <n-page-header :title="network?.name || nwid" @back="$router.push('/networks')">
      <template #subtitle>
        <n-text code>{{ nwid }}</n-text>
      </template>
      <template #extra>
        <n-space align="center">
          <n-text depth="3" style="font-size:13px">自动刷新</n-text>
          <n-switch v-model:value="autoRefresh" @update:value="toggleAutoRefresh" />
        </n-space>
      </template>
    </n-page-header>

    <n-alert v-if="error" type="error" :title="error" style="margin-top:16px" />

    <n-tabs style="margin-top:16px" type="line" animated>

      <!-- ── 网络配置 ── -->
      <n-tab-pane name="config" tab="网络配置">
        <n-card :loading="loading" style="margin-top:8px">
          <n-form v-if="network" :model="form" label-placement="left" label-width="130">
            <n-form-item label="网络名称">
              <n-input v-model:value="form.name" />
            </n-form-item>
            <n-form-item label="私有网络">
              <n-switch v-model:value="form.private" />
            </n-form-item>
            <n-form-item label="IPv4 自动分配">
              <n-switch v-model:value="form.v4AutoAssign">
                <template #checked>开启</template>
                <template #unchecked>关闭</template>
              </n-switch>
            </n-form-item>
            <n-form-item label="IP 地址池">
              <n-dynamic-input
                v-model:value="form.ipPools"
                :on-create="() => ({ ipRangeStart: '', ipRangeEnd: '' })"
              >
                <template #default="{ value }">
                  <n-input v-model:value="value.ipRangeStart" placeholder="起始 IP" style="width:200px" />
                  <n-text style="margin:0 8px">—</n-text>
                  <n-input v-model:value="value.ipRangeEnd" placeholder="结束 IP" style="width:200px" />
                </template>
              </n-dynamic-input>
            </n-form-item>
            <n-form-item label="路由">
              <n-dynamic-input
                v-model:value="form.routes"
                :on-create="() => ({ target: '', via: '' })"
              >
                <template #default="{ value }">
                  <n-input v-model:value="value.target" placeholder="目标网段，如 10.0.0.0/24" style="width:220px" />
                  <n-input v-model:value="value.via" placeholder="网关（可选）" style="width:160px;margin-left:8px" />
                </template>
              </n-dynamic-input>
            </n-form-item>
            <n-form-item>
              <n-button type="primary" :loading="saving" @click="saveNetwork">保存配置</n-button>
            </n-form-item>
          </n-form>
        </n-card>
      </n-tab-pane>

      <!-- ── 成员管理 ── -->
      <n-tab-pane name="members" tab="成员管理">
        <n-card style="margin-top:8px">
          <n-input
            v-model:value="memberSearch"
            placeholder="搜索成员 ID / IP / 名称..."
            clearable
            style="margin-bottom:12px; max-width:340px"
          />
          <n-data-table
            :columns="memberColumns"
            :data="filteredMembers"
            :loading="membersLoading"
          />
        </n-card>
      </n-tab-pane>

      <!-- ── DNS 配置 ── -->
      <n-tab-pane name="dns" tab="DNS 配置">
        <n-card style="margin-top:8px">
          <n-form :model="dnsForm" label-placement="left" label-width="120">
            <n-form-item label="DNS 域名">
              <n-input v-model:value="dnsForm.domain" placeholder="如 zt.example.com" />
            </n-form-item>
            <n-form-item label="DNS 服务器">
              <n-dynamic-input
                v-model:value="dnsForm.servers"
                :on-create="() => ''"
                #default="{ value, index }"
              >
                <n-input
                  :value="value"
                  placeholder="DNS 服务器 IP"
                  style="width:240px"
                  @update:value="(v) => dnsForm.servers[index] = v"
                />
              </n-dynamic-input>
            </n-form-item>
            <n-form-item>
              <n-space>
                <n-button type="primary" :loading="savingDns" @click="saveDns">保存 DNS</n-button>
                <n-button @click="clearDns" :loading="savingDns">清除 DNS</n-button>
              </n-space>
            </n-form-item>
          </n-form>
        </n-card>
      </n-tab-pane>

      <!-- ── 流量规则 ── -->
      <n-tab-pane name="rules" tab="流量规则">
        <n-card style="margin-top:8px">
          <n-alert type="info" style="margin-bottom:12px">
            规则为 JSON 数组格式，详见
            <n-a href="https://docs.zerotier.com/rules" target="_blank">ZeroTier 规则文档</n-a>
          </n-alert>
          <n-input
            v-model:value="rulesJson"
            type="textarea"
            :rows="18"
            :status="rulesJsonValid ? undefined : 'error'"
            placeholder="[ { &quot;etherType&quot;: 2048, &quot;not&quot;: true, &quot;or&quot;: false, &quot;type&quot;: &quot;MATCH_ETHERTYPE&quot; }, ... ]"
            style="font-family: monospace; font-size: 13px"
            @update:value="validateRulesJson"
          />
          <n-text v-if="!rulesJsonValid" type="error" style="font-size:12px">JSON 格式无效</n-text>
          <n-space style="margin-top:12px">
            <n-button type="primary" :loading="savingRules" :disabled="!rulesJsonValid" @click="saveRules">
              保存规则
            </n-button>
            <n-button @click="resetDefaultRules">恢复默认规则</n-button>
          </n-space>
        </n-card>
      </n-tab-pane>

      <!-- ── Tags & Capabilities ── -->
      <n-tab-pane name="tags" tab="Tags / Capabilities">
        <n-grid :cols="2" :x-gap="16" style="margin-top:8px">

          <!-- Tags -->
          <n-gi>
            <n-card title="Tags 标签定义">
              <n-dynamic-input
                v-model:value="tagsForm"
                :on-create="() => ({ id: nextTagId(), name: '', default: 0 })"
              >
                <template #default="{ value }">
                  <n-input-number v-model:value="value.id" :min="1" style="width:80px" />
                  <n-input v-model:value="value.name" placeholder="标签名称" style="width:160px;margin:0 8px" />
                  <n-input-number v-model:value="value.default" placeholder="默认值" :min="0" style="width:100px" />
                </template>
              </n-dynamic-input>
              <n-button type="primary" :loading="savingTags" style="margin-top:12px" @click="saveTags">
                保存 Tags
              </n-button>
            </n-card>
          </n-gi>

          <!-- Capabilities -->
          <n-gi>
            <n-card title="Capabilities 能力定义">
              <n-dynamic-input
                v-model:value="capsForm"
                :on-create="() => ({ id: nextCapId(), name: '', default: false })"
              >
                <template #default="{ value }">
                  <n-input-number v-model:value="value.id" :min="1" style="width:80px" />
                  <n-input v-model:value="value.name" placeholder="能力名称" style="width:160px;margin:0 8px" />
                  <n-switch v-model:value="value.default" size="small">
                    <template #checked>默认开</template>
                    <template #unchecked>默认关</template>
                  </n-switch>
                </template>
              </n-dynamic-input>
              <n-button type="primary" :loading="savingCaps" style="margin-top:12px" @click="saveCaps">
                保存 Capabilities
              </n-button>
            </n-card>
          </n-gi>
        </n-grid>
      </n-tab-pane>

    </n-tabs>

    <!-- Member Edit Modal -->
    <n-modal v-model:show="showMemberEdit" preset="card" title="编辑成员" style="width:560px">
      <n-form v-if="editingMember" :model="editingMember" label-placement="left" label-width="120">
        <n-form-item label="成员 ID">
          <n-text code>{{ editingMember.nodeId }}</n-text>
        </n-form-item>
        <n-form-item label="备注名称">
          <n-input v-model:value="editingMember.name" placeholder="自定义名称" />
        </n-form-item>
        <n-form-item label="授权状态">
          <n-switch v-model:value="editingMember.authorized">
            <template #checked>已授权</template>
            <template #unchecked>未授权</template>
          </n-switch>
        </n-form-item>
        <n-form-item label="手动分配 IP">
          <n-dynamic-input
            v-model:value="editingMember.ipAssignments"
            :on-create="() => ''"
            #default="{ value, index }"
          >
            <n-input
              :value="value"
              placeholder="如 10.147.17.5"
              style="width:220px"
              @update:value="(v) => editingMember.ipAssignments[index] = v"
            />
          </n-dynamic-input>
        </n-form-item>
        <n-form-item label="Tags">
          <n-dynamic-input
            v-model:value="editingMember.tags"
            :on-create="() => [0, 0]"
            #default="{ value, index }"
          >
            <n-input-number
              :value="value[0]"
              placeholder="Tag ID"
              :min="0"
              style="width:110px"
              @update:value="(v) => editingMember.tags[index] = [v, editingMember.tags[index][1]]"
            />
            <n-input-number
              :value="value[1]"
              placeholder="值"
              :min="0"
              style="width:110px;margin-left:8px"
              @update:value="(v) => editingMember.tags[index] = [editingMember.tags[index][0], v]"
            />
          </n-dynamic-input>
        </n-form-item>
        <n-form-item label="Capabilities">
          <n-select
            v-model:value="editingMember.capabilities"
            multiple
            :options="capsOptions"
            placeholder="选择赋予的 Capability"
          />
        </n-form-item>
      </n-form>
      <template #footer>
        <n-space justify="end">
          <n-button @click="showMemberEdit = false">取消</n-button>
          <n-button type="primary" :loading="savingMember" @click="saveMember">保存</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup>
import { ref, computed, h, onMounted, onUnmounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  NPageHeader, NText, NAlert, NTabs, NTabPane, NCard, NForm, NFormItem,
  NInput, NInputNumber, NSwitch, NButton, NDataTable, NDynamicInput,
  NTag, NSpace, NGrid, NGi, NSelect, NModal, NA,
} from 'naive-ui'
import { networksApi, membersApi } from '../api/index.js'

const route = useRoute()
const message = useMessage()
const nwid = route.params.nwid

// ── state ──────────────────────────────────────────────
const network = ref(null)
const loading = ref(false)
const saving = ref(false)
const error = ref('')
const form = ref({ name: '', private: true, v4AutoAssign: false, ipPools: [], routes: [] })

const members = ref([])
const membersLoading = ref(false)
const memberSearch = ref('')

const dnsForm = ref({ domain: '', servers: [] })
const savingDns = ref(false)

const rulesJson = ref('[]')
const rulesJsonValid = ref(true)
const savingRules = ref(false)

const tagsForm = ref([])
const savingTags = ref(false)
const capsForm = ref([])
const savingCaps = ref(false)

const showMemberEdit = ref(false)
const editingMember = ref(null)
const savingMember = ref(false)

const autoRefresh = ref(false)
let timer = null

// ── computed ────────────────────────────────────────────
const filteredMembers = computed(() => {
  const q = memberSearch.value.trim().toLowerCase()
  if (!q) return members.value
  return members.value.filter(m =>
    m.nodeId?.toLowerCase().includes(q) ||
    m.name?.toLowerCase().includes(q) ||
    (m.ipAssignments || []).some(ip => ip.includes(q))
  )
})

const capsOptions = computed(() =>
  capsForm.value.map(c => ({ label: `${c.name || 'Cap'} (${c.id})`, value: c.id }))
)

// ── member table columns ────────────────────────────────
const memberColumns = [
  { title: '成员 ID', key: 'nodeId', render: (row) => h('code', { style: 'font-size:12px' }, row.nodeId) },
  { title: '名称', key: 'name', render: (row) => row.name || h(NText, { depth: 3, style: 'font-size:12px' }, () => '—') },
  {
    title: 'IP 地址',
    key: 'ipAssignments',
    render: (row) => (row.ipAssignments || []).join(', ') || h(NText, { depth: 3 }, () => '—'),
  },
  {
    title: '授权',
    key: 'authorized',
    render: (row) =>
      h(NTag, {
        type: row.authorized ? 'success' : 'default',
        style: 'cursor:pointer',
        size: 'small',
        onClick: () => quickToggleAuth(row),
      }, () => row.authorized ? '已授权' : '未授权'),
  },
  {
    title: '最后在线',
    key: 'lastSeen',
    render: (row) => row.lastSeen ? new Date(row.lastSeen).toLocaleString() : '—',
  },
  {
    title: '操作',
    key: 'actions',
    render: (row) =>
      h(NSpace, { size: 'small' }, () => [
        h(NButton, { size: 'small', onClick: () => openMemberEdit(row) }, () => '编辑'),
        h(NButton, { size: 'small', type: 'error', onClick: () => deleteMember(row.nodeId) }, () => '删除'),
      ]),
  },
]

// ── network ─────────────────────────────────────────────
async function loadNetwork() {
  loading.value = true
  error.value = ''
  try {
    const r = await networksApi.get(nwid)
    network.value = r.data
    form.value = {
      name: r.data.name || '',
      private: r.data.private ?? true,
      v4AutoAssign: r.data.v4AssignMode?.zt ?? false,
      ipPools: r.data.ipAssignmentPools || [],
      routes: r.data.routes || [],
    }
    dnsForm.value = {
      domain: r.data.dns?.domain || '',
      servers: r.data.dns?.servers || [],
    }
    tagsForm.value = r.data.tags || []
    capsForm.value = r.data.capabilities || []
    try {
      rulesJson.value = JSON.stringify(r.data.rules || [], null, 2)
    } catch { rulesJson.value = '[]' }
  } catch (e) {
    error.value = e.response?.data?.detail ?? e.message
  } finally {
    loading.value = false
  }
}

async function saveNetwork() {
  saving.value = true
  try {
    await networksApi.update(nwid, {
      name: form.value.name,
      private: form.value.private,
      v4AssignMode: { zt: form.value.v4AutoAssign },
      ipAssignmentPools: form.value.ipPools.filter(p => p.ipRangeStart),
      routes: form.value.routes.filter(r => r.target),
    })
    message.success('配置已保存')
    await loadNetwork()
  } catch (e) {
    message.error(e.response?.data?.detail ?? e.message)
  } finally {
    saving.value = false
  }
}

// ── DNS ─────────────────────────────────────────────────
async function saveDns() {
  savingDns.value = true
  try {
    await networksApi.update(nwid, {
      dns: { domain: dnsForm.value.domain, servers: dnsForm.value.servers.filter(s => s) },
    })
    message.success('DNS 已保存')
  } catch (e) {
    message.error(e.response?.data?.detail ?? e.message)
  } finally {
    savingDns.value = false
  }
}

async function clearDns() {
  savingDns.value = true
  try {
    await networksApi.update(nwid, { dns: { domain: '', servers: [] } })
    dnsForm.value = { domain: '', servers: [] }
    message.success('DNS 已清除')
  } catch (e) {
    message.error(e.response?.data?.detail ?? e.message)
  } finally {
    savingDns.value = false
  }
}

// ── Rules ────────────────────────────────────────────────
function validateRulesJson(val) {
  try { JSON.parse(val); rulesJsonValid.value = true } catch { rulesJsonValid.value = false }
}

async function saveRules() {
  savingRules.value = true
  try {
    await networksApi.update(nwid, { rules: JSON.parse(rulesJson.value) })
    message.success('规则已保存')
  } catch (e) {
    message.error(e.response?.data?.detail ?? e.message)
  } finally {
    savingRules.value = false
  }
}

function resetDefaultRules() {
  rulesJson.value = JSON.stringify([
    { etherType: 2048, not: true, or: false, type: 'MATCH_ETHERTYPE' },
    { etherType: 2054, not: true, or: false, type: 'MATCH_ETHERTYPE' },
    { etherType: 34525, not: true, or: false, type: 'MATCH_ETHERTYPE' },
    { type: 'ACTION_DROP' },
    { type: 'ACTION_ACCEPT' },
  ], null, 2)
  rulesJsonValid.value = true
}

// ── Tags / Caps ──────────────────────────────────────────
function nextTagId() {
  return (tagsForm.value.length ? Math.max(...tagsForm.value.map(t => t.id)) + 1 : 1)
}
function nextCapId() {
  return (capsForm.value.length ? Math.max(...capsForm.value.map(c => c.id)) + 1 : 1)
}

async function saveTags() {
  savingTags.value = true
  try {
    await networksApi.update(nwid, { tags: tagsForm.value })
    message.success('Tags 已保存')
  } catch (e) {
    message.error(e.response?.data?.detail ?? e.message)
  } finally {
    savingTags.value = false
  }
}

async function saveCaps() {
  savingCaps.value = true
  try {
    await networksApi.update(nwid, { capabilities: capsForm.value })
    message.success('Capabilities 已保存')
  } catch (e) {
    message.error(e.response?.data?.detail ?? e.message)
  } finally {
    savingCaps.value = false
  }
}

// ── Members ──────────────────────────────────────────────
async function loadMembers() {
  membersLoading.value = true
  try {
    const r = await membersApi.list(nwid)
    members.value = r.data
  } catch (e) {
    message.error(e.response?.data?.detail ?? e.message)
  } finally {
    membersLoading.value = false
  }
}

function openMemberEdit(member) {
  editingMember.value = {
    nodeId: member.nodeId,
    name: member.name || '',
    authorized: member.authorized ?? false,
    ipAssignments: [...(member.ipAssignments || [])],
    tags: [...(member.tags || [])],
    capabilities: [...(member.capabilities || [])],
  }
  showMemberEdit.value = true
}

async function saveMember() {
  savingMember.value = true
  try {
    const m = editingMember.value
    await membersApi.update(nwid, m.nodeId, {
      name: m.name,
      authorized: m.authorized,
      ipAssignments: m.ipAssignments.filter(ip => ip),
      tags: m.tags,
      capabilities: m.capabilities,
    })
    message.success('成员已更新')
    showMemberEdit.value = false
    await loadMembers()
  } catch (e) {
    message.error(e.response?.data?.detail ?? e.message)
  } finally {
    savingMember.value = false
  }
}

async function quickToggleAuth(member) {
  try {
    await membersApi.update(nwid, member.nodeId, { authorized: !member.authorized })
    await loadMembers()
  } catch (e) {
    message.error(e.response?.data?.detail ?? e.message)
  }
}

async function deleteMember(mid) {
  if (!confirm(`确认删除成员 ${mid}？`)) return
  try {
    await membersApi.remove(nwid, mid)
    message.success('已删除')
    await loadMembers()
  } catch (e) {
    message.error(e.response?.data?.detail ?? e.message)
  }
}

// ── Auto-refresh ─────────────────────────────────────────
function toggleAutoRefresh(val) {
  clearInterval(timer)
  if (val) timer = setInterval(() => { loadNetwork(); loadMembers() }, 10000)
}

onMounted(() => { loadNetwork(); loadMembers() })
onUnmounted(() => clearInterval(timer))
</script>
