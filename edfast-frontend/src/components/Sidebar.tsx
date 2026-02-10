'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion } from 'framer-motion'
import {
  Home, User, MessageSquare, Brain, Calendar,
  FileText, BookOpen, LogOut, GraduationCap, Linkedin
} from 'lucide-react'
import { useAuth } from '@/lib/auth'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Profile', href: '/dashboard/profile', icon: User },
  { name: 'PeerHub', href: '/dashboard/peerhub', icon: MessageSquare },
  { name: 'AI Chatbot', href: '/dashboard/chatbot', icon: Brain },
  { name: 'Timetable', href: '/dashboard/timetable', icon: Calendar },
  { name: 'Resume Builder', href: '/dashboard/resume', icon: FileText },
  { name: 'Courses', href: '/dashboard/courses', icon: BookOpen },
  { name: 'LinkedIn', href: '/dashboard/linkedin', icon: Linkedin },
]

export default function Sidebar() {
  const pathname = usePathname()
  const { logout } = useAuth()

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <Link href="/dashboard" className="flex items-center gap-2">
          <GraduationCap className="w-8 h-8 text-primary-600" />
          <span className="text-2xl font-bold text-gray-900">EdFast</span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {navigation.map((item) => {
          const Icon = item.icon
          const isActive = pathname === item.href
          
          return (
            <Link key={item.name} href={item.href}>
              <motion.div
                whileHover={{ x: 4 }}
                className={`flex items-center px-4 py-3 rounded-lg transition-all ${
                  isActive
                    ? 'bg-primary-50 text-primary-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Icon className="w-5 h-5 mr-3" />
                <span className="font-medium">{item.name}</span>
              </motion.div>
            </Link>
          )
        })}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-gray-200">
        <motion.button
          whileHover={{ x: 4 }}
          onClick={logout}
          className="flex items-center px-4 py-3 w-full text-red-600 hover:bg-red-50 rounded-lg transition-all"
        >
          <LogOut className="w-5 h-5 mr-3" />
          <span className="font-medium">Logout</span>
        </motion.button>
      </div>
    </div>
  )
}




