<template>
  <div class="downloads-manager">
    <button
      class="downloads-toggle"
      @click="togglePanel"
      :class="{ 'has-active': activeCount > 0 }"
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="7 10 12 15 17 10"/>
        <line x1="12" y1="15" x2="12" y2="3"/>
      </svg>
      <span v-if="activeCount > 0" class="badge">{{ activeCount }}</span>
    </button>

    <div v-if="isOpen" class="downloads-panel card">
      <div class="panel-header">
        <div class="tabs">
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'downloads' }"
            @click="activeTab = 'downloads'"
          >
            Downloads
            <span v-if="activeCount > 0" class="tab-badge">{{ activeCount }}</span>
          </button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'history' }"
            @click="activeTab = 'history'; fetchHistory()"
          >
            History
            <span v-if="history.length > 0" class="tab-badge history-badge">{{ history.length }}</span>
          </button>
        </div>
        <div class="header-actions">
          <button
            v-if="activeTab === 'downloads' && completedCount > 0"
            class="clear-btn"
            @click="clearCompleted"
            title="Clear completed"
          >
            Clear
          </button>
          <button
            v-if="activeTab === 'history' && history.length > 0"
            class="clear-btn"
            @click="clearHistory"
            title="Clear history"
          >
            Clear
          </button>
          <button class="close-btn" @click="togglePanel">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>

      <!-- Downloads Tab -->
      <div v-if="activeTab === 'downloads'" class="downloads-list" v-show="downloads.length > 0">
        <div
          v-for="download in downloads"
          :key="download.id"
          class="download-item"
          :class="download.status"
        >
          <div class="download-info">
            <div class="download-title">
              <span :class="['platform-dot', download.platform]"></span>
              <span class="title-text">{{ truncateTitle(download.title) }}</span>
            </div>
            <div class="download-status">
              <template v-if="download.status === 'downloading'">
                <span class="percent">{{ download.percent.toFixed(1) }}%</span>
                <span class="speed">{{ download.speed_str }}</span>
                <span class="eta">ETA: {{ download.eta_str }}</span>
              </template>
              <template v-else-if="download.status === 'processing'">
                <span class="processing-text">Processing...</span>
              </template>
              <template v-else-if="download.status === 'completed'">
                <span class="completed-text">Completed</span>
              </template>
              <template v-else-if="download.status === 'cancelled'">
                <span class="cancelled-text">Cancelled</span>
              </template>
              <template v-else-if="download.status === 'error'">
                <span class="error-text" :title="download.error">Error</span>
              </template>
              <template v-else-if="download.status === 'cancelling'">
                <span class="cancelling-text">Cancelling...</span>
              </template>
              <template v-else>
                <span class="starting-text">Starting...</span>
              </template>
            </div>
          </div>

          <div class="download-progress" v-if="download.status === 'downloading' || download.status === 'processing'">
            <div
              class="progress-fill"
              :style="{ width: `${download.percent}%` }"
              :class="{ 'processing': download.status === 'processing' }"
            ></div>
          </div>

          <div class="download-actions">
            <button
              v-if="download.status === 'completed'"
              class="action-btn download-btn"
              @click="downloadFile(download.id)"
              title="Save file"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
            </button>
            <button
              v-if="['downloading', 'starting', 'processing'].includes(download.status)"
              class="action-btn cancel-btn"
              @click="cancelDownload(download.id)"
              title="Cancel download"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'downloads' && downloads.length === 0" class="empty-state">
        <p>No downloads yet</p>
      </div>

      <!-- History Tab -->
      <div v-if="activeTab === 'history'" class="downloads-list" v-show="history.length > 0">
        <div
          v-for="item in history"
          :key="item.id"
          class="download-item history-item"
          :class="item.status"
        >
          <div class="download-info">
            <div class="download-title">
              <span :class="['platform-dot', item.platform]"></span>
              <span class="title-text">{{ truncateTitle(item.title) }}</span>
            </div>
            <div class="download-meta">
              <span v-if="item.status === 'completed'" class="status-icon completed">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
              </span>
              <span v-else-if="item.status === 'cancelled'" class="status-icon cancelled">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </span>
              <span v-else-if="item.status === 'error'" class="status-icon error" :title="item.error">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"></circle>
                  <line x1="12" y1="8" x2="12" y2="12"></line>
                  <line x1="12" y1="16" x2="12.01" y2="16"></line>
                </svg>
              </span>
              <span class="size-text" v-if="item.total_str && item.status === 'completed'">{{ item.total_str }}</span>
            </div>
          </div>
          <div class="history-details">
            <span class="history-time">{{ formatHistoryTime(item.completed_at) }}</span>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 'history' && history.length === 0" class="empty-state">
        <p>No history yet</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const isOpen = ref(false)
const downloads = ref([])
const history = ref([])
const activeTab = ref('downloads')
let pollInterval = null

const activeCount = computed(() => {
  return downloads.value.filter(d =>
    ['downloading', 'starting', 'processing'].includes(d.status)
  ).length
})

const completedCount = computed(() => {
  return downloads.value.filter(d =>
    ['completed', 'cancelled', 'error'].includes(d.status)
  ).length
})

const togglePanel = () => {
  isOpen.value = !isOpen.value
}

const truncateTitle = (title) => {
  if (!title) return 'Unknown'
  if (title.length > 40) {
    return title.substring(0, 37) + '...'
  }
  return title
}

const fetchDownloads = async () => {
  try {
    const response = await fetch('/api/download/list')
    if (response.ok) {
      downloads.value = await response.json()
    }
  } catch (error) {
    console.error('Failed to fetch downloads:', error)
  }
}

const cancelDownload = async (downloadId) => {
  try {
    await fetch(`/api/download/cancel/${downloadId}`, {
      method: 'POST'
    })
    fetchDownloads()
  } catch (error) {
    console.error('Failed to cancel download:', error)
  }
}

const downloadFile = async (downloadId) => {
  try {
    const response = await fetch(`/api/download/file/${downloadId}`)

    if (!response.ok) {
      throw new Error('Failed to download file')
    }

    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = 'video.mp4'
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename\*?=['"]?(?:UTF-8'')?([^;\r\n"']*)['"]?/i)
      if (filenameMatch) {
        filename = decodeURIComponent(filenameMatch[1])
      }
    }

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
    console.error('Failed to download file:', error)
  }
}

const clearCompleted = async () => {
  try {
    await fetch('/api/download/clear', {
      method: 'POST'
    })
    fetchDownloads()
    fetchHistory()
  } catch (error) {
    console.error('Failed to clear downloads:', error)
  }
}

const fetchHistory = async () => {
  try {
    const response = await fetch('/api/download/history')
    if (response.ok) {
      history.value = await response.json()
    }
  } catch (error) {
    console.error('Failed to fetch history:', error)
  }
}

const clearHistory = async () => {
  try {
    await fetch('/api/download/history/clear', {
      method: 'POST'
    })
    history.value = []
  } catch (error) {
    console.error('Failed to clear history:', error)
  }
}

const formatHistoryTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date

  // Less than 1 minute
  if (diff < 60000) {
    return 'Just now'
  }
  // Less than 1 hour
  if (diff < 3600000) {
    const mins = Math.floor(diff / 60000)
    return `${mins}m ago`
  }
  // Today
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  // This year
  if (date.getFullYear() === now.getFullYear()) {
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
  }
  // Older
  return date.toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' })
}

// Expose method for parent to add download
const addDownload = (download) => {
  const exists = downloads.value.find(d => d.id === download.id)
  if (!exists) {
    downloads.value.unshift(download)
  }
  isOpen.value = true
}

// Expose method to update download progress
const updateDownload = (downloadId, data) => {
  const index = downloads.value.findIndex(d => d.id === downloadId)
  if (index !== -1) {
    downloads.value[index] = {
      ...downloads.value[index],
      ...data
    }
  }
}

defineExpose({
  addDownload,
  updateDownload,
  fetchDownloads,
  fetchHistory
})

onMounted(() => {
  fetchDownloads()
  fetchHistory()
  // Poll for updates every 2 seconds
  pollInterval = setInterval(fetchDownloads, 2000)
})

onUnmounted(() => {
  if (pollInterval) {
    clearInterval(pollInterval)
  }
})
</script>

<style scoped>
.downloads-manager {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 100;
}

.downloads-toggle {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(90deg, var(--accent), #a855f7);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow);
  transition: var(--transition);
  position: relative;
}

.downloads-toggle:hover {
  transform: scale(1.1);
}

.downloads-toggle.has-active {
  animation: pulse-ring 2s infinite;
}

@keyframes pulse-ring {
  0% {
    box-shadow: 0 0 0 0 rgba(108, 99, 255, 0.5);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(108, 99, 255, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(108, 99, 255, 0);
  }
}

.badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: var(--error);
  color: white;
  font-size: 12px;
  font-weight: 700;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.downloads-panel {
  position: absolute;
  bottom: 60px;
  right: 0;
  width: 380px;
  max-width: calc(100vw - 40px);
  max-height: 400px;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.2s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--bg-secondary);
}

.panel-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-primary);
}

.tabs {
  display: flex;
  gap: 4px;
}

.tab-btn {
  padding: 6px 12px;
  border-radius: 6px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 6px;
}

.tab-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.tab-btn.active {
  background: var(--accent);
  color: white;
}

.tab-badge {
  font-size: 0.7rem;
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 600;
}

.tab-btn:not(.active) .tab-badge {
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.tab-btn:not(.active) .tab-badge.history-badge {
  background: var(--bg-tertiary, var(--bg-secondary));
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.clear-btn {
  padding: 4px 10px;
  border-radius: 4px;
  background: var(--bg-secondary);
  border: none;
  color: var(--text-secondary);
  font-size: 0.8rem;
  cursor: pointer;
  transition: var(--transition);
}

.clear-btn:hover {
  background: var(--accent);
  color: white;
}

.close-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.close-btn:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.downloads-list {
  overflow-y: auto;
  max-height: 300px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.download-item {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 12px;
  position: relative;
  overflow: hidden;
}

.download-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 8px;
}

.download-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.platform-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.platform-dot.youtube {
  background: var(--youtube);
}

.platform-dot.twitter {
  background: var(--twitter);
}

.platform-dot.tiktok {
  background: linear-gradient(45deg, #00f2ea, #ff0050);
}

.platform-dot.instagram {
  background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
}

.title-text {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.download-status {
  display: flex;
  gap: 8px;
  font-size: 0.75rem;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.download-status .percent {
  color: var(--accent);
  font-weight: 600;
}

.completed-text {
  color: var(--success);
}

.cancelled-text,
.cancelling-text {
  color: var(--text-secondary);
}

.error-text {
  color: var(--error);
}

.processing-text,
.starting-text {
  color: var(--accent);
}

.download-progress {
  height: 4px;
  background: var(--bg-primary);
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 8px;
}

.download-progress .progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), #a855f7);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.download-progress .progress-fill.processing {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.download-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.action-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.action-btn.download-btn {
  background: var(--success);
  color: white;
}

.action-btn.download-btn:hover {
  background: #3db9b0;
}

.action-btn.cancel-btn {
  background: var(--error);
  color: white;
}

.action-btn.cancel-btn:hover {
  background: #e55555;
}

.empty-state {
  text-align: center;
  padding: 30px;
  color: var(--text-secondary);
}

/* History styles */
.history-item {
  padding: 10px 12px;
}

.history-item .download-info {
  margin-bottom: 4px;
}

.download-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.status-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
}

.status-icon.completed {
  background: var(--success);
  color: white;
}

.status-icon.cancelled {
  background: var(--text-secondary);
  color: white;
}

.status-icon.error {
  background: var(--error);
  color: white;
}

.size-text {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.history-details {
  display: flex;
  justify-content: flex-end;
}

.history-time {
  font-size: 0.7rem;
  color: var(--text-secondary);
  opacity: 0.8;
}

@media (max-width: 480px) {
  .downloads-panel {
    width: calc(100vw - 40px);
    right: -10px;
  }

  .download-status {
    flex-direction: column;
    gap: 2px;
  }
}
</style>
