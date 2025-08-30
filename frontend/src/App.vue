<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Debug Info (temporary) -->
    <div class="fixed top-4 right-4 bg-black/70 text-white p-2 rounded text-xs z-50">
      Current Route: {{ $route.path }}<br>
      Route Name: {{ $route.name }}<br>
      Is Loading: {{ isLoading }}<br>
      <button @click="testNavigation" class="mt-1 px-2 py-1 bg-blue-500 text-white rounded text-xs">
        Test Chat Navigation
      </button>
    </div>

    <!-- Navigation -->
    <AppNavigation />

    <!-- Main Content -->
    <main class="flex-1">
      <div class="min-h-full">
        <transition name="fade" mode="out-in">
          <RouterView />
        </transition>
      </div>
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
import { RouterView, useRoute, useRouter } from "vue-router";
import { useAppStore } from "@/stores/app";

// Components
import AppNavigation from "@/components/layout/AppNavigation.vue";
import AppFooter from "@/components/layout/AppFooter.vue";
import LoadingIndicator from "@/components/ui/LoadingIndicator.vue";
import ToastContainer from "@/components/ui/ToastContainer.vue";

// Store
const appStore = useAppStore();

// Route
const $route = useRoute();
const $router = useRouter();

// Computed
const isLoading = computed(() => appStore.isLoading);

// Methods
function testNavigation() {
  console.log('Testing navigation to /chat');
  $router.push('/chat');
}

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

/* Ensure navigation is clickable */
nav {
  position: relative;
  z-index: 40;
}

/* Debug panel styling */
.fixed.top-4.right-4 {
  z-index: 9999;
}

/* Route transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
