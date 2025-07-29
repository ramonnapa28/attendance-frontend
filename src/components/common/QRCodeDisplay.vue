<script setup lang="ts">
import QrcodeVue from 'qrcode.vue'
const props = defineProps<{ value: string }>()
</script>

<template>
  <div class="flex flex-col items-center">
    <QrcodeVue :value="props.value" :size="200" class="mb-2" level="M" />
    <a 
      v-if="props.value"
      :href="props.value" 
      target="_blank" 
      class="text-xs text-emerald-600 hover:text-emerald-800 underline break-all text-center mt-2"
    >
      {{ props.value }}
    </a>
  </div>
</template> 