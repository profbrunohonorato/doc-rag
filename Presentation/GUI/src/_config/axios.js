import axios from 'axios'
const api = axios.create({ baseURL: import.meta.env.VITE_API_BASE_URL || '/doc-rag/api/v1', timeout: 600000 })
api.interceptors.request.use(config => {
  const token = sessionStorage.getItem('doc-rag-token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})
export function errorMessage(error) {
  const detail = error.response?.data?.detail
  return typeof detail === 'string' ? detail : error.response?.status === 422 ? 'Confira os campos informados.' : 'Não foi possível conectar. Aguarde a preparação dos modelos e tente novamente.'
}
export default api
