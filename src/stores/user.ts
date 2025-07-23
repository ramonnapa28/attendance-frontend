import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/services/api'

export type UserRole = 'student' | 'instructor' | 'admin' | 'super_admin' | 'superadmin'

export interface UserProfile {
  id: string
  email: string
  role: UserRole
  name?: string
  schoolId?: string
  school?: string // Add this line to match backend data
  isActive?: boolean
}

export interface RegisterPayload {
  name?: string
  dob?: string
  address?: string
  email: string
  password: string
  role: UserRole
  studentId?: string
  instructorId?: string
}

export const useUserStore = defineStore('user', () => {
  const user = ref<UserProfile | null>(null)
  const isAuthenticated = ref(false)

  function login(profile: UserProfile) {
    user.value = profile
    isAuthenticated.value = true
  }

  function logout() {
    user.value = null
    isAuthenticated.value = false
  }

  async function loginApi(email: string, password: string) {
<<<<<<< HEAD
    const { data } = await api.post('api/auth/login', { email, password })
=======
    const { data } = await api.post('/auth/login', { email, password })
>>>>>>> d200206 (Initial commit)
    login(data.user)
  }

  async function registerApi(payload: RegisterPayload) {
<<<<<<< HEAD
    const { data } = await api.post('api/auth/register', payload)
=======
    const { data } = await api.post('/auth/register', payload)
>>>>>>> d200206 (Initial commit)
    login(data.user)
  }

  async function fetchProfile() {
<<<<<<< HEAD
    const { data } = await api.get('api/auth/profile')
=======
    const { data } = await api.get('/auth/profile')
>>>>>>> d200206 (Initial commit)
    login(data.user)
  }

  async function logoutApi() {
<<<<<<< HEAD
    await api.post('api/auth/logout')
=======
    await api.post('/auth/logout')
>>>>>>> d200206 (Initial commit)
    logout()
  }

  function setSchool(schoolId: string) {
    if (user.value) {
      user.value = { ...user.value, schoolId }
    }
  }

  return { user, isAuthenticated, login, logout, loginApi, registerApi, fetchProfile, logoutApi, setSchool }
<<<<<<< HEAD
})
=======
}) 
>>>>>>> d200206 (Initial commit)
