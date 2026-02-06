<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { Trash2 } from 'lucide-vue-next';

interface HistoryItem {
  id: number;
  task: string;
  created_at: string;
}

const emit = defineEmits<{
  (e: 'select', id: number): void;
}>();

const history = ref<HistoryItem[]>([]);
const loading = ref(true);

const fetchHistory = async () => {
  loading.value = true;
  try {
    const res = await fetch('http://localhost:8000/history');
    if (res.ok) {
      history.value = await res.json();
    }
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};

const deleteHistory = async (id: number, event: Event) => {
  event.stopPropagation();
  if (!confirm('Are you sure you want to delete this research?')) return;
  
  try {
    const res = await fetch(`http://localhost:8000/history/${id}`, {
      method: 'DELETE'
    });
    if (res.ok) {
      history.value = history.value.filter(item => item.id !== id);
    }
  } catch (e) {
    console.error('Failed to delete history', e);
  }
};

onMounted(fetchHistory);

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleString();
};

defineExpose({ refresh: fetchHistory });
</script>

<template>
  <div class="bg-gray-50 h-full flex flex-col">
    <div class="p-4 border-b border-gray-200 flex justify-between items-center bg-white">
      <h2 class="font-semibold text-gray-700">History</h2>
      <button @click="fetchHistory" class="text-gray-500 hover:text-gray-700 p-1 rounded hover:bg-gray-100 transition-colors" title="Refresh">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </div>
    
    <div class="flex-1 overflow-y-auto p-2 space-y-2">
      <div v-if="loading" class="text-center text-gray-400 py-4 text-sm">Loading...</div>
      <div v-else-if="history.length === 0" class="text-center text-gray-400 py-4 text-sm">No history yet</div>
      
      <div 
        v-for="item in history" 
        :key="item.id"
        @click="emit('select', item.id)"
        class="p-3 bg-white rounded-lg border border-gray-200 shadow-sm hover:shadow-md cursor-pointer transition-all hover:border-blue-300 group relative"
      >
        <div class="text-sm font-medium text-gray-800 line-clamp-2 group-hover:text-blue-600 pr-6">
          {{ item.task }}
        </div>
        <div class="text-xs text-gray-400 mt-2 flex justify-between items-center">
          <span>{{ new Date(item.created_at).toLocaleDateString() }}</span>
          <span>{{ new Date(item.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</span>
        </div>
        
        <button 
          @click="(e) => deleteHistory(item.id, e)"
          class="absolute top-2 right-2 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity p-1"
          title="Delete"
        >
          <Trash2 class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>
