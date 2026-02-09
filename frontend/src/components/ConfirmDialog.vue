<script setup lang="ts">
import { ref } from 'vue'
import { AlertTriangle } from 'lucide-vue-next'

interface Props {
  title?: string
  message: string
  confirmText?: string
  cancelText?: string
  confirmClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  title: 'Confirm',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  confirmClass: 'bg-red-600 hover:bg-red-700 text-white'
})

const emit = defineEmits<{
  (e: 'confirm'): void
  (e: 'cancel'): void
}>()

const isOpen = ref(false)
let resolvePromise: ((value: boolean) => void) | null = null

const open = (): Promise<boolean> => {
  isOpen.value = true
  return new Promise((resolve) => {
    resolvePromise = resolve
  })
}

const handleConfirm = () => {
  isOpen.value = false
  resolvePromise?.(true)
  emit('confirm')
}

const handleCancel = () => {
  isOpen.value = false
  resolvePromise?.(false)
  emit('cancel')
}

defineExpose({ open })
</script>

<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 z-[110] flex items-center justify-center p-4"
        @click.self="handleCancel"
      >
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm"></div>
        <div class="relative bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-md w-full p-6 space-y-4">
          <div class="flex items-start gap-4">
            <div class="p-2 bg-red-100 dark:bg-red-900/30 rounded-full">
              <AlertTriangle class="w-6 h-6 text-red-600 dark:text-red-400" />
            </div>
            <div class="flex-1">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ title }}</h3>
              <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">{{ message }}</p>
            </div>
          </div>
          <div class="flex justify-end gap-3 pt-2">
            <button
              @click="handleCancel"
              class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
            >
              {{ cancelText }}
            </button>
            <button
              @click="handleConfirm"
              :class="confirmClass"
              class="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
            >
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.modal-enter-active {
  transition: all 0.2s ease-out;
}

.modal-leave-active {
  transition: all 0.15s ease-in;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.95);
}
</style>
