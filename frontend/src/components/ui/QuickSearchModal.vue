<template>
  <div
    class="fixed inset-0 bg-black/20 backdrop-blur-sm z-50"
    @click="$emit('close')"
  >
    <div class="flex items-start justify-center min-h-screen pt-20 px-4">
      <div
        class="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-96"
        @click.stop
      >
        <div class="p-4 border-b border-gray-200">
          <div class="relative">
            <MagnifyingGlassIcon
              class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"
            />
            <input
              ref="searchInput"
              v-model="searchQuery"
              type="text"
              placeholder="Search news, entities, or topics..."
              class="w-full pl-10 pr-4 py-3 border-0 focus:ring-0 text-lg"
              @keydown.enter="performSearch"
              @keydown.escape="$emit('close')"
            />
          </div>
        </div>

        <div class="max-h-80 overflow-y-auto">
          <!-- Recent Searches -->
          <div v-if="!searchQuery && recentSearches.length > 0" class="p-4">
            <h3 class="text-sm font-medium text-gray-900 mb-3">
              Recent Searches
            </h3>
            <div class="space-y-1">
              <button
                v-for="search in recentSearches"
                :key="search"
                @click="selectSearch(search)"
                class="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md flex items-center"
              >
                <ClockIcon class="w-4 h-4 text-gray-400 mr-3" />
                {{ search }}
              </button>
            </div>
          </div>

          <!-- Search Suggestions -->
          <div v-else-if="searchQuery" class="p-4">
            <h3 class="text-sm font-medium text-gray-900 mb-3">Suggestions</h3>
            <div class="space-y-1">
              <button
                v-for="suggestion in searchSuggestions"
                :key="suggestion"
                @click="selectSearch(suggestion)"
                class="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md flex items-center"
              >
                <MagnifyingGlassIcon class="w-4 h-4 text-gray-400 mr-3" />
                {{ suggestion }}
              </button>
            </div>
          </div>

          <!-- Quick Actions -->
          <div v-if="!searchQuery" class="p-4 border-t border-gray-200">
            <h3 class="text-sm font-medium text-gray-900 mb-3">
              Quick Actions
            </h3>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="action in quickActions"
                :key="action.name"
                @click="performAction(action)"
                class="flex items-center p-3 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
              >
                <component
                  :is="action.icon"
                  class="w-4 h-4 text-gray-400 mr-3"
                />
                {{ action.name }}
              </button>
            </div>
          </div>
        </div>

        <div
          class="p-3 border-t border-gray-200 text-xs text-gray-500 flex items-center justify-between"
        >
          <div class="flex items-center space-x-4">
            <span class="flex items-center">
              <kbd class="px-2 py-1 bg-gray-100 rounded">Enter</kbd>
              <span class="ml-1">to search</span>
            </span>
            <span class="flex items-center">
              <kbd class="px-2 py-1 bg-gray-100 rounded">Esc</kbd>
              <span class="ml-1">to close</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from "vue";
import { useRouter } from "vue-router";
import {
  MagnifyingGlassIcon,
  ClockIcon,
  ChatBubbleLeftRightIcon,
  RectangleStackIcon,
  ChartBarIcon,
} from "@heroicons/vue/24/outline";

const emit = defineEmits(["close"]);
const router = useRouter();

const searchInput = ref(null);
const searchQuery = ref("");

// Mock data - replace with actual data from stores/API
const recentSearches = ref([
  "AI technology trends",
  "Climate change policy",
  "Tesla earnings",
  "OpenAI developments",
]);

const searchSuggestions = computed(() => {
  if (!searchQuery.value) return [];

  // Mock suggestions - implement actual suggestion logic
  const suggestions = [
    "artificial intelligence",
    "climate change",
    "technology trends",
    "political developments",
    "economic indicators",
  ];

  return suggestions
    .filter((s) => s.toLowerCase().includes(searchQuery.value.toLowerCase()))
    .slice(0, 5);
});

const quickActions = [
  {
    name: "AI Chat",
    icon: ChatBubbleLeftRightIcon,
    action: () => router.push("/chat"),
  },
  {
    name: "Flashcards",
    icon: RectangleStackIcon,
    action: () => router.push("/flashcards"),
  },
  {
    name: "Dashboard",
    icon: ChartBarIcon,
    action: () => router.push("/dashboard"),
  },
  {
    name: "Search",
    icon: MagnifyingGlassIcon,
    action: () => router.push("/search"),
  },
];

function performSearch() {
  if (searchQuery.value.trim()) {
    addToRecentSearches(searchQuery.value.trim());
    router.push(`/search?q=${encodeURIComponent(searchQuery.value.trim())}`);
    emit("close");
  }
}

function selectSearch(query) {
  searchQuery.value = query;
  performSearch();
}

function performAction(action) {
  action.action();
  emit("close");
}

function addToRecentSearches(query) {
  // Remove if already exists
  const index = recentSearches.value.indexOf(query);
  if (index > -1) {
    recentSearches.value.splice(index, 1);
  }

  // Add to beginning
  recentSearches.value.unshift(query);

  // Keep only last 5
  if (recentSearches.value.length > 5) {
    recentSearches.value = recentSearches.value.slice(0, 5);
  }

  // Save to localStorage
  localStorage.setItem(
    "newsNeuronRecentSearches",
    JSON.stringify(recentSearches.value),
  );
}

onMounted(async () => {
  // Load recent searches from localStorage
  const saved = localStorage.getItem("newsNeuronRecentSearches");
  if (saved) {
    try {
      recentSearches.value = JSON.parse(saved);
    } catch (error) {
      console.warn("Failed to load recent searches:", error);
    }
  }

  // Focus search input
  await nextTick();
  searchInput.value?.focus();
});
</script>
