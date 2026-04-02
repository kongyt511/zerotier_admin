import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Networks from '../views/Networks.vue'
import NetworkDetail from '../views/NetworkDetail.vue'
import Peers from '../views/Peers.vue'
import Settings from '../views/Settings.vue'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: Dashboard, meta: { title: '仪表盘' } },
  { path: '/networks', component: Networks, meta: { title: '网络管理' } },
  { path: '/networks/:nwid', component: NetworkDetail, meta: { title: '网络详情' } },
  { path: '/peers', component: Peers, meta: { title: 'Peers' } },
  { path: '/settings', component: Settings, meta: { title: '设置' } },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
