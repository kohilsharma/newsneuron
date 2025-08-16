<template>
  <div
    class="absolute right-0 top-12 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50"
  >
    <div class="p-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <h3 class="font-semibold text-gray-900">Notifications</h3>
        <button
          v-if="unreadCount > 0"
          @click="markAllRead"
          class="text-sm text-primary-600 hover:text-primary-700"
        >
          Mark all read
        </button>
      </div>
    </div>

    <div class="max-h-96 overflow-y-auto">
      <div
        v-if="notifications.length === 0"
        class="p-6 text-center text-gray-500"
      >
        <BellIcon class="w-8 h-8 mx-auto mb-2 text-gray-300" />
        <p>No notifications yet</p>
      </div>

      <div v-else>
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
          :class="{ 'bg-blue-50': !notification.read }"
          @click="markAsRead(notification.id)"
        >
          <div class="flex items-start">
            <div class="flex-shrink-0 mr-3">
              <div
                class="w-2 h-2 rounded-full mt-2"
                :class="notification.read ? 'bg-gray-300' : 'bg-primary-500'"
              ></div>
            </div>

            <div class="flex-1 min-w-0">
              <p
                v-if="notification.title"
                class="font-medium text-gray-900 text-sm"
              >
                {{ notification.title }}
              </p>
              <p
                class="text-gray-600 text-sm"
                :class="{ 'mt-1': notification.title }"
              >
                {{ notification.message }}
              </p>
              <p class="text-xs text-gray-500 mt-1">
                {{ formatTime(notification.timestamp) }}
              </p>
            </div>

            <button
              @click.stop="removeNotification(notification.id)"
              class="flex-shrink-0 ml-2 text-gray-400 hover:text-gray-600"
            >
              <XMarkIcon class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="notifications.length > 0"
      class="p-3 border-t border-gray-200 text-center"
    >
      <button
        @click="clearAll"
        class="text-sm text-gray-600 hover:text-gray-800"
      >
        Clear all notifications
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useAppStore } from "@/stores/app";
import { formatDistanceToNow } from "date-fns";
import { BellIcon, XMarkIcon } from "@heroicons/vue/24/outline";

const emit = defineEmits(["close"]);

const appStore = useAppStore();

const notifications = computed(() => appStore.notifications.slice(0, 10)); // Show max 10
const unreadCount = computed(() => appStore.unreadNotifications.length);

function markAsRead(id) {
  appStore.markNotificationRead(id);
}

function markAllRead() {
  appStore.markAllNotificationsRead();
}

function removeNotification(id) {
  appStore.removeNotification(id);
}

function clearAll() {
  appStore.clearAllNotifications();
  emit("close");
}

function formatTime(timestamp) {
  try {
    const date = new Date(timestamp);
    return formatDistanceToNow(date, { addSuffix: true });
  } catch {
    return "Just now";
  }
}
</script>
