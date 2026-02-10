'use client'

import { useState, useEffect, useRef } from 'react'
import { api } from '@/lib/api'
import toast from 'react-hot-toast'
import { Send, Bot, User, Sparkles, Trash2, Loader2, BookOpen } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function ChatbotPage() {
  const [messages, setMessages] = useState<any[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingHistory, setLoadingHistory] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadHistory()
  }, [])

  useEffect(() => {
    // Add a small delay to ensure the message is fully rendered
    const timer = setTimeout(() => {
      scrollToBottom()
    }, 100)
    return () => clearTimeout(timer)
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const formatMessageContent = (content: string) => {
    return content.split('\n').map((line, index) => {
      // Handle bullet points
      if (line.trim().startsWith('*')) {
        return (
          <div key={index} className="flex items-start gap-2 mb-1">
            <span className="text-primary-600 mt-1">•</span>
            <span>{line.trim().substring(1).trim()}</span>
          </div>
        )
      }
      // Handle bold text (simple **text** format)
      if (line.includes('**')) {
        const parts = line.split('**')
        return (
          <div key={index} className="mb-2">
            {parts.map((part, partIndex) => 
              partIndex % 2 === 1 ? (
                <strong key={partIndex} className="font-semibold text-gray-900">{part}</strong>
              ) : (
                <span key={partIndex}>{part}</span>
              )
            )}
          </div>
        )
      }
      // Handle empty lines
      if (line.trim() === '') {
        return <div key={index} className="mb-2"></div>
      }
      // Regular lines
      return (
        <div key={index} className="mb-2">
          {line}
        </div>
      )
    })
  }

  const loadHistory = async () => {
    try {
      const res = await api.getChatHistory()
      if (res.success && res.data.history) {
        setMessages(res.data.history)
      }
    } catch (error) {
      console.error('Failed to load history')
    } finally {
      setLoadingHistory(false)
    }
  }

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage = { role: 'user', content: input, timestamp: new Date().toISOString() }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const res = await api.sendChatQuery(input)
      if (res.success) {
        const responseContent = res.data.message || res.data.data?.message || 'No response received'
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: responseContent,
          timestamp: new Date().toISOString()
        }])
      } else {
        throw new Error(res.error || 'Failed to get response')
      }
    } catch (error: any) {
      toast.error(error.message || 'Failed to send message')
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      }])
    } finally {
      setLoading(false)
    }
  }

  const clearHistory = async () => {
    try {
      await api.clearChatHistory()
      setMessages([])
      toast.success('Chat history cleared')
    } catch (error) {
      toast.error('Failed to clear history')
    }
  }

  const suggestedQuestions = [
    "What courses should I take next semester?",
    "How can I improve my GPA?",
    "Tell me about career paths in my field",
    "What are the prerequisites for advanced courses?"
  ]

  return (
    <div className="h-[calc(100vh-80px)] flex flex-col">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-primary-600 to-secondary-600 text-white p-6 rounded-t-xl shadow-lg"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <motion.div
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
              className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center"
            >
              <Bot className="w-7 h-7" />
            </motion.div>
            <div>
              <h1 className="text-2xl font-bold">AI Academic Advisor</h1>
              <p className="text-sm text-white text-opacity-90">Your personal study companion powered by AI</p>
            </div>
          </div>
          {messages.length > 0 && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={clearHistory}
              className="px-4 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 rounded-lg flex items-center gap-2 transition-all"
            >
              <Trash2 className="w-4 h-4" />
              Clear Chat
            </motion.button>
          )}
        </div>
      </motion.div>

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto bg-gray-50 p-6 space-y-4 min-h-0">
        {loadingHistory ? (
          <div className="flex items-center justify-center h-full">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center"
            >
              <Loader2 className="w-12 h-12 text-primary-600 animate-spin mx-auto mb-4" />
              <p className="text-gray-600">Loading chat history...</p>
            </motion.div>
          </div>
        ) : messages.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center justify-center h-full text-center"
          >
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-24 h-24 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mb-6"
            >
              <Sparkles className="w-12 h-12 text-white" />
            </motion.div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to AI Academic Advisor!</h2>
            <p className="text-gray-600 mb-8 max-w-md">
              Ask me anything about your courses, academic planning, career guidance, or study tips.
            </p>
            
            {/* Suggested Questions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl">
              {suggestedQuestions.map((question, index) => (
                <motion.button
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ scale: 1.05, y: -2 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setInput(question)}
                  className="p-4 bg-white rounded-lg shadow-sm hover:shadow-md transition-all text-left border border-gray-200"
                >
                  <BookOpen className="w-5 h-5 text-primary-600 mb-2" />
                  <p className="text-sm text-gray-700">{question}</p>
                </motion.button>
              ))}
            </div>
          </motion.div>
        ) : (
          <AnimatePresence>
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <motion.div
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center flex-shrink-0"
                  >
                    <Bot className="w-6 h-6 text-white" />
                  </motion.div>
                )}
                <motion.div
                  whileHover={{ scale: 1.02 }}
                  className={`max-w-[85%] p-4 rounded-2xl shadow-sm ${
                    msg.role === 'user'
                      ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white'
                      : 'bg-white text-gray-900 border border-gray-200'
                  }`}
                >
                  <div className="prose prose-sm max-w-none">
                    <div className="break-words leading-relaxed text-sm">
                      {formatMessageContent(msg.content)}
                    </div>
                  </div>
                  <p className={`text-xs mt-3 ${msg.role === 'user' ? 'text-white text-opacity-70' : 'text-gray-400'}`}>
                    {new Date(msg.timestamp || Date.now()).toLocaleTimeString()}
                  </p>
                </motion.div>
                {msg.role === 'user' && (
                  <motion.div
                    whileHover={{ scale: 1.1, rotate: -5 }}
                    className="w-10 h-10 bg-gradient-to-br from-secondary-500 to-secondary-600 rounded-full flex items-center justify-center flex-shrink-0"
                  >
                    <User className="w-6 h-6 text-white" />
                  </motion.div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        )}

        {loading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-3 justify-start"
          >
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-200">
              <div className="flex gap-2">
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                  className="w-3 h-3 bg-primary-400 rounded-full"
                />
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                  className="w-3 h-3 bg-primary-400 rounded-full"
                />
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                  className="w-3 h-3 bg-primary-400 rounded-full"
                />
              </div>
            </div>
          </motion.div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white border-t border-gray-200 p-4 rounded-b-xl shadow-lg"
      >
        <div className="flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !loading && sendMessage()}
            placeholder="Type your question here... (e.g., 'What courses should I take?')"
            className="input flex-1 text-lg"
            disabled={loading}
          />
          <motion.button
            whileHover={{ scale: loading ? 1 : 1.05 }}
            whileTap={{ scale: loading ? 1 : 0.95 }}
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className={`btn btn-primary px-8 flex items-center gap-2 ${
              (!input.trim() || loading) ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" />
                Thinking...
              </>
            ) : (
              <>
                <Send className="w-5 h-5" />
                Send
              </>
            )}
          </motion.button>
        </div>
        <p className="text-xs text-gray-500 mt-2 text-center">
          💡 Tip: Ask about course recommendations, study strategies, or career advice
        </p>
      </motion.div>
    </div>
  )
}

