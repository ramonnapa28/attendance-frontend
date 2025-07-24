<script setup lang="ts">
const props = defineProps<{
  present: number
  absent: number
}>()
</script>

<template>
  <div class="flex space-x-4">
    <div class="bg-green-100 text-green-800 px-4 py-2 rounded shadow">
      Present: <span class="font-bold">{{ props.present }}</span>
    </div>
    <div class="bg-red-100 text-red-800 px-4 py-2 rounded shadow">
      Absent: <span class="font-bold">{{ props.absent }}</span>
    </div>
  </div>
</template> 