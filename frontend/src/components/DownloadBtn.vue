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

    <div class="button-group" v-if="showProgress && canCancel">
      <button
        class="btn btn-cancel"
        @click="handleCancel"
        :disabled="progressStatus === 'cancelling'"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
        {{ progressStatus === 'cancelling' ? 'Cancelling...' : 'Cancel' }}
      </button>
    </div>

    <button
      v-if="!showProgress || !canCancel"
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
  },
  title: {
    type: String,
    default: 'Unknown'
  }
})

const emit = defineEmits(['download-start', 'download-complete', 'download-error', 'download-added'])

const downloading = ref(false)
const showProgress = ref(false)
const progressStatus = ref('starting')
const progressPercent = ref(0)
const progressDownloaded = ref('0 B')
const progressTotal = ref('0 B')
const progressSpeed = ref('0 B/s')
const progressEta = ref('--:--')
const downloadId = ref(null)
const eventSource = ref(null)

const canCancel = computed(() => {
  return ['downloading', 'starting', 'processing'].includes(progressStatus.value)
})

const buttonText = computed(() => {
  if (!downloading.value) return 'Download Video'
  if (progressStatus.value === 'completed') return 'Saving file...'
  if (progressStatus.value === 'processing') return 'Processing...'
  if (progressStatus.value === 'cancelled') return 'Cancelled'
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

const handleCancel = async () => {
  if (!downloadId.value) return

  try {
    progressStatus.value = 'cancelling'

    await fetch(`/api/download/cancel/${downloadId.value}`, {
      method: 'POST'
    })

    // Close SSE connection
    if (eventSource.value) {
      eventSource.value.close()
      eventSource.value = null
    }

  } catch (error) {
    console.error('Failed to cancel download:', error)
  }
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
        format: props.format,
        title: props.title
      })
    })

    if (!startResponse.ok) {
      const errorData = await startResponse.json()
      throw new Error(errorData.error || 'Failed to start download')
    }

    const startData = await startResponse.json()
    downloadId.value = startData.download_id
    showProgress.value = true

    // Emit event for downloads manager
    emit('download-added', {
      id: startData.download_id,
      title: startData.title || props.title,
      platform: startData.platform
    })

    // Step 2: Connect to SSE for progress updates
    const completed = await new Promise((resolve, reject) => {
      eventSource.value = new EventSource(`/api/download/progress/${downloadId.value}`)

      eventSource.value.onmessage = (event) => {
        const data = JSON.parse(event.data)

        progressStatus.value = data.status
        progressPercent.value = data.percent || 0
        progressDownloaded.value = data.downloaded_str || '0 B'
        progressTotal.value = data.total_str || '0 B'
        progressSpeed.value = data.speed_str || '0 B/s'
        progressEta.value = data.eta_str || '--:--'

        if (data.status === 'completed') {
          eventSource.value.close()
          eventSource.value = null
          resolve({ completed: true, data })
        } else if (data.status === 'cancelled') {
          eventSource.value.close()
          eventSource.value = null
          resolve({ completed: false, cancelled: true })
        } else if (data.status === 'error' || data.status === 'not_found') {
          eventSource.value.close()
          eventSource.value = null
          reject(new Error(data.error || 'Download failed'))
        }
      }

      eventSource.value.onerror = () => {
        eventSource.value.close()
        eventSource.value = null
        reject(new Error('Connection to server lost'))
      }
    })

    // If cancelled, don't try to download the file
    if (!completed.completed) {
      if (completed.cancelled) {
        emit('download-error', 'Download cancelled')
      }
      return
    }

    // Step 3: Download the file
    progressStatus.value = 'completed'
    const fileResponse = await fetch(`/api/download/file/${downloadId.value}`)

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

.button-group {
  display: flex;
  gap: 12px;
  margin-top: 12px;
}

.btn-cancel {
  flex: 1;
  justify-content: center;
  background: var(--error);
  color: white;
}

.btn-cancel:hover:not(:disabled) {
  background: #e55555;
  transform: translateY(-2px);
}

.btn-cancel:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
