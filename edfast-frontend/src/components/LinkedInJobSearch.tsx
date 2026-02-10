'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2, Search, MapPin, Building, Clock, DollarSign, ExternalLink } from 'lucide-react';
import { api } from '@/lib/api';

interface Job {
  title: string;
  company: string;
  location: string;
  description: string;
  url: string;
  posted_date: string;
  salary_min: number;
  salary_max: number;
  salary_currency: string;
  job_type: string;
  company_industry: string;
  company_num_employees: string;
  company_revenue: string;
  emails: string[];
  scraped_at: string;
}

interface JobSearchForm {
  search_term: string;
  location: string;
  results_wanted: number;
  hours_old?: number;
  job_type?: string;
  is_remote: boolean;
  linkedin_fetch_description: boolean;
}

interface JobStatistics {
  total_jobs: number;
  unique_companies: number;
  unique_locations: number;
  remote_jobs: number;
  fulltime_jobs: number;
  avg_min_salary: number;
  avg_max_salary: number;
}

export default function LinkedInJobSearch() {
  const [formData, setFormData] = useState<JobSearchForm>({
    search_term: 'software engineer',
    location: 'San Francisco, CA',
    results_wanted: 20,
    is_remote: false,
    linkedin_fetch_description: true
  });
  
  const [jobs, setJobs] = useState<Job[]>([]);
  const [statistics, setStatistics] = useState<JobStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  const handleInputChange = (field: keyof JobSearchForm, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSearch = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Get auth token
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Please login to search for jobs');
        return;
      }

      // Make API call using the API client
      const data = await api.searchLinkedInJobs(formData);
      
      if (data.success && data.data.jobs) {
        // Map API response to Job interface
        const mappedJobs: Job[] = data.data.jobs.map((job: any) => ({
          title: job.title || '',
          company: job.company || '',
          location: job.location || '',
          description: job.description || '',
          url: job.url || '',
          posted_date: job.posted_date || '',
          salary_min: job.min_salary || 0,
          salary_max: job.max_salary || 0,
          salary_currency: job.currency || 'USD',
          job_type: job.job_type || '',
          company_industry: job.company_industry || '',
          company_num_employees: job.company_num_employees || '',
          company_revenue: job.company_revenue || '',
          emails: job.emails || [],
          scraped_at: job.scraped_at || ''
        }));
        
        setJobs(mappedJobs);
        setStatistics(data.data.statistics || null);
        setSessionId(data.session_id || null);
      } else {
        setError(data.message || 'No jobs found. Try different search criteria.');
        setJobs([]);
        setStatistics(null);
      }
    } catch (err: any) {
      console.error('Job search error:', err);
      let errorMessage = 'Failed to search for jobs. ';
      
      if (err.message?.includes('503')) {
        errorMessage = 'LinkedIn scraping service is unavailable. The JobSpy library may not be installed on the server. Please contact the administrator.';
      } else if (err.message?.includes('401')) {
        errorMessage = 'Authentication failed. Please log in again.';
      } else if (err.message?.includes('Network') || err.message?.includes('fetch') || err.message?.includes('ERR')) {
        errorMessage = 'Cannot connect to the server. Please make sure the backend server is running.';
      } else {
        errorMessage += err.message || 'An unexpected error occurred.';
      }
      
      setError(errorMessage);
      setJobs([]);
      setStatistics(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Search Form */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Search Parameters</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Search Term
            </label>
            <input
              type="text"
              value={formData.search_term}
              onChange={(e) => handleInputChange('search_term', e.target.value)}
              className="input"
              placeholder="e.g., software engineer"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Location
            </label>
            <input
              type="text"
              value={formData.location}
              onChange={(e) => handleInputChange('location', e.target.value)}
              className="input"
              placeholder="e.g., San Francisco, CA"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Results Wanted
            </label>
            <input
              type="number"
              value={formData.results_wanted}
              onChange={(e) => handleInputChange('results_wanted', parseInt(e.target.value))}
              className="input"
              min="1"
              max="100"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Job Type
            </label>
            <select
              value={formData.job_type || ''}
              onChange={(e) => handleInputChange('job_type', e.target.value)}
              className="input"
            >
              <option value="">All Types</option>
              <option value="full-time">Full-time</option>
              <option value="part-time">Part-time</option>
              <option value="contract">Contract</option>
              <option value="internship">Internship</option>
            </select>
          </div>
        </div>
        
        <div className="flex items-center gap-4 mb-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.is_remote}
              onChange={(e) => handleInputChange('is_remote', e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="text-sm text-gray-700">Remote Only</span>
          </label>
          
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.linkedin_fetch_description}
              onChange={(e) => handleInputChange('linkedin_fetch_description', e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="text-sm text-gray-700">Fetch Full Descriptions</span>
          </label>
        </div>
        
        <button
          onClick={handleSearch}
          disabled={loading}
          className="btn btn-primary flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Searching...
            </>
          ) : (
            <>
              <Search className="h-4 w-4" />
              Search Jobs
            </>
          )}
        </button>
      </div>

      {/* Error Message */}
      {error && (
        <div className="card border-red-200 bg-red-50">
          <div className="flex items-center gap-2 text-red-700">
            <div className="w-2 h-2 bg-red-500 rounded-full"></div>
            <span className="font-medium">Error</span>
          </div>
          <p className="text-red-600 mt-1">{error}</p>
        </div>
      )}

      {/* Statistics */}
      {statistics && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Search Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">{statistics.total_jobs}</p>
              <p className="text-sm text-gray-600">Total Jobs</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">{statistics.unique_companies}</p>
              <p className="text-sm text-gray-600">Companies</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">{statistics.remote_jobs}</p>
              <p className="text-sm text-gray-600">Remote Jobs</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">
                ${statistics.avg_min_salary.toLocaleString()}
              </p>
              <p className="text-sm text-gray-600">Avg Min Salary</p>
            </div>
          </div>
        </div>
      )}

      {/* Job Results */}
      {jobs.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Results</h3>
          <div className="space-y-4">
            {jobs.map((job, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-gray-900 mb-1">{job.title}</h4>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <div className="flex items-center gap-1">
                        <Building className="h-4 w-4" />
                        {job.company}
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="h-4 w-4" />
                        {job.location}
                      </div>
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        {job.posted_date}
                      </div>
                    </div>
                  </div>
                  <a
                    href={job.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-outline flex items-center gap-2"
                  >
                    <ExternalLink className="h-4 w-4" />
                    View Job
                  </a>
                </div>
                
                <p className="text-gray-700 mb-3 line-clamp-3">{job.description}</p>
                
                <div className="flex items-center gap-4 text-sm">
                  {job.salary_min && job.salary_max && (
                    <div className="flex items-center gap-1 text-green-600">
                      <DollarSign className="h-4 w-4" />
                      ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}
                    </div>
                  )}
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium">
                    {job.job_type}
                  </span>
                  <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">
                    {job.company_industry}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}