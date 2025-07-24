import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_FRONTEND_URL, // Change to your backend URL
  withCredentials: true, // If using cookies/session
})

export default api

// Admin CRUD
export const getAdmins = () => api.get('/api/admins')
export const createAdmin = (payload: object) => api.post('/api/admins', payload)
export const updateAdmin = (id: number | string, payload: object) =>
  api.put(`/api/admins/${id}`, payload)
export const deleteAdmin = (id: number | string) => api.delete(`/api/admins/${id}`)

// School CRUD
export const getSchools = () => api.get('/api/schools')
export const createSchool = (payload: object) => api.post('/api/schools', payload)
export const updateSchool = (id: number | string, payload: object) =>
  api.put(`/api/schools/${id}`, payload)
export const archiveSchool = (id: number | string) => api.post(`/api/schools/${id}/archive`)
export async function unarchiveSchool(id: number) {
  return await api.post(`/api/schools/${id}/unarchive`)
}

export const getPendingInstructors = () => api.get('/api/instructors/pending')
export const approveInstructor = (id: number | string) => api.post(`/api/instructors/approve/${id}`)
export const updateInstructor = (id: number | string, payload: object) =>
  api.put(`/api/users/${id}`, payload)
export const getInstructors = () => api.get('/api/instructors')
export const updateUser = (id: number | string, payload: object) => api.put(`/api/users/${id}`, payload)
export async function getAllUsers() {
  return await api.get('/api/users')
}
