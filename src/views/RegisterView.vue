<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import type { UserRole } from '@/stores/user'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const role = ref<UserRole>('student')
const userStore = useUserStore()
const router = useRouter()
const error = ref('')

async function onSubmit() {
  error.value = ''
  try {
    await userStore.registerApi({ email: email.value, password: password.value, role: role.value })
    // Redirect based on role
    if (userStore.user?.role === 'student') router.push('/student')
    else if (userStore.user?.role === 'instructor') router.push('/instructor')
    else if (userStore.user?.role === 'admin') router.push('/admin')
    else if (userStore.user?.role === 'super_admin') router.push('/super-admin')
  } catch (e) {
    error.value = 'Registration failed'
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden">
    <!-- Unique geometric SVG pattern background -->
    <svg class="absolute inset-0 w-full h-full object-cover opacity-30 z-0" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" fill="none" viewBox="0 0 1440 900">
      <defs>
        <linearGradient id="bg-gradient" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#34d399" />
          <stop offset="100%" stop-color="#065f46" />
        </linearGradient>
      </defs>
      <rect width="1440" height="900" fill="url(#bg-gradient)" />
      <g opacity="0.15">
        <polygon points="0,900 400,0 800,900" fill="#fff" />
        <polygon points="1440,900 1040,0 640,900" fill="#fff" />
        <polygon points="720,0 900,900 540,900" fill="#fff" />
      </g>
    </svg>
    <div class="w-full max-w-md p-8 bg-white rounded-2xl shadow-xl flex flex-col items-center border-t-8 border-emerald-700 relative z-10">
      <!-- AFP Attendance System Title and Icon -->
      <div class="mb-4 flex flex-col items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-emerald-700 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 2l2.09 6.26L20 9.27l-5 3.64L16.18 20 12 16.77 7.82 20 9 12.91l-5-3.64 5.91-.91z" />
        </svg>
        <h1 class="text-2xl font-extrabold text-emerald-800 tracking-tight text-center">AFP Attendance System</h1>
        <p class="text-gray-600 text-sm mt-1 text-center">Create your secure account</p>
      </div>
      <form @submit.prevent="onSubmit" class="w-full mt-4 space-y-5">
        <div>
          <label class="block mb-1 font-semibold text-emerald-800" for="email">Email</label>
          <input v-model="email" id="email" type="email" class="w-full border border-emerald-400 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition text-emerald-900 bg-emerald-50 placeholder-emerald-700/60" placeholder="Enter your email" required />
        </div>
        <div>
          <label class="block mb-1 font-semibold text-emerald-800" for="password">Password</label>
          <input v-model="password" id="password" type="password" class="w-full border border-emerald-400 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition text-emerald-900 bg-emerald-50 placeholder-emerald-700/60" placeholder="Enter your password" required />
        </div>
        <div>
          <label class="block mb-1 font-semibold text-emerald-800" for="role">Role</label>
          <select v-model="role" id="role" class="w-full border border-emerald-400 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition text-emerald-900 bg-emerald-50">
            <option value="student">Student</option>
            <option value="instructor">Instructor</option>
          </select>
        </div>
        <button type="submit" class="w-full bg-emerald-700 hover:bg-emerald-800 text-white py-3 rounded-lg font-bold text-lg shadow-md transition duration-200 hover:scale-105">Register</button>
        <div v-if="error" class="text-red-500 mt-2 text-center font-semibold">{{ error }}</div>
      </form>
      <div class="mt-8 w-full text-center text-emerald-700 font-semibold">
        Already have an account?
      </div>
      <button @click="() => router.push('/login')" class="mt-4 w-full border border-emerald-700 text-emerald-700 hover:bg-emerald-50 hover:text-emerald-900 py-2 rounded-lg font-semibold transition duration-150 bg-white">
        Login
      </button>
    </div>
  </div>
</template> 