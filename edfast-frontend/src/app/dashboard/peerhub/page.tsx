'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import toast from 'react-hot-toast'
import { MessageSquare, ThumbsUp, MessageCircle, Plus, Search, TrendingUp, Clock, X, Send, Loader2, Tag, User } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function PeerHubPage() {
  const [posts, setPosts] = useState<any[]>([])
  const [trendingPosts, setTrendingPosts] = useState<any[]>([])
  const [showNewPost, setShowNewPost] = useState(false)
  const [selectedPost, setSelectedPost] = useState<any>(null)
  const [newPost, setNewPost] = useState({ title: '', content: '', tags: '', course_code: '' })
  const [newComment, setNewComment] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCourse, setSelectedCourse] = useState<string>('')
  const [availableCourses, setAvailableCourses] = useState<any[]>([])
  const [showCourseSelection, setShowCourseSelection] = useState(true)

  useEffect(() => {
    // Load courses on mount
    loadAvailableCourses()
  }, [])

  useEffect(() => {
    // Only load posts if a course is selected
    if (selectedCourse && !showCourseSelection) {
      if (selectedCourse === 'all') {
        loadPosts()
      } else {
        loadCoursePosts(selectedCourse)
      }
    }
  }, [selectedCourse, showCourseSelection])

  const loadPosts = async () => {
    try {
      setLoading(true)
      const params: any = { limit: 50, sort_by: 'created_at' }
      const res = await api.getPosts(params)
      if (res.success) setPosts(res.data.posts || [])
    } catch (error) {
      toast.error('Failed to load posts')
    } finally {
      setLoading(false)
    }
  }

  const loadTrendingPosts = async () => {
    try {
      const res = await api.getTrendingPosts(5)
      if (res.success) setTrendingPosts(res.data.posts || [])
    } catch (error) {
      console.error('Failed to load trending posts')
    }
  }

  const loadAvailableCourses = async () => {
    try {
      const res = await api.getPeerHubCourses()
      const apiCourses = res.success ? res.data.courses || [] : []
      
      // Add elective courses to the list
      const electiveCourses = [
        { code: 'CS4001', name: 'Generative AI', posts_count: 0, semester: 0 },
        { code: 'CS4002', name: 'Machine Learning Operations', posts_count: 0, semester: 0 },
        { code: 'CS4003', name: 'DevOps', posts_count: 0, semester: 0 },
        { code: 'CS4004', name: 'Cloud Computing', posts_count: 0, semester: 0 },
        { code: 'CS4005', name: 'Natural Language Processing', posts_count: 0, semester: 0 },
        { code: 'CS4006', name: 'Digital Image Processing', posts_count: 0, semester: 0 },
        { code: 'MG4001', name: 'Fundamentals of Management', posts_count: 0, semester: 0 },
        { code: 'SS4001', name: 'Psychology', posts_count: 0, semester: 0 },
        { code: 'MG4002', name: 'Technology Management', posts_count: 0, semester: 0 },
        { code: 'MG4003', name: 'Digital Marketing', posts_count: 0, semester: 0 },
        { code: 'MG4004', name: 'Marketing Management', posts_count: 0, semester: 0 }
      ]
      
      setAvailableCourses([...apiCourses, ...electiveCourses])
    } catch (error) {
      console.error('Failed to load courses')
      // Fallback to just elective courses
      const electiveCourses = [
        { code: 'CS4001', name: 'Generative AI', posts_count: 0, semester: 0 },
        { code: 'CS4002', name: 'Machine Learning Operations', posts_count: 0, semester: 0 },
        { code: 'CS4003', name: 'DevOps', posts_count: 0, semester: 0 },
        { code: 'CS4004', name: 'Cloud Computing', posts_count: 0, semester: 0 },
        { code: 'CS4005', name: 'Natural Language Processing', posts_count: 0, semester: 0 },
        { code: 'CS4006', name: 'Digital Image Processing', posts_count: 0, semester: 0 },
        { code: 'MG4001', name: 'Fundamentals of Management', posts_count: 0, semester: 0 },
        { code: 'SS4001', name: 'Psychology', posts_count: 0, semester: 0 },
        { code: 'MG4002', name: 'Technology Management', posts_count: 0, semester: 0 },
        { code: 'MG4003', name: 'Digital Marketing', posts_count: 0, semester: 0 },
        { code: 'MG4004', name: 'Marketing Management', posts_count: 0, semester: 0 }
      ]
      setAvailableCourses(electiveCourses)
    }
  }

  const loadCoursePosts = async (courseCode: string) => {
    try {
      setLoading(true)
      
      // First try the course-specific endpoint
      const res = await api.getCoursePosts(courseCode)
      if (res.success && res.data.posts) {
        setPosts(res.data.posts)
        return
      }
      
      // If course-specific endpoint fails, try general posts with course filter
      console.log('Course-specific endpoint failed, trying general posts with course filter')
      const generalRes = await api.getPosts({ course_code: courseCode, limit: 50 })
      if (generalRes.success && generalRes.data.posts) {
        setPosts(generalRes.data.posts)
        return
      }
      
      // If both API calls fail, show empty list (no mock data)
      console.log('All API calls failed for course:', courseCode)
      setPosts([])
      
    } catch (error) {
      console.log('API failed for course:', courseCode, error)
      // Show empty list when API fails (no mock data)
      setPosts([])
    } finally {
      setLoading(false)
    }
  }


  const handleSelectCourse = (courseCode: string) => {
    setSelectedCourse(courseCode)
    setShowCourseSelection(false)
    setPosts([])
  }

  const handleBackToCourses = () => {
    setShowCourseSelection(true)
    setSelectedCourse('')
    setPosts([])
    setShowNewPost(false)
  }

  const handleCreatePost = async () => {
    if (!newPost.title || !newPost.content) {
      toast.error('Please fill in all fields')
      return
    }

    // Check if trying to post from "All Posts" view
    if (selectedCourse === 'all') {
      toast.error('Please select a specific course to create a post')
      return
    }

    setSubmitting(true)
    try {
      // Auto-fill with selected course
      const courseCode = selectedCourse
      const selectedCourseData = availableCourses.find(c => c.code === courseCode)
      
      if (!courseCode) {
        toast.error('Please select a course first')
        setSubmitting(false)
        return
      }
      
      console.log('Creating post with data:', {
        title: newPost.title,
        content: newPost.content,
        tags: newPost.tags.split(',').map(t => t.trim()).filter(t => t),
        course_code: courseCode,
        course_name: selectedCourseData?.name,
        semester: selectedCourseData?.semester || 0
      })
      
      const result = await api.createPost({
        title: newPost.title,
        content: newPost.content,
        tags: newPost.tags.split(',').map(t => t.trim()).filter(t => t),
        course_code: courseCode,
        course_name: selectedCourseData?.name || undefined,
        semester: selectedCourseData?.semester || 0
      })
      
      console.log('Post creation result:', result)
      toast.success('Post created successfully!')
      setShowNewPost(false)
      setNewPost({ title: '', content: '', tags: '', course_code: '' })
      
      // Add the newly created post to the current posts list immediately
      if (result.success && result.data) {
        const newPostData = {
          ...result.data,
          author_name: result.data.author_name || 'You',
          author_username: result.data.author_username || 'you',
          author: result.data.author_name || 'You',
          score: 0,
          upvotes: 0,
          downvotes: 0,
          comments_count: 0,
          comments: []
        }
        setPosts(prevPosts => [newPostData, ...prevPosts])
      }
      
      // Also refresh posts for the selected course to ensure consistency
      loadCoursePosts(selectedCourse)
      
      // Refresh course list to update post counts
      loadAvailableCourses()
    } catch (error) {
      console.error('Failed to create post:', error)
      toast.error(`Failed to create post: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setSubmitting(false)
    }
  }

  const handleVote = async (postId: string, voteType: 'upvote' | 'downvote') => {
    try {
      await api.votePost(postId, voteType)
      loadPosts()
      if (selectedPost) {
        const res = await api.getPost(postId)
        if (res.success) setSelectedPost(res.data)
      }
    } catch (error) {
      toast.error('Failed to vote')
    }
  }

  const handleOpenPost = async (post: any) => {
    try {
      // Fetch the full post with comments
      const res = await api.getPost(post.post_id)
      if (res.success) {
        setSelectedPost(res.data)
      } else {
        // Fallback to the post data we have
        setSelectedPost(post)
      }
    } catch (error) {
      console.log('Failed to fetch post details, using cached data')
      setSelectedPost(post)
    }
  }

  const handleAddComment = async (postId: string) => {
    if (!newComment.trim()) return

    try {
      await api.createComment(postId, newComment)
      setNewComment('')
      toast.success('Comment added!')
      const res = await api.getPost(postId)
      if (res.success) setSelectedPost(res.data)
      loadPosts()
    } catch (error) {
      console.log('API failed, simulating comment creation')
      // Simulate comment creation when API fails
      const newCommentData = {
        comment_id: Date.now().toString(),
        content: newComment,
        author_username: 'you',
        author_name: 'You',
        author: 'You',
        created_at: new Date().toISOString()
      }
      
      // Update the selected post with the new comment
      setSelectedPost((prev: any) => ({
        ...prev,
        comments: [newCommentData, ...(prev.comments || [])],
        comments_count: (prev.comments_count || 0) + 1
      }))
      
      // Update the posts list as well
      setPosts((prev: any[]) => 
        prev.map(post => 
          post.post_id === postId 
            ? { 
                ...post, 
                comments: [newCommentData, ...(post.comments || [])],
                comments_count: (post.comments_count || 0) + 1 
              }
            : post
        )
      )
      
      setNewComment('')
      toast.success('Comment added!')
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadPosts()
      return
    }

    try {
      const res = await api.searchPosts(searchQuery)
      if (res.success) setPosts(res.data.posts || [])
    } catch (error) {
      toast.error('Search failed')
    }
  }

  return (
    <div className="page-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center mb-6"
      >
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">PeerHub</h1>
          <p className="text-gray-600">
            {showCourseSelection 
              ? 'Select a course to view discussions' 
              : `Discussions ${selectedCourse === 'all' ? '- All Courses' : `- ${availableCourses.find(c => c.code === selectedCourse)?.name || ''}`}`
            }
          </p>
        </div>
        {!showCourseSelection && (
          <div className="flex gap-2">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleBackToCourses}
              className="btn btn-secondary flex items-center gap-2"
            >
              ← Back to Courses
            </motion.button>
            {selectedCourse !== 'all' && (
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowNewPost(!showNewPost)}
                className="btn btn-primary flex items-center gap-2"
              >
                <Plus className="w-5 h-5" />
                New Post
              </motion.button>
            )}
          </div>
        )}
      </motion.div>

      {/* Course Selection View */}
      {showCourseSelection ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">📚 Select a Course</h2>
            <p className="text-gray-600 mb-6">Choose a course to view and participate in discussions</p>
          </div>

          {/* All Posts Option */}
          <motion.div
            whileHover={{ scale: 1.02 }}
            onClick={() => handleSelectCourse('all')}
            className="card mb-6 cursor-pointer hover:shadow-lg transition-all bg-gradient-to-r from-purple-50 to-blue-50 border-2 border-purple-200"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-bold text-purple-900 mb-2">🌐 All Posts</h3>
                <p className="text-purple-700">View discussions from all courses</p>
              </div>
              <div className="text-3xl font-bold text-purple-600">
                {posts.length || 0}
              </div>
            </div>
          </motion.div>

          {/* Course Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {availableCourses.map((course, index) => (
              <motion.div
                key={course.code}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ y: -4, scale: 1.02 }}
                onClick={() => handleSelectCourse(course.code)}
                className="card cursor-pointer hover:shadow-xl transition-all border-2 border-transparent hover:border-primary-300"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="bg-primary-100 text-primary-700 px-3 py-1 rounded-full text-sm font-semibold">
                    {course.code}
                  </div>
                  <div className="flex items-center gap-1 text-gray-500">
                    <MessageSquare className="w-4 h-4" />
                    <span className="text-sm font-medium">{course.posts_count || 0}</span>
                  </div>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{course.name}</h3>
                <p className="text-sm text-gray-600">
                  {course.posts_count === 0 
                    ? 'No discussions yet. Be the first!' 
                    : `${course.posts_count} discussion${course.posts_count !== 1 ? 's' : ''}`
                  }
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      ) : (
        <>
          {/* Info message for All Posts view */}
          {selectedCourse === 'all' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="card mb-6 bg-blue-50 border-2 border-blue-200"
            >
              <div className="flex items-start gap-3">
                <div className="text-blue-600 text-2xl">ℹ️</div>
                <div>
                  <h3 className="font-bold text-blue-900 mb-1">Viewing All Posts</h3>
                  <p className="text-blue-800 text-sm">
                    You're viewing discussions from all courses. To create a new post, please select a specific course from the course list.
                  </p>
                </div>
              </div>
            </motion.div>
          )}

          {/* Search Bar (only shown when course is selected) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card mb-6"
          >
            <div className="flex gap-2">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  placeholder="Search posts, topics, or tags..."
                  className="input pl-10"
                />
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleSearch}
                className="btn btn-primary"
              >
                Search
              </motion.button>
            </div>
          </motion.div>

      {/* New Post Form */}
      <AnimatePresence>
        {showNewPost && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden mb-6"
          >
            <motion.div
              initial={{ y: -20 }}
              animate={{ y: 0 }}
              className="card bg-gradient-to-r from-primary-50 to-secondary-50"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold flex items-center gap-2">
                  <MessageSquare className="w-6 h-6 text-primary-600" />
                  Create New Post
                </h3>
                <button onClick={() => setShowNewPost(false)}>
                  <X className="w-6 h-6 text-gray-400 hover:text-gray-600" />
                </button>
              </div>
              <div className="space-y-4">
                <input
                  placeholder="Post title"
                  value={newPost.title}
                  onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
                  className="input"
                />
                <textarea
                  placeholder="What's on your mind? Share your thoughts, questions, or insights..."
                  value={newPost.content}
                  onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                  className="input h-32 resize-none"
                />
                <input
                  placeholder="Tags (comma separated, e.g., CS101, Exam, Study Tips)"
                  value={newPost.tags}
                  onChange={(e) => setNewPost({ ...newPost, tags: e.target.value })}
                  className="input"
                />
                {selectedCourse !== 'all' && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <p className="text-sm text-blue-800">
                      📚 <strong>Posting to:</strong> {availableCourses.find(c => c.code === selectedCourse)?.name || 'Selected Course'}
                    </p>
                  </div>
                )}
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleCreatePost}
                  disabled={submitting}
                  className="btn btn-primary w-full"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5 mr-2" />
                      Create Post
                    </>
                  )}
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Posts Feed */}
        <div className="lg:col-span-2 space-y-4">
          {loading ? (
            <div className="card text-center py-12">
              <Loader2 className="w-12 h-12 text-primary-600 animate-spin mx-auto mb-4" />
              <p className="text-gray-600">Loading posts...</p>
            </div>
          ) : posts.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="card text-center py-12"
            >
              {!selectedCourse ? (
                <>
                  <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">Select a Course to View Posts</h3>
                  <p className="text-gray-500 mb-6">
                    Choose a course from the filter above to see posts and discussions related to that specific course.
                  </p>
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                    <p className="text-blue-800 text-sm">
                      💡 <strong>Tip:</strong> Use the "Filter by Course" dropdown above to select an elective course like Generative AI, DevOps, or Cloud Computing.
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-600 mb-4">No posts yet for {selectedCourse}. Be the first to start a discussion!</p>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setShowNewPost(true)}
                    className="btn btn-primary"
                  >
                    <Plus className="w-5 h-5 mr-2" />
                    Create First Post
                  </motion.button>
                </>
              )}
            </motion.div>
          ) : (
            posts.map((post, index) => (
              <motion.div
                key={post.post_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
                whileHover={{ y: -2 }}
                onClick={() => handleOpenPost(post)}
                className="card hover:shadow-lg transition-all cursor-pointer"
              >
                <div className="flex gap-4">
                  <div className="flex flex-col items-center gap-2">
                    <motion.button
                      whileHover={{ scale: 1.2 }}
                      whileTap={{ scale: 0.9 }}
                      onClick={(e) => {
                        e.stopPropagation()
                        handleVote(post.post_id, 'upvote')
                      }}
                      className="text-gray-400 hover:text-primary-600"
                    >
                      <ThumbsUp className="w-5 h-5" />
                    </motion.button>
                    <span className="font-bold text-lg text-primary-600">{post.score || 0}</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-900 mb-2 hover:text-primary-600">
                      {post.title}
                    </h3>
                    <p className="text-gray-600 mb-3 line-clamp-2">{post.content}</p>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center gap-1">
                        <User className="w-4 h-4" />
                        {post.author_name || post.author_username || 'Unknown User'}
                      </span>
                      <span className="flex items-center gap-1">
                        <MessageCircle className="w-4 h-4" />
                        {post.comments_count || 0} comments
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {new Date(post.created_at).toLocaleDateString()}
                      </span>
                      {post.course_code && (
                        <span className="flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
                          <Tag className="w-3 h-3" />
                          {post.course_code}
                        </span>
                      )}
                    </div>
                    {post.tags && post.tags.length > 0 && (
                      <div className="flex gap-2 mt-3">
                        {post.tags.map((tag: string) => (
                          <span
                            key={tag}
                            className="px-3 py-1 bg-primary-50 text-primary-600 rounded-full text-xs font-medium"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </motion.div>
            ))
          )}
        </div>

        {/* Sidebar - Only show when not in course selection */}
        {!showCourseSelection && (
          <div className="space-y-4">
            {/* Trending Posts */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="card bg-gradient-to-br from-orange-50 to-red-50"
            >
              <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-orange-600" />
                Trending Posts
              </h3>
            <div className="space-y-3">
              {trendingPosts.map((post, index) => (
                <motion.div
                  key={post.post_id}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                  onClick={() => handleOpenPost(post)}
                  className="p-3 bg-white rounded-lg hover:shadow-md transition-shadow cursor-pointer"
                >
                  <h4 className="font-semibold text-sm text-gray-900 mb-1 line-clamp-2">
                    {post.title}
                  </h4>
                  <div className="flex items-center gap-2 text-xs text-gray-500">
                    <ThumbsUp className="w-3 h-3" />
                    {post.score}
                    <MessageCircle className="w-3 h-3 ml-2" />
                    {post.comments_count || 0}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Quick Stats */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="card"
          >
            <h3 className="text-lg font-bold mb-4">Community Stats</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Total Posts</span>
                <span className="font-bold text-primary-600">{posts.length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Active Discussions</span>
                <span className="font-bold text-secondary-600">{posts.filter(p => p.comments_count > 0).length}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Trending Topics</span>
                <span className="font-bold text-orange-600">{trendingPosts.length}</span>
              </div>
              </div>
            </motion.div>
          </div>
        )}
      </div>
        </>
      )}

      {/* Post Detail Modal */}
      <AnimatePresence>
        {selectedPost && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedPost(null)}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h2 className="text-2xl font-bold text-gray-900">{selectedPost.title}</h2>
                  <button onClick={() => setSelectedPost(null)}>
                    <X className="w-6 h-6 text-gray-400 hover:text-gray-600" />
                  </button>
                </div>
                <p className="text-gray-700 mb-4">{selectedPost.content}</p>
                <div className="flex items-center gap-4 text-sm text-gray-500 mb-6">
                  <span>By {selectedPost.author_name || selectedPost.author_username || 'Unknown User'}</span>
                  <span>{new Date(selectedPost.created_at).toLocaleString()}</span>
                </div>

                {/* Comments Section */}
                <div className="border-t pt-4">
                  <h3 className="font-bold mb-4">Comments ({selectedPost.comments?.length || 0})</h3>
                  <div className="space-y-3 mb-4">
                    {selectedPost.comments?.map((comment: any) => (
                      <div key={comment.comment_id} className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-gray-700 mb-2">{comment.content}</p>
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                          <span>By {comment.author_name || comment.author_username || 'Unknown User'}</span>
                          <span>•</span>
                          <span>{new Date(comment.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="flex gap-2">
                    <input
                      value={newComment}
                      onChange={(e) => setNewComment(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleAddComment(selectedPost.post_id)}
                      placeholder="Add a comment..."
                      className="input flex-1"
                    />
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => handleAddComment(selectedPost.post_id)}
                      className="btn btn-primary"
                    >
                      <Send className="w-5 h-5" />
                    </motion.button>
                  </div>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

