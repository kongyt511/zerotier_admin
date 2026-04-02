<template>
  <div>
    <n-page-header title="设置" />

    <n-card title="ZeroTier 连接配置" style="margin-top: 16px; max-width: 600px">
      <n-alert v-if="testResult" :type="testResult.ok ? 'success' : 'error'" style="margin-bottom: 16px">
        {{ testResult.msg }}
      </n-alert>

      <n-form :model="form" label-placement="left" label-width="120">
        <n-form-item label="ZeroTier 地址">
          <n-input v-model:value="form.zt_url" placeholder="http://localhost:9993" />
        </n-form-item>
        <n-form-item label="API Token">
          <n-input
            v-model:value="form.zt_token"
            type="password"
            show-password-on="click"
            placeholder="从 /var/lib/zerotier-one/authtoken.secret 读取"
          />
        </n-form-item>
        <n-form-item>
          <n-space>
            <n-button type="primary" :loading="saving" @click="save">保存</n-button>
            <n-button :loading="testing" @click="testConnection">测试连接</n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </n-card>

    <n-card title="Token 获取说明" style="margin-top: 16px; max-width: 600px">
      <n-ul>
        <li><b>Linux / macOS：</b><n-text code>sudo cat /var/lib/zerotier-one/authtoken.secret</n-text></li>
        <li><b>macOS (用户安装)：</b><n-text code>cat ~/Library/Application Support/ZeroTier/authtoken.secret</n-text></li>
        <li><b>Windows：</b><n-text code>%PROGRAMDATA%\ZeroTier\One\authtoken.secret</n-text></li>
      </n-ul>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import {
  NPageHeader, NCard, NAlert, NForm, NFormItem, NInput, NButton, NSpace,
  NText, NUl,
} from 'naive-ui'
import { configApi, statusApi } from '../api/index.js'

const message = useMessage()
const form = ref({ zt_url: 'http://localhost:9993', zt_token: '' })
const saving = ref(false)
const testing = ref(false)
const testResult = ref(null)

async function load() {
  try {
    const r = await configApi.get()
    form.value = r.data
  } catch (e) {
    // ignore
  }
}

async function save() {
  saving.value = true
  testResult.value = null
  try {
    await configApi.set(form.value)
    message.success('配置已保存')
  } catch (e) {
    message.error(e.response?.data?.detail ?? e.message)
  } finally {
    saving.value = false
  }
}

async function testConnection() {
  testing.value = true
  testResult.value = null
  // Save first, then test
  try {
    await configApi.set(form.value)
    const r = await statusApi.get()
    testResult.value = {
      ok: true,
      msg: `连接成功！节点地址：${r.data.address}，版本：${r.data.version}`,
    }
  } catch (e) {
    testResult.value = {
      ok: false,
      msg: e.response?.data?.detail ?? e.message,
    }
  } finally {
    testing.value = false
  }
}

onMounted(load)
</script>
