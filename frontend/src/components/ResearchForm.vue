<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search, Loader2, Settings, AlertCircle } from 'lucide-vue-next'

const MAX_QUERY_LENGTH = 500
const MIN_QUERY_LENGTH = 3

const props = defineProps<{
  isLoading: boolean
}>()

const query = ref('')
const maxLoops = ref(3)
const showSettings = ref(false)
const touched = ref(false)

const emit = defineEmits<{
  (e: 'submit', task: string, maxLoops: number): void
}>()

const validationError = computed(() => {
  const trimmed = query.value.trim()
  if (!trimmed && touched.value) {
    return 'Please enter a research topic'
  }
  if (trimmed.length > 0 && trimmed.length < MIN_QUERY_LENGTH) {
    return `Topic must be at least ${MIN_QUERY_LENGTH} characters`
  }
  if (trimmed.length > MAX_QUERY_LENGTH) {
    return `Topic must be less than ${MAX_QUERY_LENGTH} characters`
  }
  return null
})

const isValid = computed(() => {
  const trimmed = query.value.trim()
  return trimmed.length >= MIN_QUERY_LENGTH && trimmed.length <= MAX_QUERY_LENGTH
})

const characterCount = computed(() => query.value.length)

const handleSubmit = () => {
  touched.value = true
  if (!isValid.value || props.isLoading) return
  emit('submit', query.value, maxLoops.value)
  showSettings.value = false
}

const toggleSettings = () => {
  showSettings.value = !showSettings.value
}

const handleBlur = () => {
  touched.value = true
}
</script>

<template>
  <div class="w-full max-w-3xl mx-auto space-y-2">
    <div class="relative flex items-center">
      <Search class="absolute left-4 text-gray-400 w-5 h-5" />
      <input
        v-model="query"
        @keydown.enter="handleSubmit"
        @blur="handleBlur"
        type="text"
        :disabled="isLoading"
        :maxlength="MAX_QUERY_LENGTH + 10"
        placeholder="Enter a research topic (e.g., 'Analysis of DeepSeek MoE architecture')..."
        :class="[
          'w-full py-4 pl-12 pr-40 text-lg bg-white dark:bg-gray-800 dark:text-white border rounded-xl shadow-sm focus:outline-none focus:ring-2 focus:border-transparent transition-all disabled:bg-gray-50 dark:disabled:bg-gray-900 disabled:text-gray-400 dark:disabled:text-gray-600 placeholder:text-gray-400 dark:placeholder:text-gray-500',
          validationError ? 'border-red-300 dark:border-red-700 focus:ring-red-500' : 'border-gray-200 dark:border-gray-700 focus:ring-blue-500'
        ]"
        aria-describedby="query-help query-error"
      />

      <div class="absolute right-2 flex items-center gap-2">
        <button
            @click="toggleSettings"
            :disabled="isLoading"
            class="p-2 text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors relative"
            title="Settings"
            aria-label="Toggle settings"
        >
          <Settings class="w-5 h-5" />
        </button>

        <button
          @click="handleSubmit"
          :disabled="isLoading || !isValid"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium disabled:bg-blue-400 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
          <span v-else>Research</span>
        </button>
      </div>
    </div>

    <!-- Validation and Character Count -->
    <div class="flex justify-between items-center px-1">
      <div class="flex items-center gap-1.5">
        <template v-if="validationError">
          <AlertCircle class="w-4 h-4 text-red-500" />
          <span id="query-error" class="text-sm text-red-500">{{ validationError }}</span>
        </template>
        <span v-else id="query-help" class="text-sm text-gray-400 dark:text-gray-500">
          Enter a topic to research
        </span>
      </div>
      <span
        :class="[
          'text-xs',
          characterCount > MAX_QUERY_LENGTH ? 'text-red-500' : 'text-gray-400 dark:text-gray-500'
        ]"
      >
        {{ characterCount }}/{{ MAX_QUERY_LENGTH }}
      </span>
    </div>

    <!-- Settings Panel -->
    <div v-if="showSettings" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-lg animate-in fade-in slide-in-from-top-2">
      <h3 class="font-medium text-gray-700 dark:text-gray-200 mb-3">Research Settings</h3>
      <div class="space-y-4">
        <div>
          <label class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Depth (Iterations): {{ maxLoops }}</label>
          <input
            type="range"
            v-model.number="maxLoops"
            min="1"
            max="5"
            class="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
          />
          <div class="flex justify-between text-xs text-gray-400 dark:text-gray-500 mt-1">
            <span>Quick (1)</span>
            <span>Deep (5)</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
