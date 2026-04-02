import axios from 'axios'

const http = axios.create({ baseURL: '/api' })

export const configApi = {
  get: () => http.get('/config'),
  set: (data) => http.post('/config', data),
}

export const statusApi = {
  get: () => http.get('/status'),
}

export const peersApi = {
  list: () => http.get('/peers'),
}

export const networksApi = {
  list: () => http.get('/networks'),
  create: (data) => http.post('/networks', data),
  get: (nwid) => http.get(`/networks/${nwid}`),
  update: (nwid, data) => http.put(`/networks/${nwid}`, data),
  remove: (nwid) => http.delete(`/networks/${nwid}`),
  export: (nwid) => http.get(`/networks/${nwid}/export`),
  import: (nwid, data) => http.post(`/networks/${nwid}/import`, data),
}

export const membersApi = {
  list: (nwid) => http.get(`/networks/${nwid}/members`),
  get: (nwid, mid) => http.get(`/networks/${nwid}/members/${mid}`),
  update: (nwid, mid, data) => http.put(`/networks/${nwid}/members/${mid}`, data),
  remove: (nwid, mid) => http.delete(`/networks/${nwid}/members/${mid}`),
}
