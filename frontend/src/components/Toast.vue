<script setup lang="ts">
import { useToast, type ToastType } from '../composables/useToast'
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-vue-next'

const { toasts, remove } = useToast()

const iconMap: Record<ToastType, typeof CheckCircle> = {
  success: CheckCircle,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info
}

const colorMap: Record<ToastType, string> = {
  success: 'bg-green-50 dark:bg-green-900/30 border-green-200 dark:border-green-800 text-green-800 dark:text-green-200',
  error: 'bg-red-50 dark:bg-red-900/30 border-red-200 dark:border-red-800 text-red-800 dark:text-red-200',
  warning: 'bg-yellow-50 dark:bg-yellow-900/30 border-yellow-200 dark:border-yellow-800 text-yellow-800 dark:text-yellow-200',
  info: 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800 text-blue-800 dark:text-blue-200'
}

const iconColorMap: Record<ToastType, string> = {
  success: 'text-green-500 dark:text-green-400',
  error: 'text-red-500 dark:text-red-400',
  warning: 'text-yellow-500 dark:text-yellow-400',
  info: 'text-blue-500 dark:text-blue-400'
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-[100] space-y-2 pointer-events-none">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="colorMap[toast.type]"
          class="flex items-center gap-3 px-4 py-3 rounded-lg border shadow-lg max-w-sm pointer-events-auto"
        >
          <component
            :is="iconMap[toast.type]"
            :class="iconColorMap[toast.type]"
            class="w-5 h-5 flex-shrink-0"
          />
          <span class="text-sm font-medium flex-1">{{ toast.message }}</span>
          <button
            @click="remove(toast.id)"
            class="p-1 hover:bg-black/5 dark:hover:bg-white/10 rounded transition-colors flex-shrink-0"
            aria-label="Close notification"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-enter-active {
  transition: all 0.3s ease-out;
}

.toast-leave-active {
  transition: all 0.2s ease-in;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>
