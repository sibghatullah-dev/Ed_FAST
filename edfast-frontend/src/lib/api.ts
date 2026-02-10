/**
 * API Client for EdFast Backend
 * Handles all HTTP requests with authentication
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api/v1';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      timeout: 120000, // 120 second timeout (2 minutes) for long-running operations like AI chatbot
      withCredentials: true, // Important for dev tunnels
      validateStatus: (status) => status < 500, // Don't throw on 4xx errors
    });

    // Request interceptor to add token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        // Log detailed error info for debugging
        console.error('[API Error]', {
          message: error.message,
          code: error.code,
          status: error.response?.status,
          url: error.config?.url,
          baseURL: error.config?.baseURL,
        });
        
        if (error.response?.status === 401) {
          // Token expired, try to refresh
          const refreshed = await this.refreshToken();
          if (refreshed && error.config) {
            return this.client.request(error.config);
          } else {
            // Redirect to login
            this.logout();
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('access_token');
    }
    return null;
  }

  private getRefreshToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('refresh_token');
    }
    return null;
  }

  private setToken(access_token: string, refresh_token?: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', access_token);
      if (refresh_token) {
        localStorage.setItem('refresh_token', refresh_token);
      }
    }
  }

  private async refreshToken(): Promise<boolean> {
    try {
      const refreshToken = this.getRefreshToken();
      if (!refreshToken) return false;

      const response = await axios.post(`${API_URL}/auth/refresh`, {}, {
        headers: {
          Authorization: `Bearer ${refreshToken}`,
        },
      });

      if (response.data.success) {
        this.setToken(response.data.data.access_token);
        return true;
      }
      return false;
    } catch {
      return false;
    }
  }

  private logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  }

  // Auth APIs
  async register(data: { name: string; username: string; password: string; email?: string }) {
    const response = await this.client.post('/auth/register', data);
    if (response.data.success) {
      this.setToken(response.data.data.access_token, response.data.data.refresh_token);
    }
    return response.data;
  }

  async login(username: string, password: string) {
    const response = await this.client.post('/auth/login', { username, password });
    if (response.data.success) {
      this.setToken(response.data.data.access_token, response.data.data.refresh_token);
      if (typeof window !== 'undefined') {
        localStorage.setItem('user', JSON.stringify(response.data.data));
      }
    }
    return response.data;
  }

  async verifyToken() {
    const response = await this.client.get('/auth/verify');
    return response.data;
  }

  async logoutUser() {
    const response = await this.client.post('/auth/logout');
    this.logout();
    return response.data;
  }

  // User APIs
  async getCurrentUser() {
    const response = await this.client.get('/users/me');
    return response.data;
  }

  async updateProfile(data: { name?: string; description?: string }) {
    const response = await this.client.put('/users/me', data);
    return response.data;
  }

  async uploadTranscript(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/users/me/transcript', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async getResumeData() {
    const response = await this.client.get('/resume/');
    return response.data;
  }

  async updateResumeData(resume_data: any) {
    const response = await this.client.put('/resume/', { resume_data });
    return response.data;
  }

  // PeerHub APIs
  async getPosts(params?: { limit?: number; offset?: number; tag?: string; sort_by?: string; course_code?: string }) {
    const response = await this.client.get('/peerhub/posts', { params });
    return response.data;
  }

  async createPost(data: { title: string; content: string; tags?: string[]; course_code?: string; course_name?: string; semester?: number }) {
    const response = await this.client.post('/peerhub/posts', data);
    return response.data;
  }

  async getPost(postId: string) {
    const response = await this.client.get(`/peerhub/posts/${postId}`);
    return response.data;
  }

  async updatePost(postId: string, data: { title?: string; content?: string; tags?: string[] }) {
    const response = await this.client.put(`/peerhub/posts/${postId}`, data);
    return response.data;
  }

  async deletePost(postId: string) {
    const response = await this.client.delete(`/peerhub/posts/${postId}`);
    return response.data;
  }

  async getComments(postId: string) {
    const response = await this.client.get(`/peerhub/posts/${postId}/comments`);
    return response.data;
  }

  async createComment(postId: string, content: string, parent_id?: string) {
    const response = await this.client.post(`/peerhub/posts/${postId}/comments`, { content, parent_id });
    return response.data;
  }

  async votePost(postId: string, voteType: 'upvote' | 'downvote') {
    const response = await this.client.post(`/peerhub/posts/${postId}/vote`, { vote_type: voteType });
    return response.data;
  }

  async searchPosts(query: string, limit?: number) {
    const response = await this.client.get('/peerhub/search', { params: { query, limit } });
    return response.data;
  }

  async getTrendingPosts(limit?: number) {
    const response = await this.client.get('/peerhub/trending', { params: { limit } });
    return response.data;
  }

  async getPopularTags(limit?: number) {
    const response = await this.client.get('/peerhub/tags', { params: { limit } });
    return response.data;
  }

  // Course-specific PeerHub APIs
  async getPeerHubCourses() {
    const response = await this.client.get('/peerhub/courses');
    return response.data;
  }

  async getCoursePosts(courseCode: string) {
    const response = await this.client.get(`/peerhub/courses/${courseCode}`);
    return response.data;
  }

  async getCourseStats(courseCode: string) {
    const response = await this.client.get(`/peerhub/courses/${courseCode}/stats`);
    return response.data;
  }

  // Dashboard APIs
  async getDashboardStats() {
    const response = await this.client.get('/dashboard/stats');
    return response.data;
  }

  async getRecentActivity() {
    const response = await this.client.get('/dashboard/activity');
    return response.data;
  }

  // Courses APIs
  async getMyTranscriptCourses() {
    const response = await this.client.get('/courses/my-transcript');
    return response.data;
  }

  async getCourseStatistics() {
    const response = await this.client.get('/courses/statistics');
    return response.data;
  }

  // Chatbot APIs
  async sendChatQuery(message: string) {
    const response = await this.client.post('/chatbot/query', { message });
    return response.data;
  }

  async getChatHistory() {
    const response = await this.client.get('/chatbot/history');
    return response.data;
  }

  async clearChatHistory() {
    const response = await this.client.delete('/chatbot/history');
    return response.data;
  }

  // Timetable APIs
  async uploadTimetable(files: File[]) {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    const response = await this.client.post('/timetable/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  async getTimetables() {
    const response = await this.client.get('/timetable');
    return response.data;
  }

  async getTimetable(timetableId: string) {
    const response = await this.client.get(`/timetable/${timetableId}`);
    return response.data;
  }

  async filterTimetable(timetableId: string, courses: string[], departments: string[]) {
    const response = await this.client.post(`/timetable/${timetableId}/filter`, { courses, departments });
    return response.data;
  }

  async checkTimetableConflicts(timetableId: string, courses: string[]) {
    const response = await this.client.post(`/timetable/${timetableId}/conflicts`, { courses });
    return response.data;
  }

  async getTimetableStats(timetableId: string) {
    const response = await this.client.get(`/timetable/${timetableId}/stats`);
    return response.data;
  }

  // Resume APIs
  async autofillResume() {
    const response = await this.client.post('/resume/autofill');
    return response.data;
  }

  async getResumeSuggestions() {
    const response = await this.client.post('/resume/suggestions');
    return response.data;
  }

  async generateResumePDF(resume_data: any, style: string = 'professional') {
    const response = await this.client.post('/resume/generate', { style }, {
      responseType: 'blob',
    });
    return response.data;
  }

  // Courses APIs
  async getCourses(params?: { semester?: number; elective?: boolean; limit?: number }) {
    const response = await this.client.get('/courses/', { params });
    return response.data;
  }

  async getCourse(courseCode: string) {
    const response = await this.client.get(`/courses/${courseCode}`);
    return response.data;
  }

  async searchCourses(query: string, limit?: number) {
    const response = await this.client.get('/courses/search', { params: { q: query, limit } });
    return response.data;
  }

  async getElectives() {
    const response = await this.client.get('/courses/electives');
    return response.data;
  }

  // LinkedIn APIs
  async searchLinkedInJobs(params: {
    search_term: string;
    location: string;
    results_wanted: number;
    hours_old?: number;
    job_type?: string;
    is_remote: boolean;
    linkedin_fetch_description: boolean;
  }) {
    const response = await this.client.post('/linkedin/jobs/search', params);
    return response.data;
  }

  async scrapeLinkedInPosts(params: {
    profile_url: string;
    max_posts: number;
    include_comments: boolean;
    include_reactions: boolean;
  }) {
    const response = await this.client.post('/linkedin/posts/scrape', params);
    return response.data;
  }
}

export const api = new APIClient();
export default api;


