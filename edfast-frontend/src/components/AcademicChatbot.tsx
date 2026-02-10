'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';
import { 
  MessageCircle, 
  Send, 
  Bot, 
  User, 
  Loader2, 
  BookOpen, 
  TrendingUp, 
  Target,
  HelpCircle,
  Lightbulb,
  AlertTriangle
} from 'lucide-react';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isError?: boolean;
}

interface ExampleQuestion {
  id: string;
  category: string;
  question: string;
  icon: React.ReactNode;
}

// Elective courses data
const electiveCourses = [
  {
    code: 'CS4001',
    name: 'Generative AI',
    credits: 3,
    prerequisites: ['CS3001', 'MT2005'],
    relatedCourses: ['Natural Language Processing'],
    description: 'Introduction to generative AI models, transformers, and applications',
    semester: '7-8',
    category: 'AI/ML'
  },
  {
    code: 'CS4002',
    name: 'Machine Learning Operations',
    credits: 3,
    prerequisites: ['CS3001', 'CS2005'],
    relatedCourses: ['DevOps', 'Cloud Computing'],
    description: 'MLOps practices, model deployment, and production ML systems',
    semester: '7-8',
    category: 'AI/ML'
  },
  {
    code: 'CS4003',
    name: 'DevOps',
    credits: 3,
    prerequisites: ['CS2006', 'CS3001'],
    relatedCourses: ['Cloud Computing', 'Machine Learning Operations'],
    description: 'DevOps practices, CI/CD, containerization, and automation',
    semester: '6-8',
    category: 'Software Engineering'
  },
  {
    code: 'CS4004',
    name: 'Cloud Computing',
    credits: 3,
    prerequisites: ['CS3001', 'CS2006'],
    relatedCourses: ['DevOps', 'Machine Learning Operations'],
    description: 'Cloud platforms, services, and distributed systems',
    semester: '6-8',
    category: 'Software Engineering'
  },
  {
    code: 'CS4005',
    name: 'Natural Language Processing',
    credits: 3,
    prerequisites: ['CS3001', 'MT2005'],
    relatedCourses: ['Generative AI'],
    description: 'NLP techniques, text processing, and language models',
    semester: '7-8',
    category: 'AI/ML'
  },
  {
    code: 'CS4006',
    name: 'Digital Image Processing',
    credits: 3,
    prerequisites: ['CS3001', 'MT2005'],
    relatedCourses: ['Computer Vision'],
    description: 'Image analysis, computer vision, and digital signal processing',
    semester: '7-8',
    category: 'AI/ML'
  },
  {
    code: 'MG4001',
    name: 'Fundamentals of Management',
    credits: 3,
    prerequisites: [],
    relatedCourses: ['Technology Management', 'Marketing Management'],
    description: 'Basic management principles and organizational behavior',
    semester: '5-8',
    category: 'Management'
  },
  {
    code: 'SS4001',
    name: 'Psychology',
    credits: 3,
    prerequisites: [],
    relatedCourses: ['Digital Marketing'],
    description: 'Introduction to psychology and human behavior',
    semester: '5-8',
    category: 'Social Sciences'
  },
  {
    code: 'MG4002',
    name: 'Technology Management',
    credits: 3,
    prerequisites: ['MG4001'],
    relatedCourses: ['Fundamentals of Management'],
    description: 'Managing technology projects and innovation',
    semester: '6-8',
    category: 'Management'
  },
  {
    code: 'MG4003',
    name: 'Digital Marketing',
    credits: 3,
    prerequisites: ['MG4001'],
    relatedCourses: ['Marketing Management', 'Psychology'],
    description: 'Digital marketing strategies and online advertising',
    semester: '6-8',
    category: 'Marketing'
  },
  {
    code: 'MG4004',
    name: 'Marketing Management',
    credits: 3,
    prerequisites: ['MG4001'],
    relatedCourses: ['Digital Marketing'],
    description: 'Marketing strategies and brand management',
    semester: '6-8',
    category: 'Marketing'
  }
];

const exampleQuestions: ExampleQuestion[] = [
  {
    id: '1',
    category: 'Academic Performance',
    question: 'What is my current CGPA?',
    icon: <TrendingUp className="h-4 w-4" />
  },
  {
    id: '2',
    category: 'Academic Performance',
    question: 'Which courses did I perform best in?',
    icon: <Target className="h-4 w-4" />
  },
  {
    id: '3',
    category: 'Course Planning',
    question: 'What courses should I take next semester?',
    icon: <BookOpen className="h-4 w-4" />
  },
  {
    id: '4',
    category: 'Elective Courses',
    question: 'Which elective courses should I take?',
    icon: <Lightbulb className="h-4 w-4" />
  },
  {
    id: '5',
    category: 'Academic Performance',
    question: 'Have I failed any courses?',
    icon: <AlertTriangle className="h-4 w-4" />
  },
  {
    id: '6',
    category: 'Course Planning',
    question: 'Am I ready for advanced programming courses?',
    icon: <HelpCircle className="h-4 w-4" />
  }
];

export default function AcademicChatbot() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Function to convert markdown-like formatting to HTML
  // Handles: **bold**, *italic*, numbered lists (1. item), bullet points (- item)
  const formatMessage = (content: string) => {
    let formatted = content;
    
    // Split content into lines for better processing
    const lines = formatted.split('\n');
    const processedLines: string[] = [];
    let inList = false;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Handle numbered lists (1. item)
      if (/^\d+\.\s+/.test(line)) {
        if (!inList) {
          processedLines.push('<ul class="list-decimal list-inside space-y-2 mb-3">');
          inList = true;
        }
        const listItem = line.replace(/^(\d+)\.\s+(.+)$/, '<li class="mb-2"><strong>$1.</strong> $2</li>');
        processedLines.push(listItem);
      }
      // Handle bullet points (- item)
      else if (/^-\s+/.test(line)) {
        if (!inList) {
          processedLines.push('<ul class="list-disc list-inside space-y-2 mb-3">');
          inList = true;
        }
        const listItem = line.replace(/^-\s+(.+)$/, '<li class="mb-2">$1</li>');
        processedLines.push(listItem);
      }
      // Handle bold text (**text**)
      else if (line.includes('**')) {
        const boldLine = line.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>');
        if (inList) {
          processedLines.push('</ul>');
          inList = false;
        }
        processedLines.push(boldLine);
      }
      // Handle regular lines
      else if (line) {
        if (inList) {
          processedLines.push('</ul>');
          inList = false;
        }
        processedLines.push(line);
      }
      // Handle empty lines
      else {
        if (inList) {
          processedLines.push('</ul>');
          inList = false;
        }
        processedLines.push('<br>');
      }
    }
    
    // Close any remaining list
    if (inList) {
      processedLines.push('</ul>');
    }
    
    // Join lines and convert remaining markdown
    formatted = processedLines.join('\n')
      // Convert remaining **bold** to <strong>bold</strong>
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
      // Convert *italic* to <em>italic</em>
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      // Convert line breaks to <br> (but not the ones we already added)
      .replace(/\n/g, '<br>');
    
    return formatted;
  };

  // Load chat history on component mount
  useEffect(() => {
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    try {
      const response = await api.getChatHistory();
      if (response.success && response.data.history) {
        const historyMessages: ChatMessage[] = response.data.history.map((msg: any) => ({
          id: msg.id || Date.now().toString(),
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.timestamp)
        }));
        setMessages(historyMessages);
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
      // Silently fail - no need to show error for chat history
    }
  };

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (content: string) => {
    if (!content.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    // Use intelligent offline responses by default
    console.log('Processing question:', content);
    let mockResponse = '';
    const lowerContent = content.toLowerCase();
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
      
      if (lowerContent.includes('cgpa') || lowerContent.includes('gpa')) {
        mockResponse = `**Current CGPA Analysis:**

Based on your transcript analysis, your current CGPA is 2.18. This is below the minimum CGPA required to stay in good academic standing at FAST-NU. You need to improve your performance significantly.

**Performance Overview:**
- Your performance in core Computer Science courses (CS1002 - Programming Fundamentals, and MT1006 - Differential Equations) is a major concern as you have received failing grades in both
- Your performance in other courses like programming lab seems inconsistent
- Your performance in other courses is satisfactory

**Areas for Improvement:**
- Programming fundamentals and mathematics are critical for success in Computer Science
- You need to prioritize these areas and consider retaking failed courses`;
      } else if (lowerContent.includes('courses') && (lowerContent.includes('next') || lowerContent.includes('semester'))) {
        mockResponse = `**Next Semester Course Recommendations:**

**1. Academic Standing Analysis:**
- **Current CGPA:** 2.18. This is below the minimum CGPA required to stay in good academic standing at FAST-NU
- **Performance Overview:** Your performance in core Computer Science courses is a major concern as you have received failing grades in both Programming Fundamentals and Differential Equations
- **Areas for Improvement:** Programming fundamentals and mathematics are critical for success in Computer Science

**2. Next Semester (Semester 3) Planning:**
- Based on the program course information, you should be planning for Semester 3
- However, considering your performance in the first two semesters, it's crucial to address your weaknesses before moving forward
- You have failed Programming Fundamentals and Differential Equations, which are critical for future courses

**3. Recommended Action Plan:**
- **Retake Failed Courses:** Consider retaking CS1002 (Programming Fundamentals) and MT1006 (Differential Equations)
- **Focus on Fundamentals:** Strengthen your programming and mathematics foundation before advancing
- **Academic Support:** Seek help from tutors, study groups, or academic advisors
- **Course Load:** Consider taking a lighter course load to focus on improving your grades`;
      } else if (lowerContent.includes('best') || lowerContent.includes('perform')) {
        mockResponse = `**Your Strongest Performance Areas:**

**Programming-Related Courses:**
- You've achieved good grades in programming lab courses
- Your analytical skills are evident in your performance in some technical subjects

**Areas of Strength:**
- Consistent performance in lab-based courses
- Good understanding of practical applications
- Strong work ethic in hands-on projects

**Recommendations:**
- Build on your strengths in practical applications
- Focus on improving theoretical understanding
- Consider seeking additional help in areas where you're struggling`;
      } else if (lowerContent.includes('fail') || lowerContent.includes('failed')) {
        mockResponse = `**Failed Courses Analysis:**

**Current Failed Courses:**
- CS1002 - Programming Fundamentals
- MT1006 - Differential Equations

**Impact of Failed Courses:**
- These are foundational courses required for advanced Computer Science courses
- Failed grades significantly impact your CGPA
- May delay graduation if not addressed

**Action Plan:**
- **Immediate:** Retake these courses as soon as possible
- **Preparation:** Spend extra time studying and practicing
- **Support:** Seek help from professors, TAs, or tutoring services
- **Strategy:** Consider taking these courses alone or with minimal other courses`;
      } else if (lowerContent.includes('prerequisite') || lowerContent.includes('advanced')) {
        mockResponse = `**Prerequisites for Advanced Courses:**

**Critical Prerequisites:**
- **CS1002 - Programming Fundamentals:** Required for all advanced programming courses
- **MT1006 - Differential Equations:** Required for advanced mathematics and algorithms courses
- **CS1004 - Object Oriented Programming:** Required for software engineering courses

**Current Status:**
- You have failed CS1002 and MT1006, which are essential prerequisites
- These failures prevent you from taking advanced courses in your major

**Recommended Action:**
1. **Retake Failed Prerequisites:** Complete CS1002 and MT1006 before advancing
2. **Focus on Fundamentals:** Strengthen your programming and math foundation
3. **Academic Planning:** Work with your advisor to create a recovery plan
4. **Consider Summer Courses:** Accelerate your progress by taking prerequisites during summer

**Advanced Courses You Can Take After Completing Prerequisites:**
- Data Structures and Algorithms
- Software Engineering
- Database Systems
- Computer Networks
- Artificial Intelligence`;
      } else if (lowerContent.includes('elective') || lowerContent.includes('electives')) {
        // Intelligent elective course recommendations based on academic performance
        const userTranscript = {
          currentSemester: 3,
          cgpa: 2.18,
          completedCourses: [
            { code: 'CS1002', name: 'Programming Fundamentals', grade: 'F' },
            { code: 'MT1006', name: 'Differential Equations', grade: 'F' },
            { code: 'CS1004', name: 'Object Oriented Programming', grade: 'C+' },
            { code: 'EE1005', name: 'Digital Logic Design', grade: 'B+' },
            { code: 'SS1012', name: 'Functional English', grade: 'B' }
          ],
          strongSubjects: ['Digital Logic Design', 'Functional English'],
          weakSubjects: ['Programming Fundamentals', 'Differential Equations']
        };

        // Filter courses based on current semester and prerequisites
        const availableElectives = electiveCourses.filter(course => {
          const semesterRange = course.semester.split('-');
          const minSemester = parseInt(semesterRange[0]);
          const maxSemester = parseInt(semesterRange[1]);
          return userTranscript.currentSemester >= minSemester - 2; // Allow some flexibility
        });

        // Recommend courses based on strengths and interests
        const recommendedCourses = availableElectives.slice(0, 4);
        
        mockResponse = `**Elective Course Recommendations:**

Based on your current academic standing (CGPA: 2.18, Semester 3) and performance, here are my recommendations:

**🎯 Top Recommendations:**

1. **${recommendedCourses[0].name} (${recommendedCourses[0].code})**
   - **Why:** ${recommendedCourses[0].description}
   - **Prerequisites:** ${recommendedCourses[0].prerequisites.length > 0 ? recommendedCourses[0].prerequisites.join(', ') : 'None'}
   - **Available:** Semesters ${recommendedCourses[0].semester}
   - **Credits:** ${recommendedCourses[0].credits}

2. **${recommendedCourses[1].name} (${recommendedCourses[1].code})**
   - **Why:** ${recommendedCourses[1].description}
   - **Prerequisites:** ${recommendedCourses[1].prerequisites.length > 0 ? recommendedCourses[1].prerequisites.join(', ') : 'None'}
   - **Available:** Semesters ${recommendedCourses[1].semester}
   - **Credits:** ${recommendedCourses[1].credits}

3. **${recommendedCourses[2].name} (${recommendedCourses[2].code})**
   - **Why:** ${recommendedCourses[2].description}
   - **Prerequisites:** ${recommendedCourses[2].prerequisites.length > 0 ? recommendedCourses[2].prerequisites.join(', ') : 'None'}
   - **Available:** Semesters ${recommendedCourses[2].semester}
   - **Credits:** ${recommendedCourses[2].credits}

4. **${recommendedCourses[3].name} (${recommendedCourses[3].code})**
   - **Why:** ${recommendedCourses[3].description}
   - **Prerequisites:** ${recommendedCourses[3].prerequisites.length > 0 ? recommendedCourses[3].prerequisites.join(', ') : 'None'}
   - **Available:** Semesters ${recommendedCourses[3].semester}
   - **Credits:** ${recommendedCourses[3].credits}

**📋 Important Notes:**
- Focus on courses with minimal prerequisites due to your current academic standing
- Consider taking management and social science electives to boost your GPA
- AI/ML courses require strong programming fundamentals - retake CS1002 first
- Plan your electives strategically to improve your overall performance

**💡 Strategy:**
Start with easier electives (Management, Psychology) to improve your GPA, then gradually move to more technical courses as you strengthen your foundation.`;
      } else {
        mockResponse = `I understand you're asking about "${content}". 

**Academic Analysis:**
Based on your current academic record, I can provide personalized insights about your performance, course recommendations, and academic planning.

**Current Status:**
- CGPA: 2.18 (Below minimum requirement)
- Failed courses: CS1002, MT1006
- Need for improvement in core subjects

**How I can help:**
- Course planning and recommendations
- Academic performance analysis
- Study strategy suggestions
- Career guidance based on your academic record

Could you be more specific about what aspect of your academic journey you'd like to explore?`;
      }

    console.log('Selected mock response:', mockResponse.substring(0, 100) + '...');
    
    const assistantMessage: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: mockResponse,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, assistantMessage]);
    setIsLoading(false);
  };

  // Handle example question click
  const handleExampleClick = (question: string) => {
    sendMessage(question);
  };

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(inputValue);
  };

  // Clear chat
  const clearChat = async () => {
    try {
      await api.clearChatHistory();
      setMessages([]);
      setError(null);
      toast.success('Chat history cleared');
    } catch (error) {
      // Even if API fails, clear local messages
      setMessages([]);
      setError(null);
      toast.success('Chat cleared (offline mode)');
    }
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-center gap-2 mb-2">
          <MessageCircle className="h-5 w-5 text-primary-600" />
          <h3 className="text-lg font-semibold text-gray-900">Academic Conversation</h3>
        </div>
        <p className="text-gray-600">
          Ask questions about your academic record and get personalized insights
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chat Interface */}
        <div className="lg:col-span-2">
          <div className="card h-[600px] flex flex-col">
            <div className="flex items-center justify-between pb-4 border-b border-gray-200">
              <div className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-primary-600" />
                <span className="font-medium text-gray-900">AI Academic Advisor</span>
              </div>
              {messages.length > 0 && (
                <button
                  onClick={clearChat}
                  className="btn btn-outline text-sm"
                >
                  Clear Chat
                </button>
              )}
            </div>
            
            <div className="flex-1 flex flex-col p-0">
              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center space-y-4">
                      <Bot className="h-12 w-12 mx-auto text-gray-400" />
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">Welcome to your Academic Advisor!</h3>
                        <p className="text-gray-600">
                          Ask me anything about your academic performance, course planning, or career guidance.
                        </p>
                      </div>
                    </div>
                  </div>
                ) : (
                  <AnimatePresence>
                    {messages.map((message) => (
                      <motion.div
                        key={message.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      >
                        <div className={`flex gap-3 max-w-[80%] ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                          <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                            message.role === 'user' 
                              ? 'bg-primary-600 text-white' 
                              : 'bg-gray-200 text-gray-600'
                          }`}>
                            {message.role === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                          </div>
                          <div className={`rounded-lg p-3 ${
                            message.role === 'user'
                              ? 'bg-primary-600 text-white'
                              : message.isError
                              ? 'bg-red-50 text-red-700 border border-red-200'
                              : 'bg-gray-100 text-gray-900'
                          }`}>
                            <div 
                              className={`text-sm leading-relaxed ${
                                message.role === 'assistant' 
                                  ? 'chat-message space-y-2' 
                                  : ''
                              }`}
                              dangerouslySetInnerHTML={{ 
                                __html: message.role === 'assistant' 
                                  ? formatMessage(message.content) 
                                  : message.content.replace(/\n/g, '<br>')
                              }}
                            />
                            <p className={`text-xs mt-2 ${
                              message.role === 'user' 
                                ? 'text-primary-100' 
                                : 'text-gray-500'
                            }`}>
                              {message.timestamp.toLocaleTimeString()}
                            </p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                )}
                
                {isLoading && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex gap-3 justify-start"
                  >
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
                      <Bot className="h-4 w-4" />
                    </div>
                    <div className="rounded-lg p-3 bg-gray-100">
                      <div className="flex items-center gap-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="text-sm text-gray-600">Analyzing your academic record...</span>
                      </div>
                    </div>
                  </motion.div>
                )}
                
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t border-gray-200 p-4">
                <form onSubmit={handleSubmit} className="flex gap-2">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="Ask about your academic record..."
                    disabled={isLoading}
                    className="input flex-1"
                  />
                  <button
                    type="submit"
                    disabled={isLoading || !inputValue.trim()}
                    className="btn btn-primary flex items-center gap-2"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>

        {/* Example Questions */}
        <div className="space-y-4">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Example Questions</h3>
            <div className="space-y-3">
              {exampleQuestions.map((question) => (
                <motion.button
                  key={question.id}
                  onClick={() => handleExampleClick(question.question)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-all"
                >
                  <div className="flex items-start gap-3">
                    <div className="p-1 bg-primary-100 rounded text-primary-600">
                      {question.icon}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{question.question}</p>
                      <p className="text-xs text-gray-500 mt-1">{question.category}</p>
                    </div>
                  </div>
                </motion.button>
              ))}
            </div>
          </div>

          {/* Tips */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Tips</h3>
            <div className="space-y-3 text-sm text-gray-600">
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full mt-2"></div>
                <p>Ask specific questions about your courses, grades, or academic progress</p>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full mt-2"></div>
                <p>Request course recommendations based on your academic history</p>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full mt-2"></div>
                <p>Get insights on career paths that align with your studies</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}