<template>
  <div class="card video-preview" v-if="videoInfo">
    <div class="thumbnail-container">
      <img
        :src="videoInfo.thumbnail"
        :alt="videoInfo.title"
        class="thumbnail"
        @error="handleImageError"
      />
      <span :class="['platform-badge', videoInfo.platform]">
        {{ platformLabel }}
      </span>
      <span class="duration-badge">{{ videoInfo.duration }}</span>

      <!-- Thumbnail download button -->
      <button
        class="thumbnail-download-btn"
        @click="downloadThumbnail"
        :disabled="downloadingThumbnail"
        title="Download thumbnail"
      >
        <span v-if="downloadingThumbnail" class="spinner-small"></span>
        <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
          <circle cx="8.5" cy="8.5" r="1.5"/>
          <polyline points="21 15 16 10 5 21"/>
        </svg>
      </button>
    </div>

    <h3 class="video-title">{{ videoInfo.title }}</h3>
    <p class="video-uploader">{{ videoInfo.uploader }}</p>

    <div class="quality-selector" v-if="videoInfo.formats && videoInfo.formats.length > 1">
      <label class="quality-label">Select quality:</label>
      <div class="quality-options">
        <button
          v-for="format in videoInfo.formats"
          :key="format.format_id"
          :class="['quality-option', { active: selectedFormat === format.format_id }]"
          @click="selectFormat(format.format_id)"
          type="button"
        >
          {{ format.quality }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  videoInfo: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['format-selected'])

const selectedFormat = ref('')
const downloadingThumbnail = ref(false)

const platformLabel = computed(() => {
  const labels = {
    youtube: 'YouTube',
    twitter: 'X / Twitter',
    tiktok: 'TikTok',
    instagram: 'Instagram'
  }
  return labels[props.videoInfo?.platform] || props.videoInfo?.platform
})

watch(() => props.videoInfo, (newInfo) => {
  if (newInfo && newInfo.formats && newInfo.formats.length > 0) {
    selectedFormat.value = newInfo.formats[0].format_id
    emit('format-selected', selectedFormat.value)
  }
}, { immediate: true })

const selectFormat = (formatId) => {
  selectedFormat.value = formatId
  emit('format-selected', formatId)
}

const handleImageError = (e) => {
  e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360"><rect fill="%230f3460" width="640" height="360"/><text x="50%" y="50%" fill="%23a0a0b0" font-family="sans-serif" font-size="24" text-anchor="middle" dy=".3em">No thumbnail available</text></svg>'
}

const downloadThumbnail = async () => {
  if (!props.videoInfo?.thumbnail || downloadingThumbnail.value) return

  downloadingThumbnail.value = true

  try {
    const response = await fetch('/api/download/thumbnail', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: props.videoInfo.thumbnail,
        title: props.videoInfo.title
      })
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || 'Failed to download thumbnail')
    }

    // Get filename from Content-Disposition header
    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = 'thumbnail.jpg'
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename\*?=['"]?(?:UTF-8'')?([^;\r\n"']*)['"]?/i)
      if (filenameMatch) {
        filename = decodeURIComponent(filenameMatch[1])
      }
    }

    // Create blob and trigger download
    const blob = await response.blob()
    const downloadUrl = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = downloadUrl
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(downloadUrl)

  } catch (error) {
    console.error('Failed to download thumbnail:', error)
  } finally {
    downloadingThumbnail.value = false
  }
}
</script>

<style scoped>
.thumbnail-download-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  opacity: 0;
  backdrop-filter: blur(4px);
}

.thumbnail-container:hover .thumbnail-download-btn {
  opacity: 1;
}

.thumbnail-download-btn:hover:not(:disabled) {
  background: var(--accent);
  transform: scale(1.1);
}

.thumbnail-download-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
