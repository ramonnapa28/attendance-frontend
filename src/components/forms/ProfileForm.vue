<script setup lang="ts">
import { ref, watch, defineProps, defineEmits, computed } from 'vue'

const props = defineProps<{
  name?: string
  email: string
  school?: string
  studentId?: string
  schools?: { id: string; name: string }[]
  readonly?: boolean
}>()

const emit = defineEmits(['update'])

const name = ref(props.name || '')
const email = ref(props.email)
const school = ref(props.school || '')

const schoolName = computed(() => {
  if (!props.school || !props.schools) return ''
  const found = props.schools.find(s => s.id === props.school || s.name === props.school)
  return found ? found.name : props.school
})

watch([name, email, school], () => {
  emit('update', { name: name.value, email: email.value, school: school.value })
})
</script>

<template>
  <form class="space-y-4">
    <div>
      <label class="block font-medium mb-1">Name</label>
      <input v-model="name" class="w-full border rounded px-3 py-2" type="text" required :readonly="props.readonly" :disabled="props.readonly" />
    </div>
    <div>
      <label class="block font-medium mb-1">Email</label>
      <input v-model="email" class="w-full border rounded px-3 py-2" type="email" required :readonly="props.readonly" :disabled="props.readonly" />
    </div>
    <div v-if="props.schools">
      <label class="block font-medium mb-1">School</label>
      <template v-if="props.readonly">
        <input :value="schoolName" class="w-full border rounded px-3 py-2 bg-gray-100" type="text" readonly />
      </template>
      <template v-else>
        <select v-model="school" class="w-full border rounded px-3 py-2">
          <option value="">Select school</option>
          <option v-for="s in props.schools" :key="s.id" :value="s.id">{{ s.name }}</option>
        </select>
      </template>
    </div>
    <div v-if="props.studentId">
      <label class="block font-medium mb-1">Student ID</label>
      <input :value="props.studentId" class="w-full border rounded px-3 py-2 bg-gray-100" type="text" readonly />
    </div>
  </form>
</template> 