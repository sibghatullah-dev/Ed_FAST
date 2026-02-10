'use client'

import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import {
  TrendingUp, MessageSquare, FileText, Calendar,
  BookOpen, Award, Activity
} from 'lucide-react'
import { api } from '@/lib/api'
import toast from 'react-hot-toast'

export default function DashboardPage() {
  const [stats, setStats] = useState({
    posts: 0,
    trending: 0,
    courses: 0,
    activities: 0
  })
  const [recentActivity, setRecentActivity] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      const [dashboardStatsRes, activityRes, trendingRes] = await Promise.all([
        api.getDashboardStats(),
        api.getRecentActivity(),
        api.getTrendingPosts(5)
      ])
      
      if (dashboardStatsRes.success) {
        setStats({
          posts: dashboardStatsRes.data.posts || 0,
          trending: trendingRes.data?.count || 0,
          courses: dashboardStatsRes.data.courses || 0,
          activities: dashboardStatsRes.data.activities || 0
        })
      }
      
      if (activityRes.success) {
        setRecentActivity(activityRes.data.activities || [])
      }
    } catch (error) {
      console.error('Failed to load dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const cards = [
    { icon: MessageSquare, title: 'Recent Posts', value: stats.posts, color: 'from-blue-500 to-blue-600' },
    { icon: TrendingUp, title: 'Trending', value: stats.trending, color: 'from-green-500 to-green-600' },
    { icon: BookOpen, title: 'Courses', value: stats.courses, color: 'from-purple-500 to-purple-600' },
    { icon: Activity, title: 'Activities', value: stats.activities, color: 'from-orange-500 to-orange-600' },
  ]

  return (
    <div className="page-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Welcome back! Here's your academic overview.</p>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {cards.map((card, index) => (
          <motion.div
            key={card.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="card"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">{card.title}</p>
                <p className="text-3xl font-bold text-gray-900">
                  {loading ? '-' : card.value}
                </p>
              </div>
              <div className={`p-3 bg-gradient-to-br ${card.color} rounded-lg`}>
                <card.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        <div className="card">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Award className="w-6 h-6 text-primary-600" />
            Quick Actions
          </h2>
          <div className="space-y-3">
            {[
              { label: 'Upload Transcript', href: '/dashboard/profile', icon: FileText },
              { label: 'Build Resume', href: '/dashboard/resume', icon: FileText },
              { label: 'View Timetable', href: '/dashboard/timetable', icon: Calendar },
              { label: 'Ask AI', href: '/dashboard/chatbot', icon: Activity },
            ].map((action) => (
              <a
                key={action.label}
                href={action.href}
                className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <action.icon className="w-5 h-5 text-gray-600" />
                <span className="font-medium">{action.label}</span>
              </a>
            ))}
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-bold mb-4">Recent Activity</h2>
          <div className="space-y-3">
            {loading ? (
              <div className="text-center py-4">
                <p className="text-gray-500">Loading activities...</p>
              </div>
            ) : recentActivity.length > 0 ? (
              recentActivity.map((activity, index) => (
                <div key={activity.id || index} className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    activity.type === 'post' ? 'bg-primary-500' : 
                    activity.type === 'comment' ? 'bg-secondary-500' : 
                    'bg-purple-500'
                  }`}></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">{activity.title}</p>
                    <p className="text-xs text-gray-500">{activity.time_ago}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-4">
                <p className="text-gray-500">No recent activity</p>
                <p className="text-xs text-gray-400 mt-1">Start by creating a post or commenting!</p>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  )
}


