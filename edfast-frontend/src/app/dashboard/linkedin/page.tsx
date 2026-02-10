'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Info, Briefcase, Scissors, BarChart3 } from 'lucide-react';
import LinkedInJobSearch from '@/components/LinkedInJobSearch';
import LinkedInPostScraper from '@/components/LinkedInPostScraper';

export default function LinkedInPage() {
  const [activeTab, setActiveTab] = useState('jobs');
  const [showApiEndpoints, setShowApiEndpoints] = useState(false);

  return (
    <div className="page-container">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-2">LinkedIn Integration</h1>
        <p className="text-gray-600">
          Search for jobs and scrape posts from LinkedIn to enhance your career opportunities
        </p>
      </motion.div>

      {/* Info Alert */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card mb-6"
      >
        <div className="flex items-start gap-3">
          <Info className="h-5 w-5 text-blue-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-gray-900 mb-1">LinkedIn Integration Features</h3>
            <p className="text-gray-600">
              This module provides job search capabilities and post scraping functionality. 
              Job search uses the JobSpy library, while post scraping uses Selenium WebDriver for browser automation.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Feature Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Briefcase className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Job Search</h3>
          </div>
          <p className="text-gray-600 mb-4">
            Search for jobs on LinkedIn with advanced filtering options including location, 
            job type, salary range, and remote work preferences.
          </p>
          <div className="flex flex-wrap gap-2">
            <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">JobSpy</span>
            <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">Real-time</span>
            <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">Filtered</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-green-100 rounded-lg">
              <Scissors className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Post Scraping</h3>
          </div>
          <p className="text-gray-600 mb-4">
            Scrape posts from LinkedIn profiles or company pages to analyze engagement, 
            content trends, and social media presence.
          </p>
          <div className="flex flex-wrap gap-2">
            <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">Selenium</span>
            <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">Browser</span>
            <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">Analytics</span>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="card"
        >
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-purple-100 rounded-lg">
              <BarChart3 className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Analytics</h3>
          </div>
          <p className="text-gray-600 mb-4">
            View statistics and analytics from your job searches and post scraping sessions 
            to track trends and opportunities.
          </p>
          <div className="flex flex-wrap gap-2">
            <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">Statistics</span>
            <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">Trends</span>
            <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">Insights</span>
          </div>
        </motion.div>
      </div>

      {/* Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="card"
      >
        <div className="mb-6">
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('jobs')}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md font-medium transition-all ${
                activeTab === 'jobs'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Briefcase className="h-4 w-4" />
              Job Search
            </button>
            <button
              onClick={() => setActiveTab('posts')}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md font-medium transition-all ${
                activeTab === 'posts'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Scissors className="h-4 w-4" />
              Post Scraping
            </button>
          </div>
        </div>

        <div className="min-h-[400px]">
          {activeTab === 'jobs' && <LinkedInJobSearch />}
          {activeTab === 'posts' && <LinkedInPostScraper />}
        </div>
      </motion.div>

      {/* API Endpoints - Collapsible */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-bold text-gray-900">API Endpoints</h3>
            <p className="text-gray-600 text-sm mt-1">
              Available LinkedIn API endpoints for integration
            </p>
          </div>
          <button
            onClick={() => setShowApiEndpoints(!showApiEndpoints)}
            className="btn btn-outline text-sm"
          >
            {showApiEndpoints ? 'Hide API Endpoints' : 'Show API Endpoints'}
          </button>
        </div>
        
        {showApiEndpoints && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6"
          >
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Job Search</h4>
              <div className="space-y-2">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <code className="text-sm text-gray-700">POST /api/v1/linkedin/jobs/search</code>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <code className="text-sm text-gray-700">GET /api/v1/linkedin/jobs/statistics</code>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <code className="text-sm text-gray-700">GET /api/v1/linkedin/jobs/sample</code>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold text-gray-900 mb-3">Post Scraping</h4>
              <div className="space-y-2">
                <div className="bg-gray-50 p-3 rounded-lg">
                  <code className="text-sm text-gray-700">POST /api/v1/linkedin/posts/scrape</code>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <code className="text-sm text-gray-700">GET /api/v1/linkedin/posts/sample</code>
                </div>
                <div className="bg-gray-50 p-3 rounded-lg">
                  <code className="text-sm text-gray-700">GET /api/v1/linkedin/health</code>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
