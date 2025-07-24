<script setup lang="ts">
import { ref } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { useSnackbarStore } from '@/stores/snackbar'

const email = ref('')
const password = ref('')
const userStore = useUserStore()
const router = useRouter()
const error = ref('')
const snackbar = useSnackbarStore()
const showPassword = ref(false)

function goToRegister() {
  router.push('/register/role')
}

async function onSubmit() {
  error.value = ''
  try {
    await userStore.loginApi(email.value, password.value)
    snackbar.trigger('Login successful!', 'success')
    // Redirect based on role
    if (userStore.user?.role === 'student') router.push('/student')
    else if (userStore.user?.role === 'instructor') router.push('/instructor')
    else if (userStore.user?.role === 'admin') router.push('/admin')
    else if (userStore.user?.role === 'superadmin') router.push('/super-admin')
  } catch (e: any) {
    // Show backend error message if available
    if (e?.response?.data?.detail) {
      error.value = e.response.data.detail
    } else {
      error.value = 'Login failed'
    }
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden">
    <!-- Unique geometric SVG pattern background -->
    <svg
      class="absolute inset-0 w-full h-full object-cover opacity-30 z-0"
      xmlns="http://www.w3.org/2000/svg"
      preserveAspectRatio="none"
      fill="none"
      viewBox="0 0 1440 900"
    >
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
    <div
      class="w-full max-w-md p-8 bg-white rounded-2xl shadow-xl flex flex-col items-center border-t-8 border-emerald-700 relative z-10"
    >
      <!-- AFP Attendance System Title and Icon -->
      <div class="mb-4 flex flex-col items-center">
        <h1 class="text-3xl font-extrabold text-emerald-800 tracking-tight text-center">
          AFP Attendance System
        </h1>
        <p class="text-gray-600 text-md mt-1 mb-6 text-center">Sign in to your secure account</p>
      </div>
      <form @submit.prevent="onSubmit" class="w-full mt-4 space-y-5">
        <div>
          <label class="block mb-1 font-semibold text-emerald-800" for="email">Email</label>
          <input
            v-model="email"
            id="email"
            type="email"
            class="w-full border border-emerald-400 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition text-emerald-900 bg-emerald-50 placeholder-emerald-700/60"
            placeholder="Enter your email"
            required
          />
        </div>
        <div>
          <label class="block mb-1 font-semibold text-emerald-800" for="password">Password</label>
          <div class="relative">
            <input
              v-model="password"
              :type="showPassword ? 'text' : 'password'"
              id="password"
              class="w-full border border-emerald-400 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition text-emerald-900 bg-emerald-50 placeholder-emerald-700/60 pr-12"
              placeholder="Enter your password"
              required
            />
            <button
              type="button"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-emerald-700 hover:text-emerald-900 focus:outline-none"
              @click="showPassword = !showPassword"
              tabindex="-1"
            >
              <!-- Eye icon (show password) -->
              <svg
                v-if="!showPassword"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-5 h-5"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M2.25 12C3.5 7.5 7.5 4.5 12 4.5c4.5 0 8.5 3 9.75 7.5-1.25 4.5-5.25 7.5-9.75 7.5-4.5 0-8.5-3-9.75-7.5z"
                />
                <circle cx="12" cy="12" r="3" />
              </svg>
              <!-- Eye-off icon (hide password) -->
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-5 h-5"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M3.98 8.223A9.956 9.956 0 002.25 12c1.25 4.5 5.25 7.5 9.75 7.5 2.01 0 3.93-.5 5.57-1.377M6.53 6.53A9.953 9.953 0 0112 4.5c4.5 0 8.5 3 9.75 7.5-.386 1.39-1.07 2.68-2.02 3.777M15 12a3 3 0 11-6 0 3 3 0 016 0zm-6.53 6.53L3 21m0 0l3.53-3.53M3 21l3.53-3.53"
                />
              </svg>
            </button>
          </div>
        </div>
        <button
          type="submit"
          class="w-full bg-emerald-700 hover:bg-emerald-800 text-white py-3 rounded-lg font-bold text-lg shadow-md transition duration-200 hover:scale-105"
        >
          Login
        </button>
        <div v-if="error" class="text-red-500 mt-2 text-center font-semibold">{{ error }}</div>
      </form>
      <div class="mt-8 w-full text-center text-emerald-700 font-semibold">
        If you don't have an account?
      </div>
      <button
        @click="goToRegister"
        class="mt-4 w-full border border-emerald-700 text-emerald-700 hover:bg-emerald-50 hover:text-emerald-900 py-2 rounded-lg font-semibold transition duration-150 bg-white"
      >
        Create an account
      </button>
    </div>
  </div>
</template>
