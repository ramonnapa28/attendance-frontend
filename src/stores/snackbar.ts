import { defineStore } from 'pinia'

let timeoutId: ReturnType<typeof setTimeout> | null = null

export const useSnackbarStore = defineStore('snackbar', {
  state: () => ({
    show: false,
    message: '',
    color: 'success' as 'success' | 'error' | 'info' | 'warning',
    timeout: 3000,
  }),
  actions: {
    trigger(message: string, color: 'success' | 'error' | 'info' | 'warning' = 'success', timeout = 3000) {
      this.message = message
      this.color = color
      this.timeout = timeout
      this.show = true
      if (timeoutId) clearTimeout(timeoutId)
      timeoutId = setTimeout(() => {
        this.show = false
      }, timeout)
    },
    close() {
      this.show = false
      if (timeoutId) clearTimeout(timeoutId)
    }
  }
}) 