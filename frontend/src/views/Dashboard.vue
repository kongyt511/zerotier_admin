<template>
  <div>
    <n-page-header title="仪表盘" />
    <n-space vertical size="large" style="margin-top: 16px">
      <n-alert v-if="error" type="error" :title="error" />

      <n-grid :cols="3" :x-gap="16" :y-gap="16">
        <n-gi>
          <n-card title="节点状态" :loading="loading">
            <n-descriptions v-if="status" :column="1" bordered>
              <n-descriptions-item label="节点地址">
                <n-text code>{{ status.address }}</n-text>
              </n-descriptions-item>
              <n-descriptions-item label="版本">{{ status.version }}</n-descriptions-item>
              <n-descriptions-item label="在线状态">
                <n-tag :type="status.online ? 'success' : 'error'">
                  {{ status.online ? '在线' : '离线' }}
                </n-tag>
              </n-descriptions-item>
              <n-descriptions-item label="TCP 回退">
                <n-tag :type="status.tcpFallbackActive ? 'warning' : 'default'" size="small">
                  {{ status.tcpFallbackActive ? '启用' : '未启用' }}
                </n-tag>
              </n-descriptions-item>
            </n-descriptions>
            <n-empty v-else-if="!loading" description="暂无数据，请先配置 Token" />
          </n-card>
        </n-gi>

        <n-gi>
          <n-card title="控制器" :loading="loading">
            <n-descriptions v-if="status?.controller" :column="1" bordered>
              <n-descriptions-item label="控制器运行">
                <n-tag :type="status.controller.running ? 'success' : 'error'">
                  {{ status.controller.running ? '运行中' : '未运行' }}
                </n-tag>
              </n-descriptions-item>
              <n-descriptions-item label="网络数量">
                <n-text strong>{{ status.controller.networks ?? '—' }}</n-text>
              </n-descriptions-item>
            </n-descriptions>
            <n-empty v-else-if="!loading" description="控制器数据不可用" />
          </n-card>
        </n-gi>

        <n-gi>
          <n-card title="快速操作">
            <n-space vertical>
              <n-button type="primary" block @click="$router.push('/networks')">
                管理网络
              </n-button>
              <n-button block @click="$router.push('/settings')">
                修改配置
              </n-button>
              <n-button block @click="load" :loading="loading">
                刷新状态
              </n-button>
            </n-space>
          </n-card>
        </n-gi>
      </n-grid>

      <n-card v-if="status" title="节点公钥">
        <n-code :code="status.publicIdentity || '—'" word-wrap />
      </n-card>
    </n-space>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  NPageHeader, NSpace, NGrid, NGi, NCard, NAlert, NDescriptions,
  NDescriptionsItem, NText, NTag, NEmpty, NButton, NCode,
} from 'naive-ui'
import { statusApi } from '../api/index.js'

const status = ref(null)
const loading = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const r = await statusApi.get()
    status.value = r.data
  } catch (e) {
    error.value = e.response?.data?.detail ?? e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>
