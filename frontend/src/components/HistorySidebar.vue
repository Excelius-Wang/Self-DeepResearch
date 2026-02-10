<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Trash2, RefreshCw } from 'lucide-vue-next';
import { API_BASE_URL } from '../config';
import { useToast } from '../composables/useToast';
import ConfirmDialog from './ConfirmDialog.vue';
import type { HistoryItem } from '../types';

const emit = defineEmits<{
  (e: 'select', id: number): void;
}>();

const toast = useToast();
const history = ref<HistoryItem[]>([]);
const loading = ref(true);
const confirmDialog = ref<InstanceType<typeof ConfirmDialog> | null>(null);

const fetchHistory = async () => {
  loading.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/history`);
    if (res.ok) {
      history.value = await res.json();
    }
  } catch (e) {
    console.error(e);
    toast.error('Failed to load history');
  } finally {
    loading.value = false;
  }
};

const deleteHistory = async (id: number, event: Event) => {
  event.stopPropagation();

  const confirmed = await confirmDialog.value?.open();
  if (!confirmed) return;

  try {
    const res = await fetch(`${API_BASE_URL}/history/${id}`, {
      method: 'DELETE'
    });
    if (res.ok) {
      history.value = history.value.filter(item => item.id !== id);
      toast.success('Research deleted');
    } else {
      toast.error('Failed to delete research');
    }
  } catch (e) {
    console.error('Failed to delete history', e);
    toast.error('Failed to delete research');
  }
};

// Format relative time
const formatRelativeTime = (dateStr: string) => {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) {
    return 'Today';
  } else if (diffDays === 1) {
    return 'Yesterday';
  } else if (diffDays < 7) {
    return `${diffDays} days ago`;
  } else {
    return date.toLocaleDateString();
  }
};

const formatTime = (dateStr: string) => {
  return new Date(dateStr).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

onMounted(fetchHistory);

defineExpose({ refresh: fetchHistory });
</script>

<template>
  <div class="bg-gray-50 dark:bg-gray-900 h-full flex flex-col">
    <ConfirmDialog
      ref="confirmDialog"
      title="Delete Research"
      message="Are you sure you want to delete this research? This action cannot be undone."
      confirm-text="Delete"
      cancel-text="Cancel"
    />

    <!-- Header - 与主 header 高度一致 h-16 -->
    <div class="h-16 px-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-white dark:bg-gray-800 flex-shrink-0">
      <h2 class="font-semibold text-gray-800 dark:text-gray-100">History</h2>
      <button
        @click="fetchHistory"
        class="p-2 text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
        title="Refresh history"
        aria-label="Refresh history"
      >
        <RefreshCw class="w-4 h-4" />
      </button>
    </div>

    <!-- History List -->
    <div class="flex-1 overflow-y-auto p-3 space-y-2">
      <div v-if="loading" class="flex items-center justify-center py-8">
        <div class="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>

      <div v-else-if="history.length === 0" class="text-center py-12 space-y-2">
        <div class="w-12 h-12 mx-auto bg-gray-100 dark:bg-gray-800 rounded-xl flex items-center justify-center">
          <svg class="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-400">No research yet</p>
        <p class="text-xs text-gray-400 dark:text-gray-500">Start your first research above</p>
      </div>

      <div
        v-else
        v-for="item in history"
        :key="item.id"
        @click="emit('select', item.id)"
        role="button"
        tabindex="0"
        @keydown.enter="emit('select', item.id)"
        class="group relative p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 cursor-pointer transition-all duration-200 hover:border-blue-400 dark:hover:border-blue-500 hover:shadow-md hover:bg-blue-50/50 dark:hover:bg-blue-900/20 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
        :aria-label="`Load research: ${item.task}`"
      >
        <!-- Task Title -->
        <div class="text-sm font-medium text-gray-800 dark:text-gray-200 line-clamp-2 pr-8 group-hover:text-blue-700 dark:group-hover:text-blue-300 transition-colors">
          {{ item.task }}
        </div>

        <!-- Time Info & Notes Count -->
        <div class="flex items-center gap-2 mt-2 text-xs text-gray-500 dark:text-gray-400">
          <span class="font-medium">{{ formatRelativeTime(item.created_at) }}</span>
          <span class="text-gray-300 dark:text-gray-600">·</span>
          <span>{{ formatTime(item.created_at) }}</span>
          <template v-if="item.notes_count">
            <span class="text-gray-300 dark:text-gray-600">·</span>
            <span>{{ item.notes_count }} sources</span>
          </template>
        </div>

        <!-- Delete Button - 始终可见但淡化 -->
        <button
          @click="(e) => deleteHistory(item.id, e)"
          class="absolute top-3 right-3 p-1.5 text-gray-300 dark:text-gray-600 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded-md transition-all group-hover:text-gray-400 dark:group-hover:text-gray-500"
          title="Delete research"
          aria-label="Delete research"
        >
          <Trash2 class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>
