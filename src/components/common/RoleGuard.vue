<script setup lang="ts">
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'
import type { UserRole } from '@/stores/user'

const props = defineProps<{ allowed: UserRole[] }>()
const userStore = useUserStore()

const isAllowed = computed(() => {
  return userStore.user && props.allowed.includes(userStore.user.role)
})
</script>

<template>
  <slot v-if="isAllowed" />
</template> 