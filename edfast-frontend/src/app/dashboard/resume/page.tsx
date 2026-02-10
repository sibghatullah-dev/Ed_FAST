'use client'

import { useState, useEffect } from 'react'
import { api } from '@/lib/api'
import toast from 'react-hot-toast'
import { FileText, Download, Save, Sparkles, Plus, X, Edit2, Trash2, Loader2, Award, Briefcase, GraduationCap } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function ResumePage() {
  const [resumeData, setResumeData] = useState<any>({
    personal_info: { name: '', email: '', phone: '', address: '' },
    education: [],
    experience: [],
    skills: [],
    projects: [],
    certifications: [],
    languages: [],
    objective: '',
    linkedin: '',
    github: '',
    website: ''
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [editing, setEditing] = useState<string | null>(null)

  useEffect(() => {
    loadResumeData()
  }, [])

  const loadResumeData = async () => {
    try {
      const res = await api.getResumeData()
      if (res.success && res.data) {
        setResumeData(res.data)
      }
    } catch (error) {
      console.error('Failed to load resume data')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      await api.updateResumeData(resumeData)
      toast.success('Resume data saved!')
    } catch (error) {
      toast.error('Failed to save resume')
    } finally {
      setSaving(false)
    }
  }

  const handleAutoFill = async () => {
    try {
      const res = await api.autofillResume()
      if (res.success) {
        setResumeData(res.data)
        toast.success('Resume auto-filled from transcript!')
      }
    } catch (error: any) {
      toast.error(error.message || 'Auto-fill failed')
    }
  }

  const handleGeneratePDF = async () => {
    setGenerating(true)
    try {
      const blob = await api.generateResumePDF(resumeData)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'resume.pdf'
      a.click()
      toast.success('Resume PDF generated!')
    } catch (error) {
      toast.error('Failed to generate PDF')
    } finally {
      setGenerating(false)
    }
  }

  const addItem = (section: string) => {
    const newItem = section === 'education'
      ? { institution: '', degree: '', year: '', gpa: '' }
      : section === 'experience'
      ? { title: '', company: '', duration: '', description: '' }
      : section === 'projects'
      ? { name: '', description: '', technologies: '' }
      : section === 'certifications'
      ? { name: '', issuer: '', date: '' }
      : section === 'languages'
      ? { language: '', proficiency: 'Intermediate' }
      : ''

    setResumeData({
      ...resumeData,
      [section]: [...(resumeData[section] || []), newItem]
    })
  }

  const removeItem = (section: string, index: number) => {
    setResumeData({
      ...resumeData,
      [section]: resumeData[section].filter((_: any, i: number) => i !== index)
    })
  }

  const updateItem = (section: string, index: number, field: string, value: string) => {
    const updated = [...resumeData[section]]
    updated[index] = { ...updated[index], [field]: value }
    setResumeData({ ...resumeData, [section]: updated })
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
          <p className="text-gray-600">Loading resume data...</p>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="page-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Resume Builder</h1>
        <p className="text-gray-600">Create an ATS-friendly professional resume</p>
      </motion.div>

      {/* Action Bar */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card mb-6 bg-gradient-to-r from-primary-50 to-secondary-50"
      >
        <div className="flex flex-wrap gap-3">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleAutoFill}
            className="btn btn-secondary"
          >
            <Sparkles className="w-4 h-4 mr-2" />
            Auto-Fill from Transcript
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleSave}
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
            onClick={handleGeneratePDF}
            disabled={generating}
            className="btn btn-outline"
          >
            {generating ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                Download PDF
              </>
            )}
          </motion.button>
        </div>
      </motion.div>

      {/* Personal Information */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card mb-6"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-primary-100 rounded-lg">
            <FileText className="w-6 h-6 text-primary-600" />
          </div>
          <h2 className="text-xl font-bold">Personal Information</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">Full Name</label>
            <input
              type="text"
              value={resumeData.personal_info?.name || ''}
              onChange={(e) => setResumeData({
                ...resumeData,
                personal_info: { ...resumeData.personal_info, name: e.target.value }
              })}
              className="input"
              placeholder="John Doe"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">Email</label>
            <input
              type="email"
              value={resumeData.personal_info?.email || ''}
              onChange={(e) => setResumeData({
                ...resumeData,
                personal_info: { ...resumeData.personal_info, email: e.target.value }
              })}
              className="input"
              placeholder="john@example.com"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">Phone</label>
            <input
              type="tel"
              value={resumeData.personal_info?.phone || ''}
              onChange={(e) => setResumeData({
                ...resumeData,
                personal_info: { ...resumeData.personal_info, phone: e.target.value }
              })}
              className="input"
              placeholder="+1 234 567 8900"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">Address</label>
            <input
              type="text"
              value={resumeData.personal_info?.address || ''}
              onChange={(e) => setResumeData({
                ...resumeData,
                personal_info: { ...resumeData.personal_info, address: e.target.value }
              })}
              className="input"
              placeholder="City, Country"
            />
          </div>
        </div>
        <div className="mt-4">
          <label className="text-sm font-medium text-gray-700 mb-1 block">Career Objective</label>
          <textarea
            value={resumeData.objective || ''}
            onChange={(e) => setResumeData({
              ...resumeData,
              objective: e.target.value
            })}
            className="input h-24 resize-none"
            placeholder="Brief description of your career goals and what you bring to the table..."
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">LinkedIn URL</label>
            <input
              type="url"
              value={resumeData.linkedin || ''}
              onChange={(e) => setResumeData({
                ...resumeData,
                linkedin: e.target.value
              })}
              className="input"
              placeholder="https://linkedin.com/in/yourprofile"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">GitHub URL</label>
            <input
              type="url"
              value={resumeData.github || ''}
              onChange={(e) => setResumeData({
                ...resumeData,
                github: e.target.value
              })}
              className="input"
              placeholder="https://github.com/yourusername"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 mb-1 block">Portfolio Website</label>
            <input
              type="url"
              value={resumeData.website || ''}
              onChange={(e) => setResumeData({
                ...resumeData,
                website: e.target.value
              })}
              className="input"
              placeholder="https://yourportfolio.com"
            />
          </div>
        </div>
      </motion.div>

      {/* Education */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card mb-6"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-secondary-100 rounded-lg">
              <GraduationCap className="w-6 h-6 text-secondary-600" />
            </div>
            <h2 className="text-xl font-bold">Education</h2>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => addItem('education')}
            className="btn btn-secondary text-sm"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Education
          </motion.button>
        </div>
        <div className="space-y-4">
          {resumeData.education?.map((edu: any, index: number) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-4 bg-gray-50 rounded-lg"
            >
              <div className="flex justify-between items-start mb-3">
                <h3 className="font-semibold text-gray-900">Education #{index + 1}</h3>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => removeItem('education', index)}
                  className="text-red-500 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </motion.button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input
                  type="text"
                  value={edu.institution || ''}
                  onChange={(e) => updateItem('education', index, 'institution', e.target.value)}
                  className="input"
                  placeholder="Institution"
                />
                <input
                  type="text"
                  value={edu.degree || ''}
                  onChange={(e) => updateItem('education', index, 'degree', e.target.value)}
                  className="input"
                  placeholder="Degree"
                />
                <input
                  type="text"
                  value={edu.year || ''}
                  onChange={(e) => updateItem('education', index, 'year', e.target.value)}
                  className="input"
                  placeholder="Year"
                />
                <input
                  type="text"
                  value={edu.gpa || ''}
                  onChange={(e) => updateItem('education', index, 'gpa', e.target.value)}
                  className="input"
                  placeholder="GPA"
                />
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Experience */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="card mb-6"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Briefcase className="w-6 h-6 text-purple-600" />
            </div>
            <h2 className="text-xl font-bold">Experience</h2>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => addItem('experience')}
            className="btn btn-secondary text-sm"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Experience
          </motion.button>
        </div>
        <div className="space-y-4">
          {resumeData.experience?.map((exp: any, index: number) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-4 bg-gray-50 rounded-lg"
            >
              <div className="flex justify-between items-start mb-3">
                <h3 className="font-semibold text-gray-900">Experience #{index + 1}</h3>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => removeItem('experience', index)}
                  className="text-red-500 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </motion.button>
              </div>
              <div className="grid grid-cols-1 gap-3">
                <input
                  type="text"
                  value={exp.title || ''}
                  onChange={(e) => updateItem('experience', index, 'title', e.target.value)}
                  className="input"
                  placeholder="Job Title"
                />
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <input
                    type="text"
                    value={exp.company || ''}
                    onChange={(e) => updateItem('experience', index, 'company', e.target.value)}
                    className="input"
                    placeholder="Company"
                  />
                  <input
                    type="text"
                    value={exp.duration || ''}
                    onChange={(e) => updateItem('experience', index, 'duration', e.target.value)}
                    className="input"
                    placeholder="Duration (e.g., Jan 2020 - Dec 2022)"
                  />
                </div>
                <textarea
                  value={exp.description || ''}
                  onChange={(e) => updateItem('experience', index, 'description', e.target.value)}
                  className="input h-24 resize-none"
                  placeholder="Description"
                />
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Skills */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="card"
      >
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-orange-100 rounded-lg">
            <Award className="w-6 h-6 text-orange-600" />
          </div>
          <h2 className="text-xl font-bold">Skills</h2>
        </div>
        <textarea
          value={resumeData.skills?.join(', ') || ''}
          onChange={(e) => setResumeData({
            ...resumeData,
            skills: e.target.value.split(',').map(s => s.trim()).filter(s => s)
          })}
          className="input h-24 resize-none"
          placeholder="Enter skills separated by commas (e.g., Python, JavaScript, React, Node.js)"
        />
        <div className="flex flex-wrap gap-2 mt-3">
          {resumeData.skills?.map((skill: string, index: number) => (
            <motion.span
              key={index}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm font-medium"
            >
              {skill}
            </motion.span>
          ))}
        </div>
      </motion.div>

      {/* Projects */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="card mb-6"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <FileText className="w-6 h-6 text-green-600" />
            </div>
            <h2 className="text-xl font-bold">Projects</h2>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => addItem('projects')}
            className="btn btn-secondary text-sm"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Project
          </motion.button>
        </div>
        <div className="space-y-4">
          {resumeData.projects?.map((project: any, index: number) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-4 bg-gray-50 rounded-lg"
            >
              <div className="flex justify-between items-start mb-3">
                <h3 className="font-semibold text-gray-900">Project #{index + 1}</h3>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => removeItem('projects', index)}
                  className="text-red-500 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </motion.button>
              </div>
              <div className="grid grid-cols-1 gap-3">
                <input
                  type="text"
                  value={project.name || ''}
                  onChange={(e) => updateItem('projects', index, 'name', e.target.value)}
                  className="input"
                  placeholder="Project Name"
                />
                <textarea
                  value={project.description || ''}
                  onChange={(e) => updateItem('projects', index, 'description', e.target.value)}
                  className="input h-20 resize-none"
                  placeholder="Project Description"
                />
                <input
                  type="text"
                  value={project.technologies || ''}
                  onChange={(e) => updateItem('projects', index, 'technologies', e.target.value)}
                  className="input"
                  placeholder="Technologies Used (comma-separated)"
                />
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Certifications */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
        className="card mb-6"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <Award className="w-6 h-6 text-yellow-600" />
            </div>
            <h2 className="text-xl font-bold">Certifications</h2>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => addItem('certifications')}
            className="btn btn-secondary text-sm"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Certification
          </motion.button>
        </div>
        <div className="space-y-4">
          {resumeData.certifications?.map((cert: any, index: number) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-4 bg-gray-50 rounded-lg"
            >
              <div className="flex justify-between items-start mb-3">
                <h3 className="font-semibold text-gray-900">Certification #{index + 1}</h3>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => removeItem('certifications', index)}
                  className="text-red-500 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </motion.button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input
                  type="text"
                  value={cert.name || ''}
                  onChange={(e) => updateItem('certifications', index, 'name', e.target.value)}
                  className="input"
                  placeholder="Certification Name"
                />
                <input
                  type="text"
                  value={cert.issuer || ''}
                  onChange={(e) => updateItem('certifications', index, 'issuer', e.target.value)}
                  className="input"
                  placeholder="Issuing Organization"
                />
                <input
                  type="text"
                  value={cert.date || ''}
                  onChange={(e) => updateItem('certifications', index, 'date', e.target.value)}
                  className="input"
                  placeholder="Date (e.g., Jan 2023)"
                />
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Languages */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <FileText className="w-6 h-6 text-blue-600" />
            </div>
            <h2 className="text-xl font-bold">Languages</h2>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => addItem('languages')}
            className="btn btn-secondary text-sm"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Language
          </motion.button>
        </div>
        <div className="space-y-4">
          {resumeData.languages?.map((lang: any, index: number) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="p-4 bg-gray-50 rounded-lg"
            >
              <div className="flex justify-between items-start mb-3">
                <h3 className="font-semibold text-gray-900">Language #{index + 1}</h3>
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  onClick={() => removeItem('languages', index)}
                  className="text-red-500 hover:text-red-700"
                >
                  <Trash2 className="w-4 h-4" />
                </motion.button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <input
                  type="text"
                  value={lang.language || ''}
                  onChange={(e) => updateItem('languages', index, 'language', e.target.value)}
                  className="input"
                  placeholder="Language"
                />
                <select
                  value={lang.proficiency || 'Intermediate'}
                  onChange={(e) => updateItem('languages', index, 'proficiency', e.target.value)}
                  className="input"
                >
                  <option value="Basic">Basic</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Fluent">Fluent</option>
                  <option value="Native">Native</option>
                </select>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}

