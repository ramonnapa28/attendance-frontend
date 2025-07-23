<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
<<<<<<< HEAD
import api from '@/services/api'

const route = useRoute()
const student = ref(null)
const error = ref('')
const loading = ref(true)
=======
import axios from 'axios'

const route = useRoute()
const student = ref<any>(null)
const loading = ref(true)
const error = ref('')
>>>>>>> d200206 (Initial commit)

onMounted(async () => {
  const id = route.query.id as string
  if (!id) {
    error.value = 'No student ID provided.'
    loading.value = false
    return
  }
  try {
<<<<<<< HEAD
    const { data } = await api.get(`/api/students/by-id/${id}`)
    student.value = data
  } catch (err) {
    error.value = 'No student found or error occurred.'
    console.error(err)
=======
    // Use the new endpoint
    const { data } = await axios.get(`/api/students/by-id/${encodeURIComponent(id)}`)
    student.value = data
  } catch (e) {
    error.value = 'Failed to fetch student data.'
>>>>>>> d200206 (Initial commit)
  } finally {
    loading.value = false
  }
})
</script>

<<<<<<< HEAD

=======
>>>>>>> d200206 (Initial commit)
<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-emerald-100 via-white to-emerald-200 py-10">
    <div class="w-full max-w-md p-8 md:p-12 bg-white/80 backdrop-blur-lg rounded-3xl shadow-2xl border border-emerald-100 space-y-8">
      <div class="flex flex-col items-center gap-3 mb-2">
        <h1 class="text-3xl md:text-4xl font-extrabold text-emerald-800 tracking-tight">Student Info</h1>
      </div>
      <div v-if="loading" class="text-center text-emerald-700">Loading...</div>
      <div v-else-if="error" class="text-center text-red-500">{{ error }}</div>
      <div v-else-if="student" class="space-y-4">
        <div class="bg-white rounded-2xl shadow p-6 border border-emerald-50">
          <div class="mb-4">
            <span class="block text-lg font-bold text-emerald-700">Name:</span>
            <span class="block text-xl">{{ student.name }}</span>
          </div>
          <div class="mb-4">
            <span class="block text-lg font-bold text-emerald-700">School:</span>
            <span class="block text-xl">{{ student.school || 'N/A' }}</span>
          </div>
          <div>
            <span class="block text-lg font-bold text-emerald-700">Student ID:</span>
            <span class="block text-xl">{{ student.studentId }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
<<<<<<< HEAD
</template>
=======
</template> 
>>>>>>> d200206 (Initial commit)
