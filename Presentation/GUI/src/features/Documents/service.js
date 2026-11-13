import api from '../../_config/axios'
export const list = async () => (await api.get('/documents')).data
export const scan = async () => (await api.post('/documents/scan')).data
export const upload = async file => { const data = new FormData(); data.append('file', file); return (await api.post('/documents/upload', data)).data }
