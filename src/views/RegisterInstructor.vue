<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { useSnackbarStore } from '@/stores/snackbar'

const name = ref('')
const dob = ref('')
const address = ref('')
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const userStore = useUserStore()
const router = useRouter()
const error = ref('')
const snackbar = useSnackbarStore()

function generateEmployeeId() {
  return 'E' + new Date().getFullYear() + Math.floor(1000 + Math.random() * 9000)
}
const employeeId = ref(generateEmployeeId())

const passwordStrength = computed(() => {
  // At least 8 chars, 1 uppercase, 1 number, 1 symbol
  const strongRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]).{8,}$/
  return strongRegex.test(password.value)
})

async function onSubmit() {
  error.value = ''
  if (!passwordStrength.value) {
    error.value =
      'Password must be at least 8 characters and include an uppercase letter, a number, and a symbol.'
    return
  }
  try {
    await userStore.registerApi({
      name: name.value,
      dob: dob.value,
      address: address.value,
      email: email.value,
      password: password.value,
      instructorId: employeeId.value,
      role: 'instructor',
    })
    snackbar.trigger(
      'Registration submitted! Your account will be activated after admin approval.',
      'info',
    )
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (e) {
    error.value = 'Registration failed'
  }
}
</script>
<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden">
    <svg
      class="absolute inset-0 w-full h-full object-cover opacity-30 z-0 pointer-events-none"
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
      <div class="mb-4 flex flex-col items-center">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-12 w-12 text-emerald-700 mb-2"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 2l2.09 6.26L20 9.27l-5 3.64L16.18 20 12 16.77 7.82 20 9 12.91l-5-3.64 5.91-.91z"
          />
        </svg>
        <h1 class="text-2xl font-extrabold text-emerald-800 tracking-tight text-center">
          Instructor Registration
        </h1>
        <p class="text-gray-600 text-sm mt-1 text-center">Create your instructor account</p>
      </div>
      <form @submit.prevent="onSubmit" class="w-full mt-4 space-y-5">
        <div>
          <label class="block mb-1 font-semibold text-emerald-800" for="name">Name</label>
          <input
            v-model="name"
            id="name"
            type="text"
            class="w-full border border-emerald-400 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition text-emerald-900 bg-emerald-50"
            placeholder="Enter your name"
            required
          />
        </div>
        <div>
          <label class="block mb-1 font-semibold text-emerald-800" for="dob">Date of Birth</label>
          <input
            v-model="dob"
            id="dob"
            type="date"
            class="w-full border border-emerald-400 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition text-emerald-900 bg-emerald-50"
            required
          />
        </div>
        <div>
          <label class="block mb-1 font-semibold text-emerald-800" for="address">Address</label>
          <input
            v-model="address"
            id="address"
            type="text"
            class="w-full border border-emerald-400 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition text-emerald-900 bg-emerald-50"
            placeholder="Enter your address"
            required
          />
        </div>
        <div>
          <label class="block mb-1 font-semibold text-emerald-800" for="email">Email</label>
          <input
            v-model="email"
            id="email"
            type="email"
            class="w-full border border-emerald-400 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition text-emerald-900 bg-emerald-50"
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
              class="w-full border border-emerald-400 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition text-emerald-900 bg-emerald-50 pr-12"
              placeholder="Enter your password"
              required
            />
            <button
              type="button"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-emerald-700"
              @click="showPassword = !showPassword"
              tabindex="-1"
              aria-label="Toggle password visibility"
            >
              <svg
                v-if="showPassword"
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13.875 18.825A10.05 10.05 0 0112 19c-5.523 0-10-4.477-10-10 0-1.657.403-3.22 1.125-4.575M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <svg
                v-else
                xmlns="http://www.w3.org/2000/svg"
                class="h-5 w-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M3 3l18 18M9.88 9.88A3 3 0 0112 9c1.657 0 3 1.343 3 3 0 .512-.13.995-.354 1.412M6.1 6.1A9.956 9.956 0 002 12c0 5.523 4.477 10 10 10 2.21 0 4.26-.72 5.9-1.9"
                />
              </svg>
            </button>
          </div>
          <!-- Only show the error after submit attempt -->
          <div v-if="error && !passwordStrength" class="text-xs text-red-500 mt-1">
            {{ error }}
          </div>
        </div>
        <div>
          <label class="block mb-1 font-semibold text-emerald-800">Employee ID</label>
          <input
            :value="employeeId"
            type="text"
            class="w-full border border-emerald-400 rounded-lg px-4 py-3 bg-gray-100 text-gray-700"
            readonly
          />
        </div>
        <button
          type="submit"
          class="w-full bg-emerald-700 hover:bg-emerald-800 text-white py-3 rounded-lg font-bold text-lg shadow-md transition duration-200 hover:scale-105"
        >
          Register
        </button>
        <div v-if="error && passwordStrength" class="text-red-500 mt-2 text-center font-semibold">
          {{ error }}
        </div>
      </form>
    </div>
  </div>
</template>
