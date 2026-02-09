<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Trash2 } from 'lucide-vue-next';
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
const pendingDeleteId = ref<number | null>(null);

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
  pendingDeleteId.value = id;

  const confirmed = await confirmDialog.value?.open();
  if (!confirmed) {
    pendingDeleteId.value = null;
    return;
  }

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
  } finally {
    pendingDeleteId.value = null;
  }
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

    <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-white dark:bg-gray-800">
      <h2 class="font-semibold text-gray-700 dark:text-gray-200">History</h2>
      <button
        @click="fetchHistory"
        class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
        title="Refresh"
        aria-label="Refresh history"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </div>

    <div class="flex-1 overflow-y-auto p-2 space-y-2">
      <div v-if="loading" class="text-center text-gray-400 dark:text-gray-500 py-4 text-sm">Loading...</div>
      <div v-else-if="history.length === 0" class="text-center text-gray-400 dark:text-gray-500 py-4 text-sm">No history yet</div>

      <div
        v-for="item in history"
        :key="item.id"
        @click="emit('select', item.id)"
        role="button"
        tabindex="0"
        @keydown.enter="emit('select', item.id)"
        class="p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md cursor-pointer transition-all hover:border-blue-300 dark:hover:border-blue-600 group relative focus:outline-none focus:ring-2 focus:ring-blue-500"
        :aria-label="`Load research: ${item.task}`"
      >
        <div class="text-sm font-medium text-gray-800 dark:text-gray-200 line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 pr-6">
          {{ item.task }}
        </div>
        <div class="text-xs text-gray-400 dark:text-gray-500 mt-2 flex justify-between items-center">
          <span>{{ new Date(item.created_at).toLocaleDateString() }}</span>
          <span>{{ new Date(item.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</span>
        </div>

        <button
          @click="(e) => deleteHistory(item.id, e)"
          class="absolute top-2 right-2 text-gray-400 dark:text-gray-500 hover:text-red-500 dark:hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity p-1"
          title="Delete"
          aria-label="Delete research"
        >
          <Trash2 class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>
