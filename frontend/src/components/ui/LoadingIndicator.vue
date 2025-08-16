<template>
  <div
    class="fixed inset-0 bg-black/20 backdrop-blur-sm z-50 flex items-center justify-center"
  >
    <div class="bg-white rounded-lg shadow-lg p-6 max-w-sm mx-4">
      <div class="flex items-center space-x-3">
        <div class="spinner spinner-md"></div>
        <div>
          <p class="font-medium text-gray-900">{{ title }}</p>
          <p v-if="message" class="text-sm text-gray-600 mt-1">{{ message }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: "Loading...",
  },
  message: {
    type: String,
    default: "",
  },
});
</script>
