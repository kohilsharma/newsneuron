<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Search News</h1>
        <p class="text-gray-600 mt-2">
          Advanced semantic search through news articles
        </p>
      </div>

      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
        <div class="flex items-center">
          <InformationCircleIcon class="w-5 h-5 text-blue-500 mr-2" />
          <p class="text-blue-700 text-sm">
            Search functionality will be implemented here. This is a placeholder
            view.
          </p>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex space-x-4 mb-6">
          <input
            type="text"
            placeholder="Search for articles, entities, or topics..."
            class="input flex-1"
            disabled
          />
          <button class="btn-primary" disabled>Search</button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="md:col-span-2">
            <h3 class="font-semibold text-gray-900 mb-4">Search Results</h3>
            <div class="space-y-4">
              <div class="p-4 border border-gray-200 rounded-lg">
                <p class="text-gray-600">
                  No search results yet. Enter a query to get started.
                </p>
              </div>
            </div>
          </div>

          <div>
            <h3 class="font-semibold text-gray-900 mb-4">Filters</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"
                  >Search Type</label
                >
                <select class="input" disabled>
                  <option>Hybrid Search</option>
                  <option>Vector Search</option>
                  <option>Graph Search</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"
                  >Date Range</label
                >
                <input type="date" class="input" disabled />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"
                  >Entity Type</label
                >
                <select class="input" disabled>
                  <option>All Types</option>
                  <option>Person</option>
                  <option>Organization</option>
                  <option>Location</option>
                  <option>Event</option>
                </select>
              </div>
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
