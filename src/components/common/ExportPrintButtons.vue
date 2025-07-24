<script setup lang="ts">
const emit = defineEmits(['export', 'print'])
</script>

<template>
  <div class="flex space-x-2">
    <button @click="emit('export')" class="bg-green-600 text-white px-4 py-2 rounded font-semibold">Export</button>
    <button @click="emit('print')" class="bg-blue-600 text-white px-4 py-2 rounded font-semibold">Print</button>
  </div>
</template> 