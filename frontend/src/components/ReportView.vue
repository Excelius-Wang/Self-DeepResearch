<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import { FileText, Download, Loader2, Printer } from 'lucide-vue-next'

const props = defineProps<{
  content: string
  isStreaming?: boolean
}>()

const md = new MarkdownIt({
  html: true, // Enable HTML for citation badges, but we'll sanitize it
  linkify: true,
  typographer: true
})

// Text Preprocessing Pipeline
const processText = (text: string) => {
  if (!text) return ''
  
  let processed = text

  // 1. Header Fixer: Auto-detect "1. Title" patterns and convert to Markdown headers
  // Only apply if the line doesn't already start with #
  processed = processed.replace(/^(?![#])(\d+\.\s+.+)$/gm, '## $1')
  processed = processed.replace(/^(?![#])(\d+\.\d+\s+.+)$/gm, '### $1')
  
  // 2. Citation Highlighter: Convert [Source N: Title] to HTML badges
  processed = processed.replace(
    /\[Source (\d+): ([^\]]+)\]/g, 
    '<span class="citation-badge">Source $1</span>'
  )

  return processed
}

const renderedContent = computed(() => {
  const processed = processText(props.content)
  const rawHtml = md.render(processed)
  
  // Sanitize HTML to prevent XSS
  return DOMPurify.sanitize(rawHtml, {
    ALLOWED_TAGS: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'strong', 'em', 'a', 'img', 'span', 'br', 'hr', 'table', 'thead', 'tbody', 'tr', 'th', 'td'],
    ALLOWED_ATTR: ['href', 'src', 'alt', 'class', 'title', 'target'],
  })
})

const contentRef = ref<HTMLElement | null>(null)
watch(() => props.content, () => {
  if (props.isStreaming && contentRef.value) {
    const { scrollTop, scrollHeight, clientHeight } = document.documentElement
    if (scrollHeight - scrollTop - clientHeight < 200) {
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
    }
  }
})

const handleExport = () => {
  window.print()
}

const handleDownloadMarkdown = () => {
  if (!props.content) return
  const blob = new Blob([props.content], { type: 'text/markdown' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `research-report-${new Date().toISOString().slice(0, 10)}.md`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl shadow-gray-200/50 dark:shadow-none border border-gray-100 dark:border-gray-700 overflow-hidden transition-all duration-500 print:shadow-none print:border-none ring-1 ring-black/5 dark:ring-white/5">
    <!-- Header -->
    <div class="bg-white/80 dark:bg-gray-800/80 backdrop-blur-md border-b border-gray-100 dark:border-gray-700 px-6 sm:px-8 py-4 flex flex-col sm:flex-row items-start sm:items-center justify-between sticky top-16 z-10 no-print gap-4">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-blue-600 rounded-lg shadow-sm shadow-blue-200 dark:shadow-none">
          <FileText class="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 class="text-lg font-bold text-gray-900 dark:text-gray-100 tracking-tight leading-none">Research Report</h3>
          <span v-if="isStreaming" class="text-xs text-blue-600 dark:text-blue-400 font-medium flex items-center gap-1 mt-1">
            <Loader2 class="w-3 h-3 animate-spin" />
            Generating...
          </span>
        </div>
      </div>
      <div class="flex gap-2 w-full sm:w-auto">
        <button 
          class="flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-all border border-transparent hover:border-blue-100 dark:hover:border-blue-800 bg-gray-50 dark:bg-gray-700/50 sm:bg-transparent"
          @click="handleExport"
          :disabled="!content"
        >
          <Printer class="w-4 h-4" />
          Print / PDF
        </button>
        <button 
          class="flex-1 sm:flex-none flex items-center justify-center gap-2 px-4 py-2 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-all border border-transparent hover:border-blue-100 dark:hover:border-blue-800 bg-gray-50 dark:bg-gray-700/50 sm:bg-transparent"
          @click="handleDownloadMarkdown"
          :disabled="!content"
        >
          <Download class="w-4 h-4" />
          Download MD
        </button>
      </div>
    </div>

    <!-- Content -->
    <div id="report-content" class="p-8 lg:p-12 min-h-[600px] print:p-0">
      <!-- Skeleton Loading -->
      <div v-if="!content && isStreaming" class="animate-pulse space-y-8 max-w-3xl mx-auto py-8 no-print">
        <div class="space-y-4">
          <div class="h-8 bg-gray-200 dark:bg-gray-700 rounded-lg w-3/4"></div>
          <div class="h-4 bg-gray-100 dark:bg-gray-600 rounded w-1/2"></div>
        </div>
        <div class="space-y-3">
          <div class="h-4 bg-gray-100 dark:bg-gray-600 rounded"></div>
          <div class="h-4 bg-gray-100 dark:bg-gray-600 rounded"></div>
          <div class="h-4 bg-gray-100 dark:bg-gray-600 rounded w-5/6"></div>
        </div>
        <div class="space-y-3 pt-4">
          <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
          <div class="h-4 bg-gray-100 dark:bg-gray-600 rounded"></div>
          <div class="h-4 bg-gray-100 dark:bg-gray-600 rounded"></div>
          <div class="h-4 bg-gray-100 dark:bg-gray-600 rounded w-4/5"></div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!content" class="flex flex-col items-center justify-center h-full text-gray-400 dark:text-gray-500 py-32 space-y-4 no-print">
        <div class="w-16 h-16 bg-gray-50 dark:bg-gray-700/50 rounded-2xl flex items-center justify-center">
          <FileText class="w-8 h-8 text-gray-300 dark:text-gray-600" />
        </div>
        <p class="text-sm font-medium">Report will appear here</p>
      </div>
      
      <!-- Actual Content -->
      <div 
        v-else 
        ref="contentRef"
        class="mx-auto max-w-4xl pb-32
               prose prose-lg prose-slate dark:prose-invert
               prose-headings:font-bold prose-headings:tracking-tight prose-headings:text-slate-900 dark:prose-headings:text-slate-100
               prose-h1:text-4xl prose-h1:mb-10 prose-h1:mt-4
               prose-h2:text-2xl prose-h2:mt-16 prose-h2:mb-6 prose-h2:pb-2 prose-h2:border-b prose-h2:border-gray-100 dark:prose-h2:border-gray-700
               prose-h3:text-xl prose-h3:mt-8 prose-h3:mb-4
               prose-p:text-slate-600 dark:prose-p:text-slate-300 prose-p:leading-loose prose-p:mb-8
               prose-a:text-blue-600 dark:prose-a:text-blue-400 hover:prose-a:text-blue-800 dark:hover:prose-a:text-blue-300 prose-a:no-underline hover:prose-a:underline
               prose-blockquote:border-l-4 prose-blockquote:border-blue-500 prose-blockquote:bg-blue-50/30 dark:prose-blockquote:bg-blue-900/20 prose-blockquote:py-4 prose-blockquote:px-6 prose-blockquote:rounded-r-lg prose-blockquote:not-italic prose-blockquote:text-slate-700 dark:prose-blockquote:text-slate-300
               prose-li:text-slate-600 dark:prose-li:text-slate-300 prose-li:leading-loose
               prose-img:rounded-xl prose-img:shadow-lg"
      >
        <div v-html="renderedContent"></div>
        
        <!-- Cursor for streaming effect -->
        <span v-if="isStreaming" class="inline-block w-2 h-5 bg-blue-600 dark:bg-blue-400 ml-1 animate-pulse align-middle rounded-full no-print"></span>
      </div>
    </div>
  </div>
</template>
