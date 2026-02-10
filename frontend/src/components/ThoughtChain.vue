<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
import {
  Loader2,
  BrainCircuit,
  Search,
  FileText,
  ListTodo,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  PenLine
} from 'lucide-vue-next'
import type { ThoughtStep, ResearchProgress } from '../types'

const props = defineProps<{
  steps: ThoughtStep[]
  isLoading: boolean
  progress?: ResearchProgress | null
}>()

const containerRef = ref<HTMLElement | null>(null)
const expandedSources = ref<Set<string>>(new Set())
const isExpanded = ref(false)

// Auto-scroll on new steps
watch(() => props.steps.length, async () => {
  await nextTick()
  if (containerRef.value && isExpanded.value) {
    containerRef.value.scrollTop = containerRef.value.scrollHeight
  }
})


const toggleSources = (stepId: string) => {
  if (expandedSources.value.has(stepId)) {
    expandedSources.value.delete(stepId)
  } else {
    expandedSources.value.add(stepId)
  }
}

const toggleExpand = () => {
  isExpanded.value = !isExpanded.value
}

const getIcon = (type: string) => {
  switch (type) {
    case 'planner': return ListTodo
    case 'researcher': return Search
    case 'reviewer': return BrainCircuit
    default: return FileText
  }
}

const getPhaseIcon = (phase: string) => {
  switch (phase) {
    case 'planner': return ListTodo
    case 'researcher': return Search
    case 'reviewer': return BrainCircuit
    case 'reporter': return PenLine
    default: return FileText
  }
}

const getBgColor = (type: string) => {
  switch (type) {
    case 'planner': return 'bg-blue-500/10 border-blue-500/20 text-blue-500 dark:text-blue-400'
    case 'researcher': return 'bg-amber-500/10 border-amber-500/20 text-amber-500 dark:text-amber-400'
    case 'reviewer': return 'bg-purple-500/10 border-purple-500/20 text-purple-500 dark:text-purple-400'
    default: return 'bg-gray-100 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-500 dark:text-gray-400'
  }
}

// Progress bar percentage
const progressPercent = computed(() => {
  if (!props.progress) return 0
  const phaseWeights: Record<string, number> = {
    planner: 10,
    researcher: 50,
    reviewer: 70,
    reporter: 90
  }
  const basePercent = phaseWeights[props.progress.phase] || 0
  const loopFactor = props.progress.currentLoop / props.progress.maxLoops
  return Math.min(basePercent + (loopFactor * 10), 100)
})
</script>

<template>
  <div class="w-full bg-white dark:bg-gray-800 rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700 shadow-lg flex flex-col transition-all duration-500">
    <!-- Header -->
    <div
      class="px-5 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/90 flex items-center justify-between shrink-0 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors"
      @click="toggleExpand"
    >
      <div class="flex items-center gap-2.5 text-gray-800 dark:text-gray-200">
        <div class="relative">
          <BrainCircuit class="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <div v-if="isLoading" class="absolute -top-1 -right-1 w-2 h-2 bg-blue-500 rounded-full animate-ping"></div>
        </div>
        <span class="font-semibold tracking-tight">Thinking Process</span>
      </div>
      <div class="flex items-center gap-4">
        <!-- Loop indicator -->
        <div v-if="progress" class="flex items-center gap-2 text-xs font-mono text-gray-500 dark:text-gray-400">
          <span class="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded">
            Loop {{ progress.currentLoop || 1 }}/{{ progress.maxLoops }}
          </span>
          <component :is="getPhaseIcon(progress.phase)" class="w-4 h-4" />
        </div>
        <div class="text-xs font-mono text-gray-500 dark:text-gray-400">
          {{ steps.length }} steps
        </div>
        <button class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors">
          <component :is="isExpanded ? ChevronUp : ChevronDown" class="w-5 h-5" />
        </button>
      </div>
    </div>

    <!-- Progress Bar -->
    <div v-if="isLoading && progress" class="h-1 bg-gray-100 dark:bg-gray-700">
      <div
        class="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-500 ease-out"
        :style="{ width: `${progressPercent}%` }"
      ></div>
    </div>

    <!-- Content -->
    <div
      v-show="isExpanded"
      ref="containerRef"
      class="overflow-y-auto p-5 space-y-6 scrollbar-thin scroll-smooth transition-all duration-500 bg-gray-50/50 dark:bg-gray-900/30"
      :class="{'max-h-[500px]': true, 'min-h-[200px]': steps.length > 0}"
    >
      <div v-if="steps.length === 0" class="flex flex-col items-center justify-center py-12 text-gray-400 dark:text-gray-500 space-y-3">
        <div class="w-12 h-12 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
          <BrainCircuit class="w-6 h-6 opacity-50" />
        </div>
        <p class="text-sm">Waiting for research task...</p>
      </div>

      <div
        v-for="step in steps"
        :key="step.id"
        class="animate-in fade-in slide-in-from-bottom-4 duration-500"
      >
        <div class="flex gap-4 group">
          <!-- Timeline Line -->
          <div class="flex flex-col items-center">
            <div
              class="w-8 h-8 rounded-lg flex items-center justify-center border shadow-sm transition-all duration-300 z-10 bg-white dark:bg-gray-800"
              :class="getBgColor(step.type)"
            >
              <component :is="getIcon(step.type)" class="w-4 h-4" />
            </div>
            <div class="w-0.5 flex-1 bg-gray-200 dark:bg-gray-700 my-2 group-last:hidden"></div>
          </div>

          <!-- Card Content -->
          <div class="flex-1 pb-4 min-w-0">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-800 dark:text-gray-200 truncate pr-2">{{ step.title }}</span>
              <span class="text-xs font-mono text-gray-400 dark:text-gray-500 shrink-0">
                {{ new Date(step.timestamp).toLocaleTimeString([], {hour12: false, minute:'2-digit', second:'2-digit'}) }}
              </span>
            </div>

            <!-- Planner: Sub Queries List -->
            <div v-if="step.type === 'planner' && Array.isArray(step.content)" class="space-y-2">
              <div v-for="(q, idx) in step.content" :key="idx" class="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-800 p-2.5 rounded-lg border border-gray-200 dark:border-gray-700">
                <span class="text-blue-500 mt-0.5">•</span>
                <span class="leading-relaxed">{{ q }}</span>
              </div>
            </div>

            <!-- Researcher: Search Query & Sources -->
            <div v-else-if="step.type === 'researcher'" class="space-y-3">
              <div v-if="step.content && typeof step.content === 'string' && step.content.includes('Searching')" class="text-sm text-amber-600 dark:text-amber-400 italic flex items-center gap-2 bg-amber-50 dark:bg-amber-900/20 p-2 rounded border border-amber-200 dark:border-amber-800/30">
                <Search class="w-3.5 h-3.5 shrink-0" />
                <span class="truncate">{{ step.content }}</span>
              </div>

              <div v-if="step.sources && step.sources.length > 0" class="mt-2">
                <button
                  @click.stop="toggleSources(step.id)"
                  class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors mb-2"
                >
                  <span>{{ step.sources.length }} sources found</span>
                  <component :is="expandedSources.has(step.id) ? ChevronUp : ChevronDown" class="w-3 h-3" />
                </button>

                <div v-show="expandedSources.has(step.id)" class="grid gap-2 animate-in fade-in slide-in-from-top-2 duration-200">
                  <a
                    v-for="(source, idx) in step.sources"
                    :key="idx"
                    :href="source.url"
                    target="_blank"
                    class="block p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:border-amber-400 dark:hover:border-amber-500/50 hover:bg-amber-50 dark:hover:bg-amber-900/10 transition-all group/link"
                  >
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-xs font-medium text-gray-700 dark:text-gray-300 truncate pr-4">{{ source.title }}</span>
                      <ExternalLink class="w-3 h-3 text-gray-400 dark:text-gray-500 group-hover/link:text-amber-500 transition-colors shrink-0" />
                    </div>
                    <div class="text-xs text-gray-400 dark:text-gray-500 truncate font-mono">{{ source.url }}</div>
                  </a>
                </div>
              </div>

              <div v-if="step.content && typeof step.content === 'string' && !step.content.includes('Searching')" class="text-sm text-gray-600 dark:text-gray-400">
                {{ step.content }}
              </div>
            </div>

            <!-- Reviewer: Feedback -->
            <div v-else-if="step.type === 'reviewer'" class="text-sm text-gray-700 dark:text-gray-300 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800/30 p-3 rounded-lg leading-relaxed break-words">
              <span class="text-purple-600 dark:text-purple-400 font-medium block mb-1 flex items-center gap-2">
                <BrainCircuit class="w-3 h-3" />
                <span>Feedback & Reflection</span>
                <Loader2 v-if="step.status === 'processing'" class="w-3 h-3 animate-spin ml-1" />
              </span>
              <span class="whitespace-pre-wrap">{{ step.content }}</span>
              <span v-if="step.status === 'processing'" class="inline-block w-1.5 h-4 bg-purple-500 ml-0.5 animate-pulse rounded-sm"></span>
            </div>

            <!-- Default Text -->
            <div v-else class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed break-words">
              <span class="whitespace-pre-wrap">{{ step.content }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Loading Indicator at bottom -->
      <div v-if="isLoading" class="flex gap-4 animate-pulse pt-2">
        <div class="w-8 h-8 rounded-lg bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 flex items-center justify-center shrink-0">
          <Loader2 class="w-4 h-4 text-gray-400 dark:text-gray-500 animate-spin" />
        </div>
        <div class="flex-1 py-1 space-y-2">
          <div class="h-2 bg-gray-200 dark:bg-gray-700 rounded w-24"></div>
          <div class="h-2 bg-gray-100 dark:bg-gray-800 rounded w-3/4"></div>
        </div>
      </div>

      <!-- Current phase message -->
      <div v-if="isLoading && progress" class="text-center py-2">
        <span class="text-xs text-gray-500 dark:text-gray-400 italic">{{ progress.message }}</span>
      </div>

    </div>
  </div>
</template>
