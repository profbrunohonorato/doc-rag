import api from '../../_config/axios'
export const ask = async question => (await api.post('/chat/ask', { question })).data
export const history = async (offset = 0) => (await api.get('/answers', { params: { offset } })).data
