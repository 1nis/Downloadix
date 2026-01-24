<template>
  <div class="progress-container" v-if="visible">
    <div class="progress-header">
      <span class="progress-status">{{ statusText }}</span>
      <span class="progress-percent">{{ percentDisplay }}</span>
    </div>

    <div class="progress-bar">
      <div
        class="progress-fill"
        :style="{ width: `${percent}%` }"
        :class="{ 'processing': status === 'processing' }"
      ></div>
    </div>

    <div class="progress-details">
      <div class="progress-bytes">
        <span class="label">Downloaded:</span>
        <span class="value">{{ downloadedStr }} / {{ totalStr }}</span>
      </div>
      <div class="progress-speed">
        <span class="label">Speed:</span>
        <span class="value">{{ speedStr }}</span>
      </div>
      <div class="progress-eta">
        <span class="label">ETA:</span>
        <span class="value">{{ etaStr }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  status: {
    type: String,
    default: 'starting'
  },
  percent: {
    type: Number,
    default: 0
  },
  downloadedStr: {
    type: String,
    default: '0 B'
  },
  totalStr: {
    type: String,
    default: '0 B'
  },
  speedStr: {
    type: String,
    default: '0 B/s'
  },
  etaStr: {
    type: String,
    default: '--:--'
  }
})

const statusText = computed(() => {
  switch (props.status) {
    case 'starting':
      return 'Starting download...'
    case 'downloading':
      return 'Downloading...'
    case 'processing':
      return 'Processing video...'
    case 'completed':
      return 'Download complete!'
    case 'error':
      return 'Download failed'
    default:
      return 'Preparing...'
  }
})

const percentDisplay = computed(() => {
  if (props.status === 'processing') {
    return 'Processing...'
  }
  return `${props.percent.toFixed(1)}%`
})
</script>

<style scoped>
.progress-container {
  background: var(--bg-card);
  border-radius: var(--border-radius);
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: var(--shadow);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-status {
  font-weight: 600;
  color: var(--text-primary);
}

.progress-percent {
  font-weight: 700;
  color: var(--accent);
  font-size: 1.1rem;
}

.progress-bar {
  height: 12px;
  background: var(--bg-secondary);
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 16px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), #a855f7);
  border-radius: 6px;
  transition: width 0.3s ease;
  position: relative;
}

.progress-fill::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent
  );
  animation: shimmer 2s infinite;
}

.progress-fill.processing {
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.progress-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.progress-details > div {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.progress-details .label {
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.progress-details .value {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9rem;
}

@media (max-width: 480px) {
  .progress-details {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .progress-details > div {
    flex-direction: row;
    justify-content: space-between;
  }

  .progress-details .label {
    margin-bottom: 0;
  }
}
</style>
