<template>
  <div class="container">

    <DownloadsManager ref="downloadsManager" />

    <!-- Toast Notifications -->
    <div class="toast-container">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="['toast', `toast-${toast.type}`, { 'toast-leaving': toast.leaving }]"
        >
          <div class="toast-icon">
            <svg v-if="toast.type === 'success'" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
            <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </div>
          <div class="toast-content">
            <div class="toast-title">{{ toast.title }}</div>
            <div class="toast-message" v-if="toast.message">{{ toast.message }}</div>
          </div>
          <button class="toast-close" @click="removeToast(toast.id)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
          <div class="toast-progress"></div>
        </div>
      </TransitionGroup>
    </div>

    <header class="header">
      <h1>Downloadix</h1>
      <p>Download videos from your favorite platforms</p>
      <div class="platforms">
        <span class="platform-icon youtube" title="YouTube">YT</span>
        <span class="platform-icon twitter" title="X / Twitter">X</span>
        <span class="platform-icon tiktok" title="TikTok">TT</span>
        <span class="platform-icon instagram" title="Instagram">IG</span>
      </div>
    </header>

    <main>
      <VideoForm
        ref="videoForm"
        @fetch="fetchVideoInfo"
      />

      <Transition name="fade-slide">
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </Transition>

      <Transition name="fade-slide">
        <div v-if="success" class="success-message">
          {{ success }}
        </div>
      </Transition>

      <Transition name="fade-slide">
        <VideoPreview
          v-if="isLoading || videoInfo"
          :video-info="videoInfo"
          :loading="isLoading"
          @format-selected="handleFormatSelected"
        />
      </Transition>

      <Transition name="fade-slide">
        <DownloadBtn
          v-if="videoInfo"
          :url="currentUrl"
          :format="selectedFormat"
          :title="videoInfo?.title || 'Unknown'"
          :thumbnail="videoInfo?.thumbnail || ''"
          :quality="getQualityLabel(selectedFormat)"
          :disabled="!videoInfo"
          @download-start="handleDownloadStart"
          @download-complete="handleDownloadComplete"
          @download-error="handleDownloadError"
          @download-added="handleDownloadAdded"
        />
      </Transition>
    </main>

    <footer class="footer">
      <p>Powered by yt-dlp</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import VideoForm from './components/VideoForm.vue'
import VideoPreview from './components/VideoPreview.vue'
import DownloadBtn from './components/DownloadBtn.vue'

import DownloadsManager from './components/DownloadsManager.vue'

const videoForm = ref(null)
const downloadsManager = ref(null)
const videoInfo = ref(null)
const currentUrl = ref('')
const selectedFormat = ref('best')
const error = ref('')
const success = ref('')
const isLoading = ref(false)

// Toast system
const toasts = ref([])
let toastIdCounter = 0

const addToast = (type, title, message = '') => {
  const id = ++toastIdCounter
  toasts.value.push({ id, type, title, message, leaving: false })

  // Auto-dismiss after 4 seconds
  setTimeout(() => {
    const toast = toasts.value.find(t => t.id === id)
    if (toast) {
      toast.leaving = true
      setTimeout(() => {
        removeToast(id)
      }, 300)
    }
  }, 4000)
}

const removeToast = (id) => {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index !== -1) {
    toasts.value.splice(index, 1)
  }
}

const clearMessages = () => {
  error.value = ''
  success.value = ''
}

const fetchVideoInfo = async (url) => {
  clearMessages()
  videoInfo.value = null
  currentUrl.value = url
  isLoading.value = true

  try {
    const response = await fetch(`/api/info?url=${encodeURIComponent(url)}`)
    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.error || 'Failed to fetch video info')
    }

    videoInfo.value = data
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
    videoForm.value?.setLoading(false)
  }
}

const handleFormatSelected = (formatId) => {
  selectedFormat.value = formatId
}

const getQualityLabel = (formatId) => {
  // Extract quality from format like "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
  const match = formatId.match(/height<=(\d+)/)
  if (match) {
    return match[1] + 'p'
  }
  // Check videoInfo formats for quality label
  const format = videoInfo.value?.formats?.find(f => f.format_id === formatId)
  return format?.quality || 'best'
}

const handleDownloadStart = () => {
  clearMessages()
}

const handleDownloadComplete = () => {
  // Show toast notification
  addToast('success', 'Download Complete', videoInfo.value?.title || 'Your video is ready!')

  // Refresh downloads list
  downloadsManager.value?.fetchDownloads()
}

const handleDownloadError = (message) => {
  // Show toast notification
  addToast('error', 'Download Failed', message)

  // Refresh downloads list
  downloadsManager.value?.fetchDownloads()
}

const handleDownloadAdded = (download) => {
  // The downloads manager will automatically pick up the new download
  // via its polling mechanism, but we can force a refresh
  downloadsManager.value?.fetchDownloads()
}
</script>
