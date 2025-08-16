<template>
  <div
    class="card hover:shadow-md transition-all duration-200 cursor-pointer"
    @click="handleClick"
  >
    <div class="card-body">
      <div class="flex items-start justify-between mb-3">
        <h4 class="font-semibold text-gray-900 text-sm line-clamp-2">
          {{ flashcard.title }}
        </h4>
        <span class="badge badge-primary text-xs ml-2 flex-shrink-0">
          {{ flashcard.category || "General" }}
        </span>
      </div>

      <p class="text-gray-600 text-sm line-clamp-2 mb-3">
        {{ flashcard.summary }}
      </p>

      <div class="flex items-center justify-between text-xs text-gray-500">
        <span>{{ keyPointsText }}</span>
        <span>{{ timeAgo }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { formatDistanceToNow } from "date-fns";

const props = defineProps({
  flashcard: {
    type: Object,
    required: true,
  },
});

const router = useRouter();

const keyPointsText = computed(() => {
  const count = props.flashcard.key_points?.length || 0;
  return `${count} key point${count !== 1 ? "s" : ""}`;
});

const timeAgo = computed(() => {
  if (!props.flashcard.created_at) return "";

  try {
    const date = new Date(props.flashcard.created_at);
    return formatDistanceToNow(date, { addSuffix: true });
  } catch {
    return "";
  }
});

function handleClick() {
  router.push(`/flashcards/${props.flashcard.id}`);
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
