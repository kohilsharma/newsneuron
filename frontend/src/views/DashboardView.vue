<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p class="text-gray-600 mt-2">
          Your personalized news analytics overview
        </p>
      </div>

      <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
        <div class="flex items-center">
          <InformationCircleIcon class="w-5 h-5 text-blue-500 mr-2" />
          <p class="text-blue-700 text-sm">
            Dashboard functionality will be implemented here. This is a
            placeholder view.
          </p>
        </div>
      </div>

      <!-- Stats Overview -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div
              class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center"
            >
              <ChartBarIcon class="w-6 h-6 text-blue-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Articles Read</p>
              <p class="text-2xl font-bold text-gray-900">0</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div
              class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center"
            >
              <RectangleStackIcon class="w-6 h-6 text-green-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Flashcards</p>
              <p class="text-2xl font-bold text-gray-900">0</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div
              class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center"
            >
              <ChatBubbleLeftRightIcon class="w-6 h-6 text-purple-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">AI Chats</p>
              <p class="text-2xl font-bold text-gray-900">0</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow-sm p-6">
          <div class="flex items-center">
            <div
              class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center"
            >
              <ClockIcon class="w-6 h-6 text-orange-600" />
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-600">Timelines</p>
              <p class="text-2xl font-bold text-gray-900">0</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="grid lg:grid-cols-3 gap-8">
        <!-- Recent Activity -->
        <div class="lg:col-span-2">
          <div class="bg-white rounded-lg shadow-sm p-6 mb-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              Recent Activity
            </h3>
            <div class="text-center text-gray-500 py-8">
              <ChartBarIcon class="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <p>Your activity will appear here</p>
              <p class="text-sm mt-2">Start exploring to see your analytics</p>
            </div>
          </div>

          <div class="bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              Trending Topics
            </h3>
            <div class="space-y-3">
              <div
                v-for="i in 5"
                :key="i"
                class="flex items-center justify-between p-3 border border-gray-200 rounded-lg"
              >
                <div>
                  <p class="font-medium text-gray-900">Sample Topic {{ i }}</p>
                  <p class="text-sm text-gray-600">{{ 10 + i }} mentions</p>
                </div>
                <div class="w-16 h-2 bg-gray-200 rounded-full">
                  <div
                    class="h-full bg-blue-500 rounded-full"
                    :style="{ width: `${20 + i * 10}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="space-y-6">
          <!-- Quick Actions -->
          <div class="bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              Quick Actions
            </h3>
            <div class="space-y-3">
              <RouterLink to="/chat" class="btn-outline w-full">
                <ChatBubbleLeftRightIcon class="w-4 h-4" />
                Start AI Chat
              </RouterLink>
              <RouterLink to="/flashcards" class="btn-outline w-full">
                <RectangleStackIcon class="w-4 h-4" />
                View Flashcards
              </RouterLink>
              <RouterLink to="/search" class="btn-outline w-full">
                <MagnifyingGlassIcon class="w-4 h-4" />
                Search News
              </RouterLink>
            </div>
          </div>

          <!-- Saved Items -->
          <div class="bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              Saved Items
            </h3>
            <div class="text-center text-gray-500 py-6">
              <BookmarkIcon class="w-8 h-8 mx-auto mb-2 text-gray-300" />
              <p class="text-sm">No saved items yet</p>
            </div>
          </div>

          <!-- Recent Searches -->
          <div class="bg-white rounded-lg shadow-sm p-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">
              Recent Searches
            </h3>
            <div class="text-center text-gray-500 py-6">
              <MagnifyingGlassIcon class="w-8 h-8 mx-auto mb-2 text-gray-300" />
              <p class="text-sm">No recent searches</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from "vue-router";
import {
  InformationCircleIcon,
  ChartBarIcon,
  RectangleStackIcon,
  ChatBubbleLeftRightIcon,
  ClockIcon,
  MagnifyingGlassIcon,
  BookmarkIcon,
} from "@heroicons/vue/24/outline";
</script>
