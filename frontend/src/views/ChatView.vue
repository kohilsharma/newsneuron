<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div class="bg-white rounded-lg shadow-sm">
        <div class="p-6 border-b border-gray-200">
          <h1 class="text-2xl font-bold text-gray-900">AI Chat Assistant</h1>
          <p class="text-gray-600 mt-1">
            Ask questions about news and current events
          </p>
        </div>

        <div class="p-6">
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <div class="flex items-center">
              <InformationCircleIcon class="w-5 h-5 text-blue-500 mr-2" />
              <p class="text-blue-700 text-sm">
                Chat functionality will be implemented here. This is a
                placeholder view.
              </p>
            </div>
          </div>

          <div class="space-y-4">
            <div class="bg-gray-100 rounded-lg p-4">
              <p class="text-gray-700">👋 Welcome to NewsNeuron AI Chat!</p>
              <p class="text-gray-600 text-sm mt-1">
                This feature will allow you to have conversations with our AI
                assistant about news and current events.
              </p>
            </div>

            <div class="flex space-x-2">
              <input
                type="text"
                placeholder="Ask me about recent news..."
                class="input flex-1"
                disabled
              />
              <button class="btn-primary" disabled>Send</button>
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
