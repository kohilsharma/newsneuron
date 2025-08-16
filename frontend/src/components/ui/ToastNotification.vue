<template>
  <div
    class="bg-white rounded-lg shadow-lg border-l-4 p-4 max-w-sm cursor-pointer"
    :class="[
      typeClasses[notification.type],
      { 'opacity-75': notification.read },
    ]"
    @click="handleClick"
  >
    <div class="flex items-start">
      <div class="flex-shrink-0">
        <component
          :is="typeIcon[notification.type]"
          class="w-5 h-5"
          :class="typeIconClasses[notification.type]"
        />
      </div>

      <div class="ml-3 flex-1">
        <p v-if="notification.title" class="font-medium text-gray-900 text-sm">
          {{ notification.title }}
        </p>
        <p
          class="text-gray-700 text-sm"
          :class="{ 'mt-1': notification.title }"
        >
          {{ notification.message }}
        </p>
      </div>

      <div class="ml-3 flex-shrink-0">
        <button
          @click.stop="$emit('close', notification.id)"
          class="text-gray-400 hover:text-gray-600 transition-colors duration-200"
        >
          <XMarkIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Progress bar for auto-hide -->
    <div
      v-if="notification.autoHide && showProgress"
      class="mt-2 h-1 bg-gray-200 rounded-full overflow-hidden"
    >
      <div
        class="h-full transition-all ease-linear"
        :class="typeProgressClasses[notification.type]"
        :style="{ width: `${progress}%` }"
      ></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  InformationCircleIcon,
  XMarkIcon,
} from "@heroicons/vue/24/outline";

const props = defineProps({
  notification: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["close"]);

// State
const progress = ref(100);
const showProgress = ref(true);
let progressInterval = null;

// Type configurations
const typeClasses = {
  success: "border-success-400",
  error: "border-error-400",
  warning: "border-warning-400",
  info: "border-primary-400",
};

const typeIcon = {
  success: CheckCircleIcon,
  error: XCircleIcon,
  warning: ExclamationTriangleIcon,
  info: InformationCircleIcon,
};

const typeIconClasses = {
  success: "text-success-400",
  error: "text-error-400",
  warning: "text-warning-400",
  info: "text-primary-400",
};

const typeProgressClasses = {
  success: "bg-success-400",
  error: "bg-error-400",
  warning: "bg-warning-400",
  info: "bg-primary-400",
};

// Methods
function handleClick() {
  if (!props.notification.read) {
    // Mark as read if clicking on notification
    // This could trigger a store action if needed
  }
}

function startProgressTimer() {
  if (!props.notification.autoHide) return;

  const duration = props.notification.duration || 5000;
  const interval = 50; // Update every 50ms
  const step = (interval / duration) * 100;

  progressInterval = setInterval(() => {
    progress.value -= step;

    if (progress.value <= 0) {
      progress.value = 0;
      clearInterval(progressInterval);
      emit("close", props.notification.id);
    }
  }, interval);
}

function stopProgressTimer() {
  if (progressInterval) {
    clearInterval(progressInterval);
    progressInterval = null;
  }
}

// Lifecycle
onMounted(() => {
  if (props.notification.autoHide) {
    startProgressTimer();
  }
});

onUnmounted(() => {
  stopProgressTimer();
});
</script>
