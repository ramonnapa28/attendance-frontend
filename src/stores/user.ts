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
    const { data } = await api.post('/auth/login', { email, password })
    login(data.user)
  }

  async function registerApi(payload: RegisterPayload) {
    const { data } = await api.post('/auth/register', payload)
    login(data.user)
  }

  async function fetchProfile() {
    const { data } = await api.get('api/auth/profile')
    login(data.user)
  }

  async function logoutApi() {
    await api.post('api/auth/logout')
    logout()
  }

  function setSchool(schoolId: string) {
    if (user.value) {
      user.value = { ...user.value, schoolId }
    }
  }

  return { user, isAuthenticated, login, logout, loginApi, registerApi, fetchProfile, logoutApi, setSchool }
})
