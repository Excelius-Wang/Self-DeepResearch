<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Sun, Moon } from 'lucide-vue-next'

const isDark = ref(false)

const ariaLabel = computed(() =>
  isDark.value ? 'Switch to light mode' : 'Switch to dark mode'
)

const toggleTheme = () => {
  isDark.value = !isDark.value
  updateTheme()
}

const updateTheme = () => {
  const html = document.documentElement
  if (isDark.value) {
    html.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    html.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches

  if (savedTheme === 'dark' || (!savedTheme && systemDark)) {
    isDark.value = true
  } else {
    isDark.value = false
  }
  updateTheme()
})
</script>

<template>
  <button
    @click="toggleTheme"
    class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800 transition-colors"
    :title="ariaLabel"
    :aria-label="ariaLabel"
  >
    <Sun v-if="!isDark" class="w-5 h-5" />
    <Moon v-else class="w-5 h-5" />
  </button>
</template>
