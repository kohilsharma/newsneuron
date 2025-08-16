<template>
  <div class="min-h-screen">
    <!-- Hero Section -->
    <section
      class="relative bg-gradient-to-br from-primary-50 via-white to-accent-50 py-20 sm:py-32"
    >
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center">
          <h1
            class="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6"
          >
            Where News Meets
            <span class="text-gradient">Intelligence</span>
          </h1>

          <p class="text-xl sm:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
            AI-powered news analysis with hybrid vector-graph intelligence.
            Discover insights, track stories, and understand the connections
            that matter.
          </p>

          <div
            class="flex flex-col sm:flex-row gap-4 justify-center items-center"
          >
            <RouterLink to="/chat" class="btn-primary btn-lg">
              <ChatBubbleLeftRightIcon class="w-5 h-5" />
              Start AI Chat
            </RouterLink>

            <RouterLink to="/flashcards" class="btn-outline btn-lg">
              <RectangleStackIcon class="w-5 h-5" />
              View Flashcards
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- Background decoration -->
      <div class="absolute inset-0 overflow-hidden pointer-events-none">
        <div
          class="absolute -top-40 -right-40 w-80 h-80 bg-gradient-to-br from-primary-200 to-accent-200 rounded-full opacity-20 blur-3xl"
        ></div>
        <div
          class="absolute -bottom-40 -left-40 w-80 h-80 bg-gradient-to-tr from-accent-200 to-primary-200 rounded-full opacity-20 blur-3xl"
        ></div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Intelligent News Analysis
          </h2>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Our hybrid AI system combines vector search with knowledge graphs to
            deliver deep insights into news and current events.
          </p>
        </div>

        <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          <FeatureCard
            v-for="feature in features"
            :key="feature.title"
            :feature="feature"
          />
        </div>
      </div>
    </section>

    <!-- How It Works Section -->
    <section class="py-20 bg-gray-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            How NewsNeuron Works
          </h2>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Our AI processes news like interconnected neurons, understanding
            both content and relationships between entities.
          </p>
        </div>

        <div class="grid lg:grid-cols-3 gap-8">
          <ProcessStep
            v-for="(step, index) in processSteps"
            :key="step.title"
            :step="step"
            :number="index + 1"
          />
        </div>
      </div>
    </section>

    <!-- Recent Activity Section -->
    <section class="py-20 bg-white">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <h2 class="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Latest Insights
          </h2>
          <p class="text-xl text-gray-600">
            Recent flashcards and trending topics from our AI analysis
          </p>
        </div>

        <div class="grid lg:grid-cols-2 gap-12">
          <!-- Recent Flashcards -->
          <div>
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-xl font-semibold text-gray-900">
                Recent Flashcards
              </h3>
              <RouterLink
                to="/flashcards"
                class="text-primary-600 hover:text-primary-700 font-medium"
              >
                View All →
              </RouterLink>
            </div>

            <div v-if="isLoadingFlashcards" class="space-y-4">
              <div v-for="i in 3" :key="i" class="skeleton-card"></div>
            </div>

            <div v-else class="space-y-4">
              <FlashcardPreview
                v-for="flashcard in recentFlashcards"
                :key="flashcard.id"
                :flashcard="flashcard"
              />
            </div>
          </div>

          <!-- Trending Topics -->
          <div>
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-xl font-semibold text-gray-900">
                Trending Topics
              </h3>
              <RouterLink
                to="/search"
                class="text-primary-600 hover:text-primary-700 font-medium"
              >
                Explore →
              </RouterLink>
            </div>

            <div v-if="isLoadingTrends" class="space-y-3">
              <div v-for="i in 5" :key="i" class="skeleton-text"></div>
            </div>

            <div v-else class="space-y-3">
              <TrendingTopic
                v-for="topic in trendingTopics"
                :key="topic.topic"
                :topic="topic"
              />
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-20 bg-gradient-to-r from-primary-600 to-accent-600">
      <div class="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
        <h2 class="text-3xl sm:text-4xl font-bold text-white mb-4">
          Ready to Transform Your News Experience?
        </h2>
        <p class="text-xl text-primary-100 mb-8">
          Join the future of news analysis with AI-powered insights and
          intelligent discovery.
        </p>

        <div class="flex flex-col sm:flex-row gap-4 justify-center">
          <RouterLink
            to="/chat"
            class="btn bg-white text-primary-600 hover:bg-gray-50 btn-lg"
          >
            Start Exploring
          </RouterLink>
          <RouterLink
            to="/about"
            class="btn border-white text-white hover:bg-white/10 btn-lg"
          >
            Learn More
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { RouterLink } from "vue-router";
import { useFlashcardsStore } from "@/stores/flashcards";
import { useErrorHandler } from "@/utils/errorHandler";

// Icons
import {
  ChatBubbleLeftRightIcon,
  RectangleStackIcon,
  MagnifyingGlassIcon,
  ClockIcon,
  CpuChipIcon,
  LightBulbIcon,
  GlobeAltIcon,
} from "@heroicons/vue/24/outline";

// Components
import FeatureCard from "@/components/ui/FeatureCard.vue";
import ProcessStep from "@/components/ui/ProcessStep.vue";
import FlashcardPreview from "@/components/flashcards/FlashcardPreview.vue";
import TrendingTopic from "@/components/ui/TrendingTopic.vue";

// Stores
const flashcardsStore = useFlashcardsStore();
const { withErrorHandling } = useErrorHandler();

// State
const isLoadingFlashcards = ref(false);
const isLoadingTrends = ref(false);
const recentFlashcards = ref([]);
const trendingTopics = ref([]);

// Features data
const features = [
  {
    title: "AI-Powered Chat",
    description:
      "Engage with our intelligent assistant for contextual news discussions and insights.",
    icon: ChatBubbleLeftRightIcon,
    color: "primary",
  },
  {
    title: "Smart Flashcards",
    description:
      "Get concise, AI-generated summaries of news stories with key insights highlighted.",
    icon: RectangleStackIcon,
    color: "accent",
  },
  {
    title: "Timeline Analysis",
    description:
      "Visualize story evolution and track entity relationships over time.",
    icon: ClockIcon,
    color: "success",
  },
  {
    title: "Semantic Search",
    description:
      "Advanced search that understands context and meaning, not just keywords.",
    icon: MagnifyingGlassIcon,
    color: "warning",
  },
];

// Process steps data
const processSteps = [
  {
    title: "Data Ingestion",
    description:
      "We collect and process news articles from multiple sources, extracting entities and generating embeddings.",
    icon: GlobeAltIcon,
  },
  {
    title: "AI Analysis",
    description:
      "Our hybrid AI system combines vector search with knowledge graphs for deep understanding.",
    icon: CpuChipIcon,
  },
  {
    title: "Intelligent Insights",
    description:
      "Generate personalized insights, timelines, and connections that matter to you.",
    icon: LightBulbIcon,
  },
];

// Methods
async function loadRecentFlashcards() {
  const { success, data } = await withErrorHandling(
    () => flashcardsStore.getRecentFlashcards(3),
    "Failed to load recent flashcards",
    {
      showLoading: false, // We handle loading state manually
      fallbackValue: [],
    },
  );

  if (success) {
    recentFlashcards.value = data;
  } else {
    recentFlashcards.value = [];
  }
}

async function loadTrendingTopics() {
  const { success, data } = await withErrorHandling(
    async () => {
      // Mock trending topics for now - replace with actual API call
      await new Promise((resolve) => setTimeout(resolve, 500)); // Simulate API delay
      return [
        {
          topic: "Artificial Intelligence",
          mention_count: 45,
          trend_score: 0.85,
        },
        { topic: "Climate Change", mention_count: 38, trend_score: 0.72 },
        { topic: "Technology", mention_count: 52, trend_score: 0.68 },
        { topic: "Politics", mention_count: 41, trend_score: 0.65 },
        { topic: "Economy", mention_count: 33, trend_score: 0.58 },
      ];
    },
    "Failed to load trending topics",
    {
      showLoading: false, // We handle loading state manually
      fallbackValue: [],
    },
  );

  if (success) {
    trendingTopics.value = data;
  } else {
    trendingTopics.value = [];
  }
}

// Lifecycle
onMounted(async () => {
  // Set loading states
  isLoadingFlashcards.value = true;
  isLoadingTrends.value = true;

  // Load data in parallel
  await Promise.all([
    loadRecentFlashcards().finally(() => (isLoadingFlashcards.value = false)),
    loadTrendingTopics().finally(() => (isLoadingTrends.value = false)),
  ]);
});
</script>

<style scoped>
.skeleton-card {
  @apply bg-gray-200 rounded-lg h-32 animate-pulse;
}
</style>
