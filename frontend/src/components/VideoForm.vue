<template>
  <div class="card">
    <form class="url-form" @submit.prevent="handleSubmit">
      <input
        type="text"
        v-model="url"
        class="url-input"
        placeholder="Paste video URL (YouTube, X/Twitter, TikTok)"
        :disabled="loading"
      />
      <button type="submit" class="btn btn-primary" :disabled="loading || !url.trim()">
        <span v-if="loading" class="spinner"></span>
        <span v-else>Fetch</span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['fetch'])

const url = ref('')
const loading = ref(false)

const handleSubmit = async () => {
  if (!url.value.trim()) return

  loading.value = true
  emit('fetch', url.value.trim())
}

const setLoading = (value) => {
  loading.value = value
}

const clearUrl = () => {
  url.value = ''
}

defineExpose({ setLoading, clearUrl })
</script>
