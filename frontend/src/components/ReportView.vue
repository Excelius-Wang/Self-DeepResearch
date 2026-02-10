<script setup lang="ts">
import { computed, ref, watch, onMounted, nextTick } from 'vue'
import MarkdownIt from 'markdown-it'
import DOMPurify from 'dompurify'
import { FileText, Download, Loader2, Printer, Search, List } from 'lucide-vue-next'
import { useCitations, type Citation } from '../composables/useCitations'
import type { Source } from '../types'

const props = defineProps<{
  content: string
  isStreaming?: boolean
  sources?: Source[]
}>()

const emit = defineEmits<{
  (e: 'continue-research', topic: string): void
}>()

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

// 引用系统
const contentRef = computed(() => props.content)
const sourcesRef = computed(() => props.sources || [])
const { citations, hasCitations } = useCitations(contentRef, sourcesRef)

// 创建引用映射用于快速查找
const citationMap = computed(() => {
  const map = new Map<number, Citation>()
  citations.value.forEach(c => map.set(c.index, c))
  return map
})

// Text Preprocessing Pipeline
const processText = (text: string) => {
  if (!text) return ''

  let processed = text

  // 修正非标准 Source 引用格式: [Source N(url)] → 上标引用徽章
  // 匹配 [Source 数字(URL)] 或 [Source 数字 (URL)] 格式
  // 添加 data-* 属性用于 tooltip
  processed = processed.replace(
    /\[Source\s*(\d+)\s*\(([^)]+)\)\]/gi,
    (_, index, url) => {
      const citation = citationMap.value.get(parseInt(index, 10))
      const title = citation?.title || `Source ${index}`
      const domain = citation?.domain || ''
      return `<sup><a href="${url}" target="_blank" rel="noopener" class="citation-link" data-citation-index="${index}" data-citation-title="${title.replace(/"/g, '&quot;')}" data-citation-domain="${domain}" title="${title}">[${index}]</a></sup>`
    }
  )

  // 保留旧格式支持: [Source N: Title]
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
    ALLOWED_TAGS: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'strong', 'em', 'a', 'img', 'span', 'br', 'hr', 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'sup', 'sub'],
    ALLOWED_ATTR: ['href', 'src', 'alt', 'class', 'title', 'target', 'rel', 'id', 'data-citation-index', 'data-citation-title', 'data-citation-domain'],
  })
})

// TOC 目录系统
interface TocItem {
  id: string
  text: string
  level: number
}

const tocItems = ref<TocItem[]>([])
const showToc = ref(false)
const articleRef = ref<HTMLElement | null>(null)

// 提取标题生成 TOC
const extractToc = () => {
  if (!articleRef.value) return

  const headings = articleRef.value.querySelectorAll('h1, h2, h3')
  const items: TocItem[] = []

  headings.forEach((heading, index) => {
    const tagChar = heading.tagName[1]
    if (!tagChar) return
    const level = parseInt(tagChar)
    const text = heading.textContent || ''
    const id = `heading-${index}`

    // 为标题添加 ID
    heading.id = id

    items.push({ id, text, level })
  })

  tocItems.value = items
}

// 监听内容变化重新提取 TOC
watch(() => props.content, async () => {
  await nextTick()
  extractToc()

  // 流式输出时的自动滚动
  if (props.isStreaming && articleRef.value) {
    const { scrollTop, scrollHeight, clientHeight } = document.documentElement
    if (scrollHeight - scrollTop - clientHeight < 200) {
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
    }
  }
})

onMounted(() => {
  nextTick(() => extractToc())
})

// 点击 TOC 跳转
const scrollToHeading = (id: string) => {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

const toggleToc = () => {
  showToc.value = !showToc.value
}

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

const continueResearchInput = ref('')
const showContinueInput = ref(false)

const handleContinueResearch = () => {
  if (continueResearchInput.value.trim()) {
    emit('continue-research', continueResearchInput.value.trim())
    continueResearchInput.value = ''
    showContinueInput.value = false
  }
}

const toggleContinueInput = () => {
  showContinueInput.value = !showContinueInput.value
  if (showContinueInput.value) {
    // Auto focus after toggle
    setTimeout(() => {
      const input = document.getElementById('continue-research-input')
      input?.focus()
    }, 100)
  }
}
</script>

<template>
  <div class="report-container bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden transition-all duration-300">
    <!-- Header -->
    <div class="report-header bg-gray-50 dark:bg-gray-800/90 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <div class="p-2 bg-blue-600 rounded-lg">
          <FileText class="w-5 h-5 text-white" />
        </div>
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Research Report</h3>
          <span v-if="isStreaming" class="text-xs text-blue-600 dark:text-blue-400 font-medium flex items-center gap-1 mt-0.5">
            <Loader2 class="w-3 h-3 animate-spin" />
            Generating...
          </span>
        </div>
      </div>
      <div class="flex gap-2 w-full sm:w-auto">
        <!-- TOC Toggle Button -->
        <button
          v-if="content && tocItems.length > 0"
          class="btn-tooltip flex-1 sm:flex-none flex items-center justify-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
          :class="{ 'bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400': showToc }"
          @click="toggleToc"
          data-tooltip="Toggle table of contents"
        >
          <List class="w-4 h-4" />
          <span class="hidden sm:inline">TOC</span>
        </button>
        <!-- Continue Research Button -->
        <button
          v-if="content && !isStreaming"
          class="btn-tooltip flex-1 sm:flex-none flex items-center justify-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
          @click="toggleContinueInput"
          :disabled="!content"
          data-tooltip="Continue researching a specific topic"
        >
          <Search class="w-4 h-4" />
          <span class="hidden sm:inline">Deep Dive</span>
        </button>
        <button
          class="btn-tooltip flex-1 sm:flex-none flex items-center justify-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          @click="handleExport"
          :disabled="!content"
          data-tooltip="Print or save as PDF"
        >
          <Printer class="w-4 h-4" />
          <span class="hidden sm:inline">Print</span>
        </button>
        <button
          class="btn-tooltip flex-1 sm:flex-none flex items-center justify-center gap-2 px-3 py-1.5 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          @click="handleDownloadMarkdown"
          :disabled="!content"
          data-tooltip="Download as Markdown file"
        >
          <Download class="w-4 h-4" />
          <span class="hidden sm:inline">Download</span>
        </button>
      </div>
    </div>

    <!-- Continue Research Input -->
    <div v-if="showContinueInput" class="px-6 py-3 bg-blue-50 dark:bg-blue-900/20 border-b border-blue-200 dark:border-blue-800/30 animate-in fade-in slide-in-from-top-2 duration-200">
      <div class="flex items-center gap-2">
        <Search class="w-4 h-4 text-blue-500 flex-shrink-0" />
        <input
          id="continue-research-input"
          v-model="continueResearchInput"
          @keydown.enter="handleContinueResearch"
          type="text"
          placeholder="What aspect would you like to explore deeper?"
          class="flex-1 px-3 py-2 text-sm bg-white dark:bg-gray-800 border border-blue-200 dark:border-blue-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 text-gray-800 dark:text-gray-200 placeholder:text-gray-400"
        />
        <button
          @click="handleContinueResearch"
          :disabled="!continueResearchInput.trim()"
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Research
        </button>
      </div>
    </div>

    <!-- Content Wrapper with TOC -->
    <div class="relative flex">
      <!-- TOC Sidebar -->
      <aside
        v-if="showToc && tocItems.length > 0"
        class="toc-sidebar hidden lg:block w-56 flex-shrink-0 border-r border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50 overflow-y-auto"
      >
        <nav class="p-4 sticky top-0">
          <h4 class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Contents</h4>
          <ul class="space-y-1">
            <li
              v-for="item in tocItems"
              :key="item.id"
              :class="[
                'text-sm cursor-pointer hover:text-blue-600 dark:hover:text-blue-400 transition-colors truncate',
                item.level === 1 ? 'font-medium text-gray-800 dark:text-gray-200' : '',
                item.level === 2 ? 'pl-3 text-gray-600 dark:text-gray-400' : '',
                item.level === 3 ? 'pl-6 text-gray-500 dark:text-gray-500 text-xs' : ''
              ]"
              @click="scrollToHeading(item.id)"
              :title="item.text"
            >
              {{ item.text }}
            </li>
          </ul>
        </nav>
      </aside>

      <!-- Main Content -->
      <div id="report-content" class="flex-1 p-6 sm:p-8 lg:p-10 min-h-[400px]">
        <!-- Skeleton Loading -->
        <div v-if="!content && isStreaming" class="animate-pulse space-y-6 max-w-3xl mx-auto py-4">
          <div class="space-y-3">
            <div class="h-7 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
            <div class="h-4 bg-gray-100 dark:bg-gray-600 rounded w-1/3"></div>
          </div>
          <div class="space-y-2">
            <div class="h-4 bg-gray-100 dark:bg-gray-600 rounded"></div>
            <div class="h-4 bg-gray-100 dark:bg-gray-600 rounded"></div>
            <div class="h-4 bg-gray-100 dark:bg-gray-600 rounded w-4/5"></div>
          </div>
          <div class="space-y-2 pt-2">
            <div class="h-5 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
            <div class="h-4 bg-gray-100 dark:bg-gray-600 rounded"></div>
            <div class="h-4 bg-gray-100 dark:bg-gray-600 rounded w-5/6"></div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else-if="!content" class="flex flex-col items-center justify-center text-gray-400 dark:text-gray-500 py-20 space-y-3">
          <div class="w-14 h-14 bg-gray-100 dark:bg-gray-700 rounded-xl flex items-center justify-center">
            <FileText class="w-7 h-7 text-gray-300 dark:text-gray-600" />
          </div>
          <p class="text-sm">Report will appear here</p>
        </div>

        <!-- Actual Content -->
        <article
          v-else
          ref="articleRef"
          class="report-content mx-auto max-w-4xl
                 prose prose-slate dark:prose-invert
                 prose-headings:font-semibold
                 prose-h1:text-2xl prose-h1:mb-6 prose-h1:mt-0 prose-h1:pb-3 prose-h1:border-b-2 prose-h1:border-blue-500
                 prose-h2:text-xl prose-h2:mt-8 prose-h2:mb-4 prose-h2:pl-3 prose-h2:border-l-4 prose-h2:border-blue-500
                 prose-h3:text-lg prose-h3:mt-6 prose-h3:mb-3
                 prose-p:my-4 prose-p:leading-7
                 prose-a:text-blue-600 dark:prose-a:text-blue-400 prose-a:no-underline hover:prose-a:underline
                 prose-blockquote:border-l-4 prose-blockquote:border-blue-500 prose-blockquote:bg-blue-50 dark:prose-blockquote:bg-blue-900/20 prose-blockquote:py-1 prose-blockquote:px-4 prose-blockquote:rounded-r prose-blockquote:not-italic
                 prose-ul:my-4 prose-ol:my-4 prose-li:my-1
                 prose-code:bg-gray-100 dark:prose-code:bg-gray-800 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-code:before:content-none prose-code:after:content-none
                 prose-pre:bg-gray-900 prose-pre:text-gray-100
                 prose-img:rounded-lg prose-img:shadow-md
                 prose-table:text-sm prose-th:bg-gray-50 dark:prose-th:bg-gray-800 prose-th:px-3 prose-th:py-2 prose-td:px-3 prose-td:py-2"
        >
          <div v-html="renderedContent"></div>

          <!-- Cursor for streaming effect -->
          <span v-if="isStreaming" class="inline-block w-1.5 h-5 bg-blue-500 ml-0.5 animate-pulse rounded-sm"></span>

          <!-- References Section -->
          <section v-if="hasCitations && !isStreaming" class="references-section mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 mb-4 flex items-center gap-2">
              <span class="w-1 h-6 bg-blue-500 rounded"></span>
              References
            </h2>
            <ol class="list-decimal list-inside space-y-2 text-sm">
              <li
                v-for="citation in citations"
                :key="citation.index"
                class="text-gray-600 dark:text-gray-400"
              >
                <a
                  :href="citation.url"
                  target="_blank"
                  rel="noopener"
                  class="text-blue-600 dark:text-blue-400 hover:underline"
                >
                  {{ citation.title }}
                </a>
                <span class="text-gray-400 dark:text-gray-500 ml-2 text-xs">
                  ({{ citation.domain }})
                </span>
              </li>
            </ol>
          </section>
        </article>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* TOC Sidebar Styles */
.toc-sidebar {
  max-height: calc(100vh - 200px);
}

/* Print Styles */
@media print {
  .report-header {
    display: none !important;
  }

  .report-container {
    box-shadow: none !important;
    border: none !important;
  }

  #report-content {
    padding: 0 !important;
  }

  .toc-sidebar {
    display: none !important;
  }

  .references-section {
    page-break-before: always;
  }
}
</style>
