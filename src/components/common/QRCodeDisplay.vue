<script setup lang="ts">
import QrcodeVue from 'qrcode.vue'
const props = defineProps<{ value: string }>()
</script>

<template>
  <div class="flex flex-col items-center">
    <QrcodeVue :value="props.value" :size="128" class="mb-2" />
    <span class="text-xs text-gray-500 break-all text-center mt-2">QR: {{ props.value }}</span>
  </div>
</template> 