<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { Loader2, CheckCircle2, Terminal } from 'lucide-vue-next'

interface LogItem {
  type: 'log' | 'error'
  content: string
  timestamp: number
}

const props = defineProps<{
  logs: LogItem[]
  isLoading: boolean
}>()

const logContainer = ref<HTMLElement | null>(null)

// Auto-scroll to bottom
watch(() => props.logs.length, async () => {
  await nextTick()
  if (logContainer.value) {
    logContainer.value.scrollTop = logContainer.value.scrollHeight
  }
})
</script>

<template>
  <div class="w-full bg-slate-900 rounded-xl overflow-hidden border border-slate-800 shadow-xl flex flex-col h-[500px]">
    <div class="px-4 py-3 bg-slate-950 border-b border-slate-800 flex items-center justify-between">
      <div class="flex items-center gap-2 text-slate-400">
        <Terminal class="w-4 h-4" />
        <span class="text-sm font-medium">Research Logs</span>
      </div>
      <div v-if="isLoading" class="flex items-center gap-2 text-blue-400 text-xs">
        <Loader2 class="w-3 h-3 animate-spin" />
        <span>Processing...</span>
      </div>
      <div v-else class="flex items-center gap-2 text-green-400 text-xs">
        <CheckCircle2 class="w-3 h-3" />
        <span>Ready</span>
      </div>
    </div>
    
    <div ref="logContainer" class="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-sm">
      <div v-if="logs.length === 0" class="text-slate-600 italic text-center mt-20">
        Waiting for tasks...
      </div>
      
      <div 
        v-for="(log, index) in logs" 
        :key="index"
        class="animate-in fade-in slide-in-from-bottom-2 duration-300"
      >
        <div class="flex gap-3">
          <span class="text-slate-600 shrink-0">
            {{ new Date(log.timestamp).toLocaleTimeString([], {hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit'}) }}
          </span>
          <span 
            :class="{
              'text-slate-300': log.type === 'log',
              'text-red-400': log.type === 'error',
              'text-blue-300': log.content.includes('Planner'),
              'text-yellow-300': log.content.includes('Researcher'),
              'text-purple-300': log.content.includes('Reviewer'),
              'text-green-300': log.content.includes('Reporter'),
            }"
          >
            {{ log.content }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
