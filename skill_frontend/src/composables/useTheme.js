import { ref, watchEffect } from 'vue'

const isDarkMode = ref(localStorage.getItem('skillswap_theme') === 'dark')

watchEffect(() => {
  document.documentElement.classList.toggle('dark', isDarkMode.value)
  localStorage.setItem('skillswap_theme', isDarkMode.value ? 'dark' : 'light')
})

export function useTheme() {
  function toggleTheme(dark) {
    isDarkMode.value = dark
  }
  return { isDarkMode, toggleTheme }
}
