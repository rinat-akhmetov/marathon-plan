
import axios from 'axios'
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})
export const uploadZip = async (file) => {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/upload-data', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
export const getResults = async (id) => {
  const { data } = await api.get(`/results/${id}`)
  return data
}
