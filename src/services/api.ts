import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_FRONTEND_URL, // Change to your backend URL

  withCredentials: true, // If using cookies/session
})

export default api

// Admin CRUD
export const getAdmins = () => api.get('/admins')
export const createAdmin = (payload: object) => api.post('/admins', payload)
export const updateAdmin = (id: number | string, payload: object) =>
  api.put(`/admins/${id}`, payload)
export const deleteAdmin = (id: number | string) => api.delete(`/admins/${id}`)

// School CRUD
export const getSchools = () => api.get('/schools')
export const createSchool = (payload: object) => api.post('/schools', payload)
export const updateSchool = (id: number | string, payload: object) =>
  api.put(`/schools/${id}`, payload)
export const archiveSchool = (id: number | string) => api.post(`/schools/${id}/archive`)
export async function unarchiveSchool(id: number) {
  return await api.post(`/schools/${id}/unarchive`)
}

export const getPendingInstructors = () => api.get('/instructors/pending')
export const approveInstructor = (id: number | string) => api.post(`/instructors/approve/${id}`)
export const updateInstructor = (id: number | string, payload: object) =>
  api.put(`/users/${id}`, payload)
export const getInstructors = () => api.get('/instructors')
export const updateUser = (id: number | string, payload: object) => api.put(`/users/${id}`, payload)
export async function getAllUsers() {
  return await api.get('/users')
}
