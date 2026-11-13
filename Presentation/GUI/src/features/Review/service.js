import api from '../../_config/axios'
export const pending = async () => (await api.get('/answers', { params: { status: 'pending' } })).data
export const review = async (id, values) => (await api.post(`/answers/${id}/review`, values)).data
