<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Timeline Analysis</h1>
        <p class="text-gray-600 mt-2">
          Visualize story evolution and entity timelines
        </p>
      </div>

      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
        <div class="flex items-center">
          <InformationCircleIcon class="w-5 h-5 text-blue-500 mr-2" />
          <p class="text-blue-700 text-sm">
            Timeline functionality will be implemented here. This is a
            placeholder view.
          </p>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
        <div class="flex flex-col sm:flex-row gap-4 mb-6">
          <input
            type="text"
            placeholder="Enter entity name (e.g., OpenAI, Tesla, Elon Musk)"
            class="input flex-1"
            disabled
          />
          <button class="btn-primary" disabled>Generate Timeline</button>
        </div>

        <div class="grid md:grid-cols-4 gap-4">
          <div class="md:col-span-3">
            <h3 class="font-semibold text-gray-900 mb-4">Timeline View</h3>
            <div
              class="p-8 border-2 border-dashed border-gray-300 rounded-lg text-center text-gray-500"
            >
              <ClockIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Timeline visualization will appear here</p>
              <p class="text-sm mt-2">
                Enter an entity name to generate a timeline
              </p>
            </div>
          </div>

          <div>
            <h3 class="font-semibold text-gray-900 mb-4">Timeline Controls</h3>
            <div class="space-y-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"
                  >Date Range</label
                >
                <div class="space-y-2">
                  <input type="date" class="input" disabled />
                  <input type="date" class="input" disabled />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"
                  >Max Events</label
                >
                <select class="input" disabled>
                  <option>25 events</option>
                  <option>50 events</option>
                  <option>100 events</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2"
                  >View Type</label
                >
                <select class="input" disabled>
                  <option>Chronological</option>
                  <option>Clustered</option>
                  <option>Network</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="grid md:grid-cols-2 gap-6">
        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="font-semibold text-gray-900 mb-4">Related Entities</h3>
          <div class="text-center text-gray-500 py-8">
            <p>Related entities will appear here</p>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6">
          <h3 class="font-semibold text-gray-900 mb-4">Timeline Summary</h3>
          <div class="text-center text-gray-500 py-8">
            <p>Timeline statistics will appear here</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { InformationCircleIcon, ClockIcon } from "@heroicons/vue/24/outline";
</script>
