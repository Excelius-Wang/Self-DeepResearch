<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search, Loader2, Settings, AlertCircle, Sparkles, Clock } from 'lucide-vue-next'

const MAX_QUERY_LENGTH = 500
const MIN_QUERY_LENGTH = 3

// Example topics for inspiration
const exampleTopics = [
  'DeepSeek MoE architecture analysis',
  'Latest trends in AI agents',
  'How does RAG work?',
]

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

// Estimated time based on depth
const estimatedTime = computed(() => {
  if (maxLoops.value === 1) return '1-2 min'
  if (maxLoops.value === 2) return '2-3 min'
  if (maxLoops.value === 3) return '3-5 min'
  if (maxLoops.value === 4) return '5-8 min'
  return '8-12 min'
})

const depthLabel = computed(() => {
  if (maxLoops.value === 1) return 'Quick'
  if (maxLoops.value === 2) return 'Standard'
  if (maxLoops.value === 3) return 'Thorough'
  if (maxLoops.value === 4) return 'Deep'
  return 'Comprehensive'
})

const handleSubmit = () => {
  touched.value = true
  if (!isValid.value || props.isLoading) return
  emit('submit', query.value, maxLoops.value)
  showSettings.value = false
}

const toggleSettings = () => {
  showSettings.value = !showSettings.value
}

const useExample = (topic: string) => {
  query.value = topic
  touched.value = false
}
</script>

<template>
  <div class="w-full max-w-3xl mx-auto space-y-3">
    <!-- Search Input -->
    <div class="relative flex items-center">
      <Search class="absolute left-4 text-gray-400 w-5 h-5 pointer-events-none" />
      <input
        v-model="query"
        @keydown.enter="handleSubmit"
        @focus="touched = false"
        type="text"
        :disabled="isLoading"
        :maxlength="MAX_QUERY_LENGTH + 10"
        placeholder="What would you like to research?"
        :class="[
          'w-full py-4 pl-12 pr-32 text-base bg-white dark:bg-gray-800 dark:text-white border-2 rounded-xl shadow-sm transition-all duration-200',
          'focus:outline-none focus:shadow-lg',
          'disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:text-gray-400 dark:disabled:text-gray-600',
          'placeholder:text-gray-400 dark:placeholder:text-gray-500',
          validationError
            ? 'border-red-300 dark:border-red-700 focus:border-red-400 focus:ring-4 focus:ring-red-100 dark:focus:ring-red-900/30'
            : 'border-gray-200 dark:border-gray-700 focus:border-blue-500 focus:ring-4 focus:ring-blue-100 dark:focus:ring-blue-900/30'
        ]"
        aria-label="Research topic"
        aria-describedby="query-error"
      />

      <div class="absolute right-2 flex items-center gap-1">
        <button
          @click="toggleSettings"
          :disabled="isLoading"
          class="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
          title="Research settings"
          aria-label="Toggle settings"
        >
          <Settings class="w-5 h-5" />
        </button>

        <button
          @click="handleSubmit"
          :disabled="isLoading || !isValid"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all font-medium disabled:bg-gray-300 dark:disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed flex items-center gap-2 shadow-sm hover:shadow-md disabled:shadow-none"
        >
          <Loader2 v-if="isLoading" class="w-4 h-4 animate-spin" />
          <span>{{ isLoading ? 'Researching...' : 'Research' }}</span>
        </button>
      </div>
    </div>

    <!-- Validation Error / Character Count Row -->
    <div class="flex justify-between items-center px-1 min-h-[20px]">
      <div class="flex items-center gap-1.5">
        <template v-if="validationError">
          <AlertCircle class="w-4 h-4 text-red-500 flex-shrink-0" />
          <span id="query-error" class="text-sm text-red-500">{{ validationError }}</span>
        </template>
      </div>
      <span
        v-if="characterCount > 0"
        :class="[
          'text-xs font-medium tabular-nums',
          characterCount > MAX_QUERY_LENGTH ? 'text-red-500' : 'text-gray-400 dark:text-gray-500'
        ]"
      >
        {{ characterCount }}/{{ MAX_QUERY_LENGTH }}
      </span>
    </div>

    <!-- Example Topics -->
    <div v-if="!isLoading && query.length === 0" class="flex flex-wrap items-center gap-2 px-1">
      <span class="text-xs text-gray-400 dark:text-gray-500 flex items-center gap-1">
        <Sparkles class="w-3 h-3" />
        Try:
      </span>
      <button
        v-for="topic in exampleTopics"
        :key="topic"
        @click="useExample(topic)"
        class="text-xs px-2.5 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded-full hover:bg-blue-100 dark:hover:bg-blue-900/30 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
      >
        {{ topic }}
      </button>
    </div>

    <!-- Settings Panel -->
    <div v-if="showSettings" class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4 shadow-lg animate-in fade-in slide-in-from-top-2 duration-200">
      <div class="flex items-center justify-between mb-3">
        <h3 class="font-medium text-gray-800 dark:text-gray-200 text-sm">Research Depth</h3>
        <span class="text-xs font-medium px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded">
          {{ depthLabel }}
        </span>
      </div>
      <div class="space-y-3">
        <div class="flex items-center gap-4">
          <input
            type="range"
            v-model.number="maxLoops"
            min="1"
            max="5"
            class="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
          <span class="text-sm font-semibold text-blue-600 dark:text-blue-400 w-8 text-center">{{ maxLoops }}</span>
        </div>
        <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400">
          <span>Quick (1 loop)</span>
          <span>Deep (5 loops)</span>
        </div>
        <!-- Estimated Time -->
        <div class="flex items-center justify-center gap-2 pt-2 border-t border-gray-100 dark:border-gray-700">
          <Clock class="w-4 h-4 text-gray-400" />
          <span class="text-xs text-gray-500 dark:text-gray-400">
            Estimated time: <span class="font-medium text-gray-700 dark:text-gray-300">{{ estimatedTime }}</span>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
