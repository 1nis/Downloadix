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

const platformLabel = computed(() => {
  const labels = {
    youtube: 'YouTube',
    twitter: 'X / Twitter',
    tiktok: 'TikTok'
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
</script>
