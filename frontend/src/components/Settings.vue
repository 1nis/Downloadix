<template>
  <div class="settings-container">
    <button class="settings-toggle" @click="toggleSettings" :title="isOpen ? 'Close settings' : 'Open settings'">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="3"></circle>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
      </svg>
    </button>

    <div v-if="isOpen" class="settings-panel card">
      <div class="settings-header">
        <h3>Settings</h3>
        <button class="close-btn" @click="toggleSettings">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <div class="settings-content">
        <div class="setting-item">
          <label class="setting-label">Download Folder</label>
          <div class="input-group">
            <input
              type="text"
              class="url-input"
              v-model="downloadFolder"
              placeholder="Enter download folder path"
              @keyup.enter="saveSettings"
            />
            <button class="btn btn-primary" @click="saveSettings" :disabled="saving">
              <span v-if="saving" class="spinner"></span>
              <span v-else>Save</span>
            </button>
          </div>
          <p class="setting-hint">Enter the full path where you want to save downloaded videos.</p>
        </div>

        <div v-if="message" :class="['message', messageType]">
          {{ message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const isOpen = ref(false)
const downloadFolder = ref('')
const saving = ref(false)
const message = ref('')
const messageType = ref('success')

const toggleSettings = () => {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    loadSettings()
  }
}

const loadSettings = async () => {
  try {
    const response = await fetch('/api/settings')
    if (response.ok) {
      const data = await response.json()
      downloadFolder.value = data.download_folder || ''
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
  }
}

const saveSettings = async () => {
  if (saving.value) return

  saving.value = true
  message.value = ''

  try {
    const response = await fetch('/api/settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        download_folder: downloadFolder.value
      })
    })

    const data = await response.json()

    if (response.ok) {
      message.value = 'Settings saved successfully!'
      messageType.value = 'success'
      downloadFolder.value = data.download_folder
    } else {
      message.value = data.error || 'Failed to save settings'
      messageType.value = 'error'
    }
  } catch (error) {
    message.value = 'Failed to save settings: ' + error.message
    messageType.value = 'error'
  } finally {
    saving.value = false
    setTimeout(() => {
      message.value = ''
    }, 3000)
  }
}

onMounted(() => {
  loadSettings()
})
</script>

<style scoped>
.settings-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 100;
}

.settings-toggle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--bg-card);
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow);
  transition: var(--transition);
}

.settings-toggle:hover {
  background: var(--accent);
  transform: rotate(45deg);
}

.settings-panel {
  position: absolute;
  top: 54px;
  right: 0;
  width: 350px;
  max-width: calc(100vw - 40px);
  animation: slideIn 0.2s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.settings-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.settings-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: var(--text-primary);
}

.close-btn {
  width: 32px;
  height: 32px;
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

.setting-item {
  margin-bottom: 16px;
}

.setting-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-primary);
}

.input-group {
  display: flex;
  gap: 8px;
}

.input-group .url-input {
  flex: 1;
  padding: 10px 14px;
  font-size: 0.9rem;
}

.input-group .btn {
  padding: 10px 16px;
  white-space: nowrap;
}

.setting-hint {
  margin-top: 8px;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.message {
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 0.9rem;
  margin-top: 12px;
}

.message.success {
  background: rgba(78, 205, 196, 0.1);
  border: 1px solid var(--success);
  color: var(--success);
}

.message.error {
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid var(--error);
  color: var(--error);
}

@media (max-width: 480px) {
  .settings-panel {
    width: calc(100vw - 40px);
    right: -10px;
  }

  .input-group {
    flex-direction: column;
  }

  .input-group .btn {
    width: 100%;
  }
}
</style>
