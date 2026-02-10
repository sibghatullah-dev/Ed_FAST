
# EdFast API Documentation

## Base URL
```
http://localhost:5000/api/v1
```

## Authentication
All endpoints (except auth endpoints) require JWT authentication.

**Header:**
```
Authorization: Bearer <access_token>
```

---

## 🔐 Authentication Endpoints (`/auth`)

### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "username": "johndoe",
  "password": "password123",
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "username": "johndoe",
    "name": "John Doe",
    "access_token": "eyJ0eXAiOiJKV1...",
    "refresh_token": "eyJ0eXAiOiJKV1..."
  }
}
```

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "password123"
}
```

### Refresh Token
```http
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

### Verify Token
```http
GET /api/v1/auth/verify
Authorization: Bearer <access_token>
```

### Logout
```http
POST /api/v1/auth/logout
Authorization: Bearer <access_token>
```

---

## 👤 User Endpoints (`/users`)

### Get Current User Profile
```http
GET /api/v1/users/me
Authorization: Bearer <access_token>
```

### Update Profile
```http
PUT /api/v1/users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "New Name",
  "description": "Updated description"
}
```

### Upload Transcript
```http
POST /api/v1/users/me/transcript
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <image_file>
```

### Get Resume Data
```http
GET /api/v1/users/me/resume
Authorization: Bearer <access_token>
```

---

## 💬 PeerHub Endpoints (`/peerhub`)

### Get Posts
```http
GET /api/v1/peerhub/posts?limit=50&offset=0&sort_by=created_at
```

**Query Parameters:**
- `limit` - Number of posts (default: 50)
- `offset` - Pagination offset (default: 0)
- `tag` - Filter by tag
- `author` - Filter by author username
- `course_code` - Filter by course
- `sort_by` - Sort option: `created_at`, `score`, `comments`

### Create Post
```http
POST /api/v1/peerhub/posts
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "My Post Title",
  "content": "Post content here...",
  "tags": ["programming", "help"],
  "course_code": "CS101",
  "course_name": "Introduction to Programming"
}
```

### Get Single Post
```http
GET /api/v1/peerhub/posts/{post_id}
```

### Update Post
```http
PUT /api/v1/peerhub/posts/{post_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content"
}
```

### Delete Post
```http
DELETE /api/v1/peerhub/posts/{post_id}
Authorization: Bearer <access_token>
```

### Get Comments
```http
GET /api/v1/peerhub/posts/{post_id}/comments
```

### Create Comment
```http
POST /api/v1/peerhub/posts/{post_id}/comments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "My comment",
  "parent_id": "optional_parent_comment_id"
}
```

### Vote on Post
```http
POST /api/v1/peerhub/posts/{post_id}/vote
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "vote_type": "upvote"
}
```

### Search Posts
```http
GET /api/v1/peerhub/search?query=programming&limit=20
```

### Get Trending Posts
```http
GET /api/v1/peerhub/trending?limit=10&days=7
```

### Get Popular Tags
```http
GET /api/v1/peerhub/tags?limit=20
```

### Get Platform Statistics
```http
GET /api/v1/peerhub/stats
```

---

## 🤖 Chatbot Endpoints (`/chatbot`)

### Send Chat Query
```http
POST /api/v1/chatbot/query
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "What courses should I take next semester?"
}
```

### Get Chat History
```http
GET /api/v1/chatbot/history
Authorization: Bearer <access_token>
```

### Clear Chat History
```http
DELETE /api/v1/chatbot/history
Authorization: Bearer <access_token>
```

---

## 📅 Timetable Endpoints (`/timetable`)

### Upload Timetable
```http
POST /api/v1/timetable/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

files: <excel_or_csv_files>
```

### Get User Timetables
```http
GET /api/v1/timetable/
Authorization: Bearer <access_token>
```

### Get Specific Timetable
```http
GET /api/v1/timetable/{timetable_id}
Authorization: Bearer <access_token>
```

### Filter Timetable
```http
POST /api/v1/timetable/{timetable_id}/filter
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "courses": ["CS101", "MATH201"],
  "departments": ["Computer Science"]
}
```

### Check Conflicts
```http
POST /api/v1/timetable/{timetable_id}/conflicts
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "courses": ["CS101", "MATH201"]
}
```

### Get Statistics
```http
GET /api/v1/timetable/{timetable_id}/stats
Authorization: Bearer <access_token>
```

---

## 📄 Resume Builder Endpoints (`/resume`)

### Get Resume Data
```http
GET /api/v1/resume/
Authorization: Bearer <access_token>
```

### Update Resume
```http
PUT /api/v1/resume/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "resume_data": {
    "personal_info": {...},
    "education": [...],
    "skills": {...}
  }
}
```

### Auto-fill Resume
```http
POST /api/v1/resume/autofill
Authorization: Bearer <access_token>
```

### Get AI Suggestions
```http
POST /api/v1/resume/suggestions
Authorization: Bearer <access_token>
```

### Generate PDF
```http
POST /api/v1/resume/generate
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "style": "professional"
}
```

**Response:** PDF file download

### Check Completeness
```http
GET /api/v1/resume/completeness
Authorization: Bearer <access_token>
```

---

## 📚 Courses Endpoints (`/courses`)

### Get All Courses
```http
GET /api/v1/courses/?semester=1&elective=false&limit=50&offset=0
```

### Get Specific Course
```http
GET /api/v1/courses/{course_code}
```

### Search Courses
```http
GET /api/v1/courses/search?q=programming&limit=20
```

### Get Electives
```http
GET /api/v1/courses/electives
```

### Get Semesters
```http
GET /api/v1/courses/semesters
```

### Get Statistics
```http
GET /api/v1/courses/statistics
```

---

## 🔧 Utility Endpoints

### Health Check
```http
GET /api/v1/health
```

### API Info
```http
GET /api/v1
```

---

## Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "error": "Error title",
  "message": "Detailed error message"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `500` - Internal Server Error
- `503` - Service Unavailable

---

## Rate Limiting

Currently no rate limiting is implemented. Will be added in production.

## CORS

CORS is enabled for:
- `http://localhost:3000`
- `http://localhost:3001`

---

## Testing with cURL

### Register User
```bash
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","username":"johndoe","password":"password123"}'
```

### Login
```bash
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"johndoe","password":"password123"}'
```

### Get User Profile (with token)
```bash
curl -X GET http://localhost:5000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Testing with Postman

1. Import the API endpoints into Postman
2. Set environment variable `base_url` = `http://localhost:5000/api/v1`
3. Set environment variable `token` after login
4. Use `{{base_url}}` and `{{token}}` in requests

---

**API Version:** 1.0.0  
**Last Updated:** 2025-01-13




