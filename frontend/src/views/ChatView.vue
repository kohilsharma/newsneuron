<template>
  <div class="chat-view min-h-screen bg-neuron-bg-primary">
    
    <!-- Neural Background Particles -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div v-for="i in 15" :key="i" 
           class="absolute w-1 h-1 bg-neuron-glow/20 rounded-full animate-pulse"
           :style="particleStyle(i)">
      </div>
    </div>

    <!-- Chat Header -->
    <header class="sticky top-0 z-30 bg-neuron-bg-content/50 backdrop-blur-sm border-b border-neuron-border">
      <div class="content-width px-6 py-4">
        <div class="flex items-center justify-between">
          
          <!-- Left: AI Assistant Info -->
          <div class="flex items-center space-x-4">
            <div class="relative">
              <div class="w-12 h-12 bg-gradient-to-br from-neuron-glow to-neuron-glow-hover rounded-full flex items-center justify-center shadow-glow">
                <Brain class="w-6 h-6 text-white animate-synapse-pulse" />
              </div>
              <div class="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-neuron-bg-content animate-pulse"></div>
            </div>
            <div>
              <h1 class="text-xl text-heading text-neuron-text-primary">Neural Assistant</h1>
              <div class="flex items-center space-x-2 text-sm text-body-sans text-neuron-text-secondary">
                <div class="w-2 h-2 bg-neuron-glow rounded-full animate-pulse"></div>
                <span>{{ aiStatus }}</span>
              </div>
            </div>
          </div>
          
          <!-- Right: Chat Controls -->
          <div class="flex items-center space-x-3">
            
            <!-- Knowledge Graph Toggle -->
            <button
              @click="showKnowledgeGraph = !showKnowledgeGraph"
              class="btn-icon"
              :class="{ 'text-neuron-glow': showKnowledgeGraph }"
              title="Toggle knowledge graph"
            >
              <Network class="w-4 h-4" />
            </button>
            
            <!-- Settings -->
            <button
              @click="showSettings = !showSettings"
              class="btn-icon"
              title="Chat settings"
            >
              <Settings class="w-4 h-4" />
            </button>
            
            <!-- Clear Chat -->
            <button
              @click="clearChat"
              class="btn-icon text-red-400 hover:text-red-300"
              title="Clear conversation"
              :disabled="messages.length === 0"
            >
              <Trash2 class="w-4 h-4" />
            </button>
            
          </div>
        </div>
      </div>
    </header>

    <!-- Main Chat Interface -->
    <div class="flex h-[calc(100vh-5rem)]">
      
      <!-- Chat Messages Area -->
      <div class="flex-1 flex flex-col">
        
        <!-- Messages Container -->
        <div 
          ref="messagesContainer"
          class="flex-1 overflow-y-auto px-6 py-6 space-y-6"
          @scroll="handleScroll"
        >
          
          <!-- Welcome Message -->
          <div v-if="messages.length === 0" class="text-center py-12">
            <div class="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-neuron-glow to-neuron-glow-hover rounded-full flex items-center justify-center shadow-glow-lg animate-synapse-pulse">
              <MessageSquare class="w-12 h-12 text-white" />
            </div>
            <h2 class="text-2xl font-heading font-bold text-neuron-text-primary mb-4">Welcome to Neural Chat</h2>
            <p class="text-neuron-text-secondary mb-8 max-w-md mx-auto">
              Ask me anything about news, current events, or explore connections between topics. 
              I'll provide insights backed by our knowledge graph.
            </p>
            
            <!-- Suggested Questions -->
            <div class="flex flex-wrap justify-center gap-3">
              <button
                v-for="suggestion in suggestions"
                :key="suggestion"
                @click="sendMessage(suggestion)"
                class="suggestion-chip bg-neuron-bg-content border border-neuron-border hover:border-neuron-glow/30 hover:bg-neuron-glow/5 px-4 py-2 rounded-full text-sm text-neuron-text-secondary hover:text-neuron-text-primary transition-all duration-300"
              >
                {{ suggestion }}
              </button>
            </div>
          </div>
          
          <!-- Message List -->
          <div class="content-width mx-auto space-y-6">
            
            <!-- Individual Messages -->
            <div
              v-for="message in messages"
              :key="message.id"
              class="message-container"
              :class="message.type === 'user' ? 'user-message' : 'assistant-message'"
            >
              
              <!-- User Message -->
              <div v-if="message.type === 'user'" class="flex justify-end">
                <div class="max-w-2xl bg-neuron-glow text-white rounded-2xl rounded-br-sm px-4 py-3 shadow-glow">
                  <p class="whitespace-pre-wrap">{{ message.content }}</p>
                  <div class="text-xs text-blue-100 mt-2 opacity-75">
                    {{ formatTime(message.timestamp) }}
                  </div>
                </div>
              </div>
              
              <!-- Assistant Message -->
              <div v-else-if="message.type === 'assistant'" class="flex items-start space-x-3">
                <div class="w-8 h-8 bg-neuron-glow rounded-full flex items-center justify-center flex-shrink-0">
                  <Brain class="w-4 h-4 text-white" />
                </div>
                <div class="flex-1 max-w-2xl">
                  <div class="bg-neuron-bg-content border border-neuron-border rounded-2xl rounded-bl-sm px-4 py-3">
                    <div class="prose prose-sm max-w-none text-neuron-text-primary">
                      <div v-if="message.isStreaming" class="typing-effect">
                        {{ message.content }}
                      </div>
                      <div v-else v-html="formatMarkdown(message.content)"></div>
                    </div>
                    
                    <!-- Sources and Connections -->
                    <div v-if="message.sources && message.sources.length > 0 && showSources" class="mt-4 pt-3 border-t border-neuron-border">
                      <h5 class="text-xs font-medium text-neuron-text-secondary mb-2">Sources:</h5>
                      <div class="space-y-1">
                        <button
                          v-for="source in message.sources"
                          :key="source.title"
                          @click="handleSourceClick(source)"
                          class="block text-xs text-neuron-glow hover:text-neuron-glow-hover transition-colors"
                        >
                          {{ source.title }} ({{ Math.round(source.confidence * 100) }}%)
                        </button>
                      </div>
                    </div>
                    
                    <div class="flex items-center justify-between mt-3 text-xs text-neuron-text-secondary">
                      <span>{{ formatTime(message.timestamp) }}</span>
                      <div class="flex space-x-2">
                        <button
                          @click="copyMessage(message.content)"
                          class="hover:text-neuron-text-primary transition-colors"
                          title="Copy message"
                        >
                          <Copy class="w-3 h-3" />
                        </button>
                        <button
                          v-if="message.isError"
                          @click="retryMessage(message.id)"
                          class="hover:text-neuron-text-primary transition-colors"
                          title="Retry"
                        >
                          <RotateCcw class="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- System Message -->
              <div v-else-if="message.type === 'system'" class="flex justify-center">
                <div class="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded-lg text-sm">
                  {{ message.content }}
                </div>
              </div>
              
            </div>
            
            <!-- Typing Indicator -->
            <div v-if="isTyping" class="flex items-start space-x-3">
              <div class="w-8 h-8 bg-neuron-glow rounded-full flex items-center justify-center flex-shrink-0">
                <Brain class="w-4 h-4 text-white" />
              </div>
              <div class="bg-neuron-bg-content border border-neuron-border rounded-2xl rounded-bl-sm px-4 py-3">
                <TypingIndicator />
              </div>
            </div>
          </div>
          
        </div>
        
        <!-- Message Input Area -->
        <div class="border-t border-neuron-border bg-neuron-bg-content/30 backdrop-blur-sm">
          <div class="content-width mx-auto px-6 py-4">
            
            <!-- Active Context Bar -->
            <div v-if="activeContext.length > 0" class="mb-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-neuron-text-primary">Active Context:</span>
                <button
                  @click="clearContext"
                  class="text-xs text-neuron-text-secondary hover:text-neuron-text-primary"
                >
                  Clear
                </button>
              </div>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="context in activeContext"
                  :key="context"
                  class="inline-flex items-center px-2 py-1 bg-neuron-glow/10 border border-neuron-glow/20 rounded-md text-xs text-neuron-glow"
                >
                  {{ context }}
                  <button
                    @click="removeContext(context)"
                    class="ml-1 hover:text-neuron-glow-hover"
                  >
                    <X class="w-3 h-3" />
                  </button>
                </span>
              </div>
            </div>
            
            <!-- Input Form -->
            <form @submit.prevent="handleSubmit" class="relative">
              <div class="flex items-end space-x-3">
                
                <!-- Message Input -->
                <div class="flex-1 relative">
                  <textarea
                    ref="messageInput"
                    v-model="currentMessage"
                    :placeholder="inputPlaceholder"
                    class="input-neuron resize-none max-h-32 min-h-[3rem] py-3 pr-12"
                    :disabled="isLoading"
                    @keydown.enter.exact.prevent="handleSubmit"
                    @keydown.enter.shift.exact="handleNewLine"
                    @input="handleInputChange"
                  />
                  
                  <!-- Attachment Button -->
                  <button
                    type="button"
                    @click="showAttachmentMenu = !showAttachmentMenu"
                    class="absolute right-3 bottom-3 text-neuron-text-secondary hover:text-neuron-text-primary transition-colors"
                    title="Attach file or context"
                  >
                    <Paperclip class="w-4 h-4" />
                  </button>
                  
                  <!-- Attachment Menu -->
                  <div v-if="showAttachmentMenu" class="absolute right-0 bottom-full mb-2 w-48 bg-neuron-bg-content border border-neuron-border rounded-lg shadow-neuron-lg p-2 z-20">
                    <button
                      @click="attachCurrentNews"
                      class="w-full text-left px-3 py-2 text-sm text-neuron-text-primary hover:bg-neuron-bg-primary rounded-md transition-colors"
                    >
                      <Newspaper class="w-4 h-4 inline mr-2" />
                      Current News Context
                    </button>
                    <button
                      @click="attachTimeline"
                      class="w-full text-left px-3 py-2 text-sm text-neuron-text-primary hover:bg-neuron-bg-primary rounded-md transition-colors"
                    >
                      <Clock class="w-4 h-4 inline mr-2" />
                      Timeline Context
                    </button>
                  </div>
                </div>
                
                <!-- Send Button -->
                <button
                  type="submit"
                  :disabled="!canSend"
                  class="btn-neuron p-3 rounded-xl flex-shrink-0 disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Send message (Enter)"
                >
                  <Send v-if="!isLoading" class="w-5 h-5" />
                  <Loader2 v-else class="w-5 h-5 animate-spin" />
                </button>
                
              </div>
              
              <!-- Input Hints -->
              <div class="flex items-center justify-between mt-2 text-xs text-neuron-text-secondary">
                <div class="flex items-center space-x-4">
                  <span>Enter to send, Shift+Enter for new line</span>
                  <span v-if="currentMessage.length > 0">{{ currentMessage.length }}/2000</span>
                </div>
                <div class="flex items-center space-x-3">
                  <label class="flex items-center space-x-1">
                    <input
                      v-model="showSources"
                      type="checkbox"
                      class="w-3 h-3 text-neuron-glow bg-neuron-bg-primary border-neuron-border rounded focus:ring-neuron-glow focus:ring-1"
                    />
                    <span>Sources</span>
                  </label>
                  <label class="flex items-center space-x-1">
                    <input
                      v-model="showConnections"
                      type="checkbox"
                      class="w-3 h-3 text-neuron-glow bg-neuron-bg-primary border-neuron-border rounded focus:ring-neuron-glow focus:ring-1"
                    />
                    <span>Connections</span>
                  </label>
                </div>
              </div>
              
            </form>
          </div>
        </div>
        
      </div>
      
      <!-- Knowledge Graph Sidebar -->
      <div
        v-if="showKnowledgeGraph"
        class="w-80 border-l border-neuron-border bg-neuron-bg-content/30 backdrop-blur-sm flex flex-col"
      >
        <div class="p-4 border-b border-neuron-border">
          <div class="flex items-center justify-between">
            <h3 class="font-heading font-medium text-neuron-text-primary">Knowledge Graph</h3>
            <button
              @click="showKnowledgeGraph = false"
              class="btn-icon p-1"
            >
              <X class="w-4 h-4" />
            </button>
          </div>
        </div>
        
        <div class="flex-1 p-4 overflow-y-auto">
          <!-- Placeholder for Knowledge Graph Visualization -->
          <div class="text-center py-8">
            <Network class="w-16 h-16 mx-auto text-neuron-glow/50 mb-4" />
            <p class="text-neuron-text-secondary text-sm">
              Knowledge graph visualization will appear here when entities are detected in the conversation.
            </p>
            
            <!-- Mock entities when there are extracted entities -->
            <div v-if="extractedEntities.length > 0" class="mt-6 space-y-3">
              <h4 class="text-sm font-medium text-neuron-text-primary">Detected Entities:</h4>
              <div class="space-y-2">
                <button
                  v-for="entity in extractedEntities"
                  :key="entity"
                  @click="handleEntityClick(entity)"
                  class="block w-full text-left px-3 py-2 bg-neuron-bg-primary border border-neuron-border rounded-md text-sm text-neuron-text-primary hover:border-neuron-glow/30 transition-colors"
                >
                  {{ entity }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
    </div>
    
    <!-- Settings Modal -->
    <div v-if="showSettings" class="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div class="bg-neuron-bg-content border border-neuron-border rounded-2xl w-full max-w-lg p-6">
        <div class="flex items-center justify-between mb-6">
          <h3 class="text-lg font-heading font-medium text-neuron-text-primary">Chat Settings</h3>
          <button
            @click="showSettings = false"
            class="btn-icon p-1"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-neuron-text-primary mb-2">AI Model</label>
            <select v-model="chatSettings.model" class="input-neuron text-sm">
              <option value="gpt-4">GPT-4 (Recommended)</option>
              <option value="gpt-3.5">GPT-3.5 Turbo</option>
              <option value="claude">Claude 3</option>
            </select>
          </div>
          
          <div class="flex items-center justify-between">
            <label class="text-sm font-medium text-neuron-text-primary">Enable RAG</label>
            <input
              v-model="chatSettings.enableRAG"
              type="checkbox"
              class="w-4 h-4 text-neuron-glow bg-neuron-bg-primary border-neuron-border rounded focus:ring-neuron-glow focus:ring-1"
            />
          </div>
          
          <div class="flex items-center justify-between">
            <label class="text-sm font-medium text-neuron-text-primary">Stream Response</label>
            <input
              v-model="chatSettings.streamResponse"
              type="checkbox"
              class="w-4 h-4 text-neuron-glow bg-neuron-bg-primary border-neuron-border rounded focus:ring-neuron-glow focus:ring-1"
            />
          </div>
        </div>
        
        <div class="flex justify-end space-x-3 mt-6">
          <button
            @click="showSettings = false"
            class="btn-ghost text-sm"
          >
            Cancel
          </button>
          <button
            @click="showSettings = false"
            class="btn-neuron text-sm"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
    
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'

// Icons
import {
  Brain,
  MessageSquare,
  Network,
  Settings,
  Trash2,
  Send,
  Loader2,
  Paperclip,
  Newspaper,
  Clock,
  X,
  Copy,
  RotateCcw
} from 'lucide-vue-next'

// Components
import TypingIndicator from '@/components/ui/TypingIndicator.vue'

// Router
const router = useRouter()

// Refs
const messagesContainer = ref(null)
const messageInput = ref(null)

// Reactive state
const messages = ref([])
const currentMessage = ref('')
const isLoading = ref(false)
const isTyping = ref(false)
const showSources = ref(true)
const showConnections = ref(true)
const showKnowledgeGraph = ref(false)
const showSettings = ref(false)
const showAttachmentMenu = ref(false)
const activeContext = ref([])
const extractedEntities = ref([])
const entityConnections = ref([])
const mentionedEntities = ref([])

// AI Status
const aiStatus = ref('Ready to assist with news analysis')

// Chat settings
const chatSettings = ref({
  model: 'gpt-4',
  temperature: 0.7,
  maxTokens: 2000,
  enableRAG: true,
  enableKnowledgeGraph: true,
  streamResponse: true
})

// Suggestions for new users
const suggestions = [
  "What's the latest in AI technology?",
  "Analyze recent political developments",
  "Show me connections between tech and finance news",
  "What are the trending topics today?",
  "Explain the impact of recent economic changes"
]

// Computed
const inputPlaceholder = computed(() => {
  if (isLoading.value) return 'Processing your message...'
  if (activeContext.value.length > 0) return 'Continue the conversation with context...'
  return 'Ask me about news, trends, or explore connections...'
})

const canSend = computed(() => {
  return currentMessage.value.trim().length > 0 && !isLoading.value && currentMessage.value.length <= 2000
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

const formatTime = (timestamp) => {
  const now = new Date()
  const time = new Date(timestamp)
  const diffMs = now - time
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  
  return time.toLocaleDateString()
}

const formatMarkdown = (text) => {
  // Simple markdown formatting
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code class="bg-neuron-bg-primary px-1 rounded">$1</code>')
    .replace(/\n/g, '<br>')
}

const handleSubmit = async () => {
  if (!canSend.value) return
  
  const message = currentMessage.value.trim()
  currentMessage.value = ''
  showAttachmentMenu.value = false
  
  // Add user message
  const userMessage = {
    id: Date.now(),
    type: 'user',
    content: message,
    timestamp: new Date(),
    context: [...activeContext.value]
  }
  
  messages.value.push(userMessage)
  scrollToBottom()
  
  // Start AI response
  await sendToAI(message)
}

const sendMessage = async (message) => {
  currentMessage.value = message
  await handleSubmit()
}

const sendToAI = async (message) => {
  isLoading.value = true
  isTyping.value = true
  aiStatus.value = 'Analyzing your question...'
  
  try {
    // Simulate AI processing with progressive updates
    const aiMessage = {
      id: Date.now() + 1,
      type: 'assistant',
      content: '',
      timestamp: new Date(),
      sources: [],
      connections: [],
      entities: [],
      isStreaming: true
    }
    
    messages.value.push(aiMessage)
    
    // Simulate streaming response
    const fullResponse = `I understand you're asking about **"${message}"**. Based on my analysis of recent news and knowledge graph connections, here's what I found:

This is a sophisticated analysis that takes into account multiple data sources and entity relationships. The neural network has processed relevant information to provide you with comprehensive insights.

**Key Points:**
• Analysis based on current knowledge graph
• Cross-referenced with multiple news sources  
• Contextual connections identified
• Real-time data integration

**Related Entities:** Technology, Innovation, Markets, Economy

Would you like me to explore any specific aspect further or show you related topics?`

    // Stream the response
    let currentIndex = 0
    const streamInterval = setInterval(() => {
      if (currentIndex < fullResponse.length) {
        const chunk = fullResponse.slice(0, currentIndex + Math.floor(Math.random() * 5) + 1)
        aiMessage.content = chunk
        currentIndex = chunk.length
        scrollToBottom()
      } else {
        clearInterval(streamInterval)
        aiMessage.isStreaming = false
        
        // Add mock sources and connections
        aiMessage.sources = [
          { title: 'Reuters Analysis', url: '#', confidence: 0.95 },
          { title: 'Tech News Daily', url: '#', confidence: 0.87 }
        ]
        
        aiMessage.connections = [
          { entity: 'Technology', relation: 'relates_to', target: 'Innovation' },
          { entity: 'Markets', relation: 'affects', target: 'Economy' }
        ]
        
        aiMessage.entities = ['Technology', 'Innovation', 'Markets', 'Economy']
        
        // Update knowledge graph
        extractedEntities.value = aiMessage.entities
        mentionedEntities.value = aiMessage.entities
        
        isTyping.value = false
        isLoading.value = false
        aiStatus.value = 'Ready for your next question'
      }
    }, 50)
    
  } catch (error) {
    console.error('Chat error:', error)
    isLoading.value = false
    isTyping.value = false
    aiStatus.value = 'Error occurred - please try again'
    
    // Add error message
    messages.value.push({
      id: Date.now() + 2,
      type: 'system',
      content: 'Sorry, I encountered an error processing your request. Please try again.',
      timestamp: new Date(),
      isError: true
    })
  }
}

const retryMessage = async (messageId) => {
  const messageIndex = messages.value.findIndex(msg => msg.id === messageId)
  if (messageIndex > 0) {
    const userMessage = messages.value[messageIndex - 1]
    if (userMessage.type === 'user') {
      // Remove failed message and retry
      messages.value.splice(messageIndex)
      await sendToAI(userMessage.content)
    }
  }
}

const copyMessage = (content) => {
  navigator.clipboard.writeText(content)
  // Could show toast notification here
}

const handleSourceClick = (source) => {
  if (source.url && source.url !== '#') {
    window.open(source.url, '_blank')
  }
}

const handleConnectionClick = (connection) => {
  // Navigate to timeline or search view with the connection
  router.push(`/search?q=${encodeURIComponent(connection.entity)}`)
}

const handleEntityClick = (entity) => {
  // Add entity to context or search
  if (!activeContext.value.includes(entity)) {
    activeContext.value.push(entity)
  }
}

const clearChat = () => {
  if (confirm('Are you sure you want to clear the conversation?')) {
    messages.value = []
    activeContext.value = []
    extractedEntities.value = []
    mentionedEntities.value = []
    aiStatus.value = 'Ready to start a new conversation'
  }
}

const clearContext = () => {
  activeContext.value = []
}

const removeContext = (context) => {
  const index = activeContext.value.indexOf(context)
  if (index > -1) {
    activeContext.value.splice(index, 1)
  }
}

const attachCurrentNews = () => {
  activeContext.value.push('Current News Headlines')
  showAttachmentMenu.value = false
}

const attachTimeline = () => {
  activeContext.value.push('Recent Timeline Events')
  showAttachmentMenu.value = false
}

const handleNewLine = () => {
  currentMessage.value += '\n'
}

const handleInputChange = () => {
  // Auto-resize textarea
  if (messageInput.value) {
    messageInput.value.style.height = 'auto'
    messageInput.value.style.height = Math.min(messageInput.value.scrollHeight, 128) + 'px'
  }
}

const handleScroll = () => {
  // Could implement scroll-based features here
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const updateSettings = (newSettings) => {
  chatSettings.value = { ...chatSettings.value, ...newSettings }
  showSettings.value = false
}

// Close attachment menu when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showAttachmentMenu.value = false
  }
}

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  // Focus input on mount
  if (messageInput.value) {
    messageInput.value.focus()
  }
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// Watch for new messages to scroll
watch(messages, scrollToBottom, { deep: true })
</script>

<style scoped>
/* Chat-specific animations */
.suggestion-chip {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.suggestion-chip:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 167, 225, 0.2);
}

/* Message animations */
.message-container {
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Typing effect */
.typing-effect::after {
  content: '|';
  animation: blink 1s infinite;
  color: var(--neuron-glow);
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

/* Input area styling */
.input-neuron {
  transition: all 0.3s ease;
}

.input-neuron:focus {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 167, 225, 0.1);
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .content-width {
    max-width: 100%;
  }
  
  .w-80 {
    width: 100%;
    position: fixed;
    top: 0;
    right: 0;
    height: 100vh;
    z-index: 40;
  }
}

/* Smooth scrolling */
.overflow-y-auto {
  scroll-behavior: smooth;
}

/* Custom scrollbar for messages */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: rgba(48, 54, 61, 0.3);
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(0, 167, 225, 0.3);
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 167, 225, 0.5);
}

/* Message styling improvements */
.user-message .bg-neuron-glow {
  box-shadow: 0 4px 12px rgba(0, 167, 225, 0.3);
}

.assistant-message .bg-neuron-bg-content {
  backdrop-filter: blur(8px);
}

/* Prose styling for assistant messages */
.prose strong {
  color: var(--neuron-text-primary);
  font-weight: 600;
}

.prose em {
  color: var(--neuron-glow);
  font-style: italic;
}
</style>
