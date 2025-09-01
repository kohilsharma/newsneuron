<template>
  <div class="dashboard-view h-full overflow-y-auto">
    
    <!-- Hero Section -->
    <section class="hero-section relative px-6 py-12 bg-gradient-to-br from-neuron-bg-primary via-neuron-bg-content to-neuron-bg-primary">
      <div class="content-width">
        <div class="text-center space-y-6">
          
          <!-- Main Heading -->
          <h1 class="text-4xl lg:text-5xl font-ui font-bold text-gradient">
            Your Neural News Feed
          </h1>
          
          <!-- Subtitle -->
          <p class="text-xl text-neuron-text-secondary max-w-2xl mx-auto leading-relaxed">
            AI-curated insights from the world's information, 
            <span class="text-neuron-glow">processed like interconnected neurons</span> 
            for maximum clarity and understanding.
          </p>
          
          <!-- Quick Stats -->
          <div class="flex justify-center items-center space-x-8 pt-6">
            <div class="text-center">
              <div class="text-2xl font-bold text-neuron-glow">{{ totalFlashcards }}</div>
              <div class="text-sm text-neuron-text-secondary">Insights</div>
            </div>
            <div class="w-px h-8 bg-neuron-border"></div>
            <div class="text-center">
              <div class="text-2xl font-bold text-neuron-glow">{{ connectionsCount }}</div>
              <div class="text-sm text-neuron-text-secondary">Connections</div>
            </div>
            <div class="w-px h-8 bg-neuron-border"></div>
            <div class="text-center">
              <div class="text-2xl font-bold text-neuron-glow">{{ todayCount }}</div>
              <div class="text-sm text-neuron-text-secondary">Today</div>
            </div>
          </div>
          
        </div>
      </div>
      
      <!-- Animated background particles -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div v-for="i in 20" :key="i" 
             class="absolute w-1 h-1 bg-neuron-glow/20 rounded-full animate-pulse"
             :style="particleStyle(i)">
        </div>
      </div>
    </section>
    
    <!-- Quick Actions Bar -->
    <section class="quick-actions bg-neuron-bg-content/50 backdrop-blur-sm border-b border-neuron-border sticky top-0 z-30">
      <div class="content-width px-6 py-4">
        <div class="flex items-center justify-between">
          
          <!-- Left Actions -->
          <div class="flex items-center space-x-4">
            <h2 class="text-lg font-ui font-medium text-neuron-text-primary">Latest Insights</h2>
            <div class="flex items-center space-x-2">
              <div class="w-2 h-2 bg-neuron-glow rounded-full animate-pulse"></div>
              <span class="text-sm text-neuron-text-secondary">Live Feed</span>
            </div>
          </div>
          
          <!-- Filter & Sort Controls -->
          <div class="flex items-center space-x-3">
            
            <!-- View Toggle -->
            <div class="flex items-center bg-neuron-bg-primary rounded-lg p-1">
              <button
                @click="viewMode = 'masonry'"
                :class="viewMode === 'masonry' ? 'btn-neuron text-xs px-3 py-1' : 'btn-ghost text-xs px-3 py-1'"
              >
                <LayoutGrid class="w-4 h-4 mr-1" />
                Cards
              </button>
              <button
                @click="viewMode = 'list'"
                :class="viewMode === 'list' ? 'btn-neuron text-xs px-3 py-1' : 'btn-ghost text-xs px-3 py-1'"
              >
                <List class="w-4 h-4 mr-1" />
                List
              </button>
            </div>
            
            <!-- Filter Dropdown -->
            <div class="relative">
              <button
                @click="showFilters = !showFilters"
                class="btn-ghost text-sm"
                :class="{ 'text-neuron-glow': hasActiveFilters }"
              >
                <Filter class="w-4 h-4 mr-2" />
                Filter
                <ChevronDown class="w-4 h-4 ml-1" />
              </button>
              
              <!-- Filter Menu -->
              <div v-if="showFilters" class="absolute right-0 top-full mt-2 w-64 bg-neuron-bg-content border border-neuron-border rounded-lg shadow-neuron-lg z-40 p-4">
                <div class="space-y-4">
                  
                  <!-- Category Filter -->
                  <div>
                    <label class="text-sm font-medium text-neuron-text-primary">Category</label>
                    <select v-model="selectedCategory" class="input-neuron mt-1 text-sm">
                      <option value="">All Categories</option>
                      <option value="technology">Technology</option>
                      <option value="politics">Politics</option>
                      <option value="business">Business</option>
                      <option value="science">Science</option>
                    </select>
                  </div>
                  
                  <!-- Time Range -->
                  <div>
                    <label class="text-sm font-medium text-neuron-text-primary">Time Range</label>
                    <select v-model="selectedTimeRange" class="input-neuron mt-1 text-sm">
                      <option value="today">Today</option>
                      <option value="week">This Week</option>
                      <option value="month">This Month</option>
                      <option value="all">All Time</option>
                    </select>
                  </div>
                  
                  <!-- Clear Filters -->
                  <button @click="clearFilters" class="btn-ghost text-sm w-full">
                    Clear Filters
                  </button>
                  
                </div>
              </div>
            </div>
            
            <!-- Refresh -->
            <button
              @click="refreshFeed"
              class="btn-icon"
              :class="{ 'animate-spin': isRefreshing }"
              title="Refresh feed"
            >
              <RefreshCw class="w-4 h-4" />
            </button>
            
          </div>
        </div>
      </div>
    </section>
    
    <!-- Main Content Area -->
    <section class="main-content px-6 py-8">
      <div class="content-width">
        
        <!-- Loading State -->
        <div v-if="isLoading" class="flex justify-center items-center py-20">
          <SynapseLoader size="lg" show-text loading-text="Analyzing neural connections..." />
        </div>
        
        <!-- Empty State -->
        <div v-else-if="filteredFlashcards.length === 0" class="text-center py-20">
          <div class="w-24 h-24 mx-auto mb-6 bg-neuron-bg-content rounded-full flex items-center justify-center">
            <Brain class="w-12 h-12 text-neuron-text-secondary" />
          </div>
          <h3 class="text-xl font-ui font-medium text-neuron-text-primary mb-2">No insights found</h3>
          <p class="text-neuron-text-secondary mb-6">Try adjusting your filters or check back later for new content.</p>
          <button @click="clearFilters" class="btn-neuron">
            Clear Filters
          </button>
        </div>
        
        <!-- Flashcards Grid (Masonry Layout) -->
        <div v-else-if="viewMode === 'masonry'" 
             class="masonry-grid columns-1 md:columns-2 lg:columns-3 xl:columns-4 gap-6 space-y-6">
          
          <FlashcardPreview
            v-for="flashcard in filteredFlashcards"
            :key="flashcard.id"
            :flashcard="flashcard"
            class="break-inside-avoid mb-6 animate-fade-in"
            @click="openFlashcard(flashcard)"
            @bookmark="toggleBookmark(flashcard)"
            @share="shareFlashcard(flashcard)"
          />
          
        </div>
        
        <!-- List View -->
        <div v-else class="space-y-4">
          <FlashcardListItem
            v-for="flashcard in filteredFlashcards"
            :key="flashcard.id"
            :flashcard="flashcard"
            @click="openFlashcard(flashcard)"
            @bookmark="toggleBookmark(flashcard)"
            @share="shareFlashcard(flashcard)"
          />
        </div>
        
        <!-- Load More -->
        <div v-if="hasMore && !isLoading" class="text-center pt-12">
          <button
            @click="loadMore"
            class="btn-ghost"
            :disabled="isLoadingMore"
          >
            <Loader2 v-if="isLoadingMore" class="w-4 h-4 mr-2 animate-spin" />
            <Plus v-else class="w-4 h-4 mr-2" />
            Load More Insights
          </button>
        </div>
        
      </div>
    </section>
    
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// Icons
import {
  LayoutGrid,
  List,
  Filter,
  ChevronDown,
  RefreshCw,
  Brain,
  Plus,
  Loader2
} from 'lucide-vue-next'

// Components
import SynapseLoader from '@/components/ui/SynapseLoader.vue'
import FlashcardPreview from '@/components/flashcards/FlashcardPreview.vue'
import FlashcardListItem from '@/components/flashcards/FlashcardListItem.vue'

// Mock data for development
const mockFlashcards = ref([
  {
    id: 1,
    title: "AI Breakthrough in Quantum Computing",
    summary: "Scientists achieve quantum supremacy with new AI-assisted algorithms, potentially revolutionizing cryptography and drug discovery.",
    category: "technology",
    created_at: new Date().toISOString(),
    connections: [2, 3],
    source: "Nature",
    reading_time: "3 min read"
  },
  {
    id: 2,
    title: "Global Climate Summit Results",
    summary: "World leaders commit to ambitious carbon reduction targets following breakthrough negotiations on renewable energy infrastructure.",
    category: "politics",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    connections: [1],
    source: "Reuters",
    reading_time: "5 min read"
  },
  {
    id: 3,
    title: "Market Volatility Amid Tech Earnings",
    summary: "Technology stocks show mixed results as investors react to AI spending announcements and regulatory concerns.",
    category: "business",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(),
    connections: [1],
    source: "Financial Times",
    reading_time: "2 min read"
  }
])

// Reactive state
const viewMode = ref('masonry')
const showFilters = ref(false)
const selectedCategory = ref('')
const selectedTimeRange = ref('today')
const isRefreshing = ref(false)
const isLoading = ref(false)
const isLoadingMore = ref(false)
const hasMore = ref(true)

// Computed
const totalFlashcards = computed(() => mockFlashcards.value.length)
const connectionsCount = computed(() => mockFlashcards.value.reduce((acc, card) => acc + (card.connections?.length || 0), 0))
const todayCount = computed(() => mockFlashcards.value.filter(card => isToday(card.created_at)).length)

const hasActiveFilters = computed(() => 
  selectedCategory.value !== '' || selectedTimeRange.value !== 'all'
)

const filteredFlashcards = computed(() => {
  let filtered = [...mockFlashcards.value]
  
  // Category filter
  if (selectedCategory.value) {
    filtered = filtered.filter(card => 
      card.category?.toLowerCase() === selectedCategory.value.toLowerCase()
    )
  }
  
  // Time range filter
  if (selectedTimeRange.value !== 'all') {
    const now = new Date()
    filtered = filtered.filter(card => {
      const cardDate = new Date(card.created_at)
      switch (selectedTimeRange.value) {
        case 'today':
          return isToday(cardDate)
        case 'week':
          return now - cardDate <= 7 * 24 * 60 * 60 * 1000
        case 'month':
          return now - cardDate <= 30 * 24 * 60 * 60 * 1000
        default:
          return true
      }
    })
  }
  
  return filtered
})

// Methods
const particleStyle = (index) => {
  return {
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    animationDelay: `${Math.random() * 3}s`,
    animationDuration: `${3 + Math.random() * 2}s`
  }
}

const isToday = (date) => {
  const today = new Date()
  const cardDate = new Date(date)
  return cardDate.toDateString() === today.toDateString()
}

const refreshFeed = async () => {
  isRefreshing.value = true
  // Simulate API call
  setTimeout(() => {
    isRefreshing.value = false
  }, 1000)
}

const clearFilters = () => {
  selectedCategory.value = ''
  selectedTimeRange.value = 'all'
  showFilters.value = false
}

const openFlashcard = (flashcard) => {
  console.log('Opening flashcard:', flashcard)
}

const toggleBookmark = (flashcard) => {
  console.log('Toggle bookmark:', flashcard)
}

const shareFlashcard = (flashcard) => {
  console.log('Share flashcard:', flashcard)
}

const loadMore = () => {
  isLoadingMore.value = true
  setTimeout(() => {
    isLoadingMore.value = false
  }, 1000)
}

// Close filters when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showFilters.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* Masonry Grid Optimization */
.masonry-grid {
  column-fill: balance;
}

/* Hero section gradient animation */
.hero-section {
  background: linear-gradient(135deg, 
    var(--neuron-bg-primary) 0%, 
    var(--neuron-bg-content) 50%, 
    var(--neuron-bg-primary) 100%);
  background-size: 200% 200%;
  animation: gradient-shift 8s ease-in-out infinite;
}

@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

/* Smooth transitions for layout changes */
.main-content {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Enhanced quick actions bar */
.quick-actions {
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

/* Focus states for accessibility */
button:focus-visible,
select:focus-visible {
  outline: 2px solid var(--neuron-glow);
  outline-offset: 2px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .masonry-grid {
    columns: 1;
  }
  
  .hero-section {
    padding: 2rem 1rem;
  }
}
</style>
