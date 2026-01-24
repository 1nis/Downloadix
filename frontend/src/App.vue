<template>
  <div class="container">
    <Settings />

    <header class="header">
      <h1>Downloadix</h1>
      <p>Download videos from your favorite platforms</p>
      <div class="platforms">
        <span class="platform-icon youtube" title="YouTube">YT</span>
        <span class="platform-icon twitter" title="X / Twitter">X</span>
        <span class="platform-icon tiktok" title="TikTok">TT</span>
      </div>
    </header>

    <main>
      <VideoForm
        ref="videoForm"
        @fetch="fetchVideoInfo"
      />

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <div v-if="success" class="success-message">
        {{ success }}
      </div>

      <VideoPreview
        v-if="videoInfo"
        :video-info="videoInfo"
        @format-selected="handleFormatSelected"
      />

      <DownloadBtn
        v-if="videoInfo"
        :url="currentUrl"
        :format="selectedFormat"
        :disabled="!videoInfo"
        @download-start="handleDownloadStart"
        @download-complete="handleDownloadComplete"
        @download-error="handleDownloadError"
      />
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
import Settings from './components/Settings.vue'

const videoForm = ref(null)
const videoInfo = ref(null)
const currentUrl = ref('')
const selectedFormat = ref('best')
const error = ref('')
const success = ref('')

const clearMessages = () => {
  error.value = ''
  success.value = ''
}

const fetchVideoInfo = async (url) => {
  clearMessages()
  videoInfo.value = null
  currentUrl.value = url

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
    videoForm.value?.setLoading(false)
  }
}

const handleFormatSelected = (formatId) => {
  selectedFormat.value = formatId
}

const handleDownloadStart = () => {
  clearMessages()
}

const handleDownloadComplete = () => {
  success.value = 'Download completed successfully!'
  setTimeout(() => {
    success.value = ''
  }, 5000)
}

const handleDownloadError = (message) => {
  error.value = message
}
</script>
