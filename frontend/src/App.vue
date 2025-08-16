<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <AppNavigation />

    <!-- Main Content -->
    <main class="flex-1">
      <RouterView />
    </main>

    <!-- Footer -->
    <AppFooter />

    <!-- Global Loading Indicator -->
    <LoadingIndicator v-if="isLoading" />

    <!-- Toast Notifications -->
    <ToastContainer />
  </div>
</template>

<script setup>
import { computed } from "vue";
import { RouterView } from "vue-router";
import { useAppStore } from "@/stores/app";

// Components
import AppNavigation from "@/components/layout/AppNavigation.vue";
import AppFooter from "@/components/layout/AppFooter.vue";
import LoadingIndicator from "@/components/ui/LoadingIndicator.vue";
import ToastContainer from "@/components/ui/ToastContainer.vue";

// Store
const appStore = useAppStore();

// Computed
const isLoading = computed(() => appStore.isLoading);

// Initialize app
appStore.initialize();
</script>

<style scoped>
#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex: 1;
}
</style>
