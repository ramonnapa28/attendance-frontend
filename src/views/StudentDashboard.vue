```vue
<script setup lang="ts">
import AttendanceSummary from '@/components/common/AttendanceSummary.vue'
import QRCodeDisplay from '@/components/common/QRCodeDisplay.vue'
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const schools = ref<{ id: string; name: string }[]>([])
const profile = ref<{
  id?: string // Numeric ID for student
  name: string
  email: string
  studentId: string
  school?: string
  dob?: string
}>({
  id: '',
  name: '',
  email: '',
  studentId: '',
  school: '',
  dob: '',
})
const attendance = ref({ present: 0, absent: 0, total: 0 })
const attendanceRecords = ref<{ date: string; status: string }[]>([])
const lastAttendance = computed(() => {
  if (!attendanceRecords.value.length) return null
  return [...attendanceRecords.value].sort(
    (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime(),
  )[0]
})
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const schoolsRes = await api.get('/schools')
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
    schools.value = schoolsRes.data.map((s: any) => ({ id: String(s.id), name: s.name }))

    if (!userStore.user || !userStore.user.email) {
      error.value = 'Not logged in.'
      return
    }

    const { data } = await api.post('/auth/profile', {
      email: userStore.user.email,
    })
    profile.value = {
      id: data.id, // Capture numeric ID
      name: data.name,
      email: data.email,
      studentId: data.studentId || '',
      school: data.school || '',
      dob: data.dob || '',
    }

    if (data.id) {
      const summaryRes = await api.get(`/attendance/summary/${data.id}`)
      attendance.value = summaryRes.data
    }

    if (profile.value.studentId) {
      const recordsRes = await api.get(`/attendance/by-student/${profile.value.studentId}`)
      attendanceRecords.value = recordsRes.data
    }
  } catch (e) {
    console.error('Error loading profile:', e)
    error.value = 'Failed to load profile.'
  } finally {
    loading.value = false
  }
})

function toPhilippineTime(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const utc = date.getTime() + date.getTimezoneOffset() * 60000
  const phTime = new Date(utc + 8 * 60 * 60 * 1000)
  return phTime.toLocaleString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true,
  })
}

const schoolName = computed(() => {
  if (!profile.value.school) return ''
  const found = schools.value.find(
    (s) => s.name === profile.value.school || s.id === profile.value.school,
  )
  return found ? found.name : profile.value.school
})

// Ensure BASE_URL points to the frontend
const BASE_URL = import.meta.env.VITE_FRONTEND_URL || 'https://your-frontend-domain.com' // Replace with your actual frontend URL
const qrValue = computed(() => {
  const url = profile.value.id
    ? `${BASE_URL}/student-info?id=${encodeURIComponent(profile.value.id)}`
    : ''
  console.log('BASE_URL:', BASE_URL) // Debug BASE_URL
  console.log('QR Code URL:', url) // Debug QR code URL
  return url
})

const router = useRouter()
const showLogoutConfirm = ref(false)

function openLogoutConfirm() {
  showLogoutConfirm.value = true
}
function closeLogoutConfirm() {
  showLogoutConfirm.value = false
}
function confirmLogout() {
  userStore.logout?.()
  closeLogoutConfirm()
  router.push('/login')
}
</script>

<template>
  <div
    class="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-100 via-white to-emerald-200 py-10"
  >
    <div
      class="w-full max-w-4xl p-8 md:p-12 bg-white/70 backdrop-blur-lg rounded-3xl shadow-2xl border border-emerald-100 space-y-10"
    >
      <div class="flex items-center gap-3 mb-2 justify-between">
        <div class="flex items-center gap-3">
          <h1 class="text-3xl md:text-4xl font-extrabold text-emerald-800 tracking-tight">
            Student Dashboard
          </h1>
        </div>
        <button
          @click="openLogoutConfirm"
          class="profile-btn flex items-center justify-center w-12 h-12 rounded-full bg-transparent hover:bg-emerald-50 transition focus:outline-none focus:ring-2 focus:ring-emerald-300"
          aria-label="Logout"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-8 w-8 text-emerald-700"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H7a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v1"
            />
          </svg>
        </button>
      </div>
      <div v-if="loading" class="text-center text-emerald-700">Loading...</div>
      <div v-else-if="error" class="text-center text-red-500">{{ error }}</div>
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div class="space-y-8">
          <div class="bg-white/80 rounded-2xl shadow p-6 border border-emerald-50">
            <div class="flex items-center gap-2 mb-4">
              <svg
                class="h-6 w-6 text-emerald-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5.121 17.804A13.937 13.937 0 0112 15c2.485 0 4.797.657 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <h2 class="text-xl font-bold text-emerald-700">Profile</h2>
            </div>
            <div class="mb-2">
              <span class="block text-lg font-bold text-emerald-700">Name:</span>
              <span class="block text-xl">{{ profile.name }}</span>
            </div>
            <div class="mb-2">
              <span class="block text-lg font-bold text-emerald-700">Email:</span>
              <span class="block text-xl">{{ profile.email }}</span>
            </div>
            <div class="mb-2">
              <span class="block text-lg font-bold text-emerald-700">Student ID:</span>
              <span class="block text-xl">{{ profile.studentId }}</span>
            </div>
            <div class="mb-2">
              <span class="block text-lg font-bold text-emerald-700">Date of Birth:</span>
              <span class="block text-xl">{{ profile.dob }}</span>
            </div>
          </div>
          <div class="bg-white/80 rounded-2xl shadow p-6 border border-emerald-50">
            <div class="flex items-center gap-2 mb-4">
              <svg
                class="h-6 w-6 text-emerald-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 11c0-1.104.896-2 2-2s2 .896 2 2-.896 2-2 2-2-.896-2-2zm0 0V7m0 4v4m0 0h4m-4 0H8"
                />
              </svg>
              <h2 class="text-xl font-bold text-emerald-700">Last Attendance</h2>
            </div>
            <div v-if="lastAttendance">
              <span class="block text-lg font-bold text-emerald-700">Date:</span>
              <span class="block text-xl">{{ toPhilippineTime(lastAttendance.date) }}</span>
              <span class="block text-lg font-bold text-emerald-700 mt-2">Status:</span>
              <span
                class="block text-xl"
                :class="{
                  'text-emerald-600 font-semibold': lastAttendance.status === 'present',
                  'text-red-600 font-semibold': lastAttendance.status === 'absent',
                }"
              >
                {{ lastAttendance.status === 'present' ? 'Present' : 'Absent' }}
              </span>
            </div>
            <div v-else>
              <span class="block text-gray-500">No attendance yet.</span>
            </div>
          </div>
        </div>
        <div class="space-y-8">
          <div class="bg-white/80 rounded-2xl shadow p-6 border border-emerald-50">
            <div class="flex items-center gap-2 mb-4">
              <svg
                class="h-6 w-6 text-emerald-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 17v-2a4 4 0 018 0v2"
                />
              </svg>
              <h2 class="text-xl font-bold text-emerald-700">Attendance Summary</h2>
            </div>
            <AttendanceSummary :present="attendance.present" :absent="attendance.absent" />
          </div>
          <div class="bg-white/80 rounded-2xl shadow p-6 border border-emerald-50">
            <div class="flex items-center gap-2 mb-4">
              <svg
                class="h-6 w-6 text-emerald-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M16 7a4 4 0 01-8 0"
                />
              </svg>
              <h2 class="text-xl font-bold text-emerald-700">Select School</h2>
            </div>
            <div class="mb-2">
              <span class="block text-lg font-bold text-emerald-700">School:</span>
              <span class="block text-xl">
                {{ schoolName || 'Not selected yet. Please select your school.' }}
              </span>
            </div>
          </div>
          <div
            class="bg-white/80 rounded-2xl shadow p-6 border border-emerald-50 flex flex-col items-center min-h-[220px] justify-center"
          >
            <div class="flex items-center gap-2 mb-4">
              <svg
                class="h-6 w-6 text-emerald-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 11c0-1.104.896-2 2-2s2 .896 2 2-.896 2-2 2-2-.896-2-2zm0 0V7m0 4v4m0 0h4m-4 0H8"
                />
              </svg>
              <h2 class="text-xl font-bold text-emerald-700">Your QR Code</h2>
            </div>
            <QRCodeDisplay :value="qrValue" />
          </div>
        </div>
      </div>
      <div
        v-if="showLogoutConfirm"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-40"
      >
        <div class="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-sm relative">
          <div class="flex items-center mb-4">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-emerald-700 mr-2"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H7a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v1"
              />
            </svg>
            <h3 class="font-bold text-xl text-emerald-800">Confirm Logout</h3>
          </div>
          <p class="mb-6 text-gray-700">Are you sure you want to log out?</p>
          <div class="flex justify-end gap-3">
            <button
              @click="closeLogoutConfirm"
              class="px-4 py-2 rounded font-semibold bg-gray-100 text-gray-700 hover:bg-gray-200"
            >
              Cancel
            </button>
            <button
              @click="confirmLogout"
              class="px-4 py-2 rounded font-semibold bg-red-600 text-white hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-btn {
  background: transparent !important;
}
</style>
```
