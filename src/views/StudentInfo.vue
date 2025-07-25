<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'

// Define the Student interface to match the expected API response
interface Student {
  id: string
  name: string
  school?: string // Optional, as you use || 'N/A' in the template
  studentId: string
}

const route = useRoute()
const student = ref<Student | null>(null) // Explicitly type student as Student or null
const error = ref<string>('') // Explicitly type error as string
const loading = ref<boolean>(true) // Explicitly type loading as boolean

onMounted(async () => {
  const id = route.query.id as string
  if (!id) {
    error.value = 'No student ID provided.'
    loading.value = false
    return
  }

  try {
    const { data } = await api.get(`/students/by-id/${id}`)
    // Ensure the API response matches the Student interface
    if (data && typeof data === 'object' && 'id' in data && 'name' in data && 'studentId' in data) {
      student.value = data as Student
    } else {
      throw new Error('Invalid student data')
    }
  } catch (err) {
    error.value = 'No student found or error occurred.'
    console.error(err)
  } finally {
    loading.value = false
  }
})
</script>

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
</template>
