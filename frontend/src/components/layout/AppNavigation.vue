<template>
  <nav class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <!-- Logo and Brand -->
        <div class="flex items-center">
          <RouterLink to="/" class="flex items-center space-x-3 group">
            <div
              class="w-8 h-8 bg-gradient-to-r from-primary-600 to-accent-600 rounded-lg flex items-center justify-center"
            >
              <span class="text-white font-bold text-sm">NN</span>
            </div>
            <div class="hidden sm:block">
              <h1 class="text-xl font-bold text-gradient">NewsNeuron</h1>
              <p class="text-xs text-gray-500 -mt-1">
                Where News Meets Intelligence
              </p>
            </div>
          </RouterLink>
        </div>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center space-x-1">
          <RouterLink
            v-for="item in navigationItems"
            :key="item.name"
            :to="item.to"
            class="nav-link"
            :class="{ 'nav-link-active': $route.name === item.name }"
          >
            <component :is="item.icon" class="w-4 h-4" />
            <span>{{ item.label }}</span>
          </RouterLink>
        </div>

        <!-- Right Side Actions -->
        <div class="flex items-center space-x-3">
          <!-- Search Button -->
          <button
            @click="openQuickSearch"
            class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors duration-200"
            title="Quick Search (Ctrl+K)"
          >
            <MagnifyingGlassIcon class="w-5 h-5" />
          </button>

          <!-- Theme Toggle -->
          <button
            @click="appStore.toggleTheme()"
            class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors duration-200"
            :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
          >
            <SunIcon v-if="isDarkMode" class="w-5 h-5" />
            <MoonIcon v-else class="w-5 h-5" />
          </button>

          <!-- Notifications -->
          <div class="relative">
            <button
              @click="showNotifications = !showNotifications"
              class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              title="Notifications"
            >
              <BellIcon class="w-5 h-5" />
              <span
                v-if="unreadNotifications.length > 0"
                class="absolute -top-1 -right-1 w-3 h-3 bg-error-500 text-white text-xs rounded-full flex items-center justify-center"
              >
                {{
                  unreadNotifications.length > 9
                    ? "9+"
                    : unreadNotifications.length
                }}
              </span>
            </button>

            <!-- Notifications Dropdown -->
            <NotificationDropdown
              v-if="showNotifications"
              @close="showNotifications = false"
            />
          </div>

          <!-- Mobile Menu Button -->
          <button
            @click="mobileMenuOpen = !mobileMenuOpen"
            class="md:hidden p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors duration-200"
          >
            <Bars3Icon v-if="!mobileMenuOpen" class="w-5 h-5" />
            <XMarkIcon v-else class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile Navigation Menu -->
    <div
      v-if="mobileMenuOpen"
      class="md:hidden border-t border-gray-200 bg-white"
    >
      <div class="px-4 py-3 space-y-1">
        <RouterLink
          v-for="item in navigationItems"
          :key="item.name"
          :to="item.to"
          class="mobile-nav-link"
          :class="{ 'mobile-nav-link-active': $route.name === item.name }"
          @click="mobileMenuOpen = false"
        >
          <component :is="item.icon" class="w-5 h-5" />
          <span>{{ item.label }}</span>
        </RouterLink>
      </div>
    </div>

    <!-- Quick Search Modal -->
    <QuickSearchModal v-if="quickSearchOpen" @close="quickSearchOpen = false" />
  </nav>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { RouterLink } from "vue-router";
import { useAppStore } from "@/stores/app";

// Icons
import {
  MagnifyingGlassIcon,
  BellIcon,
  SunIcon,
  MoonIcon,
  Bars3Icon,
  XMarkIcon,
  HomeIcon,
  ChatBubbleLeftRightIcon,
  RectangleStackIcon,
  ClockIcon,
  ChartBarIcon,
} from "@heroicons/vue/24/outline";

// Components
import NotificationDropdown from "@/components/ui/NotificationDropdown.vue";
import QuickSearchModal from "@/components/ui/QuickSearchModal.vue";

// Store
const appStore = useAppStore();

// State
const mobileMenuOpen = ref(false);
const showNotifications = ref(false);
const quickSearchOpen = ref(false);

// Computed
const isDarkMode = computed(() => appStore.isDarkMode);
const unreadNotifications = computed(() => appStore.unreadNotifications);

// Navigation items
const navigationItems = [
  {
    name: "home",
    label: "Home",
    to: "/",
    icon: HomeIcon,
  },
  {
    name: "chat",
    label: "AI Chat",
    to: "/chat",
    icon: ChatBubbleLeftRightIcon,
  },
  {
    name: "flashcards",
    label: "Flashcards",
    to: "/flashcards",
    icon: RectangleStackIcon,
  },
  {
    name: "timeline",
    label: "Timeline",
    to: "/timeline",
    icon: ClockIcon,
  },
  {
    name: "dashboard",
    label: "Dashboard",
    to: "/dashboard",
    icon: ChartBarIcon,
  },
];

// Methods
function openQuickSearch() {
  quickSearchOpen.value = true;
}

function handleKeydown(event) {
  // Ctrl+K or Cmd+K for quick search
  if ((event.ctrlKey || event.metaKey) && event.key === "k") {
    event.preventDefault();
    openQuickSearch();
  }

  // Escape to close mobile menu
  if (event.key === "Escape") {
    mobileMenuOpen.value = false;
    showNotifications.value = false;
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener("keydown", handleKeydown);
});

onUnmounted(() => {
  document.removeEventListener("keydown", handleKeydown);
});
</script>

<style scoped>
.nav-link {
  @apply flex items-center space-x-2 px-3 py-2 text-sm font-medium text-gray-600 rounded-lg hover:text-gray-900 hover:bg-gray-100 transition-all duration-200;
}

.nav-link-active {
  @apply text-primary-600 bg-primary-50 hover:text-primary-700 hover:bg-primary-100;
}

.mobile-nav-link {
  @apply flex items-center space-x-3 px-3 py-2 text-base font-medium text-gray-600 rounded-lg hover:text-gray-900 hover:bg-gray-100 transition-all duration-200;
}

.mobile-nav-link-active {
  @apply text-primary-600 bg-primary-50 hover:text-primary-700 hover:bg-primary-100;
}
</style>
