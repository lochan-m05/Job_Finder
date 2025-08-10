import axios from 'axios';

// Default to nginx proxy path in container/runtime. Allow override via env at build-time.
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api';

// Create axios instance
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Job-related API calls
export const apiService = {
  // Health check
  async healthCheck() {
    const response = await apiClient.get('/health');
    return response.data;
  },

  // Get dashboard data
  async getDashboardData(timeRange: string = '7d') {
    const response = await apiClient.get(`/analytics/dashboard?time_range=${timeRange}`);
    return response.data;
  },

  // Search jobs
  async searchJobs(params: {
    q?: string;
    hashtags?: string[];
    sources?: string[];
    timeFilter?: string;
    location?: string;
    jobType?: string;
    experienceLevel?: string;
    salaryMin?: number;
    salaryMax?: number;
    skills?: string[];
    sortBy?: string;
    page?: number;
    limit?: number;
  }) {
    const queryParams = new URLSearchParams();
    
    if (params.hashtags?.length) {
      queryParams.append('hashtags', params.hashtags.join(','));
    }
    if (params.q) {
      queryParams.append('q', params.q);
    }
    if (params.limit) {
      queryParams.append('limit', params.limit.toString());
    }
    if (params.page) {
      queryParams.append('offset', ((params.page - 1) * (params.limit || 20)).toString());
    }
    
    const response = await apiClient.get(`/jobs?${queryParams.toString()}`);
    return response.data;
  },

  // Start scraping
  async startScraping(params: {
    hashtags: string[];
    sources: string[];
    timeFilter: string;
  }) {
    const response = await apiClient.post('/scrape-jobs', params);
    return response.data;
  },

  // Get recent jobs
  async getRecentJobs(limit: number = 10) {
    const response = await apiClient.get(`/jobs?limit=${limit}`);
    return response.data.jobs;
  },

  // Get saved jobs (mock)
  async getSavedJobs() {
    // This would typically fetch from user's saved jobs
    return [];
  },

  // Get job by ID
  async getJobById(jobId: string) {
    // Mock implementation
    return {
      id: jobId,
      title: 'Software Developer',
      company: 'Tech Company',
      description: 'Job description here...',
      skills: ['JavaScript', 'React', 'Node.js'],
      location: 'Mumbai, India',
      salary: { min: 500000, max: 800000, currency: 'INR' },
      postedAt: new Date().toISOString(),
    };
  },

  // Authentication (placeholder)
  async login(email: string, password: string) {
    // Mock login
    return {
      access_token: 'mock-token',
      token_type: 'bearer',
      user: { email, name: 'Demo User' }
    };
  },

  async register(userData: any) {
    // Mock registration
    return {
      message: 'User registered successfully',
      user: userData
    };
  },

  // Contact related
  async getContacts() {
    return [];
  },

  // Analytics
  async getAnalytics() {
    return await this.getDashboardData();
  }
};

export default apiService;
