<template>
  <div class="text-center">
    <div class="relative">
      <!-- Step Number -->
      <div
        class="w-12 h-12 mx-auto mb-4 bg-primary-600 text-white rounded-full flex items-center justify-center font-bold text-lg"
      >
        {{ number }}
      </div>

      <!-- Step Icon -->
      <div
        class="absolute -top-2 -right-2 w-8 h-8 bg-accent-500 text-white rounded-full flex items-center justify-center"
      >
        <component :is="step.icon" class="w-4 h-4" />
      </div>
    </div>

    <h3 class="text-xl font-semibold text-gray-900 mb-3">
      {{ step.title }}
    </h3>

    <p class="text-gray-600">
      {{ step.description }}
    </p>
  </div>
</template>

<script setup>
defineProps({
  step: {
    type: Object,
    required: true,
  },
  number: {
    type: Number,
    required: true,
  },
});
</script>
