'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import toast from 'react-hot-toast'
import { Upload, User, FileText, Loader2, CheckCircle, Image as ImageIcon, Edit2, Save } from 'lucide-react'
import { motion } from 'framer-motion'

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>(null)
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [editing, setEditing] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const res = await api.getCurrentUser()
      if (res.success) {
        setProfile(res.data)
        setDescription(res.data.description || '')
      }
    } catch (error) {
      toast.error('Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const handleTranscriptUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    try {
      const res = await api.uploadTranscript(file)
      if (res.success) {
        toast.success('Transcript uploaded successfully!')
        loadProfile()
      }
    } catch (error: any) {
      toast.error(error.message || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleUpdateDescription = async () => {
    setSaving(true)
    try {
      await api.updateProfile({ description })
      toast.success('Description updated!')
      setEditing(false)
      loadProfile()
    } catch (error) {
      toast.error('Update failed')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="page-container flex items-center justify-center h-96">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center"
        >
          <Loader2 className="w-12 h-12 text-primary-600 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading profile...</p>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="page-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-2">My Profile</h1>
        <p className="text-gray-600">Manage your personal information and academic data</p>
      </motion.div>

      {/* Profile Header Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card mb-6 bg-gradient-to-r from-primary-50 to-secondary-50"
      >
        <div className="flex items-center gap-6">
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="w-24 h-24 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center text-white text-4xl font-bold shadow-lg"
          >
            {profile?.name?.charAt(0).toUpperCase() || 'U'}
          </motion.div>
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-1">{profile?.name}</h2>
            <p className="text-gray-600 mb-2">@{profile?.username}</p>
            <div className="flex gap-2">
              {profile?.has_transcript && (
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-700">
                  <CheckCircle className="w-4 h-4 mr-1" />
                  Transcript Verified
                </span>
              )}
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-700">
                <User className="w-4 h-4 mr-1" />
                Active Student
              </span>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Personal Information */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-primary-100 rounded-lg">
              <User className="w-6 h-6 text-primary-600" />
            </div>
            <h2 className="text-xl font-bold">Personal Information</h2>
          </div>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium text-gray-600">Full Name</label>
              <p className="text-lg font-semibold text-gray-900">{profile?.name}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">Username</label>
              <p className="text-lg font-semibold text-gray-900">@{profile?.username}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-gray-600">Member Since</label>
              <p className="text-lg font-semibold text-gray-900">
                {new Date(profile?.created_at || Date.now()).toLocaleDateString()}
              </p>
            </div>
          </div>
        </motion.div>

        {/* Transcript Upload */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-3 bg-secondary-100 rounded-lg">
              <FileText className="w-6 h-6 text-secondary-600" />
            </div>
            <h2 className="text-xl font-bold">Academic Transcript</h2>
          </div>
          <div className="space-y-4">
            <p className="text-gray-600">
              Upload your academic transcript for AI-powered analysis and personalized recommendations.
            </p>
            <label className="btn btn-primary cursor-pointer inline-flex items-center gap-2">
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  {profile?.has_transcript ? 'Update Transcript' : 'Upload Transcript'}
                </>
              )}
              <input
                type="file"
                onChange={handleTranscriptUpload}
                className="hidden"
                accept="image/*,.pdf"
                disabled={uploading}
              />
            </label>
            {profile?.has_transcript && (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                className="flex items-center gap-2 text-green-600"
              >
                <CheckCircle className="w-5 h-5" />
                <span className="font-medium">Transcript uploaded and processed</span>
              </motion.div>
            )}
          </div>
        </motion.div>
      </div>

      {/* Description Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Edit2 className="w-6 h-6 text-purple-600" />
            </div>
            <h2 className="text-xl font-bold">About Me</h2>
          </div>
          {!editing && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => setEditing(true)}
              className="btn btn-outline text-sm"
            >
              <Edit2 className="w-4 h-4 mr-2" />
              Edit
            </motion.button>
          )}
        </div>
        {editing ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="input h-32 resize-none"
              placeholder="Tell us about yourself, your academic interests, goals, and achievements..."
            />
            <div className="flex gap-2">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleUpdateDescription}
                disabled={saving}
                className="btn btn-primary"
              >
                {saving ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Save
                  </>
                )}
              </motion.button>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  setEditing(false)
                  setDescription(profile?.description || '')
                }}
                className="btn btn-secondary"
              >
                Cancel
              </motion.button>
            </div>
          </motion.div>
        ) : (
          <p className="text-gray-700 leading-relaxed">
            {description || 'No description added yet. Click Edit to add information about yourself.'}
          </p>
        )}
      </motion.div>

      {/* Quick Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6"
      >
        {[
          { label: 'Posts Created', value: profile?.posts_count || 0, color: 'from-blue-500 to-blue-600' },
          { label: 'Comments', value: profile?.comments_count || 0, color: 'from-green-500 to-green-600' },
          { label: 'Upvotes Received', value: profile?.upvotes_count || 0, color: 'from-purple-500 to-purple-600' },
          { label: 'Reputation', value: profile?.reputation || 0, color: 'from-orange-500 to-orange-600' },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 + index * 0.1 }}
            whileHover={{ y: -5 }}
            className="card text-center"
          >
            <div className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-lg flex items-center justify-center mx-auto mb-3`}>
              <span className="text-2xl font-bold text-white">{stat.value}</span>
            </div>
            <p className="text-sm font-medium text-gray-600">{stat.label}</p>
          </motion.div>
        ))}
      </motion.div>
    </div>
  )
}

