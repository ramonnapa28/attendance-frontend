<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
function selectRole(role: string) {
  if (role === 'student') router.push('/register/student')
  else if (role === 'instructor') router.push('/register/instructor')
}
</script>
<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden">
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
      <div class="mb-4 flex flex-col items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-emerald-700 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 2l2.09 6.26L20 9.27l-5 3.64L16.18 20 12 16.77 7.82 20 9 12.91l-5-3.64 5.91-.91z" />
        </svg>
        <h1 class="text-2xl font-extrabold text-emerald-800 tracking-tight text-center">Register as</h1>
        <p class="text-gray-600 text-sm mt-1 text-center">Choose your role to continue registration</p>
      </div>
      <div class="flex flex-col gap-6 w-full mt-6">
        <button @click="() => selectRole('student')" class="w-full bg-emerald-700 hover:bg-emerald-800 text-white py-3 rounded-lg font-bold text-lg shadow-md transition duration-200 hover:scale-105">Student</button>
        <button @click="() => selectRole('instructor')" class="w-full bg-emerald-700 hover:bg-emerald-800 text-white py-3 rounded-lg font-bold text-lg shadow-md transition duration-200 hover:scale-105">Instructor</button>
      </div>
    </div>
  </div>
</template> 