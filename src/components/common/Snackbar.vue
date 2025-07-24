<template>
  <transition name="slide-fade">
    <div
      v-if="snackbar.show"
      :class="[
        'fixed bottom-8 left-1/2 transform -translate-x-1/2 flex items-center min-w-[260px] max-w-[90vw] px-5 py-4 rounded-xl shadow-2xl z-50 border-l-8',
        colorClass,
        borderClass
      ]"
      role="alert"
      aria-live="assertive"
    >
      <span class="mr-3 text-2xl">
        <component :is="iconComponent" />
      </span>
      <span class="flex-1 font-medium text-base">{{ snackbar.message }}</span>
      <button @click="onClose" class="ml-4 text-xl focus:outline-none hover:scale-125 transition-transform" aria-label="Close snackbar">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSnackbarStore } from '@/stores/snackbar'

const snackbar = useSnackbarStore()

function onClose() {
  snackbar.close()
}

const colorClass = computed(() => {
  switch (snackbar.color) {
    case 'success': return 'bg-green-50 text-green-900'
    case 'error': return 'bg-red-50 text-red-900'
    case 'info': return 'bg-blue-50 text-blue-900'
    case 'warning': return 'bg-yellow-50 text-yellow-900'
    default: return 'bg-gray-800 text-white'
  }
})

const borderClass = computed(() => {
  switch (snackbar.color) {
    case 'success': return 'border-green-500'
    case 'error': return 'border-red-500'
    case 'info': return 'border-blue-500'
    case 'warning': return 'border-yellow-400'
    default: return 'border-gray-800'
  }
})

const iconComponent = computed(() => {
  switch (snackbar.color) {
    case 'success':
      return {
        template: `<svg class='h-6 w-6 text-green-500' fill='none' viewBox='0 0 24 24' stroke='currentColor'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M5 13l4 4L19 7' /></svg>`
      }
    case 'error':
      return {
        template: `<svg class='h-6 w-6 text-red-500' fill='none' viewBox='0 0 24 24' stroke='currentColor'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M6 18L18 6M6 6l12 12' /></svg>`
      }
    case 'info':
      return {
        template: `<svg class='h-6 w-6 text-blue-500' fill='none' viewBox='0 0 24 24' stroke='currentColor'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M13 16h-1v-4h-1m1-4h.01' /></svg>`
      }
    case 'warning':
      return {
        template: `<svg class='h-6 w-6 text-yellow-500' fill='none' viewBox='0 0 24 24' stroke='currentColor'><path stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M12 8v4m0 4h.01M4.93 19h14.14a2 2 0 001.74-2.99l-7.07-12.25a2 2 0 00-3.48 0L3.19 16.01A2 2 0 004.93 19z' /></svg>`
      }
    default:
      return {
        template: `<svg class='h-6 w-6 text-gray-500' fill='none' viewBox='0 0 24 24' stroke='currentColor'><circle cx='12' cy='12' r='10' stroke-width='2' /></svg>`
      }
  }
})
</script>

<style scoped>
.slide-fade-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  transform: translateY(40px);
  opacity: 0;
}
.slide-fade-enter-to {
  transform: translateY(0);
  opacity: 1;
}
.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 1;
}
.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(40px);
}
</style> 