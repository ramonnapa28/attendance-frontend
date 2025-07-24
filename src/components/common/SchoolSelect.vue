<script setup lang="ts">
const props = defineProps<{ schools: { id: string; name: string }[]; modelValue?: string }>()
const emit = defineEmits(['update:modelValue'])

function onChange(event: Event) {
  const target = event.target as HTMLSelectElement | null
  if (target) {
    emit('update:modelValue', target.value)
  }
}
</script>

<template>
  <select
    :value="props.modelValue"
    @change="onChange"
    class="w-full border rounded px-3 py-2"
  >
    <option value="">Select school</option>
    <option v-for="school in props.schools" :key="school.id" :value="school.id">
      {{ school.name }}
    </option>
  </select>
</template> 