<script setup lang="ts">
import { ref, computed, defineAsyncComponent } from 'vue'
import { fetchEventSource } from '@microsoft/fetch-event-source'
import { Menu, X, StopCircle } from 'lucide-vue-next'
import ResearchForm from './components/ResearchForm.vue'
import ThemeToggle from './components/ThemeToggle.vue'
import Toast from './components/Toast.vue'
import type { ThoughtStep, ResearchProgress } from './types'
import { API_BASE_URL } from './config'
import { useToast } from './composables/useToast'

// Lazy load heavy components
const ThoughtChain = defineAsyncComponent(() => import('./components/ThoughtChain.vue'))
const ReportView = defineAsyncComponent(() => import('./components/ReportView.vue'))
const HistorySidebar = defineAsyncComponent(() => import('./components/HistorySidebar.vue'))

const toast = useToast()

const steps = ref<ThoughtStep[]>([])
const report = ref<string>('')
const isLoading = ref(false)
const hasStarted = ref(false)
const abortController = ref<AbortController | null>(null)
const desktopSidebarRef = ref<{ refresh: () => void } | null>(null)
const mobileSidebarRef = ref<{ refresh: () => void } | null>(null)
const isSidebarOpen = ref(false)
const currentSessionId = ref<string | null>(null)
const progress = ref<ResearchProgress | null>(null)
const queuePosition = ref<number | null>(null)

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const refreshSidebars = () => {
  desktopSidebarRef.value?.refresh()
  mobileSidebarRef.value?.refresh()
}

const cancelResearch = async () => {
  // First abort the fetch connection
  if (abortController.value) {
    abortController.value.abort()
    abortController.value = null
  }

  // Then call backend cancel endpoint if we have a session ID
  if (currentSessionId.value) {
    try {
      await fetch(`${API_BASE_URL}/research/${currentSessionId.value}/cancel`, {
        method: 'POST'
      })
    } catch (e) {
      // Ignore errors on cancel
    }
    currentSessionId.value = null
  }

  isLoading.value = false
  queuePosition.value = null
  progress.value = null
  toast.info('Research cancelled')
}

const handleResearch = async (task: string, maxLoops: number = 3) => {
  if (isLoading.value) return

  // Reset state
  steps.value = []
  report.value = ''
  isLoading.value = true
  hasStarted.value = true
  progress.value = null
  queuePosition.value = null
  currentSessionId.value = null

  if (abortController.value) {
    abortController.value.abort()
  }
  abortController.value = new AbortController()

  try {
    await fetchEventSource(`${API_BASE_URL}/research/stream`, {
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

          // Handle session start
          if (data.type === 'session_start') {
            currentSessionId.value = data.session_id
          }
          // Handle queue position
          else if (data.type === 'queued') {
            queuePosition.value = data.position
            currentSessionId.value = data.session_id
            toast.info(`You are #${data.position} in queue. Please wait...`)
          }
          // Handle cancelled
          else if (data.type === 'cancelled') {
            isLoading.value = false
            queuePosition.value = null
            progress.value = null
          }
          // Handle progress updates
          else if (data.type === 'progress') {
            progress.value = {
              currentLoop: data.current_loop,
              maxLoops: data.max_loops,
              phase: data.phase,
              message: data.message
            }
            queuePosition.value = null // Clear queue position once research starts
          }
          else if (data.type === 'log') {
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
          } else if (data.type === 'reviewer_chunk') {
            // Find existing reviewer step or create streaming placeholder
            const existingReviewerStep = steps.value.find(
              s => s.type === 'reviewer' && s.status === 'processing'
            )
            if (existingReviewerStep) {
              existingReviewerStep.content = (existingReviewerStep.content as string) + data.content
            } else {
              steps.value.push({
                id: `review-streaming-${now}`,
                type: 'reviewer',
                title: 'Reviewing Findings',
                content: data.content,
                status: 'processing',
                timestamp: now
              })
            }
          } else if (data.type === 'reviewer') {
            // Remove streaming placeholder and add final result
            const streamingIdx = steps.value.findIndex(
              s => s.type === 'reviewer' && s.status === 'processing'
            )
            if (streamingIdx !== -1) {
              steps.value.splice(streamingIdx, 1)
            }
            steps.value.push({
              id: `review-${now}`,
              type: 'reviewer',
              title: data.has_more_queries ? 'Needs More Research' : 'Reviewing Findings',
              content: data.feedback,
              status: 'completed',
              timestamp: now
            })
          } else if (data.type === 'report_chunk') {
            report.value += data.content
          } else if (data.type === 'saved') {
            // Refresh sidebar when saved
            refreshSidebars()
            toast.success('Research saved successfully')
          } else if (data.type === 'done') {
            isLoading.value = false
            progress.value = null
            currentSessionId.value = null
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
            progress.value = null
            toast.error(data.content || 'Research encountered an error')
          }
        } catch (e) {
          console.error('Failed to parse SSE message', e)
        }
      },
      onerror(err) {
        isLoading.value = false
        progress.value = null
        toast.error('Connection lost. Please try again.')
        throw err
      }
    })
  } catch (e: unknown) {
    if (e instanceof Error && e.name === 'AbortError') {
      // User cancelled, already handled
      return
    }
    console.error('Research failed', e)
    isLoading.value = false
    progress.value = null
    toast.error('Failed to start research. Please check your connection.')
  }
}

const loadHistory = async (id: number) => {
  if (isLoading.value) return

  try {
    const res = await fetch(`${API_BASE_URL}/history/${id}`)
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

      // Handle notes from history - parse notes_json if needed
      const notes = data.notes_json ? JSON.parse(data.notes_json) : (data.notes || [])
      if (notes && notes.length > 0) {
        steps.value.push({
           id: `notes-${id}`,
           type: 'researcher',
           title: 'Referenced Sources',
           content: `Loaded ${notes.length} sources from history`,
           sources: notes,
           status: 'completed',
           timestamp: new Date(data.created_at).getTime()
        })
      }
    } else {
      toast.error('Failed to load history')
    }
  } catch (e) {
    console.error('Failed to load history', e)
    toast.error('Failed to load history. Please check your connection.')
  }
}

const continueResearch = (topic: string) => {
  handleResearch(`Based on previous research, explore in more depth: ${topic}`, 3)
}

// 收集所有 sources 数据传递给 ReportView
const allSources = computed(() => {
  return steps.value
    .filter(s => s.type === 'researcher' && s.sources)
    .flatMap(s => s.sources || [])
})
</script>

<template>
  <div class="flex h-screen bg-gray-50 dark:bg-gray-900 overflow-hidden font-sans text-gray-900 dark:text-gray-100 transition-colors duration-300">
    <!-- Toast Notifications -->
    <Toast />

    <!-- Desktop Sidebar -->
    <HistorySidebar
      ref="desktopSidebarRef"
      @select="loadHistory"
      class="flex-shrink-0 w-64 border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 hidden md:flex z-30"
    />

    <!-- Mobile Sidebar Drawer -->
    <div v-if="isSidebarOpen" class="fixed inset-0 z-50 flex md:hidden">
      <!-- Backdrop -->
      <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="toggleSidebar"></div>
      <!-- Drawer Content -->
      <div class="relative w-72 bg-white dark:bg-gray-900 h-full shadow-2xl flex flex-col animate-in slide-in-from-left duration-300">
        <div class="h-16 px-4 flex justify-between items-center border-b border-gray-200 dark:border-gray-800">
          <span class="font-semibold text-gray-800 dark:text-gray-100">History</span>
          <button
            @click="toggleSidebar"
            class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
            aria-label="Close sidebar"
          >
            <X class="w-5 h-5 text-gray-500 dark:text-gray-400" />
          </button>
        </div>
        <HistorySidebar
          ref="mobileSidebarRef"
          @select="loadHistory"
          class="flex-1 overflow-hidden"
        />
      </div>
    </div>

    <!-- Main Content Wrapper -->
    <div class="flex-1 flex flex-col min-w-0 h-full relative">
      <!-- Header -->
      <header class="h-16 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 flex-shrink-0 z-20">
        <div class="h-full max-w-[1400px] mx-auto px-4 sm:px-6 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <!-- Mobile Menu Button -->
            <button
              @click="toggleSidebar"
              class="md:hidden p-2 -ml-2 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              aria-label="Open history sidebar"
            >
              <Menu class="w-5 h-5" />
            </button>

            <div class="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center text-white text-sm font-bold shadow-md">
              DR
            </div>
            <h1 class="text-lg font-semibold text-gray-900 dark:text-white">DeepResearch</h1>
          </div>

          <div class="flex items-center gap-2">
            <!-- Queue Position -->
            <span v-if="queuePosition" class="text-sm text-amber-600 dark:text-amber-400 font-medium px-2 py-1 bg-amber-50 dark:bg-amber-900/20 rounded-lg">
              Queue: #{{ queuePosition }}
            </span>
            <!-- Cancel Button -->
            <button
              v-if="isLoading"
              @click="cancelResearch"
              class="flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-colors"
              aria-label="Cancel research"
            >
              <StopCircle class="w-4 h-4" />
              <span class="hidden sm:inline">Cancel</span>
            </button>
            <ThemeToggle />
          </div>
        </div>
      </header>

      <!-- Main Content -->
      <main class="flex-1 overflow-y-auto">
        <div class="max-w-[1400px] mx-auto px-4 sm:px-6 py-6">
          <!-- Hero Section -->
          <section :class="[hasStarted ? 'pb-6' : 'py-16 sm:py-24']" class="transition-all duration-500">
            <div v-if="!hasStarted" class="text-center mb-8 space-y-4">
              <h2 class="text-3xl sm:text-4xl font-bold tracking-tight text-gray-900 dark:text-white">
                What would you like to research?
              </h2>
              <p class="text-base text-gray-500 dark:text-gray-400 max-w-xl mx-auto">
                Our AI agent will plan, search, analyze, and write a comprehensive report for you.
              </p>
            </div>

            <div :class="[hasStarted ? 'max-w-7xl' : 'max-w-2xl']" class="mx-auto transition-all duration-500">
              <ResearchForm @submit="handleResearch" :is-loading="isLoading" />
            </div>
          </section>

          <!-- Results Section -->
          <div v-if="hasStarted" class="max-w-7xl mx-auto space-y-6 pb-12">
            <!-- Thought Chain (Process) -->
            <ThoughtChain :steps="steps" :is-loading="isLoading" :progress="progress" />

            <!-- Report (Result) -->
            <ReportView :content="report" :is-streaming="isLoading" :sources="allSources" @continue-research="continueResearch" />
          </div>

          <!-- Footer - 仅在首页显示 -->
          <footer v-if="!hasStarted" class="text-center pt-12">
            <p class="text-xs text-gray-400 dark:text-gray-600">
              Powered by LangGraph & Tavily
            </p>
          </footer>
        </div>
      </main>
    </div>
  </div>
</template>
