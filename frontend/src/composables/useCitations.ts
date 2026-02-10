import { computed, type Ref } from 'vue'
import type { Source } from '../types'

export interface Citation {
  index: number
  url: string
  title: string
  domain: string
}

/**
 * 从 URL 中提取域名
 */
function extractDomain(url: string): string {
  try {
    const urlObj = new URL(url)
    return urlObj.hostname.replace(/^www\./, '')
  } catch {
    return url
  }
}

/**
 * 从 Markdown 内容中提取引用信息
 * 匹配格式: [Source N(url)] 或 [Source N (url)]
 */
export function extractCitationsFromMarkdown(content: string): Citation[] {
  const citations: Citation[] = []
  const seen = new Set<number>()

  // 匹配 [Source N(url)] 或 [Source N (url)] 格式
  const regex = /\[Source\s*(\d+)\s*\(([^)]+)\)\]/gi
  let match

  while ((match = regex.exec(content)) !== null) {
    const indexStr = match[1]
    const urlStr = match[2]

    if (!indexStr || !urlStr) continue

    const index = parseInt(indexStr, 10)
    const url = urlStr

    if (!seen.has(index)) {
      seen.add(index)
      citations.push({
        index,
        url,
        title: `Source ${index}`,
        domain: extractDomain(url)
      })
    }
  }

  // 按索引排序
  return citations.sort((a, b) => a.index - b.index)
}

/**
 * 将 sources 数据与 Markdown 内容中提取的引用合并
 * 优先使用 sources 中的 title
 */
export function mergeCitationsWithSources(
  citations: Citation[],
  sources: Source[]
): Citation[] {
  return citations.map(citation => {
    // 尝试从 sources 中找到匹配的 URL
    const matchedSource = sources.find(s => s.url === citation.url)
    if (matchedSource && matchedSource.title) {
      return {
        ...citation,
        title: matchedSource.title
      }
    }
    return citation
  })
}

/**
 * useCitations composable
 * 提取并管理报告中的引用信息
 */
export function useCitations(
  content: Ref<string>,
  sources?: Ref<Source[]>
) {
  const citations = computed(() => {
    const extracted = extractCitationsFromMarkdown(content.value)
    if (sources?.value && sources.value.length > 0) {
      return mergeCitationsWithSources(extracted, sources.value)
    }
    return extracted
  })

  /**
   * 根据引用索引获取引用信息
   */
  const getCitation = (index: number): Citation | undefined => {
    return citations.value.find(c => c.index === index)
  }

  /**
   * 检查是否有引用
   */
  const hasCitations = computed(() => citations.value.length > 0)

  return {
    citations,
    getCitation,
    hasCitations
  }
}
