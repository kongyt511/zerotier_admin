<template>
  <n-config-provider :theme="theme" :locale="zhCN" :date-locale="dateZhCN">
    <n-message-provider>
      <n-layout style="min-height: 100vh">
        <n-layout-header bordered style="padding: 0 24px; display: flex; align-items: center; height: 60px; gap: 16px">
          <n-text strong style="font-size: 18px">
            🌐 ZeroTier Admin
          </n-text>
          <n-space style="margin-left: auto">
            <n-button text @click="toggleTheme">
              {{ isDark ? '☀️ 亮色' : '🌙 暗色' }}
            </n-button>
          </n-space>
        </n-layout-header>
        <n-layout has-sider>
          <n-layout-sider bordered :width="200" content-style="padding: 16px 0">
            <n-menu :options="menuOptions" :value="activeKey" @update:value="navigate" />
          </n-layout-sider>
          <n-layout-content content-style="padding: 24px">
            <router-view />
          </n-layout-content>
        </n-layout>
      </n-layout>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  NConfigProvider, NLayout, NLayoutHeader, NLayoutSider, NLayoutContent,
  NMenu, NText, NButton, NSpace, NMessageProvider,
  darkTheme, zhCN, dateZhCN,
} from 'naive-ui'

const router = useRouter()
const route = useRoute()
const isDark = ref(false)
const theme = computed(() => isDark.value ? darkTheme : null)

function toggleTheme() { isDark.value = !isDark.value }

const menuOptions = [
  { label: '仪表盘', key: '/dashboard' },
  { label: '网络管理', key: '/networks' },
  { label: 'Peers 节点', key: '/peers' },
  { label: '设置', key: '/settings' },
]

const activeKey = computed(() => {
  if (route.path.startsWith('/networks/')) return '/networks'
  return route.path
})

function navigate(key) { router.push(key) }
</script>
