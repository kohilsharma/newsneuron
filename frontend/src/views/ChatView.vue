<template>
  <div class="chat-view min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-gray-900 dark:via-slate-900 dark:to-gray-800">
    <!-- Debug Info (temporary) -->
    <div class="fixed top-20 left-4 bg-black/70 text-white p-2 rounded text-xs z-50">
      ChatView Loaded: {{ new Date().toLocaleTimeString() }}<br>
      Messages: {{ messages.length }}<br>
      Is Loading: {{ isLoading }}<br>
      API Base: {{ apiBaseUrl }}
    </div>

    <!-- Animated Background Elements -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="floating-orb floating-orb-1"></div>
      <div class="floating-orb floating-orb-2"></div>
      <div class="floating-orb floating-orb-3"></div>
    </div>

    <!-- Header with Glassmorphism -->
    <div class="relative z-10 backdrop-blur-lg bg-white/70 dark:bg-gray-900/70 border-b border-white/20 dark:border-gray-700/50 shadow-lg">
      <div class="max-w-6xl mx-auto px-4 py-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <div class="avatar-container">
              <div class="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
                <span class="text-white text-xl font-bold animate-pulse">N</span>
              </div>
            </div>
            <div>
              <h1 class="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent animate-gradient">
                NewsNeuron Chat
              </h1>
              <p class="text-gray-600 dark:text-gray-300 font-medium">
                {{ typingStatus || "AI-powered news analysis with source verification" }}
              </p>
            </div>
          </div>
          
          <!-- Quality Indicator -->
          <div v-if="currentQuality" class="quality-badge" :class="getQualityClass(currentQuality.score)">
            <div class="flex items-center space-x-2">
              <div class="w-2 h-2 rounded-full bg-current animate-pulse"></div>
              <span class="text-sm font-medium">{{ currentQuality.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Chat Container -->
    <div class="relative z-10 max-w-6xl mx-auto px-4 py-8">
      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        <!-- Sidebar -->
        <div class="lg:col-span-1 space-y-4">
          <!-- Conversation List -->
          <div class="card-glass p-4">
            <h3 class="text-lg font-semibold text-gray-800 dark:text-white mb-4 flex items-center">
              <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"></path>
              </svg>
              Conversations
            </h3>
            <div class="space-y-2">
              <div v-for="conv in conversations" :key="conv.conversation_id" 
                   class="conversation-item" @click="loadConversation(conv.conversation_id)">
                <div class="font-medium text-sm">{{ conv.title }}</div>
                <div class="text-xs text-gray-500">{{ conv.message_count }} messages</div>
              </div>
              <button @click="startNewConversation" class="new-conversation-btn">
                <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clip-rule="evenodd"></path>
                </svg>
                New Chat
              </button>
            </div>
          </div>

          <!-- Quick Actions -->
          <div class="card-glass p-4">
            <h3 class="text-lg font-semibold text-gray-800 dark:text-white mb-4">Quick Actions</h3>
            <div class="space-y-2">
              <button v-for="action in quickActions" :key="action.text" 
                      @click="sendQuickMessage(action.text)"
                      class="quick-action-btn">
                <span>{{ action.icon }}</span>
                {{ action.text }}
              </button>
            </div>
          </div>
        </div>

        <!-- Chat Area -->
        <div class="lg:col-span-3">
          <!-- Messages Container -->
          <div ref="messagesContainer" class="card-glass chat-messages-container">
            
            <!-- Welcome Screen -->
            <div v-if="messages.length === 0" class="welcome-screen">
              <div class="welcome-animation">
                <div class="robot-avatar">
                  <div class="robot-face">
                    <div class="robot-eyes">
                      <div class="eye"></div>
                      <div class="eye"></div>
                    </div>
                    <div class="robot-mouth"></div>
                  </div>
                </div>
              </div>
              <h3 class="text-2xl font-bold text-gray-800 dark:text-white mb-4">
                Welcome to NewsNeuron! 🚀
              </h3>
              <p class="text-gray-600 dark:text-gray-300 mb-6 max-w-md">
                Ask me anything about current news and I'll provide verified information with source citations.
              </p>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl">
                <button v-for="example in exampleQuestions" :key="example"
                        @click="sendQuickMessage(example)"
                        class="example-question-btn">
                  {{ example }}
                </button>
              </div>
            </div>

            <!-- Messages -->
            <div v-for="(message, index) in messages" :key="message.id || index" 
                 class="message-wrapper" 
                 :class="message.role"
                 :style="{ animationDelay: `${index * 0.1}s` }">
              
              <!-- User Message -->
              <div v-if="message.role === 'user'" class="user-message">
                <div class="message-content">
                  <div class="message-text">{{ message.content }}</div>
                  <div class="message-timestamp">{{ formatTime(message.timestamp) }}</div>
                </div>
                <div class="user-avatar">
                  <div class="avatar-bg">
                    <span class="text-white font-bold">{{ getUserInitial() }}</span>
                  </div>
                </div>
              </div>

              <!-- Assistant Message -->
              <div v-else class="assistant-message">
                <div class="assistant-avatar">
                  <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
                    <svg class="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                  </div>
                </div>
                <div class="message-content">
                  <div class="message-text" v-html="processMessageContent(message.content)"></div>
                  
                  <!-- Interactive Elements -->
                  <div v-if="message.interactive_elements" class="interactive-elements">
                    <div v-for="element in message.interactive_elements" :key="element.type" class="interactive-element">
                      
                      <!-- Quality Indicator -->
                      <div v-if="element.type === 'quality_indicator'" class="quality-indicator" :class="getQualityClass(element.score)">
                        <div class="flex items-center space-x-2">
                          <div class="quality-icon"></div>
                          <span class="text-sm font-medium">{{ element.label }}</span>
                          <span class="text-xs opacity-75">({{ (element.score * 100).toFixed(0) }}%)</span>
                        </div>
                      </div>

                      <!-- Entity Chips -->
                      <div v-if="element.type === 'entity_chips'" class="entity-chips">
                        <span v-for="entity in element.entities" :key="entity.name" 
                              @click="searchEntity(entity.name)"
                              class="entity-chip">
                          {{ entity.name }}
                        </span>
                      </div>

                      <!-- Reading Time -->
                      <div v-if="element.type === 'reading_time'" class="reading-time">
                        <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"></path>
                        </svg>
                        {{ element.minutes }} min read
                      </div>
                    </div>
                  </div>

                  <!-- Sources -->
                  <div v-if="message.sources && message.sources.length > 0" class="sources-section">
                    <h4 class="sources-title">Sources & Citations</h4>
                    <div class="sources-grid">
                      <div v-for="source in message.sources" :key="source.id" 
                           class="source-card" @click="openSourceVerification(source)">
                        <div class="source-header">
                          <div class="source-icon">📰</div>
                          <div class="source-info">
                            <div class="source-title">{{ source.title }}</div>
                            <div class="source-publication">{{ source.source }}</div>
                          </div>
                        </div>
                        <div v-if="source.similarity_score" class="source-relevance">
                          Relevance: {{ (source.similarity_score * 100).toFixed(0) }}%
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Suggested Questions -->
                  <div v-if="message.suggested_questions && message.suggested_questions.length > 0" class="suggested-questions">
                    <h4 class="suggestions-title">💡 Follow up with:</h4>
                    <div class="suggestions-grid">
                      <button v-for="question in message.suggested_questions.slice(0, 4)" 
                              :key="question" 
                              @click="sendQuickMessage(question)"
                              class="suggestion-btn">
                        {{ question }}
                      </button>
                    </div>
                  </div>

                  <div class="message-footer">
                    <div class="message-timestamp">{{ formatTime(message.timestamp) }}</div>
                    <div class="message-actions">
                      <button @click="copyMessage(message.content)" class="action-btn" title="Copy">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z"></path>
                          <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z"></path>
                        </svg>
                      </button>
                      <button @click="shareMessage(message)" class="action-btn" title="Share">
                        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z"></path>
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Typing Indicator -->
            <div v-if="isLoading" class="typing-indicator">
              <div class="assistant-avatar">
                <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
                  <div class="typing-animation">
                    <div class="dot"></div>
                    <div class="dot"></div>
                    <div class="dot"></div>
                  </div>
                </div>
              </div>
              <div class="typing-content">
                <div class="typing-bubble">
                  <div class="typing-text">{{ currentTypingStage }}</div>
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: typingProgress + '%' }"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Input Area -->
          <div class="input-area card-glass">
            <form @submit.prevent="sendMessage" class="input-form">
              <div class="input-container">
                <div class="input-wrapper">
                  <input
                    ref="messageInput"
                    v-model="currentMessage"
                    type="text"
                    placeholder="Ask about the latest news..."
                    class="message-input"
                    :disabled="isLoading"
                    @keydown.up="navigateHistory(-1)"
                    @keydown.down="navigateHistory(1)"
                    @input="handleTyping"
                  />
                  <div class="input-actions">
                    <button type="button" @click="openEmojiPicker" class="emoji-btn" title="Add emoji">
                      😊
                    </button>
                    <button type="button" @click="openFileUpload" class="attachment-btn" title="Attach file">
                      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M8 4a3 3 0 00-3 3v4a5 5 0 0010 0V7a1 1 0 112 0v4a7 7 0 11-14 0V7a5 5 0 0110 0v4a3 3 0 11-6 0V7a1 1 0 012 0v4a1 1 0 102 0V7a3 3 0 00-3-3z" clip-rule="evenodd"></path>
                      </svg>
                    </button>
                  </div>
                </div>
                <button
                  type="submit"
                  :disabled="isLoading || !currentMessage.trim()"
                  class="send-btn"
                  :class="{ 'sending': isLoading }"
                >
                  <svg v-if="!isLoading" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z"></path>
                  </svg>
                  <div v-else class="loading-spinner"></div>
                </button>
              </div>
              
              <!-- Character count and shortcuts -->
              <div class="input-footer">
                <div class="character-count" :class="{ 'warning': currentMessage.length > 1800 }">
                  {{ currentMessage.length }}/2000
                </div>
                <div class="shortcuts">
                  <kbd>↑↓</kbd> History · <kbd>Ctrl+Enter</kbd> Send
                </div>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Citation Verification Modal -->
    <div v-if="showCitationModal" class="citation-modal-overlay" @click="closeCitationModal">
      <div class="citation-modal" @click.stop>
        <div class="citation-modal-header">
          <h3 class="text-xl font-bold">Source Verification</h3>
          <button @click="closeCitationModal" class="close-btn">
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
            </svg>
          </button>
        </div>
        <div class="citation-modal-content">
          <div v-if="selectedCitation" class="citation-details">
            <div class="citation-header">
              <h4 class="font-bold text-lg">{{ selectedCitation.title }}</h4>
              <div class="citation-meta">
                <span class="publication">{{ selectedCitation.publication }}</span>
                <span v-if="selectedCitation.published_date" class="date">{{ formatDate(selectedCitation.published_date) }}</span>
              </div>
            </div>
            
            <div class="verification-methods">
              <h5 class="font-semibold mb-3">Verification Methods:</h5>
              <div class="verification-grid">
                <div class="verification-item">
                  <div class="verification-icon">🔗</div>
                  <div class="verification-info">
                    <div class="verification-label">Original Source</div>
                    <a v-if="selectedCitation.url" :href="selectedCitation.url" target="_blank" class="verification-link">
                      View Article
                    </a>
                    <span v-else class="verification-status unavailable">Not Available</span>
                  </div>
                </div>
                
                <div class="verification-item">
                  <div class="verification-icon">📊</div>
                  <div class="verification-info">
                    <div class="verification-label">Relevance Score</div>
                    <div class="verification-value">{{ (selectedCitation.similarity_score * 100).toFixed(0) }}%</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="selectedCitation.snippet" class="citation-snippet">
              <h5 class="font-semibold mb-2">Content Preview:</h5>
              <p class="snippet-text">{{ selectedCitation.snippet }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Modal -->
    <div v-if="showSettingsModal" class="settings-modal-overlay" @click="closeSettingsModal">
      <div class="settings-modal" @click.stop>
        <!-- Settings content would go here -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, onUnmounted, computed, watch } from 'vue'
import api from '@/services/api'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()

// Reactive data
const messages = ref([])
const conversations = ref([])
const currentMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref(null)
const messageInput = ref(null)
const currentConversationId = ref(null)
const messageHistory = ref([])
const historyIndex = ref(-1)
const typingStatus = ref('')
const currentTypingStage = ref('Analyzing your question...')
const typingProgress = ref(0)
const showCitationModal = ref(false)
const showSettingsModal = ref(false)
const selectedCitation = ref(null)
const currentQuality = ref(null)

// Example questions with randomization
const baseQuestions = [
  "What are the latest AI breakthroughs?",
  "Tell me about recent climate developments",
  "What's happening in technology today?",
  "Recent political developments worldwide",
  "Latest business and economic news",
  "Scientific discoveries this month"
]

const exampleQuestions = ref([])
const quickActions = ref([
  { icon: '🤖', text: 'AI & Technology' },
  { icon: '🌍', text: 'Climate & Environment' },
  { icon: '🏛️', text: 'Politics & Government' },
  { icon: '💼', text: 'Business & Economy' }
])

// Computed properties
const getUserInitial = () => {
  return 'U' // In production, get from user profile
}

const apiBaseUrl = computed(() => {
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
})

// Methods
const startNewConversation = () => {
  messages.value = []
  currentConversationId.value = null
  currentQuality.value = null
  focusInput()
}

const loadConversation = (conversationId) => {
  // In production, load conversation from API
  currentConversationId.value = conversationId
}

const sendQuickMessage = (message) => {
  currentMessage.value = message
  sendMessage()
}

const sendMessage = async () => {
  if (!currentMessage.value.trim() || isLoading.value) return

  console.log('Sending message:', currentMessage.value)

  const userMessage = {
    id: `msg_${Date.now()}`,
    role: 'user',
    content: currentMessage.value,
    timestamp: new Date()
  }

  messages.value.push(userMessage)
  messageHistory.value.unshift(currentMessage.value)
  historyIndex.value = -1

  const messageToSend = currentMessage.value
  currentMessage.value = ''
  isLoading.value = true

  // Start typing animation
  startTypingAnimation()

  try {
    console.log('Making API call to /chat/')
    const response = await api.post('/chat/', {
      message: messageToSend,
      conversation_id: currentConversationId.value,
      use_hybrid_search: true,
      include_citations: true,
      response_style: 'balanced'
    })

    console.log('API response received:', response.data)

    const assistantMessage = {
      id: response.data.message_id,
      role: 'assistant',
      content: response.data.response,
      sources: response.data.sources || [],
      citations: response.data.citations || [],
      suggested_questions: response.data.suggested_questions || [],
      interactive_elements: response.data.interactive_elements || [],
      timestamp: new Date(),
      rag_quality: response.data.rag_quality
    }

    // Update current quality indicator
    if (response.data.rag_quality && response.data.rag_quality.quality_score > 0) {
      currentQuality.value = {
        score: response.data.rag_quality.quality_score,
        label: getQualityLabel(response.data.rag_quality.quality_score)
      }
    }

    // Update conversation ID
    if (!currentConversationId.value) {
      currentConversationId.value = response.data.conversation_id
    }

    messages.value.push(assistantMessage)

    // Load conversations list
    loadConversations()

  } catch (error) {
    console.error('Error sending message:', error)
    appStore.setError('Failed to send message. Please check your connection.')

    messages.value.push({
      id: `error_${Date.now()}`,
      role: 'assistant',
      content: 'Sorry, I encountered an error. Please check your internet connection and try again.',
      timestamp: new Date()
    })
  } finally {
    isLoading.value = false
    stopTypingAnimation()
    await nextTick()
    scrollToBottom()
    focusInput()
  }
}

const startTypingAnimation = () => {
  const stages = [
    'Analyzing your question...',
    'Searching knowledge base...',
    'Retrieving relevant sources...',
    'Generating response...',
    'Verifying citations...'
  ]
  
  let stageIndex = 0
  typingProgress.value = 0
  
  const stageInterval = setInterval(() => {
    if (!isLoading.value) {
      clearInterval(stageInterval)
      return
    }
    
    currentTypingStage.value = stages[stageIndex]
    stageIndex = (stageIndex + 1) % stages.length
  }, 2000)
  
  const progressInterval = setInterval(() => {
    if (!isLoading.value) {
      clearInterval(progressInterval)
      return
    }
    
    typingProgress.value = Math.min(typingProgress.value + Math.random() * 15, 90)
  }, 300)
}

const stopTypingAnimation = () => {
  typingProgress.value = 100
  setTimeout(() => {
    typingProgress.value = 0
  }, 200)
}

const processMessageContent = (content) => {
  // Process citations to make them clickable
  return content.replace(
    /\[Sources?:\s*([^\]]+)\]/g,
    '<span class="citation-link" onclick="handleCitationClick(\'$1\')">[$1]</span>'
  )
}

const openSourceVerification = (source) => {
  selectedCitation.value = source
  showCitationModal.value = true
}

const closeCitationModal = () => {
  showCitationModal.value = false
  selectedCitation.value = null
}

const closeSettingsModal = () => {
  showSettingsModal.value = false
}

const searchEntity = (entityName) => {
  currentMessage.value = `Tell me more about ${entityName}`
  sendMessage()
}

const navigateHistory = (direction) => {
  if (messageHistory.value.length === 0) return
  
  historyIndex.value = Math.max(-1, Math.min(messageHistory.value.length - 1, historyIndex.value + direction))
  
  if (historyIndex.value === -1) {
    currentMessage.value = ''
  } else {
    currentMessage.value = messageHistory.value[historyIndex.value]
  }
}

const handleTyping = () => {
  // Add typing indicators or auto-suggestions here
}

const copyMessage = async (content) => {
  try {
    await navigator.clipboard.writeText(content)
    appStore.showSuccess('Message copied to clipboard')
  } catch (error) {
    console.error('Failed to copy message:', error)
  }
}

const shareMessage = (message) => {
  if (navigator.share) {
    navigator.share({
      title: 'NewsNeuron Chat',
      text: message.content,
      url: window.location.href
    })
  }
}

const openEmojiPicker = () => {
  // Implement emoji picker
}

const openFileUpload = () => {
  // Implement file upload
}

const getQualityClass = (score) => {
  if (score >= 0.9) return 'quality-excellent'
  if (score >= 0.7) return 'quality-good'
  if (score >= 0.5) return 'quality-moderate'
  return 'quality-limited'
}

const getQualityLabel = (score) => {
  if (score >= 0.9) return 'Excellent Sources'
  if (score >= 0.7) return 'Good Sources'
  if (score >= 0.5) return 'Moderate Sources'
  return 'Limited Sources'
}

const formatTime = (timestamp) => {
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const focusInput = () => {
  nextTick(() => {
    if (messageInput.value) {
      messageInput.value.focus()
    }
  })
}

const testAPIConnection = async () => {
  try {
    console.log('Testing API connection...')
    const response = await api.get('/health')
    console.log('API connection successful:', response.data)
    return true
  } catch (error) {
    console.error('API connection failed:', error)
    throw new Error('Cannot connect to the backend API. Please check if the server is running.')
  }
}

const loadConversations = async () => {
  try {
    console.log('Loading conversations...')
    const response = await api.get('/chat/conversations')
    conversations.value = response.data.conversations || []
    console.log('Conversations loaded:', conversations.value.length)
  } catch (error) {
    console.error('Error loading conversations:', error)
    // Don't show error for conversation loading - it's not critical
  }
}

const randomizeQuestions = () => {
  // Shuffle and select random questions to avoid AI-generated feel
  const shuffled = [...baseQuestions].sort(() => 0.5 - Math.random())
  exampleQuestions.value = shuffled.slice(0, 4)
}

// Lifecycle
onMounted(async () => {
  try {
    console.log('ChatView mounted successfully')

    // Test API connectivity first
    await testAPIConnection()

    randomizeQuestions()
    loadConversations()
    focusInput()

    // Add some random floating elements
    setTimeout(() => {
      const orbs = document.querySelectorAll('.floating-orb')
      orbs.forEach((orb, index) => {
        orb.style.animationDelay = `${index * 1.5}s`
      })
    }, 100)

    // Global citation click handler
    window.handleCitationClick = (citationText) => {
      // Find and show citation details
      console.log('Citation clicked:', citationText)
    }

    console.log('ChatView initialization complete')
  } catch (error) {
    console.error('Error during ChatView mount:', error)
    appStore.setError('Failed to initialize chat. Please check your connection and refresh the page.')
  }
})

onUnmounted(() => {
  // Clean up global handler
  if (window.handleCitationClick) {
    delete window.handleCitationClick
  }
})

// Auto-scroll to bottom when new messages arrive
watch(messages, () => {
  nextTick(() => {
    scrollToBottom()
  })
}, { deep: true })
</script>

<style scoped>
/* Enhanced Animations and Styling */
@keyframes gradient {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  33% { transform: translateY(-10px) rotate(5deg); }
  66% { transform: translateY(5px) rotate(-5deg); }
}

@keyframes pulse-glow {
  0%, 100% { box-shadow: 0 0 20px rgba(59, 130, 246, 0.3); }
  50% { box-shadow: 0 0 30px rgba(59, 130, 246, 0.6); }
}

@keyframes slide-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.chat-view {
  min-height: 100vh;
  position: relative;
}

/* Floating Background Elements */
.floating-orb {
  position: absolute;
  border-radius: 50%;
  background: linear-gradient(45deg, rgba(59, 130, 246, 0.1), rgba(147, 51, 234, 0.1));
  animation: float 20s ease-in-out infinite;
  pointer-events: none;
}

.floating-orb-1 {
  width: 300px;
  height: 300px;
  top: 10%;
  left: -5%;
  animation-duration: 25s;
}

.floating-orb-2 {
  width: 200px;
  height: 200px;
  top: 50%;
  right: -5%;
  animation-duration: 30s;
  animation-delay: 10s;
}

.floating-orb-3 {
  width: 150px;
  height: 150px;
  bottom: 20%;
  left: 20%;
  animation-duration: 35s;
  animation-delay: 20s;
}

/* Glassmorphism Cards */
.card-glass {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.dark .card-glass {
  background: rgba(17, 24, 39, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.card-glass:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

/* Animated Gradient Text */
.animate-gradient {
  background-size: 200% 200%;
  animation: gradient 3s ease infinite;
}

/* Quality Badge */
.quality-badge {
  padding: 8px 16px;
  border-radius: 12px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.quality-excellent {
  background: linear-gradient(135deg, #10b981, #34d399);
  color: white;
}

.quality-good {
  background: linear-gradient(135deg, #3b82f6, #60a5fa);
  color: white;
}

.quality-moderate {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
  color: white;
}

.quality-limited {
  background: linear-gradient(135deg, #ef4444, #f87171);
  color: white;
}

/* Conversation Items */
.conversation-item {
  padding: 12px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.conversation-item:hover {
  background: rgba(59, 130, 246, 0.1);
  transform: translateX(4px);
}

.new-conversation-btn {
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: white;
  font-weight: 600;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.new-conversation-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
}

/* Quick Actions */
.quick-action-btn {
  width: 100%;
  padding: 10px 12px;
  text-align: left;
  border-radius: 10px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  gap: 8px;
}

.quick-action-btn:hover {
  background: rgba(59, 130, 246, 0.1);
  transform: translateX(4px);
}

/* Chat Messages Container */
.chat-messages-container {
  height: 600px;
  overflow-y: auto;
  padding: 24px;
  scroll-behavior: smooth;
}

/* Welcome Screen */
.welcome-screen {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: 40px;
}

.welcome-animation {
  margin-bottom: 30px;
}

.robot-avatar {
  width: 120px;
  height: 120px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  animation: pulse-glow 2s ease-in-out infinite;
}

.robot-face {
  color: white;
  font-size: 24px;
}

.robot-eyes {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.eye {
  width: 8px;
  height: 8px;
  background: white;
  border-radius: 50%;
  animation: blink 3s ease-in-out infinite;
}

.robot-mouth {
  width: 20px;
  height: 10px;
  border: 2px solid white;
  border-top: none;
  border-radius: 0 0 10px 10px;
}

@keyframes blink {
  0%, 90%, 100% { transform: scaleY(1); }
  95% { transform: scaleY(0.1); }
}

.example-question-btn {
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
  text-align: left;
  font-size: 14px;
}

.example-question-btn:hover {
  background: rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

/* Message Wrappers */
.message-wrapper {
  margin-bottom: 24px;
  animation: slide-in-up 0.5s ease;
}

.user-message {
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  gap: 12px;
}

.assistant-message {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  gap: 12px;
}

.user-avatar, .assistant-avatar {
  flex-shrink: 0;
}

.user-avatar .avatar-bg {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #059669, #10b981);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.message-content {
  max-width: 85%;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 18px;
  padding: 16px 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.user-message .message-content {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
}

.message-text {
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 8px;
}

.message-timestamp {
  font-size: 12px;
  opacity: 0.6;
  margin-top: 8px;
}

.message-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.message-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  opacity: 0.6;
}

.action-btn:hover {
  opacity: 1;
  background: rgba(59, 130, 246, 0.1);
  transform: scale(1.1);
}

/* Interactive Elements */
.interactive-elements {
  margin-top: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.quality-indicator {
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
}

.entity-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.entity-chip {
  padding: 4px 10px;
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: 20px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.entity-chip:hover {
  background: rgba(59, 130, 246, 0.2);
  transform: scale(1.05);
}

.reading-time {
  display: flex;
  align-items: center;
  font-size: 12px;
  opacity: 0.7;
}

/* Sources Section */
.sources-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.sources-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #374151;
}

.sources-grid {
  display: grid;
  gap: 12px;
}

.source-card {
  padding: 12px;
  background: rgba(248, 250, 252, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.source-card:hover {
  background: rgba(59, 130, 246, 0.05);
  border-color: rgba(59, 130, 246, 0.2);
  transform: translateY(-2px);
}

.source-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.source-icon {
  font-size: 16px;
}

.source-info .source-title {
  font-weight: 600;
  font-size: 13px;
  color: #1f2937;
  margin-bottom: 2px;
}

.source-info .source-publication {
  font-size: 12px;
  color: #6b7280;
}

.source-relevance {
  font-size: 11px;
  color: #059669;
  font-weight: 500;
}

/* Suggested Questions */
.suggested-questions {
  margin-top: 20px;
}

.suggestions-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #374151;
}

.suggestions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
}

.suggestion-btn {
  padding: 10px 14px;
  background: rgba(59, 130, 246, 0.05);
  border: 1px solid rgba(59, 130, 246, 0.1);
  border-radius: 10px;
  font-size: 13px;
  text-align: left;
  transition: all 0.3s ease;
}

.suggestion-btn:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.2);
  transform: translateY(-1px);
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 24px;
  animation: slide-in-up 0.3s ease;
}

.typing-content {
  max-width: 85%;
}

.typing-bubble {
  background: rgba(255, 255, 255, 0.9);
  border-radius: 18px;
  padding: 16px 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.typing-text {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 12px;
}

.progress-bar {
  width: 100%;
  height: 3px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.typing-animation {
  display: flex;
  gap: 3px;
  align-items: center;
}

.typing-animation .dot {
  width: 4px;
  height: 4px;
  background: white;
  border-radius: 50%;
  animation: typing-dots 1.5s ease-in-out infinite;
}

.typing-animation .dot:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-animation .dot:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing-dots {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  30% {
    transform: translateY(-8px);
    opacity: 1;
  }
}

/* Input Area */
.input-area {
  margin-top: 20px;
  padding: 20px;
}

.input-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.input-wrapper {
  flex: 1;
  position: relative;
}

.message-input {
  width: 100%;
  padding: 16px 60px 16px 20px;
  border: 2px solid transparent;
  border-radius: 25px;
  background: rgba(255, 255, 255, 0.9);
  font-size: 15px;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.message-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.input-actions {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  gap: 4px;
}

.emoji-btn, .attachment-btn {
  padding: 6px;
  border-radius: 8px;
  background: transparent;
  transition: all 0.3s ease;
  opacity: 0.6;
}

.emoji-btn:hover, .attachment-btn:hover {
  opacity: 1;
  background: rgba(59, 130, 246, 0.1);
}

.send-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-btn.sending {
  animation: pulse-glow 1s ease-in-out infinite;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  opacity: 0.6;
  padding: 0 4px;
}

.character-count.warning {
  color: #ef4444;
  font-weight: 600;
}

.shortcuts {
  display: flex;
  gap: 8px;
  align-items: center;
}

.shortcuts kbd {
  padding: 2px 6px;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  font-size: 10px;
  font-family: monospace;
}

/* Citation Modal */
.citation-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fade-in 0.3s ease;
}

.citation-modal {
  background: white;
  border-radius: 20px;
  padding: 24px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
  animation: modal-slide-in 0.3s ease;
}

.citation-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.close-btn {
  padding: 8px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.citation-details {
  space-y: 20px;
}

.citation-header {
  margin-bottom: 16px;
}

.citation-meta {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  font-size: 14px;
  color: #6b7280;
}

.verification-methods {
  margin-bottom: 20px;
}

.verification-grid {
  display: grid;
  gap: 12px;
}

.verification-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(248, 250, 252, 0.8);
  border-radius: 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

.verification-icon {
  font-size: 20px;
}

.verification-info {
  flex: 1;
}

.verification-label {
  font-weight: 600;
  font-size: 14px;
  color: #374151;
  margin-bottom: 4px;
}

.verification-link {
  color: #3b82f6;
  text-decoration: underline;
  font-size: 13px;
}

.verification-value {
  font-weight: 600;
  color: #059669;
  font-size: 13px;
}

.verification-status.unavailable {
  color: #6b7280;
  font-size: 13px;
}

.citation-snippet {
  background: rgba(248, 250, 252, 0.8);
  padding: 16px;
  border-radius: 12px;
  border-left: 4px solid #3b82f6;
}

.snippet-text {
  font-style: italic;
  color: #4b5563;
  line-height: 1.6;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modal-slide-in {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* Citation Links */
:deep(.citation-link) {
  color: #3b82f6;
  cursor: pointer;
  text-decoration: underline;
  text-decoration-style: dotted;
  transition: all 0.3s ease;
}

:deep(.citation-link:hover) {
  color: #1d4ed8;
  background: rgba(59, 130, 246, 0.1);
  padding: 2px 4px;
  border-radius: 4px;
}

/* Responsive Design */
@media (max-width: 1024px) {
  .lg\\:col-span-1, .lg\\:col-span-3 {
    grid-column: span 1;
  }
  
  .chat-messages-container {
    height: 500px;
  }
}

@media (max-width: 768px) {
  .input-container {
    flex-direction: column;
    gap: 12px;
  }
  
  .send-btn {
    width: 100%;
    height: 48px;
    border-radius: 12px;
  }
  
  .message-content {
    max-width: 95%;
  }
  
  .suggestions-grid {
    grid-template-columns: 1fr;
  }
}

/* Dark Mode Adjustments */
.dark .card-glass {
  background: rgba(17, 24, 39, 0.8);
}

.dark .message-content {
  background: rgba(31, 41, 55, 0.9);
  color: white;
}

.dark .message-input {
  background: rgba(31, 41, 55, 0.9);
  color: white;
}

.dark .citation-modal {
  background: #1f2937;
  color: white;
}

/* Smooth Transitions */
* {
  transition: color 0.3s ease, background-color 0.3s ease, border-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
}
</style>