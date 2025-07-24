<script setup lang="ts">
import { RouterView } from 'vue-router'
import Snackbar from '@/components/common/Snackbar.vue'
</script>

<template>
  <div class="h-screen overflow-hidden">
    <main class="h-screen overflow-hidden">
      <RouterView />
      <Snackbar />
    </main>
  </div>
</template>
