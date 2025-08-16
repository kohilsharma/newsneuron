<template>
  <div class="fixed top-4 right-4 z-50 space-y-3 max-w-sm">
    <TransitionGroup name="toast" tag="div">
      <ToastNotification
        v-for="notification in notifications"
        :key="notification.id"
        :notification="notification"
        @close="removeNotification"
      />
    </TransitionGroup>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useAppStore } from "@/stores/app";
import ToastNotification from "./ToastNotification.vue";

const appStore = useAppStore();

const notifications = computed(() => appStore.notifications);

function removeNotification(id) {
  appStore.removeNotification(id);
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>
