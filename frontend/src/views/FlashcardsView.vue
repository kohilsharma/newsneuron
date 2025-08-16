<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">News Flashcards</h1>
        <p class="text-gray-600 mt-2">
          AI-generated summaries of recent news stories
        </p>
      </div>

      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
        <div class="flex items-center">
          <InformationCircleIcon class="w-5 h-5 text-blue-500 mr-2" />
          <p class="text-blue-700 text-sm">
            Flashcards functionality will be implemented here. This is a
            placeholder view.
          </p>
        </div>
      </div>

      <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 6" :key="i" class="card">
          <div class="card-body">
            <div class="flex items-center justify-between mb-3">
              <span class="badge badge-primary">Sample Category</span>
              <span class="text-xs text-gray-500">2 hours ago</span>
            </div>

            <h3 class="font-semibold text-gray-900 mb-2">
              Sample Flashcard Title {{ i }}
            </h3>

            <p class="text-gray-600 text-sm mb-3">
              This is a sample flashcard summary that would contain key insights
              from recent news stories.
            </p>

            <div
              class="flex items-center justify-between text-xs text-gray-500"
            >
              <span>3 key points</span>
              <span>5 min read</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { InformationCircleIcon } from "@heroicons/vue/24/outline";
</script>
