<script setup lang="ts">
import { ref } from 'vue'
import { fetchEventSource } from '@microsoft/fetch-event-source'
import { Menu, X } from 'lucide-vue-next'
import ResearchForm from './components/ResearchForm.vue'
import ThoughtChain from './components/ThoughtChain.vue'
import ReportView from './components/ReportView.vue'
import HistorySidebar from './components/HistorySidebar.vue'
import ThemeToggle from './components/ThemeToggle.vue'
import type { ThoughtStep } from './types'

const steps = ref<ThoughtStep[]>([])
const report = ref<string>('')
const isLoading = ref(false)
const hasStarted = ref(false)
const abortController = ref<AbortController | null>(null)
const historySidebar = ref<InstanceType<typeof HistorySidebar> | null>(null)
const isSidebarOpen = ref(false)

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const handleResearch = async (task: string, maxLoops: number = 3) => {
  if (isLoading.value) return

  // Reset state
  steps.value = []
  report.value = ''
  isLoading.value = true
  hasStarted.value = true
  
  if (abortController.value) {
    abortController.value.abort()
  }
  abortController.value = new AbortController()
  
  try {
    await fetchEventSource('http://localhost:8000/research/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ task, max_loops: maxLoops }),
      signal: abortController.value.signal,
      openWhenHidden: true,
      onmessage(msg) {
        if (!msg.data) return
        
        try {
          const data = JSON.parse(msg.data)
          const now = Date.now()
          
          if (data.type === 'log') {
             // Legacy log support
          } else if (data.type === 'planner') {
            steps.value.push({
              id: `plan-${now}`,
              type: 'planner',
              title: 'Planning Research Strategy',
              content: data.content,
              status: 'completed',
              timestamp: now
            })
          } else if (data.type === 'researcher') {
            if (data.action === 'searching') {
              steps.value.push({
                id: `search-${now}`,
                type: 'researcher',
                title: 'Searching Information',
                content: data.query,
                status: 'processing',
                timestamp: now
              })
            } else if (data.action === 'notes') {
              steps.value.push({
                id: `notes-${now}`,
                type: 'researcher',
                title: 'Reading & Summarizing',
                content: `Processed ${data.data.length} new sources`,
                sources: data.data,
                status: 'completed',
                timestamp: now
              })
            }
          } else if (data.type === 'reviewer') {
            steps.value.push({
              id: `review-${now}`,
              type: 'reviewer',
              title: 'Reviewing Findings',
              content: data.feedback,
              status: 'completed',
              timestamp: now
            })
          } else if (data.type === 'report_chunk') {
            report.value += data.content
          } else if (data.type === 'saved') {
            // Refresh sidebar when saved
            historySidebar.value?.refresh()
          } else if (data.type === 'done') {
            isLoading.value = false
          } else if (data.type === 'error') {
            steps.value.push({
              id: `error-${now}`,
              type: 'error',
              title: 'Error Occurred',
              content: data.content,
              status: 'error',
              timestamp: now
            })
            isLoading.value = false
          }
        } catch (e) {
          console.error('Failed to parse SSE message', e)
        }
      },
      onerror(err) {
        isLoading.value = false
        throw err 
      }
    })
  } catch (e) {
    console.error('Research failed', e)
    isLoading.value = false
  }
}

const loadHistory = async (id: number) => {
  if (isLoading.value) return
  
  try {
    const res = await fetch(`http://localhost:8000/history/${id}`)
    if (res.ok) {
      const data = await res.json()
      report.value = data.report_content
      hasStarted.value = true
      // Close mobile sidebar on selection
      isSidebarOpen.value = false
      
      // Clear previous steps and add summary
      steps.value = []
      steps.value.push({
         id: `history-${id}`,
         type: 'planner',
         title: 'Research History Loaded',
         content: [`Task: ${data.task}`],
         status: 'completed',
         timestamp: new Date(data.created_at).getTime()
      })
      
      if (data.notes) {
        steps.value.push({
           id: `notes-${id}`,
           type: 'researcher',
           title: 'Referenced Sources',
           content: `Loaded ${data.notes.length} sources from history`,
           sources: data.notes,
           status: 'completed',
           timestamp: new Date(data.created_at).getTime()
        })
      }
    }
  } catch (e) {
    console.error('Failed to load history', e)
  }
}
</script>

<template>
  <div class="flex h-screen bg-gray-50 dark:bg-gray-900 overflow-hidden font-sans text-gray-900 dark:text-gray-100 transition-colors duration-300">
    <!-- Desktop Sidebar -->
    <HistorySidebar 
      ref="historySidebar" 
      @select="loadHistory" 
      class="flex-shrink-0 w-72 border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 hidden md:flex shadow-[4px_0_24px_rgba(0,0,0,0.02)] z-30" 
    />

    <!-- Mobile Sidebar Drawer -->
    <div v-if="isSidebarOpen" class="fixed inset-0 z-50 flex md:hidden">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="toggleSidebar"></div>
      <!-- Drawer Content -->
      <div class="relative w-72 bg-white dark:bg-gray-900 h-full shadow-2xl flex flex-col animate-in slide-in-from-left duration-300">
        <div class="p-4 flex justify-between items-center border-b border-gray-200 dark:border-gray-800">
          <span class="font-bold text-lg dark:text-white">History</span>
          <button @click="toggleSidebar" class="p-1 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800">
            <X class="w-6 h-6 text-gray-500 dark:text-gray-400" />
          </button>
        </div>
        <HistorySidebar 
          ref="historySidebar" 
          @select="loadHistory" 
          class="flex-1 overflow-hidden" 
        />
      </div>
    </div>
    
    <!-- Main Content Wrapper -->
    <div class="flex-1 flex flex-col min-w-0 h-full relative">
      <header class="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-800 sticky top-0 z-20 transition-all duration-300">
        <div class="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <!-- Mobile Menu Button -->
            <button @click="toggleSidebar" class="md:hidden p-2 -ml-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
              <Menu class="w-6 h-6" />
            </button>
            
            <div class="w-9 h-9 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/20">
              DR
            </div>
            <h1 class="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400">DeepResearch</h1>
          </div>
          <div class="flex items-center gap-4">
            <div class="hidden sm:block text-sm font-medium text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-3 py-1 rounded-full">
              Powered by LangGraph & Tavily
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 scrollbar-thin dark:scrollbar-thumb-gray-700 dark:scrollbar-track-gray-900">
        <div class="max-w-[1600px] mx-auto space-y-8 h-full">
          <section :class="{'py-20': !hasStarted, 'py-8': hasStarted}" class="transition-all duration-700 ease-in-out">
            <div v-if="!hasStarted" class="text-center mb-12 space-y-6 animate-in fade-in slide-in-from-bottom-8 duration-700">
              <h2 class="text-5xl font-extrabold tracking-tight text-gray-900 dark:text-white sm:text-6xl bg-clip-text text-transparent bg-gradient-to-b from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 pb-2">
                What do you want to research?
              </h2>
              <p class="text-xl text-gray-500 dark:text-gray-400 max-w-2xl mx-auto leading-relaxed">
                Our autonomous agent will plan, search, reflect, and write a comprehensive report for you.
              </p>
            </div>
            
            <div :class="{'max-w-3xl mx-auto': !hasStarted, 'max-w-4xl mx-auto': hasStarted}" class="transition-all duration-500">
              <ResearchForm @submit="handleResearch" :is-loading="isLoading" />
            </div>
          </section>

          <div v-if="hasStarted" class="max-w-4xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-8 duration-700 pb-20">
            
            <!-- Thought Chain (Process) -->
            <div class="transition-all duration-500">
              <ThoughtChain :steps="steps" :is-loading="isLoading" />
            </div>

            <!-- Report (Result) -->
            <div class="transition-all duration-500">
              <ReportView :content="report" :is-streaming="isLoading" />
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>
