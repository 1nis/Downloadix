<template>
  <div class="card">
    <form class="url-form" @submit.prevent="handleSubmit">
      <div class="input-wrapper">
        <input
          type="text"
          v-model="url"
          class="url-input"
          :class="{ 'has-platform': detectedPlatform }"
          placeholder="Paste video URL (YouTube, X/Twitter, TikTok)"
          :disabled="loading"
          @paste="handlePaste"
        />
        <Transition name="platform-fade">
          <div v-if="detectedPlatform" :class="['platform-indicator', detectedPlatform]">
            <component :is="platformIcon" />
            <span>{{ platformLabel }}</span>
          </div>
        </Transition>
      </div>
      <button type="submit" class="btn btn-primary" :disabled="loading || !url.trim()">
        <span v-if="loading" class="spinner"></span>
        <span v-else>Fetch</span>
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch, h } from 'vue'

const emit = defineEmits(['fetch'])

const url = ref('')
const loading = ref(false)
const detectedPlatform = ref(null)

// Platform detection patterns
const platformPatterns = {
  youtube: /(?:youtube\.com|youtu\.be)/i,
  twitter: /(?:twitter\.com|x\.com)/i,
  tiktok: /tiktok\.com/i,
  instagram: /instagram\.com/i
}

// Detect platform from URL
const detectPlatform = (inputUrl) => {
  if (!inputUrl) return null
  for (const [platform, pattern] of Object.entries(platformPatterns)) {
    if (pattern.test(inputUrl)) {
      return platform
    }
  }
  return null
}

// Watch URL changes to detect platform
watch(url, (newUrl) => {
  detectedPlatform.value = detectPlatform(newUrl)
})

// Platform label
const platformLabel = computed(() => {
  const labels = {
    youtube: 'YouTube',
    twitter: 'X / Twitter',
    tiktok: 'TikTok',
    instagram: 'Instagram'
  }
  return labels[detectedPlatform.value] || ''
})

// Platform icons as render functions
const YouTubeIcon = () => h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M23.5 6.2a3 3 0 0 0-2.1-2.1C19.5 3.5 12 3.5 12 3.5s-7.5 0-9.4.6A3 3 0 0 0 .5 6.2 31.4 31.4 0 0 0 0 12c0 2 .2 4 .5 5.8a3 3 0 0 0 2.1 2.1c1.9.6 9.4.6 9.4.6s7.5 0 9.4-.6a3 3 0 0 0 2.1-2.1c.4-1.8.5-3.8.5-5.8s-.2-4-.5-5.8zM9.5 15.5v-7l6.3 3.5-6.3 3.5z' })
])

const TwitterIcon = () => h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z' })
])

const TikTokIcon = () => h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z' })
])

const InstagramIcon = () => h('svg', { width: 16, height: 16, viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z' })
])

const platformIcon = computed(() => {
  const icons = {
    youtube: YouTubeIcon,
    twitter: TwitterIcon,
    tiktok: TikTokIcon,
    instagram: InstagramIcon
  }
  return icons[detectedPlatform.value] || null
})

// Handle paste event - auto-fetch if valid URL
const handlePaste = (event) => {
  // Get pasted text
  const pastedText = event.clipboardData?.getData('text') || ''

  // Check if it's a valid URL and detect platform
  const platform = detectPlatform(pastedText)

  if (platform && !loading.value) {
    // Small delay to let v-model update
    setTimeout(() => {
      if (url.value.trim()) {
        loading.value = true
        emit('fetch', url.value.trim())
      }
    }, 100)
  }
}

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
  detectedPlatform.value = null
}

defineExpose({ setLoading, clearUrl })
</script>

<style scoped>
.input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
  align-items: center;
}

.url-input.has-platform {
  padding-right: 140px;
}

.platform-indicator {
  position: absolute;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  font-size: 0.8rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.platform-indicator.youtube {
  color: #ff0000;
  background: rgba(255, 0, 0, 0.1);
}

.platform-indicator.twitter {
  color: #1da1f2;
  background: rgba(29, 161, 242, 0.1);
}

.platform-indicator.tiktok {
  color: #ff0050;
  background: rgba(255, 0, 80, 0.1);
}

.platform-indicator.instagram {
  color: #e1306c;
  background: rgba(225, 48, 108, 0.1);
}

.platform-fade-enter-active,
.platform-fade-leave-active {
  transition: all 0.2s ease;
}

.platform-fade-enter-from,
.platform-fade-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

@media (max-width: 640px) {
  .input-wrapper {
    width: 100%;
  }

  .url-input.has-platform {
    padding-right: 16px;
  }

  .platform-indicator {
    display: none;
  }
}
</style>
