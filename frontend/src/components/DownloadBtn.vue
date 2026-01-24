<template>
  <div class="download-section">
    <ProgressBar
      :visible="showProgress"
      :status="progressStatus"
      :percent="progressPercent"
      :downloaded-str="progressDownloaded"
      :total-str="progressTotal"
      :speed-str="progressSpeed"
      :eta-str="progressEta"
    />

    <button
      class="btn btn-download"
      :disabled="disabled || downloading"
      @click="handleDownload"
    >
      <span v-if="downloading && !showProgress" class="spinner"></span>
      <span v-else-if="!downloading">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
          <polyline points="7 10 12 15 17 10"/>
          <line x1="12" y1="15" x2="12" y2="3"/>
        </svg>
      </span>
      {{ buttonText }}
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import ProgressBar from './ProgressBar.vue'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  },
  url: {
    type: String,
    required: true
  },
  format: {
    type: String,
    default: 'best'
  }
})

const emit = defineEmits(['download-start', 'download-complete', 'download-error'])

const downloading = ref(false)
const showProgress = ref(false)
const progressStatus = ref('starting')
const progressPercent = ref(0)
const progressDownloaded = ref('0 B')
const progressTotal = ref('0 B')
const progressSpeed = ref('0 B/s')
const progressEta = ref('--:--')
const downloadId = ref(null)

const buttonText = computed(() => {
  if (!downloading.value) return 'Download Video'
  if (progressStatus.value === 'completed') return 'Saving file...'
  if (progressStatus.value === 'processing') return 'Processing...'
  if (showProgress.value) return 'Downloading...'
  return 'Starting...'
})

const resetProgress = () => {
  progressStatus.value = 'starting'
  progressPercent.value = 0
  progressDownloaded.value = '0 B'
  progressTotal.value = '0 B'
  progressSpeed.value = '0 B/s'
  progressEta.value = '--:--'
}

const handleDownload = async () => {
  if (downloading.value || props.disabled) return

  downloading.value = true
  showProgress.value = false
  resetProgress()
  emit('download-start')

  try {
    // Step 1: Start the download
    const startResponse = await fetch('/api/download/start', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: props.url,
        format: props.format
      })
    })

    if (!startResponse.ok) {
      const errorData = await startResponse.json()
      throw new Error(errorData.error || 'Failed to start download')
    }

    const { download_id } = await startResponse.json()
    downloadId.value = download_id
    showProgress.value = true

    // Step 2: Connect to SSE for progress updates
    await new Promise((resolve, reject) => {
      const eventSource = new EventSource(`/api/download/progress/${download_id}`)

      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data)

        progressStatus.value = data.status
        progressPercent.value = data.percent || 0
        progressDownloaded.value = data.downloaded_str || '0 B'
        progressTotal.value = data.total_str || '0 B'
        progressSpeed.value = data.speed_str || '0 B/s'
        progressEta.value = data.eta_str || '--:--'

        if (data.status === 'completed') {
          eventSource.close()
          resolve(data)
        } else if (data.status === 'error' || data.status === 'not_found') {
          eventSource.close()
          reject(new Error(data.error || 'Download failed'))
        }
      }

      eventSource.onerror = () => {
        eventSource.close()
        reject(new Error('Connection to server lost'))
      }
    })

    // Step 3: Download the file
    progressStatus.value = 'completed'
    const fileResponse = await fetch(`/api/download/file/${download_id}`)

    if (!fileResponse.ok) {
      const errorData = await fileResponse.json()
      throw new Error(errorData.error || 'Failed to download file')
    }

    // Get filename from Content-Disposition header
    const contentDisposition = fileResponse.headers.get('Content-Disposition')
    let filename = 'video.mp4'
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename\*?=['"]?(?:UTF-8'')?([^;\r\n"']*)['"]?/i)
      if (filenameMatch) {
        filename = decodeURIComponent(filenameMatch[1])
      }
    }

    // Create blob and trigger download
    const blob = await fileResponse.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(downloadUrl)

    emit('download-complete')
  } catch (error) {
    emit('download-error', error.message)
  } finally {
    downloading.value = false
    setTimeout(() => {
      showProgress.value = false
      resetProgress()
    }, 2000)
  }
}
</script>

<style scoped>
.download-section {
  width: 100%;
}
</style>
