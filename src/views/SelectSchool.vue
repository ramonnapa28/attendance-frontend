<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { useSnackbarStore } from '@/stores/snackbar'
import { getSchools, updateUser } from '@/services/api'
import axios from 'axios'
<<<<<<< HEAD
import api from '@/services/api'
=======
>>>>>>> d200206 (Initial commit)

const userStore = useUserStore()
const router = useRouter()
const snackbar = useSnackbarStore()

const schools = ref<{ id: string; name: string }[]>([])
const search = ref('')
const selectedSchoolId = ref<string | null>(null)

const filteredSchools = computed(() => {
  if (!search.value) return schools.value
  return schools.value.filter(s =>
    s.name.toLowerCase().includes(search.value.toLowerCase())
  )
})

function selectSchool(schoolId: string) {
  selectedSchoolId.value = schoolId
}

async function confirmSelection() {
  if (!selectedSchoolId.value) return
  const selectedSchool = filteredSchools.value.find(s => s.id === selectedSchoolId.value)
  const user = userStore.user
  if (!user || !user.id || !selectedSchool) {
    snackbar.trigger('Missing user or school information', 'error')
    return
  }
  try {
    await updateUser(user.id, { school: selectedSchool.name })
    userStore.setSchool(selectedSchool.name)
    snackbar.trigger('School selection saved! Registration is for account approval by instructor.', 'info')
    setTimeout(() => {
      router.push('/login')
    }, 1200)
  } catch (e) {
    snackbar.trigger('Failed to save school selection', 'error')
  }
}

onMounted(async () => {
  try {
    const { data } = await getSchools()
    schools.value = data.map((s: any) => ({ id: String(s.id), name: s.name }))
  } catch (e) {
    snackbar.trigger('Failed to load schools', 'error')
  }

  // Fallback: fetch user by email from /api/users if not in store
  if (!userStore.user || !userStore.user.id) {
    const email = localStorage.getItem('registeredEmail')
    if (email) {
      try {
<<<<<<< HEAD
        const { data: users } = await api.get('/api/users')
=======
        const { data: users } = await axios.get('/api/users')
>>>>>>> d200206 (Initial commit)
        const found = users.find((u: any) => u.email === email)
        if (found) userStore.login(found)
      } catch (e) {
        snackbar.trigger('Failed to load user profile', 'error')
      }
    }
  }
})
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-100 via-white to-emerald-200 py-10">
    <div class="w-full max-w-lg p-8 md:p-12 bg-white/80 backdrop-blur-lg rounded-3xl shadow-2xl border border-emerald-100 space-y-8">
      <div class="flex items-center gap-3 mb-2">
        <h1 class="text-3xl md:text-4xl font-extrabold text-emerald-800 tracking-tight">Select Your School</h1>
      </div>
      <input
        v-model="search"
        type="text"
        placeholder="Search schools..."
        class="w-full border border-emerald-400 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-600 transition text-emerald-900 bg-emerald-50 mb-4"
      />
      <div class="space-y-2 max-h-60 overflow-y-auto">
        <div
          v-for="school in filteredSchools"
          :key="school.id"
          @click="selectSchool(school.id)"
          :class="[
            'cursor-pointer px-4 py-3 rounded-lg border',
            selectedSchoolId === school.id
              ? 'bg-emerald-100 border-emerald-500 text-emerald-900 font-bold'
              : 'bg-white border-emerald-200 hover:bg-emerald-50'
          ]"
        >
          {{ school.name }}
        </div>
      </div>
      <button
        :disabled="!selectedSchoolId"
        @click="confirmSelection"
        class="w-full bg-emerald-700 hover:bg-emerald-800 text-white py-3 rounded-lg font-bold text-lg shadow-md transition duration-200 hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed mt-4"
      >
        Confirm Selection
      </button>
    </div>
  </div>
</template> 