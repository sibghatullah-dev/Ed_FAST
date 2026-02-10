'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import toast from 'react-hot-toast'
import { BookOpen, Search, Filter, Star, Clock, Award, TrendingUp, Loader2, ChevronRight } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function CoursesPage() {
  const [courses, setCourses] = useState<any[]>([])
  const [filteredCourses, setFilteredCourses] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedDepartment, setSelectedDepartment] = useState('')
  const [selectedSemester, setSelectedSemester] = useState('')
  const [selectedCourse, setSelectedCourse] = useState<any>(null)
  const [stats, setStats] = useState<any>({})

  const departments = ['All', 'Computer Science', 'Mathematics', 'Engineering', 'Business', 'Science']
  const semesters = ['All', '1', '2', '3', '4', '5', '6', '7', '8']

  useEffect(() => {
    loadCourses()
    loadStats()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [courses, searchQuery, selectedDepartment, selectedSemester])

  const loadCourses = async () => {
    try {
      const res = await api.getMyTranscriptCourses()
      if (res.success && res.data.courses) {
        setCourses(res.data.courses)
        setFilteredCourses(res.data.courses)
        setStats(res.data.statistics)
      }
    } catch (error) {
      toast.error('Failed to load courses')
    } finally {
      setLoading(false)
    }
  }

  const loadStats = async () => {
    try {
      const res = await api.getMyTranscriptCourses()
      if (res.success && res.data.statistics) {
        setStats(res.data.statistics)
      }
    } catch (error) {
      console.error('Failed to load stats')
    }
  }

  const applyFilters = () => {
    let filtered = [...courses]

    if (searchQuery) {
      filtered = filtered.filter(course =>
        course.code?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        course.name?.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    if (selectedDepartment && selectedDepartment !== 'All') {
      filtered = filtered.filter(course => course.type === selectedDepartment)
    }

    if (selectedSemester && selectedSemester !== 'All') {
      filtered = filtered.filter(course => course.semester?.includes(selectedSemester))
    }

    setFilteredCourses(filtered)
  }

  const colors = [
    'from-blue-500 to-blue-600',
    'from-green-500 to-green-600',
    'from-purple-500 to-purple-600',
    'from-pink-500 to-pink-600',
    'from-orange-500 to-orange-600',
    'from-teal-500 to-teal-600',
  ]

  const getColorForIndex = (index: number) => colors[index % colors.length]

  return (
    <div className="page-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Course Catalog</h1>
        <p className="text-gray-600">Browse and explore available courses</p>
      </motion.div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Total Courses', value: stats.total_courses || 0, icon: BookOpen, color: 'from-blue-500 to-blue-600' },
          { label: 'Total Credits', value: stats.total_credits || 0, icon: Award, color: 'from-green-500 to-green-600' },
          { label: 'CGPA', value: stats.cgpa || 0, icon: Star, color: 'from-purple-500 to-purple-600' },
          { label: 'Semesters', value: stats.semesters_completed || 0, icon: TrendingUp, color: 'from-orange-500 to-orange-600' },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ y: -5 }}
            className="card"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">{stat.label}</p>
                <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
              </div>
              <div className={`p-3 bg-gradient-to-br ${stat.color} rounded-lg`}>
                <stat.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Search and Filters */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card mb-6"
      >
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search courses by code or name..."
                className="input pl-10"
              />
            </div>
          </div>
          <div>
            <select
              value={selectedDepartment}
              onChange={(e) => setSelectedDepartment(e.target.value)}
              className="input"
            >
              {departments.map(dept => (
                <option key={dept} value={dept}>{dept}</option>
              ))}
            </select>
          </div>
          <div>
            <select
              value={selectedSemester}
              onChange={(e) => setSelectedSemester(e.target.value)}
              className="input"
            >
              <option value="">All Semesters</option>
              {semesters.filter(s => s !== 'All').map(sem => (
                <option key={sem} value={sem}>Semester {sem}</option>
              ))}
            </select>
          </div>
        </div>
      </motion.div>

      {/* Courses Grid */}
      {loading ? (
        <div className="card text-center py-12">
          <Loader2 className="w-12 h-12 text-primary-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading courses...</p>
        </div>
      ) : filteredCourses.length === 0 ? (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="card text-center py-12"
        >
          <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Courses Found</h3>
          <p className="text-gray-600">Try adjusting your filters or search query</p>
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((course, index) => (
            <motion.div
              key={course.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
              whileHover={{ y: -5, scale: 1.02 }}
              onClick={() => setSelectedCourse(course)}
              className="card cursor-pointer hover:shadow-xl transition-all"
            >
              {/* Course Header */}
              <div className={`h-3 bg-gradient-to-r ${getColorForIndex(index)} rounded-t-lg -m-6 mb-4`} />
              
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-lg font-bold text-gray-900 mb-1">{course.code}</h3>
                  <p className="text-sm text-gray-600">{course.type}</p>
                </div>
                <div className="flex flex-col gap-1">
                  {course.grade && (
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      course.grade === 'A' || course.grade === 'A+' ? 'bg-green-100 text-green-700' :
                      course.grade === 'B' || course.grade === 'B+' ? 'bg-blue-100 text-blue-700' :
                      course.grade === 'C' || course.grade === 'C+' ? 'bg-yellow-100 text-yellow-700' :
                      course.grade === 'D' ? 'bg-orange-100 text-orange-700' :
                      'bg-red-100 text-red-700'
                    }`}>
                      Grade: {course.grade}
                    </span>
                  )}
                </div>
              </div>

              <h4 className="font-semibold text-gray-900 mb-3 line-clamp-2">{course.name}</h4>

              {course.description && (
                <p className="text-sm text-gray-600 mb-4 line-clamp-3">{course.description}</p>
              )}

              <div className="flex items-center justify-between text-sm text-gray-600 pt-3 border-t border-gray-100">
                <span className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  {course.semester}
                </span>
                <span className="flex items-center gap-1">
                  <Award className="w-4 h-4" />
                  {course.credit_hours} credits
                </span>
              </div>

              {course.prerequisites && course.prerequisites.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <p className="text-xs text-gray-500 mb-1">Prerequisites:</p>
                  <div className="flex flex-wrap gap-1">
                    {course.prerequisites.slice(0, 2).map((prereq: string, i: number) => (
                      <span key={i} className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                        {prereq}
                      </span>
                    ))}
                    {course.prerequisites.length > 2 && (
                      <span className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                        +{course.prerequisites.length - 2} more
                      </span>
                    )}
                  </div>
                </div>
              )}

              <motion.div
                className="mt-4 flex items-center text-primary-600 font-medium text-sm"
                whileHover={{ x: 5 }}
              >
                View Details
                <ChevronRight className="w-4 h-4 ml-1" />
              </motion.div>
            </motion.div>
          ))}
        </div>
      )}

      {/* Course Detail Modal */}
      <AnimatePresence>
        {selectedCourse && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedCourse(null)}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className={`h-3 bg-gradient-to-r ${getColorForIndex(0)} rounded-t-xl`} />
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-1">{selectedCourse.code}</h2>
                    <p className="text-gray-600">{selectedCourse.name}</p>
                  </div>
                  <button
                    onClick={() => setSelectedCourse(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Semester</p>
                    <p className="text-lg font-bold text-gray-900">{selectedCourse.semester}</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Credits</p>
                    <p className="text-lg font-bold text-gray-900">{selectedCourse.credit_hours}</p>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Grade</p>
                    <p className="text-lg font-bold text-gray-900">{selectedCourse.grade || 'N/A'}</p>
                  </div>
                </div>

                {selectedCourse.description && (
                  <div className="mb-6">
                    <h3 className="font-bold text-gray-900 mb-2">Description</h3>
                    <p className="text-gray-700 leading-relaxed">{selectedCourse.description}</p>
                  </div>
                )}

                {selectedCourse.prerequisites && selectedCourse.prerequisites.length > 0 && (
                  <div className="mb-6">
                    <h3 className="font-bold text-gray-900 mb-2">Prerequisites</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedCourse.prerequisites.map((prereq: string, index: number) => (
                        <span key={index} className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium">
                          {prereq}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="mb-4">
                  <h3 className="font-bold text-gray-900 mb-2">Course Type</h3>
                  <p className="text-gray-700">{selectedCourse.type}</p>
                </div>

                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setSelectedCourse(null)}
                  className="btn btn-primary w-full"
                >
                  Close
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

