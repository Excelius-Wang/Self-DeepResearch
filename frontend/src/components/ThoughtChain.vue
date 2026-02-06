<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { 
  Loader2, 
  BrainCircuit, 
  Search, 
  FileText, 
  ListTodo,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Maximize2,
  Minimize2
} from 'lucide-vue-next'
import type { ThoughtStep } from '../types'

const props = defineProps<{
  steps: ThoughtStep[]
  isLoading: boolean
}>()

const containerRef = ref<HTMLElement | null>(null)
const expandedSources = ref<Set<string>>(new Set())
const isExpanded = ref(true)

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

const getBgColor = (type: string) => {
  switch (type) {
    case 'planner': return 'bg-blue-500/10 border-blue-500/20 text-blue-400'
    case 'researcher': return 'bg-amber-500/10 border-amber-500/20 text-amber-400'
    case 'reviewer': return 'bg-purple-500/10 border-purple-500/20 text-purple-400'
    default: return 'bg-slate-800 border-slate-700 text-slate-400'
  }
}
</script>

<template>
  <div class="w-full bg-slate-950 dark:bg-slate-950 rounded-xl overflow-hidden border border-slate-800/50 dark:border-slate-800/50 shadow-2xl flex flex-col transition-all duration-500">
    <!-- Header -->
    <div 
      class="px-5 py-4 border-b border-slate-800 dark:border-slate-800 bg-slate-900/50 dark:bg-slate-900/50 flex items-center justify-between shrink-0 cursor-pointer hover:bg-slate-900 transition-colors"
      @click="toggleExpand"
    >
      <div class="flex items-center gap-2.5 text-slate-200 dark:text-slate-200">
        <div class="relative">
          <BrainCircuit class="w-5 h-5 text-blue-400" />
          <div v-if="isLoading" class="absolute -top-1 -right-1 w-2 h-2 bg-blue-500 rounded-full animate-ping"></div>
        </div>
        <span class="font-semibold tracking-tight">Thinking Process</span>
      </div>
      <div class="flex items-center gap-4">
        <div class="text-xs font-mono text-slate-500 dark:text-slate-500">
          {{ steps.length }} steps processed
        </div>
        <button class="text-slate-500 hover:text-slate-300 transition-colors">
          <component :is="isExpanded ? ChevronUp : ChevronDown" class="w-5 h-5" />
        </button>
      </div>
    </div>
    
    <!-- Content -->
    <div 
      v-show="isExpanded"
      ref="containerRef" 
      class="overflow-y-auto p-5 space-y-6 scrollbar-thin scroll-smooth transition-all duration-500"
      :class="{'max-h-[500px]': true, 'min-h-[200px]': steps.length > 0}"
    >
      <div v-if="steps.length === 0" class="flex flex-col items-center justify-center py-12 text-slate-600 dark:text-slate-600 space-y-3">
        <div class="w-12 h-12 rounded-full bg-slate-900 dark:bg-slate-900 flex items-center justify-center">
          <BrainCircuit class="w-6 h-6 opacity-50" />
        </div>
        <p class="text-sm">Waiting for research task...</p>
      </div>
      
      <div 
        v-for="step in steps" 
        :key="step.id"
        class="animate-in fade-in slide-in-from-bottom-4 duration-500"
      >
        <!-- (Step content remains same, just ensuring correct nesting) -->
        <div class="flex gap-4 group">
          <!-- Timeline Line -->
          <div class="flex flex-col items-center">
            <div 
              class="w-8 h-8 rounded-lg flex items-center justify-center border shadow-lg transition-all duration-300 z-10 bg-slate-950 dark:bg-slate-950"
              :class="getBgColor(step.type)"
            >
              <component :is="getIcon(step.type)" class="w-4 h-4" />
            </div>
            <div class="w-0.5 flex-1 bg-slate-800 dark:bg-slate-800 my-2 group-last:hidden"></div>
          </div>

          <!-- Card Content -->
          <div class="flex-1 pb-4 min-w-0">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-slate-200 dark:text-slate-200 truncate pr-2">{{ step.title }}</span>
              <span class="text-xs font-mono text-slate-600 dark:text-slate-600 shrink-0">
                {{ new Date(step.timestamp).toLocaleTimeString([], {hour12: false, minute:'2-digit', second:'2-digit'}) }}
              </span>
            </div>

            <!-- Planner: Sub Queries List -->
            <div v-if="step.type === 'planner' && Array.isArray(step.content)" class="space-y-2">
              <div v-for="(q, idx) in step.content" :key="idx" class="flex items-start gap-2 text-sm text-slate-400 dark:text-slate-400 bg-slate-900/50 dark:bg-slate-900/50 p-2.5 rounded-lg border border-slate-800/50 dark:border-slate-800/50">
                <span class="text-blue-500/70 mt-0.5">•</span>
                <span class="leading-relaxed">{{ q }}</span>
              </div>
            </div>

            <!-- Researcher: Search Query & Sources -->
            <div v-else-if="step.type === 'researcher'" class="space-y-3">
              <div v-if="step.content" class="text-sm text-amber-200/80 dark:text-amber-200/80 italic flex items-center gap-2 bg-amber-500/5 dark:bg-amber-500/5 p-2 rounded border border-amber-500/10 dark:border-amber-500/10">
                <Search class="w-3.5 h-3.5 shrink-0" />
                <span class="truncate">Searching: "{{ step.content }}"</span>
              </div>
              
              <div v-if="step.sources && step.sources.length > 0" class="mt-2">
                <button 
                  @click="toggleSources(step.id)"
                  class="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-500 hover:text-slate-300 dark:hover:text-slate-300 transition-colors mb-2"
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
                    class="block p-3 rounded-lg bg-slate-900 dark:bg-slate-900 border border-slate-800 dark:border-slate-800 hover:border-amber-500/30 hover:bg-slate-800 dark:hover:bg-slate-800 transition-all group/link"
                  >
                    <div class="flex items-center justify-between mb-1">
                      <span class="text-xs font-medium text-slate-300 dark:text-slate-300 truncate pr-4">{{ source.title }}</span>
                      <ExternalLink class="w-3 h-3 text-slate-600 dark:text-slate-600 group-hover/link:text-amber-500 transition-colors shrink-0" />
                    </div>
                    <div class="text-xs text-slate-500 dark:text-slate-500 truncate font-mono">{{ source.url }}</div>
                  </a>
                </div>
              </div>
            </div>

            <!-- Reviewer: Feedback -->
            <div v-else-if="step.type === 'reviewer'" class="text-sm text-slate-300 dark:text-slate-300 bg-purple-500/5 dark:bg-purple-500/5 border border-purple-500/10 dark:border-purple-500/10 p-3 rounded-lg leading-relaxed">
              <span class="text-purple-400 font-medium block mb-1 flex items-center gap-2">
                <BrainCircuit class="w-3 h-3" />
                Feedback & Reflection
              </span>
              {{ step.content }}
            </div>

            <!-- Default Text -->
            <div v-else class="text-sm text-slate-400 dark:text-slate-400 leading-relaxed">
              {{ step.content }}
            </div>
          </div>
        </div>
      </div>
      
      <!-- Loading Indicator at bottom -->
      <div v-if="isLoading" class="flex gap-4 animate-pulse pt-2">
        <div class="w-8 h-8 rounded-lg bg-slate-900 dark:bg-slate-900 border border-slate-800 dark:border-slate-800 flex items-center justify-center shrink-0">
          <Loader2 class="w-4 h-4 text-slate-600 dark:text-slate-600 animate-spin" />
        </div>
        <div class="flex-1 py-1 space-y-2">
          <div class="h-2 bg-slate-800 dark:bg-slate-800 rounded w-24"></div>
          <div class="h-2 bg-slate-900 dark:bg-slate-900 rounded w-3/4"></div>
        </div>
      </div>

    </div>
  </div>
</template>
