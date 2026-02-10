'use client';

import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { api } from '@/lib/api';
import { 
  Upload, 
  Filter, 
  Calendar, 
  BarChart3, 
  Download, 
  Clock, 
  MapPin, 
  Users,
  BookOpen,
  Building,
  CheckCircle,
  AlertTriangle,
  FileSpreadsheet
} from 'lucide-react';

interface TimetableEntry {
  id: string;
  course: string;
  section: string;
  day: string;
  time: string;
  type: 'Theory' | 'Lab';
  room: string;
  instructor?: string;
  course_code?: string;
  course_name?: string;
  semester?: number;
}

interface ConflictInfo {
  day: string;
  course1: string;
  section1: string;
  time1: string;
  room1: string;
  course2: string;
  section2: string;
  time2: string;
  room2: string;
  type: string;
}

interface ScheduleRecommendation {
  conflict_type: string;
  conflicted_courses: string[];
  day: string;
  suggestions: Array<{
    course: string;
    alternative_section: string;
    alternative_time: string;
    alternative_room: string;
  }>;
}

interface TimetableStats {
  totalClasses: number;
  uniqueCourses: number;
  theoryClasses: number;
  labClasses: number;
  uniqueRooms: number;
  daysCovered: number;
}

export default function TimetableManager() {
  const [activeTab, setActiveTab] = useState('upload');
  const [timetableData, setTimetableData] = useState<TimetableEntry[]>([]);
  const [filteredData, setFilteredData] = useState<TimetableEntry[]>([]);
  const [stats, setStats] = useState<TimetableStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentTimetableId, setCurrentTimetableId] = useState<string | null>(null);
  const [conflicts, setConflicts] = useState<ConflictInfo[]>([]);
  const [recommendations, setRecommendations] = useState<ScheduleRecommendation[]>([]);
  const [selectedCourses, setSelectedCourses] = useState<string[]>([]);
  const [availableCourses, setAvailableCourses] = useState<string[]>([]);
  const [showConflictModal, setShowConflictModal] = useState(false);

  const [filters, setFilters] = useState({
    course: '',
    day: '',
    type: '',
    room: '',
    department: ''
  });

  const handleFileUpload = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    setLoading(true);
    setError(null);

    try {
      // Convert FileList to Array
      const fileArray = Array.from(files);
      
      // Upload files using the API
      const response = await api.uploadTimetable(fileArray);
      console.log('Upload response:', response);
      
      if (response.success) {
        const timetableId = response.data.timetable_id;
        setCurrentTimetableId(timetableId);
        
        // Load the uploaded timetable data
        await loadTimetableData(timetableId);
        
        setActiveTab('view');
      } else {
        setError(response.error || 'Failed to upload timetable');
      }
    } catch (err: any) {
      console.error('Upload error:', err);
      setError(err.message || 'Failed to process timetable file. Please try again.');
      
      // Fallback: Try to process the file locally for immediate display
      try {
        await processFileLocally(files[0]);
      } catch (fallbackErr) {
        console.error('Fallback processing failed:', fallbackErr);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const processFileLocally = async (file: File) => {
    // This is a fallback for when the API fails
    // We'll create some mock data based on the file name
    console.log('Processing file locally as fallback:', file.name);
    
    const mockData: TimetableEntry[] = [
      {
        id: '1',
        course: 'CS2001',
        section: 'A',
        day: 'Monday',
        time: '09:00-10:30',
        type: 'Theory',
        room: 'CS-101',
        course_code: 'CS2001',
        course_name: 'Data Structures',
        semester: 2
      },
      {
        id: '2',
        course: 'CS2001',
        section: 'A',
        day: 'Wednesday',
        time: '09:00-10:30',
        type: 'Theory',
        room: 'CS-101',
        course_code: 'CS2001',
        course_name: 'Data Structures',
        semester: 2
      },
      {
        id: '3',
        course: 'CS2001',
        section: 'A',
        day: 'Friday',
        time: '14:00-15:30',
        type: 'Lab',
        room: 'CS-Lab-1',
        course_code: 'CS2001',
        course_name: 'Data Structures Lab',
        semester: 2
      }
    ];

    setTimetableData(mockData);
    setFilteredData(mockData);
    
    // Extract unique courses for selection
    const uniqueCourses = [...new Set(mockData.map(item => item.course))].filter(Boolean);
    setAvailableCourses(uniqueCourses);
    
    // Calculate stats
    const newStats: TimetableStats = {
      totalClasses: mockData.length,
      uniqueCourses: uniqueCourses.length,
      theoryClasses: mockData.filter(item => item.type === 'Theory').length,
      labClasses: mockData.filter(item => item.type === 'Lab').length,
      uniqueRooms: new Set(mockData.map(item => item.room)).size,
      daysCovered: new Set(mockData.map(item => item.day)).size
    };
    setStats(newStats);
    
    setActiveTab('view');
    setError('API unavailable - showing sample data. Please try uploading again later.');
  };

  const loadTimetableData = useCallback(async (timetableId: string) => {
    try {
      console.log('Loading timetable data for ID:', timetableId);
      const response = await api.getTimetable(timetableId);
      console.log('API Response:', response);
      
      if (response.success) {
        // Convert the API response to our format
        const allEntries: TimetableEntry[] = [];
        
        // Handle different response structures
        let dataToProcess = response.data.data || response.data || {};
        
        // If data is an array directly, process it
        if (Array.isArray(dataToProcess)) {
          dataToProcess.forEach((entry: any, index: number) => {
            allEntries.push({
              id: `entry_${index}`,
              course: entry.Course || entry.course || entry.course_name || '',
              section: entry.Section || entry.section || '',
              day: entry.Day || entry.day || '',
              time: entry.Time || entry.time || '',
              type: (entry.Type || entry.type || 'Theory') as 'Theory' | 'Lab',
              room: entry.Class || entry.room || entry.location || '',
              course_code: entry.course_code || entry.Course || entry.course,
              course_name: entry.course_name || entry.Course || entry.course,
              semester: entry.semester
            });
          });
        } else {
          // Process each file's data
          Object.entries(dataToProcess).forEach(([filename, fileData]: [string, any]) => {
            if (Array.isArray(fileData)) {
              fileData.forEach((entry: any, index: number) => {
                allEntries.push({
                  id: `${filename}_${index}`,
                  course: entry.Course || entry.course || entry.course_name || '',
                  section: entry.Section || entry.section || '',
                  day: entry.Day || entry.day || '',
                  time: entry.Time || entry.time || '',
                  type: (entry.Type || entry.type || 'Theory') as 'Theory' | 'Lab',
                  room: entry.Class || entry.room || entry.location || '',
                  course_code: entry.course_code || entry.Course || entry.course,
                  course_name: entry.course_name || entry.Course || entry.course,
                  semester: entry.semester
                });
              });
            }
          });
        }

        console.log('Processed entries:', allEntries);
        setTimetableData(allEntries);
        setFilteredData(allEntries);
        
        // Extract unique courses for selection
        const uniqueCourses = [...new Set(allEntries.map(item => item.course))].filter(Boolean);
        setAvailableCourses(uniqueCourses);
        
        // Calculate stats
        const newStats: TimetableStats = {
          totalClasses: allEntries.length,
          uniqueCourses: uniqueCourses.length,
          theoryClasses: allEntries.filter(item => item.type === 'Theory').length,
          labClasses: allEntries.filter(item => item.type === 'Lab').length,
          uniqueRooms: new Set(allEntries.map(item => item.room)).size,
          daysCovered: new Set(allEntries.map(item => item.day)).size
        };
        setStats(newStats);
        
        console.log('Stats calculated:', newStats);
      } else {
        console.error('API response not successful:', response);
        setError(response.error || 'Failed to load timetable data');
      }
    } catch (err: any) {
      console.error('Error loading timetable data:', err);
      setError(err.message || 'Failed to load timetable data');
    }
  }, []);

  const applyFilters = useCallback(() => {
    let filtered = [...timetableData];

    if (filters.course) {
      filtered = filtered.filter(item => 
        item.course.toLowerCase().includes(filters.course.toLowerCase())
      );
    }

    if (filters.day) {
      filtered = filtered.filter(item => item.day === filters.day);
    }

    if (filters.type) {
      filtered = filtered.filter(item => item.type === filters.type);
    }

    if (filters.room) {
      filtered = filtered.filter(item => 
        item.room.toLowerCase().includes(filters.room.toLowerCase())
      );
    }

    setFilteredData(filtered);
  }, [timetableData, filters]);

  React.useEffect(() => {
    applyFilters();
  }, [applyFilters]);

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const clearFilters = () => {
    setFilters({
      course: '',
      day: '',
      type: '',
      room: '',
      department: ''
    });
  };

  const clearAllData = async () => {
    try {
      // Clear backend data
      const response = await fetch('https://x7mq0j1w-5000.asse.devtunnels.ms/api/v1/timetable/clear', {
        method: 'POST'
      });
      
      if (response.ok) {
        console.log('Backend data cleared');
      }
    } catch (err) {
      console.error('Error clearing backend data:', err);
    }
    
    // Clear frontend data
    setCurrentTimetableId(null);
    setTimetableData([]);
    setFilteredData([]);
    setAvailableCourses([]);
    setSelectedCourses([]);
    setStats(null);
    setConflicts([]);
    setRecommendations([]);
    setError(null);
    setActiveTab('upload');
  };

  const checkConflicts = useCallback(async () => {
    if (!currentTimetableId || selectedCourses.length === 0) {
      setError('Please select courses to check for conflicts');
      return;
    }

    try {
      setLoading(true);
      const response = await api.checkTimetableConflicts(currentTimetableId, selectedCourses);
      
      if (response.success) {
        setConflicts(response.data.conflicts || []);
        setRecommendations(response.data.recommendations || []);
        setShowConflictModal(true);
      } else {
        setError(response.error || 'Failed to check conflicts');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to check conflicts');
    } finally {
      setLoading(false);
    }
  }, [currentTimetableId, selectedCourses]);

  const handleCourseSelection = (course: string, checked: boolean) => {
    if (checked) {
      setSelectedCourses(prev => [...prev, course]);
    } else {
      setSelectedCourses(prev => prev.filter(c => c !== course));
    }
  };

  const buildPersonalSchedule = useCallback(async () => {
    if (!currentTimetableId || selectedCourses.length === 0) {
      setError('Please select courses to build schedule');
      return;
    }

    try {
      setLoading(true);
      // Filter timetable for selected courses
      const filteredResponse = await api.filterTimetable(currentTimetableId, selectedCourses, []);
      
      if (filteredResponse.success) {
        // Convert filtered data to our format
        const allEntries: TimetableEntry[] = [];
        Object.entries(filteredResponse.data.filtered_data).forEach(([filename, fileData]: [string, any]) => {
          fileData.forEach((entry: any, index: number) => {
            allEntries.push({
              id: `${filename}_${index}`,
              course: entry.Course || entry.course || '',
              section: entry.Section || entry.section || '',
              day: entry.Day || entry.day || '',
              time: entry.Time || entry.time || '',
              type: (entry.Type || entry.type || 'Theory') as 'Theory' | 'Lab',
              room: entry.Class || entry.room || '',
              course_code: entry.course_code,
              course_name: entry.course_name,
              semester: entry.semester
            });
          });
        });

        setFilteredData(allEntries);
        setActiveTab('view');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to build personal schedule');
    } finally {
      setLoading(false);
    }
  }, [currentTimetableId, selectedCourses]);

  const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
  const types = ['Theory', 'Lab'];

  // Load existing timetables on component mount
  React.useEffect(() => {
    loadExistingTimetables();
  }, []);

  const loadExistingTimetables = useCallback(async () => {
    try {
      const response = await api.getTimetables();
      console.log('Existing timetables:', response);
      
      if (response.success && response.data.timetables && response.data.timetables.length > 0) {
        // Load the most recent timetable
        const mostRecentTimetable = response.data.timetables[0];
        setCurrentTimetableId(mostRecentTimetable.id);
        await loadTimetableData(mostRecentTimetable.id);
        setActiveTab('view');
      } else {
        // No timetables found, clear any stale ID and show upload prompt
        console.log('No timetables found, clearing stale data');
        setCurrentTimetableId(null);
        setTimetableData([]);
        setFilteredData([]);
        setAvailableCourses([]);
        setStats(null);
        setActiveTab('upload');
      }
    } catch (err: any) {
      console.error('Error loading existing timetables:', err);
      
      // Check if it's an authentication error
      if (err.response?.status === 401) {
        console.log('Authentication required - trying test data');
        // Try to load test data instead
        try {
          await loadTestTimetable();
        } catch (testErr) {
          console.error('Test data also failed:', testErr);
          setError('Please log in to access your timetables');
        }
      } else {
        // Other errors - clear stale data
        setCurrentTimetableId(null);
        setTimetableData([]);
        setFilteredData([]);
        setAvailableCourses([]);
        setStats(null);
      }
    }
  }, [loadTimetableData]);

  const loadTestTimetable = useCallback(async () => {
    try {
      console.log('Loading test timetable data...');
      const response = await fetch('https://x7mq0j1w-5000.asse.devtunnels.ms/api/v1/timetable/test');
      const data = await response.json();
      console.log('Test timetables response:', data);
      
      if (data.success && data.data.timetables && data.data.timetables.length > 0) {
        const testTimetable = data.data.timetables[0];
        setCurrentTimetableId(testTimetable.id);
        await loadTestTimetableData(testTimetable.id);
        setActiveTab('view');
        setError('Using test data - please log in for your actual timetables');
      }
    } catch (err: any) {
      console.error('Error loading test timetable:', err);
      throw err;
    }
  }, []);

  const loadTestTimetableData = useCallback(async (timetableId: string) => {
    try {
      console.log('Loading test timetable data for ID:', timetableId);
      const response = await fetch(`https://x7mq0j1w-5000.asse.devtunnels.ms/api/v1/timetable/test/${timetableId}`);
      const data = await response.json();
      console.log('Test timetable data response:', data);
      
      if (data.success) {
        // Convert the API response to our format
        const allEntries: TimetableEntry[] = [];
        
        // Handle different response structures
        let dataToProcess = data.data.data || data.data || {};
        
        // If data is an array directly, process it
        if (Array.isArray(dataToProcess)) {
          dataToProcess.forEach((entry: any, index: number) => {
            allEntries.push({
              id: `entry_${index}`,
              course: entry.Course || entry.course || entry.course_name || '',
              section: entry.Section || entry.section || '',
              day: entry.Day || entry.day || '',
              time: entry.Time || entry.time || '',
              type: (entry.Type || entry.type || 'Theory') as 'Theory' | 'Lab',
              room: entry.Class || entry.room || entry.location || '',
              course_code: entry.course_code || entry.Course || entry.course,
              course_name: entry.course_name || entry.Course || entry.course,
              semester: entry.semester
            });
          });
        } else {
          // Process each file's data
          Object.entries(dataToProcess).forEach(([filename, fileData]: [string, any]) => {
            if (Array.isArray(fileData)) {
              fileData.forEach((entry: any, index: number) => {
                allEntries.push({
                  id: `${filename}_${index}`,
                  course: entry.Course || entry.course || entry.course_name || '',
                  section: entry.Section || entry.section || '',
                  day: entry.Day || entry.day || '',
                  time: entry.Time || entry.time || '',
                  type: (entry.Type || entry.type || 'Theory') as 'Theory' | 'Lab',
                  room: entry.Class || entry.room || entry.location || '',
                  course_code: entry.course_code || entry.Course || entry.course,
                  course_name: entry.course_name || entry.Course || entry.course,
                  semester: entry.semester
                });
              });
            }
          });
        }

        console.log('Processed test entries:', allEntries);
        setTimetableData(allEntries);
        setFilteredData(allEntries);
        
        // Extract unique courses for selection
        const uniqueCourses = [...new Set(allEntries.map(item => item.course))].filter(Boolean);
        setAvailableCourses(uniqueCourses);
        
        // Calculate stats
        const newStats: TimetableStats = {
          totalClasses: allEntries.length,
          uniqueCourses: uniqueCourses.length,
          theoryClasses: allEntries.filter(item => item.type === 'Theory').length,
          labClasses: allEntries.filter(item => item.type === 'Lab').length,
          uniqueRooms: new Set(allEntries.map(item => item.room)).size,
          daysCovered: new Set(allEntries.map(item => item.day)).size
        };
        setStats(newStats);
        
        console.log('Test stats calculated:', newStats);
      } else {
        console.error('Test API response not successful:', data);
        setError(data.error || 'Failed to load test timetable data');
      }
    } catch (err: any) {
      console.error('Error loading test timetable data:', err);
      setError(err.message || 'Failed to load test timetable data');
    }
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-center gap-2 mb-2">
          <Calendar className="h-5 w-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Timetable Manager</h3>
        </div>
        <p className="text-gray-600">
          Upload, view, and manage your academic timetable
        </p>
      </div>

      {/* Tabs */}
      <div className="card">
        <div className="mb-6">
          <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md font-medium transition-all ${
                activeTab === 'upload'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Upload className="h-4 w-4" />
              Upload
            </button>
            <button
              onClick={() => setActiveTab('view')}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md font-medium transition-all ${
                activeTab === 'view'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Calendar className="h-4 w-4" />
              View
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md font-medium transition-all ${
                activeTab === 'stats'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <BarChart3 className="h-4 w-4" />
              Statistics
            </button>
            <button
              onClick={() => setActiveTab('conflicts')}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md font-medium transition-all ${
                activeTab === 'conflicts'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <AlertTriangle className="h-4 w-4" />
              Conflicts
            </button>
            <button
              onClick={() => setActiveTab('schedule')}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md font-medium transition-all ${
                activeTab === 'schedule'
                  ? 'bg-white text-primary-600 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Calendar className="h-4 w-4" />
              Schedule
            </button>
          </div>
        </div>

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <div className="space-y-4">
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
              <FileSpreadsheet className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Upload Timetable</h3>
              <p className="text-gray-600 mb-4">
                Upload your timetable file (Excel, CSV, or PDF format)
              </p>
              <input
                type="file"
                accept=".xlsx,.xls,.csv,.pdf"
                onChange={(e) => handleFileUpload(e.target.files)}
                className="hidden"
                id="file-upload"
              />
              <label
                htmlFor="file-upload"
                className="btn btn-primary cursor-pointer inline-flex items-center"
              >
                <Upload className="h-4 w-4 mr-2" />
                Choose File
              </label>
            </div>

            {loading && (
              <div className="text-center py-4">
                <div className="inline-flex items-center gap-2 text-primary-600">
                  <div className="w-4 h-4 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
                  Processing timetable...
                </div>
              </div>
            )}

            {error && (
              <div className="card border-red-200 bg-red-50">
                <div className="flex items-center gap-2 text-red-700">
                  <AlertTriangle className="h-4 w-4" />
                  <span className="font-medium">Error</span>
                </div>
                <p className="text-red-600 mt-1">{error}</p>
                <div className="mt-3 flex gap-2">
                  <button
                    onClick={() => setError(null)}
                    className="btn btn-outline text-sm"
                  >
                    Dismiss
                  </button>
                  {currentTimetableId && (
                    <button
                      onClick={() => loadTimetableData(currentTimetableId)}
                      className="btn btn-primary text-sm"
                    >
                      Retry
                    </button>
                  )}
                  {error.includes('log in') && (
                    <button
                      onClick={() => window.location.href = '/login'}
                      className="btn btn-primary text-sm"
                    >
                      Go to Login
                    </button>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* View Tab */}
        {activeTab === 'view' && (
          <div className="space-y-4">

            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Course</label>
                <input
                  type="text"
                  value={filters.course}
                  onChange={(e) => handleFilterChange('course', e.target.value)}
                  placeholder="Filter by course"
                  className="input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Day</label>
                <select
                  value={filters.day}
                  onChange={(e) => handleFilterChange('day', e.target.value)}
                  className="input"
                >
                  <option value="">All Days</option>
                  {days.map(day => (
                    <option key={day} value={day}>{day}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
                <select
                  value={filters.type}
                  onChange={(e) => handleFilterChange('type', e.target.value)}
                  className="input"
                >
                  <option value="">All Types</option>
                  {types.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Room</label>
                <input
                  type="text"
                  value={filters.room}
                  onChange={(e) => handleFilterChange('room', e.target.value)}
                  placeholder="Filter by room"
                  className="input"
                />
              </div>
            </div>

            <div className="flex justify-between items-center">
              <p className="text-sm text-gray-600">
                Showing {filteredData.length} of {timetableData.length} classes
              </p>
              <button
                onClick={clearFilters}
                className="btn btn-outline text-sm"
              >
                Clear Filters
              </button>
            </div>

            {/* Timetable Data */}
            {filteredData.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-gray-200">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="border border-gray-200 px-4 py-2 text-left">Course</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Section</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Day</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Time</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Type</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Room</th>
                      <th className="border border-gray-200 px-4 py-2 text-left">Instructor</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredData.map((entry) => (
                      <tr key={entry.id} className="hover:bg-gray-50">
                        <td className="border border-gray-200 px-4 py-2">
                          <div className="flex items-center gap-2">
                            <BookOpen className="h-4 w-4 text-primary-600" />
                            {entry.course}
                          </div>
                        </td>
                        <td className="border border-gray-200 px-4 py-2">{entry.section}</td>
                        <td className="border border-gray-200 px-4 py-2">{entry.day}</td>
                        <td className="border border-gray-200 px-4 py-2">
                          <div className="flex items-center gap-1">
                            <Clock className="h-4 w-4 text-gray-500" />
                            {entry.time}
                          </div>
                        </td>
                        <td className="border border-gray-200 px-4 py-2">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            entry.type === 'Theory' 
                              ? 'bg-blue-100 text-blue-700' 
                              : 'bg-green-100 text-green-700'
                          }`}>
                            {entry.type}
                          </span>
                        </td>
                        <td className="border border-gray-200 px-4 py-2">
                          <div className="flex items-center gap-1">
                            <MapPin className="h-4 w-4 text-gray-500" />
                            {entry.room}
                          </div>
                        </td>
                        <td className="border border-gray-200 px-4 py-2">
                          {entry.instructor && (
                            <div className="flex items-center gap-1">
                              <Users className="h-4 w-4 text-gray-500" />
                              {entry.instructor}
                            </div>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-8">
                <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                {currentTimetableId && timetableData.length === 0 ? (
                  <>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">Timetable Data Missing</h3>
                    <p className="text-gray-600 mb-4">
                      Your timetable ID exists but the data is missing. This may happen if the server was restarted or the data was cleared.
                    </p>
                    <div className="flex gap-3 justify-center">
                      <button
                        onClick={clearAllData}
                        className="btn btn-outline"
                      >
                        Clear and Start Fresh
                      </button>
                      <button
                        onClick={() => setActiveTab('upload')}
                        className="btn btn-primary"
                      >
                        Upload New Timetable
                      </button>
                    </div>
                  </>
                ) : (
                  <>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">No Timetable Data</h3>
                    <p className="text-gray-600 mb-4">Upload a timetable file to get started</p>
                    <button
                      onClick={() => setActiveTab('upload')}
                      className="btn btn-primary"
                    >
                      Upload Timetable
                    </button>
                  </>
                )}
              </div>
            )}
          </div>
        )}

        {/* Statistics Tab */}
        {activeTab === 'stats' && (
          <div className="space-y-6">
            {stats ? (
              <>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{stats.totalClasses}</div>
                    <div className="text-sm text-gray-600">Total Classes</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{stats.uniqueCourses}</div>
                    <div className="text-sm text-gray-600">Unique Courses</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{stats.theoryClasses}</div>
                    <div className="text-sm text-gray-600">Theory Classes</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{stats.labClasses}</div>
                    <div className="text-sm text-gray-600">Lab Classes</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{stats.uniqueRooms}</div>
                    <div className="text-sm text-gray-600">Unique Rooms</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900">{stats.daysCovered}</div>
                    <div className="text-sm text-gray-600">Days Covered</div>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No Statistics Available</h3>
                <p className="text-gray-600">Upload a timetable to view statistics</p>
              </div>
            )}
          </div>
        )}

        {/* Conflicts Tab */}
        {activeTab === 'conflicts' && (
          <div className="space-y-6">
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Course Selection</h3>
              <p className="text-gray-600 mb-4">Select courses to check for scheduling conflicts</p>
              
              {availableCourses.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
                  {availableCourses.map((course) => (
                    <label key={course} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedCourses.includes(course)}
                        onChange={(e) => handleCourseSelection(course, e.target.checked)}
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                      <span className="text-sm text-gray-700">{course}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 mb-4">No courses available. Upload a timetable first.</p>
              )}

              <div className="flex gap-3">
                <button
                  onClick={checkConflicts}
                  disabled={selectedCourses.length === 0 || loading}
                  className="btn btn-primary"
                >
                  {loading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  ) : (
                    <AlertTriangle className="h-4 w-4 mr-2" />
                  )}
                  Check Conflicts
                </button>
                <button
                  onClick={buildPersonalSchedule}
                  disabled={selectedCourses.length === 0 || loading}
                  className="btn btn-outline"
                >
                  <Calendar className="h-4 w-4 mr-2" />
                  Build Schedule
                </button>
              </div>
            </div>

            {conflicts.length > 0 && (
              <div className="card border-red-200 bg-red-50">
                <h3 className="text-lg font-semibold text-red-900 mb-4">
                  <AlertTriangle className="h-5 w-5 inline mr-2" />
                  Found {conflicts.length} Conflicts
                </h3>
                <div className="space-y-3">
                  {conflicts.map((conflict, index) => (
                    <div key={index} className="p-3 bg-white rounded border border-red-200">
                      <div className="font-medium text-red-900">{conflict.day}</div>
                      <div className="text-sm text-red-700">
                        <span className="font-medium">{conflict.course1} ({conflict.section1})</span> at {conflict.time1} in {conflict.room1}
                        <br />
                        <span className="font-medium">{conflict.course2} ({conflict.section2})</span> at {conflict.time2} in {conflict.room2}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {recommendations.length > 0 && (
              <div className="card border-blue-200 bg-blue-50">
                <h3 className="text-lg font-semibold text-blue-900 mb-4">
                  <CheckCircle className="h-5 w-5 inline mr-2" />
                  Recommendations
                </h3>
                <div className="space-y-3">
                  {recommendations.map((rec, index) => (
                    <div key={index} className="p-3 bg-white rounded border border-blue-200">
                      <div className="font-medium text-blue-900">{rec.conflict_type} - {rec.day}</div>
                      <div className="text-sm text-blue-700">
                        <div className="mb-2">Conflicted courses: {rec.conflicted_courses.join(', ')}</div>
                        {rec.suggestions.length > 0 && (
                          <div>
                            <div className="font-medium mb-1">Alternative sections:</div>
                            {rec.suggestions.map((suggestion, i) => (
                              <div key={i} className="ml-2">
                                {suggestion.course} - Section {suggestion.alternative_section} at {suggestion.alternative_time} in {suggestion.alternative_room}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Schedule Builder Tab */}
        {activeTab === 'schedule' && (
          <div className="space-y-6">
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Personal Schedule Builder</h3>
              <p className="text-gray-600 mb-4">Select your courses to build a personalized schedule</p>
              
              {availableCourses.length > 0 ? (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-6">
                  {availableCourses.map((course) => (
                    <label key={course} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedCourses.includes(course)}
                        onChange={(e) => handleCourseSelection(course, e.target.checked)}
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                      />
                      <span className="text-sm text-gray-700">{course}</span>
                    </label>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 mb-4">No courses available. Upload a timetable first.</p>
              )}

              <div className="flex gap-3">
                <button
                  onClick={buildPersonalSchedule}
                  disabled={selectedCourses.length === 0 || loading}
                  className="btn btn-primary"
                >
                  {loading ? (
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                  ) : (
                    <Calendar className="h-4 w-4 mr-2" />
                  )}
                  Build My Schedule
                </button>
              </div>
            </div>

            {selectedCourses.length > 0 && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Selected Courses</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedCourses.map((course) => (
                    <span key={course} className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm">
                      {course}
                      <button
                        onClick={() => handleCourseSelection(course, false)}
                        className="ml-2 text-primary-600 hover:text-primary-800"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}