'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth'
import { motion } from 'framer-motion'
import { BookOpen, Brain, Calendar, FileText, MessageSquare, TrendingUp } from 'lucide-react'

export default function LandingPage() {
  const router = useRouter()
  const { isAuthenticated, isLoading } = useAuth()

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard')
    }
  }, [isAuthenticated, isLoading, router])

  const features = [
    { icon: Brain, title: 'AI Chatbot', desc: 'Get personalized academic guidance' },
    { icon: MessageSquare, title: 'PeerHub', desc: 'Connect with fellow students' },
    { icon: Calendar, title: 'Timetable', desc: 'Organize your schedule efficiently' },
    { icon: FileText, title: 'Resume Builder', desc: 'Create ATS-friendly resumes' },
    { icon: BookOpen, title: 'Course Explorer', desc: 'Browse and plan courses' },
    { icon: TrendingUp, title: 'Analytics', desc: 'Track your academic progress' },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      {/* Hero Section */}
      <div className="page-container min-h-screen flex flex-col justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h1 className="text-6xl font-bold text-gray-900 mb-6">
            Welcome to <span className="text-primary-600">EdFast</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Your AI-powered academic companion. Analyze transcripts, get personalized guidance,
            and manage your academic journey efficiently.
          </p>
          <div className="flex gap-4 justify-center">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => router.push('/login')}
              className="btn btn-primary text-lg px-8 py-3"
            >
              Get Started
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => router.push('/register')}
              className="btn btn-outline text-lg px-8 py-3"
            >
              Sign Up
            </motion.button>
          </div>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
              className="card hover:shadow-lg transition-shadow"
            >
              <feature.icon className="w-12 h-12 text-primary-600 mb-4" />
              <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  )
}




