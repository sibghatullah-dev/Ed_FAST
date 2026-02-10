'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Loader2, Scissors, Heart, MessageCircle, Repeat, ExternalLink, Calendar, User } from 'lucide-react';
import { api } from '@/lib/api';

interface Post {
  post_url: string;
  content: string;
  type: string;
  like_count: string;
  comment_count: string;
  repost_count: string;
  img_url: string;
  video_url: string;
  author_name: string;
  author_url: string;
  author_img: string;
  author_followers: string;
  author_headline: string;
  posted_date: string;
  scraped_at: string;
}

interface PostScrapingForm {
  profile_url: string;
  max_posts: number;
  include_comments: boolean;
  include_reactions: boolean;
}

interface PostStatistics {
  total_posts: number;
  total_likes: number;
  total_comments: number;
  total_reposts: number;
  avg_engagement: number;
  top_post_type: string;
}

export default function LinkedInPostScraper() {
  const [formData, setFormData] = useState<PostScrapingForm>({
    profile_url: '',
    max_posts: 10,
    include_comments: false,
    include_reactions: true
  });
  
  const [posts, setPosts] = useState<Post[]>([]);
  const [statistics, setStatistics] = useState<PostStatistics | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (field: keyof PostScrapingForm, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleScrape = async () => {
    if (!formData.profile_url.trim()) {
      setError('Please enter a LinkedIn profile URL');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    try {
      // Get auth token
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Please login to scrape posts');
        return;
      }

      // Make API call using the API client
      const data = await api.scrapeLinkedInPosts(formData);
      
      if (data.success && data.data.posts) {
        // Map API response to Post interface
        const mappedPosts: Post[] = data.data.posts.map((post: any) => ({
          post_url: post.post_url || '',
          content: post.content || '',
          type: post.type || 'text',
          like_count: post.like_count || '0',
          comment_count: post.comment_count || '0',
          repost_count: post.repost_count || '0',
          img_url: post.img_url || '',
          video_url: post.video_url || '',
          author_name: post.author_name || post.profile_name || '',
          author_url: post.author_url || post.profile_url || '',
          author_img: post.author_img || '',
          author_followers: post.author_followers || '',
          author_headline: post.author_headline || '',
          posted_date: post.posted_date || '',
          scraped_at: post.scraped_at || ''
        }));
        
        setPosts(mappedPosts);
        
        // Transform statistics if provided
        if (data.data.statistics) {
          const stats = data.data.statistics;
          setStatistics({
            total_posts: stats.total_posts || mappedPosts.length,
            total_likes: stats.total_likes || 0,
            total_comments: stats.total_comments || 0,
            total_reposts: stats.total_reposts || 0,
            avg_engagement: stats.avg_engagement || 0,
            top_post_type: stats.top_post_type || 'text'
          });
        }
      } else {
        setError(data.message || 'No posts found. Try a different profile URL.');
        setPosts([]);
        setStatistics(null);
      }
    } catch (err: any) {
      console.error('Post scraping error:', err);
      let errorMessage = 'Failed to scrape posts. ';
      
      if (err.message?.includes('503')) {
        errorMessage = 'LinkedIn scraping service is unavailable. Please contact the administrator.';
      } else if (err.message?.includes('401')) {
        errorMessage = 'Authentication failed. Please log in again.';
      } else if (err.message?.includes('Network') || err.message?.includes('fetch') || err.message?.includes('ERR')) {
        errorMessage = 'Cannot connect to the server. Please make sure the backend server is running.';
      } else {
        errorMessage += err.message || 'An unexpected error occurred.';
      }
      
      setError(errorMessage);
      setPosts([]);
      setStatistics(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Scraping Form */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Post Scraping Parameters</h3>
        
        <div className="space-y-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              LinkedIn Profile URL
            </label>
            <input
              type="url"
              value={formData.profile_url}
              onChange={(e) => handleInputChange('profile_url', e.target.value)}
              className="input"
              placeholder="https://linkedin.com/in/username"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Maximum Posts to Scrape
            </label>
            <input
              type="number"
              value={formData.max_posts}
              onChange={(e) => handleInputChange('max_posts', parseInt(e.target.value))}
              className="input"
              min="1"
              max="100"
            />
          </div>
        </div>
        
        <div className="flex items-center gap-4 mb-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.include_comments}
              onChange={(e) => handleInputChange('include_comments', e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="text-sm text-gray-700">Include Comments</span>
          </label>
          
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.include_reactions}
              onChange={(e) => handleInputChange('include_reactions', e.target.checked)}
              className="rounded border-gray-300"
            />
            <span className="text-sm text-gray-700">Include Reactions</span>
          </label>
        </div>
        
        <button
          onClick={handleScrape}
          disabled={loading}
          className="btn btn-primary flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Scraping Posts...
            </>
          ) : (
            <>
              <Scissors className="h-4 w-4" />
              Scrape Posts
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
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Scraping Statistics</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">{statistics.total_posts}</p>
              <p className="text-sm text-gray-600">Total Posts</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">{statistics.total_likes}</p>
              <p className="text-sm text-gray-600">Total Likes</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">{statistics.total_comments}</p>
              <p className="text-sm text-gray-600">Total Comments</p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-2xl font-bold text-gray-900">{statistics.avg_engagement}</p>
              <p className="text-sm text-gray-600">Avg Engagement</p>
            </div>
          </div>
        </div>
      )}

      {/* Post Results */}
      {posts.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Scraped Posts</h3>
          <div className="space-y-4">
            {posts.map((post, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start gap-3 mb-3">
                  <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                    <User className="h-5 w-5 text-gray-500" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-semibold text-gray-900">{post.author_name}</h4>
                      <span className="text-sm text-gray-500">•</span>
                      <span className="text-sm text-gray-500">{post.author_followers} followers</span>
                    </div>
                    <p className="text-sm text-gray-600">{post.author_headline}</p>
                  </div>
                  <a
                    href={post.post_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-outline flex items-center gap-2"
                  >
                    <ExternalLink className="h-4 w-4" />
                    View Post
                  </a>
                </div>
                
                <p className="text-gray-700 mb-3">{post.content}</p>
                
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-4 w-4" />
                    {post.posted_date}
                  </div>
                  <div className="flex items-center gap-1">
                    <Heart className="h-4 w-4" />
                    {post.like_count}
                  </div>
                  <div className="flex items-center gap-1">
                    <MessageCircle className="h-4 w-4" />
                    {post.comment_count}
                  </div>
                  <div className="flex items-center gap-1">
                    <Repeat className="h-4 w-4" />
                    {post.repost_count}
                  </div>
                  <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-xs font-medium">
                    {post.type}
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