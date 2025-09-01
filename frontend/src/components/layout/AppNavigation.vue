<template>
  <nav class="navbar bg-neuron-bg-content border-b border-neuron-border sticky top-0 z-50 backdrop-blur-sm">
    <div class="navbar-container max-w-8xl mx-auto px-6 py-4">
      <div class="flex items-center justify-between">
        
        <!-- Left: Logo & Brand -->
        <div class="flex items-center space-x-6">
          <div class="flex items-center space-x-3">
            <NeuronLogo class="w-8 h-8 text-neuron-glow animate-synapse-pulse" />
            <div class="flex flex-col">
              <h1 class="text-lg font-ui font-bold text-gradient">NewsNeuron</h1>
              <p class="text-xs text-neuron-text-secondary">AI News Analysis</p>
            </div>
          </div>
          
          <!-- Desktop Navigation Links -->
          <div class="hidden lg:flex items-center space-x-1">
            <NavLink
              to="/"
              :icon="LayoutDashboard"
              horizontal
            >
              Dashboard
            </NavLink>
            
            <NavLink
              to="/chat"
              :icon="MessageSquare"
              horizontal
            >
              Chat
            </NavLink>
            
            <NavLink
              to="/search"
              :icon="Search"
              horizontal
            >
              Search
            </NavLink>
            
            <NavLink
              to="/timeline"
              :icon="Clock"
              horizontal
            >
              Timeline
            </NavLink>
            
            <NavLink
              to="/flashcards"
              :icon="BookOpen"
              horizontal
              :badge="flashcardCount > 0 ? flashcardCount.toString() : null"
            >
              Flashcards
            </NavLink>
            
            <NavLink
              to="/about"
              :icon="HelpCircle"
              horizontal
            >
              About
            </NavLink>
          </div>
        </div>
        
        <!-- Right: Status & Actions -->
        <div class="flex items-center space-x-4">
          
          <!-- Neural Status Indicator -->
          <div class="hidden md:flex items-center space-x-2">
            <div class="flex items-center space-x-1">
              <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
              <span class="text-xs text-green-400 font-medium">Neural Active</span>
            </div>
            
            <!-- Mini Activity Bars -->
            <div class="flex space-x-1">
              <div 
                v-for="i in 4" 
                :key="i"
                class="w-1 h-4 bg-neuron-glow/20 rounded-full overflow-hidden"
              >
                <div 
                  class="h-full bg-gradient-to-t from-neuron-glow to-neuron-glow-hover animate-pulse"
                  :style="{ height: Math.random() * 100 + '%' }"
                ></div>
              </div>
            </div>
          </div>
          
          <!-- Settings Button -->
          <button class="btn-icon p-2">
            <Settings class="w-5 h-5" />
          </button>
          
          <!-- Mobile Menu Toggle -->
          <button 
            @click="showMobileMenu = !showMobileMenu"
            class="lg:hidden btn-icon p-2"
            :aria-label="showMobileMenu ? 'Close menu' : 'Open menu'"
          >
            <Menu v-if="!showMobileMenu" class="w-5 h-5" />
            <X v-else class="w-5 h-5" />
          </button>
        </div>
      </div>
      
      <!-- Mobile Menu -->
      <div 
        v-if="showMobileMenu"
        class="lg:hidden mt-4 pt-4 border-t border-neuron-border"
      >
        <div class="grid grid-cols-2 gap-2">
          <NavLink
            to="/"
            :icon="LayoutDashboard"
            mobile
            @click="showMobileMenu = false"
          >
            Dashboard
          </NavLink>
          
          <NavLink
            to="/chat"
            :icon="MessageSquare"
            mobile
            @click="showMobileMenu = false"
          >
            Chat
          </NavLink>
          
          <NavLink
            to="/search"
            :icon="Search"
            mobile
            @click="showMobileMenu = false"
          >
            Search
          </NavLink>
          
          <NavLink
            to="/timeline"
            :icon="Clock"
            mobile
            @click="showMobileMenu = false"
          >
            Timeline
          </NavLink>
          
          <NavLink
            to="/flashcards"
            :icon="BookOpen"
            mobile
            :badge="flashcardCount > 0 ? flashcardCount.toString() : null"
            @click="showMobileMenu = false"
          >
            Flashcards
          </NavLink>
          
          <NavLink
            to="/about"
            :icon="HelpCircle"
            mobile
            @click="showMobileMenu = false"
          >
            About
          </NavLink>
        </div>
        
        <!-- Mobile Neural Status -->
        <div class="mt-4 pt-4 border-t border-neuron-border flex items-center justify-center space-x-2">
          <div class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
          <span class="text-xs text-green-400 font-medium">Neural System Active</span>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useFlashcardsStore } from '@/stores/flashcards'

// Icons
import {
  LayoutDashboard,
  MessageSquare,
  Search,
  Clock,
  BookOpen,
  HelpCircle,
  Settings,
  Menu,
  X
} from 'lucide-vue-next'

// Components
import NavLink from './NavLink.vue'
import NeuronLogo from '@/components/ui/NeuronLogo.vue'

// State
const showMobileMenu = ref(false)

// Store
const flashcardsStore = useFlashcardsStore()

// Computed
const flashcardCount = computed(() => flashcardsStore.flashcards.length)
</script>

<style scoped>
/* Navbar Styles */
.navbar {
  background: rgba(32, 35, 42, 0.95);
  backdrop-filter: blur(8px);
}

/* Text Gradient for Brand */
.text-gradient {
  background: linear-gradient(135deg, theme('colors.neuron.glow'), theme('colors.neuron.glow-hover'));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Responsive container */
.navbar-container {
  max-width: 1440px;
}

/* Mobile menu animation */
.mobile-menu-enter-active,
.mobile-menu-leave-active {
  transition: all 0.3s ease;
}

.mobile-menu-enter-from,
.mobile-menu-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Animation Performance */
@media (prefers-reduced-motion: reduce) {
  .animate-pulse,
  .animate-synapse-pulse {
    animation: none !important;
  }
}
</style>
