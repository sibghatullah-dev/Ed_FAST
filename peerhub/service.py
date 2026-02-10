"""
Service layer for PeerHub - Peer Discussion Hub
Handles business logic and API operations
"""

import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from .models import PeerHubDatabase, User, Post, Comment, Vote


class PeerHubService:
    """Service class for PeerHub operations"""
    
    def __init__(self, data_dir: str = "peerhub_data"):
        self.db = PeerHubDatabase(data_dir)
    
    # User operations
    def create_user(self, username: str, name: str, email: str = "") -> Optional[User]:
        """Create a new user"""
        # Check if username already exists
        if self.db.get_user_by_username(username):
            return None
        
        user_id = str(uuid.uuid4())
        user = User(
            user_id=user_id,
            username=username,
            name=name,
            email=email
        )
        
        if self.db.create_user(user):
            return user
        return None
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.db.get_user(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.get_user_by_username(username)
    
    def update_user(self, user: User) -> bool:
        """Update user information"""
        return self.db.update_user(user)
    
    # Post operations
    def create_post(self, title: str, content: str, author_id: str, 
                   tags: List[str] = None, file_link: str = "", 
                   course_code: str = None, course_name: str = None, 
                   semester: int = None) -> Optional[Post]:
        """Create a new post"""
        post_id = str(uuid.uuid4())
        post = Post(
            post_id=post_id,
            title=title,
            content=content,
            author_id=author_id,
            tags=tags or [],
            file_link=file_link,
            course_code=course_code,
            course_name=course_name,
            semester=semester
        )
        
        if self.db.create_post(post):
            return post
        return None
    
    def get_post(self, post_id: str) -> Optional[Post]:
        """Get post by ID"""
        return self.db.get_post(post_id)
    
    def get_posts(self, limit: int = 50, offset: int = 0, tag: str = None,
                  author_id: str = None, course_code: str = None, sort_by: str = "created_at") -> List[Post]:
        """Get posts with filtering and sorting"""
        return self.db.get_posts(limit, offset, tag, author_id, course_code, sort_by)
    
    def update_post(self, post: Post) -> bool:
        """Update post"""
        post.updated_at = datetime.now().isoformat()
        return self.db.update_post(post)
    
    def delete_post(self, post_id: str, user_id: str) -> bool:
        """Delete post (only by author)"""
        post = self.db.get_post(post_id)
        if post and post.author_id == user_id:
            return self.db.delete_post(post_id)
        return False
    
    def search_posts(self, query: str, limit: int = 20, search_type: str = "all") -> List[Post]:
        """Advanced search posts with multiple search types"""
        posts = self.db.get_posts(limit=1000)  # Get all posts for search
        query_lower = query.lower()
        
        matching_posts = []
        for post in posts:
            match_found = False
            
            if search_type == "all" or search_type == "title":
                if query_lower in post.title.lower():
                    match_found = True
            
            if search_type == "all" or search_type == "content":
                if query_lower in post.content.lower():
                    match_found = True
            
            if search_type == "all" or search_type == "tags":
                if any(query_lower in tag.lower() for tag in post.tags):
                    match_found = True
            
            if match_found:
                matching_posts.append(post)
        
        # Advanced relevance scoring
        matching_posts.sort(key=lambda p: self._calculate_relevance_score(p, query_lower), reverse=True)
        
        return matching_posts[:limit]
    
    def _calculate_relevance_score(self, post: Post, query: str) -> float:
        """Calculate relevance score for search results"""
        score = 0.0
        
        # Title matches (highest weight)
        if query in post.title.lower():
            score += 10.0
            # Exact title match gets bonus
            if post.title.lower() == query:
                score += 5.0
        
        # Content matches
        content_matches = post.content.lower().count(query)
        score += content_matches * 2.0
        
        # Tag matches
        tag_matches = sum(1 for tag in post.tags if query in tag.lower())
        score += tag_matches * 3.0
        
        # Post score (engagement)
        score += post.score * 0.1
        
        # Recency bonus
        from datetime import datetime
        days_old = (datetime.now() - datetime.fromisoformat(post.created_at)).days
        recency_bonus = max(0, 5 - days_old) * 0.5
        score += recency_bonus
        
        return score
    
    def advanced_search(self, query: str = "", tags: List[str] = None, 
                       author_id: str = None, date_from: str = None, 
                       date_to: str = None, min_score: int = None,
                       sort_by: str = "relevance", limit: int = 50) -> List[Post]:
        """Advanced search with multiple filters"""
        posts = self.db.get_posts(limit=1000)
        
        # Apply text search
        if query:
            posts = [p for p in posts if self._matches_text_search(p, query)]
        
        # Apply tag filters
        if tags:
            posts = [p for p in posts if any(tag in p.tags for tag in tags)]
        
        # Apply author filter
        if author_id:
            posts = [p for p in posts if p.author_id == author_id]
        
        # Apply date filters
        if date_from:
            from datetime import datetime
            cutoff_date = datetime.fromisoformat(date_from)
            posts = [p for p in posts if datetime.fromisoformat(p.created_at) >= cutoff_date]
        
        if date_to:
            from datetime import datetime
            cutoff_date = datetime.fromisoformat(date_to)
            posts = [p for p in posts if datetime.fromisoformat(p.created_at) <= cutoff_date]
        
        # Apply score filter
        if min_score is not None:
            posts = [p for p in posts if p.score >= min_score]
        
        # Sort results
        if sort_by == "relevance" and query:
            posts.sort(key=lambda p: self._calculate_relevance_score(p, query.lower()), reverse=True)
        elif sort_by == "date":
            posts.sort(key=lambda p: p.created_at, reverse=True)
        elif sort_by == "score":
            posts.sort(key=lambda p: p.score, reverse=True)
        elif sort_by == "comments":
            posts.sort(key=lambda p: p.comments_count, reverse=True)
        
        return posts[:limit]
    
    def _matches_text_search(self, post: Post, query: str) -> bool:
        """Check if post matches text search query"""
        query_lower = query.lower()
        return (query_lower in post.title.lower() or 
                query_lower in post.content.lower() or
                any(query_lower in tag.lower() for tag in post.tags))
    
    def get_search_suggestions(self, partial_query: str) -> List[str]:
        """Get search suggestions based on partial query"""
        posts = self.db.get_posts(limit=1000)
        suggestions = set()
        
        partial_lower = partial_query.lower()
        
        # Get suggestions from titles
        for post in posts:
            words = post.title.lower().split()
            for word in words:
                if word.startswith(partial_lower) and len(word) > len(partial_lower):
                    suggestions.add(word)
        
        # Get suggestions from tags
        all_tags = self.get_all_tags()
        for tag in all_tags:
            if tag.lower().startswith(partial_lower):
                suggestions.add(tag)
        
        return sorted(list(suggestions))[:10]
    
    def get_advanced_filters(self) -> Dict[str, Any]:
        """Get available filter options"""
        posts = self.db.get_posts(limit=1000)
        users = self.db._load_data(self.db.users_file)
        
        # Get all unique tags
        all_tags = self.get_all_tags()
        
        # Get all authors
        authors = []
        for user in users:
            user_posts = [p for p in posts if p.author_id == user['user_id']]
            if user_posts:
                authors.append({
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'name': user['name'],
                    'posts_count': len(user_posts)
                })
        
        # Sort authors by post count
        authors.sort(key=lambda x: x['posts_count'], reverse=True)
        
        return {
            'available_tags': all_tags,
            'available_authors': authors,
            'sort_options': [
                {'value': 'relevance', 'label': 'Relevance'},
                {'value': 'date', 'label': 'Date (Newest)'},
                {'value': 'score', 'label': 'Score (Highest)'},
                {'value': 'comments', 'label': 'Comments (Most)'}
            ]
        }
    
    def get_trending_posts(self, limit: int = 10) -> List[Post]:
        """Get trending posts (high score and recent activity)"""
        posts = self.db.get_posts(limit=100)  # Get recent posts
        
        # Calculate trending score based on score and recency
        now = datetime.now()
        trending_posts = []
        
        for post in posts:
            post_date = datetime.fromisoformat(post.created_at)
            days_old = (now - post_date).days
            
            # Trending score: (upvotes - downvotes) / (days_old + 1)
            trending_score = post.score / (days_old + 1)
            trending_posts.append((trending_score, post))
        
        # Sort by trending score
        trending_posts.sort(key=lambda x: x[0], reverse=True)
        
        return [post for _, post in trending_posts[:limit]]
    
    def get_popular_tags(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get popular tags with usage counts"""
        posts = self.db.get_posts(limit=1000)
        tag_counts = {}
        
        for post in posts:
            for tag in post.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by count
        popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [{"tag": tag, "count": count} for tag, count in popular_tags[:limit]]
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags used in posts"""
        posts = self.db.get_posts(limit=1000)
        tags = set()
        
        for post in posts:
            for tag in post.tags:
                tags.add(tag.lower().strip())
        
        return sorted(list(tags))
    
    def get_courses_from_transcript(self) -> List[Dict[str, Any]]:
        """Get courses from the transcript data"""
        try:
            import json
            from config.constants import COURSES_FILE
            
            with open(COURSES_FILE, 'r') as f:
                courses_data = json.load(f)
            
            courses = []
            for program in courses_data.get('programs', []):
                for semester in program.get('semesters', []):
                    for course in semester.get('courses', []):
                        courses.append({
                            'code': course.get('code', ''),
                            'name': course.get('name', ''),
                            'credit_hours': course.get('credit_hours', ''),
                            'semester': semester.get('number', 0),
                            'program': program.get('name', ''),
                            'program_code': program.get('code', '')
                        })
            
            return courses
        except Exception as e:
            print(f"Error loading courses: {e}")
            return []
    
    def get_elective_courses(self) -> List[Dict[str, Any]]:
        """Get elective courses from the elective_courses.txt file"""
        try:
            with open('elective_courses.txt', 'r') as f:
                course_names = [line.strip() for line in f.readlines() if line.strip()]
            
            courses = []
            for i, course_name in enumerate(course_names, 1):
                courses.append({
                    'code': f"EL{i:03d}",  # Generate course codes like EL001, EL002, etc.
                    'name': course_name,
                    'credit_hours': '3+0',  # Default credit hours for electives
                    'semester': 0,  # Elective courses don't have a specific semester
                    'program': 'Elective',
                    'program_code': 'EL'
                })
            
            return courses
        except Exception as e:
            print(f"Error loading elective courses: {e}")
            return []
    
    def get_posts_by_course(self, course_code: str, limit: int = 50) -> List[Post]:
        """Get all posts for a specific course"""
        return self.db.get_posts(limit=limit, course_code=course_code)
    
    def get_course_stats(self, course_code: str) -> Dict[str, Any]:
        """Get statistics for a specific course"""
        posts = self.get_posts_by_course(course_code)
        
        if not posts:
            return {"course_code": course_code, "count": 0, "total_score": 0, "avg_score": 0}
        
        total_score = sum(post.score for post in posts)
        avg_score = total_score / len(posts)
        
        # Get course info
        courses = self.get_courses_from_transcript()
        course_info = next((c for c in courses if c['code'] == course_code), {})
        
        return {
            "course_code": course_code,
            "course_name": course_info.get('name', 'Unknown Course'),
            "semester": course_info.get('semester', 0),
            "program": course_info.get('program', 'Unknown Program'),
            "count": len(posts),
            "total_score": total_score,
            "avg_score": avg_score,
            "recent_posts": posts[:5]  # Last 5 posts for this course
        }
    
    def get_available_courses(self) -> List[Dict[str, Any]]:
        """Get all available elective courses with post counts"""
        courses = self.get_elective_courses()
        course_stats = []
        
        for course in courses:
            posts = self.get_posts_by_course(course['code'])
            course_stats.append({
                'code': course['code'],
                'name': course['name'],
                'semester': course['semester'],
                'program': course['program'],
                'posts_count': len(posts),
                'recent_activity': len([p for p in posts if self._is_recent_post(p)])
            })
        
        # Sort by posts count (most active first)
        course_stats.sort(key=lambda x: x['posts_count'], reverse=True)
        return course_stats
    
    def _is_recent_post(self, post: Post, days: int = 7) -> bool:
        """Check if post is recent (within specified days)"""
        from datetime import datetime, timedelta
        post_date = datetime.fromisoformat(post.created_at)
        cutoff_date = datetime.now() - timedelta(days=days)
        return post_date > cutoff_date
    
    def get_posts_by_tag(self, tag: str, limit: int = 50) -> List[Post]:
        """Get all posts with a specific tag"""
        return self.db.get_posts(limit=limit, tag=tag)
    
    def search_tags(self, query: str) -> List[str]:
        """Search for tags matching a query"""
        all_tags = self.get_all_tags()
        query_lower = query.lower()
        
        matching_tags = [tag for tag in all_tags if query_lower in tag.lower()]
        return matching_tags[:20]  # Limit results
    
    def get_tag_suggestions(self, partial_tag: str) -> List[str]:
        """Get tag suggestions based on partial input"""
        all_tags = self.get_all_tags()
        partial_lower = partial_tag.lower()
        
        suggestions = [tag for tag in all_tags if tag.lower().startswith(partial_lower)]
        return suggestions[:10]  # Limit suggestions
    
    def merge_tags(self, old_tag: str, new_tag: str) -> bool:
        """Merge two tags (rename all posts with old_tag to use new_tag)"""
        posts = self.get_posts_by_tag(old_tag)
        
        for post in posts:
            # Replace old tag with new tag
            post.tags = [new_tag if tag.lower() == old_tag.lower() else tag for tag in post.tags]
            self.update_post(post)
        
        return True
    
    def get_tag_stats(self, tag: str) -> Dict[str, Any]:
        """Get statistics for a specific tag"""
        posts = self.get_posts_by_tag(tag)
        
        if not posts:
            return {"tag": tag, "count": 0, "total_score": 0, "avg_score": 0}
        
        total_score = sum(post.score for post in posts)
        avg_score = total_score / len(posts)
        
        return {
            "tag": tag,
            "count": len(posts),
            "total_score": total_score,
            "avg_score": avg_score,
            "recent_posts": posts[:5]  # Last 5 posts with this tag
        }
    
    # Comment operations
    def create_comment(self, post_id: str, content: str, author_id: str, 
                      parent_id: str = None) -> Optional[Comment]:
        """Create a new comment"""
        comment_id = str(uuid.uuid4())
        comment = Comment(
            comment_id=comment_id,
            post_id=post_id,
            content=content,
            author_id=author_id,
            parent_id=parent_id
        )
        
        if self.db.create_comment(comment):
            return comment
        return None
    
    def get_comments(self, post_id: str) -> List[Comment]:
        """Get comments for a post"""
        return self.db.get_comments(post_id)
    
    def get_comment(self, comment_id: str) -> Optional[Comment]:
        """Get comment by ID"""
        return self.db.get_comment(comment_id)
    
    def update_comment(self, comment: Comment) -> bool:
        """Update comment"""
        comment.updated_at = datetime.now().isoformat()
        return self.db.update_comment(comment)
    
    def delete_comment(self, comment_id: str, user_id: str) -> bool:
        """Delete comment (only by author)"""
        comment = self.db.get_comment(comment_id)
        if comment and comment.author_id == user_id:
            return self.db.delete_comment(comment_id)
        return False
    
    def get_nested_comments(self, post_id: str) -> List[Dict[str, Any]]:
        """Get comments with nested structure"""
        comments = self.get_comments(post_id)
        
        # Separate top-level comments and replies
        top_level = [c for c in comments if c.parent_id is None]
        replies = {c.parent_id: [] for c in comments if c.parent_id is not None}
        
        for comment in comments:
            if comment.parent_id is not None:
                replies[comment.parent_id].append(comment)
        
        # Build nested structure
        nested_comments = []
        for comment in top_level:
            comment_dict = {
                'comment': comment,
                'replies': replies.get(comment.comment_id, [])
            }
            nested_comments.append(comment_dict)
        
        return nested_comments
    
    # Vote operations
    def vote(self, user_id: str, target_type: str, target_id: str, 
             vote_type: str) -> bool:
        """Vote on a post or comment"""
        vote_id = str(uuid.uuid4())
        vote = Vote(
            vote_id=vote_id,
            user_id=user_id,
            target_type=target_type,
            target_id=target_id,
            vote_type=vote_type
        )
        
        return self.db.create_vote(vote)
    
    def get_user_vote(self, user_id: str, target_type: str, target_id: str) -> Optional[Vote]:
        """Get user's vote on a target"""
        return self.db.get_user_vote(user_id, target_type, target_id)
    
    def remove_vote(self, user_id: str, target_type: str, target_id: str) -> bool:
        """Remove user's vote"""
        votes = self.db._load_data(self.db.votes_file)
        
        for i, vote_data in enumerate(votes):
            if (vote_data['user_id'] == user_id and 
                vote_data['target_type'] == target_type and 
                vote_data['target_id'] == target_id):
                del votes[i]
                self.db._save_data(self.db.votes_file, votes)
                self.db._update_vote_counts(target_type, target_id)
                return True
        
        return False
    
    # Statistics and analytics
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        user = self.get_user(user_id)
        if not user:
            return {}
        
        posts = self.db.get_posts(author_id=user_id)
        total_score = sum(post.score for post in posts)
        
        return {
            'user': user,
            'posts_count': len(posts),
            'comments_count': user.comments_count,
            'total_score': total_score,
            'reputation': user.reputation,
            'recent_posts': posts[:5]  # Last 5 posts
        }
    
    def get_post_stats(self, post_id: str) -> Dict[str, Any]:
        """Get post statistics"""
        post = self.get_post(post_id)
        if not post:
            return {}
        
        comments = self.get_comments(post_id)
        author = self.get_user(post.author_id)
        
        return {
            'post': post,
            'author': author,
            'comments_count': len(comments),
            'score': post.score,
            'engagement_rate': len(comments) / max(1, (datetime.now() - datetime.fromisoformat(post.created_at)).days)
        }
    
    def get_platform_stats(self) -> Dict[str, Any]:
        """Get platform-wide statistics"""
        posts = self.db.get_posts(limit=1000)
        users = self.db._load_data(self.db.users_file)
        comments = self.db._load_data(self.db.comments_file)
        votes = self.db._load_data(self.db.votes_file)
        
        total_posts = len([p for p in posts if not p.is_deleted])
        total_users = len(users)
        total_comments = len([c for c in comments if not c.get('is_deleted', False)])
        total_votes = len(votes)
        
        # Calculate engagement metrics
        total_upvotes = sum(post.upvotes for post in posts)
        total_downvotes = sum(post.downvotes for post in posts)
        net_score = total_upvotes - total_downvotes
        
        # Calculate average engagement
        total_score = sum(post.score for post in posts)
        avg_score = total_score / max(1, total_posts)
        
        # Recent activity (last 7 days)
        recent_activity = self._get_recent_activity(posts, days=7)
        
        # User engagement
        active_users = self._get_active_users(users, days=30)
        
        return {
            'total_posts': total_posts,
            'total_users': total_users,
            'total_comments': total_comments,
            'total_votes': total_votes,
            'total_upvotes': total_upvotes,
            'total_downvotes': total_downvotes,
            'net_score': net_score,
            'average_score': avg_score,
            'popular_tags': self.get_popular_tags(10),
            'recent_activity': recent_activity,
            'active_users': active_users,
            'engagement_rate': self._calculate_engagement_rate(posts, users)
        }
    
    def _get_recent_activity(self, posts: List[Post], days: int = 7) -> Dict[str, Any]:
        """Get recent activity statistics"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_posts = [p for p in posts if datetime.fromisoformat(p.created_at) > cutoff_date]
        
        return {
            'posts_last_7_days': len(recent_posts),
            'avg_posts_per_day': len(recent_posts) / days,
            'most_active_day': self._get_most_active_day(recent_posts)
        }
    
    def _get_active_users(self, users: List[Dict], days: int = 30) -> int:
        """Get number of active users in the last N days"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        active_count = 0
        
        for user in users:
            user_date = datetime.fromisoformat(user.get('created_at', '2020-01-01'))
            if user_date > cutoff_date:
                active_count += 1
        
        return active_count
    
    def _calculate_engagement_rate(self, posts: List[Post], users: List[Dict]) -> float:
        """Calculate platform engagement rate"""
        if not users:
            return 0.0
        
        total_interactions = sum(post.upvotes + post.downvotes + post.comments_count for post in posts)
        total_users = len(users)
        
        return total_interactions / max(1, total_users)
    
    def _get_most_active_day(self, posts: List[Post]) -> str:
        """Get the most active day of the week"""
        from datetime import datetime
        from collections import Counter
        
        days = [datetime.fromisoformat(post.created_at).strftime('%A') for post in posts]
        day_counts = Counter(days)
        
        return max(day_counts, key=day_counts.get) if day_counts else "No activity"
    
    def get_trending_analytics(self, limit: int = 10) -> Dict[str, Any]:
        """Get trending content analytics"""
        trending_posts = self.get_trending_posts(limit)
        
        # Analyze trending patterns
        trending_tags = []
        for post in trending_posts:
            trending_tags.extend(post.tags)
        
        from collections import Counter
        tag_frequency = Counter(trending_tags)
        
        return {
            'trending_posts': trending_posts,
            'trending_tags': dict(tag_frequency.most_common(5)),
            'avg_trending_score': sum(post.score for post in trending_posts) / len(trending_posts) if trending_posts else 0
        }
    
    def get_user_engagement_patterns(self, user_id: str) -> Dict[str, Any]:
        """Get user engagement patterns"""
        user_posts = self.db.get_posts(author_id=user_id)
        user_comments = self.db._load_data(self.db.comments_file)
        user_comments = [c for c in user_comments if c['author_id'] == user_id]
        
        # Calculate patterns
        post_times = [datetime.fromisoformat(post.created_at).hour for post in user_posts]
        comment_times = [datetime.fromisoformat(comment['created_at']).hour for comment in user_comments]
        
        from collections import Counter
        post_hour_dist = Counter(post_times)
        comment_hour_dist = Counter(comment_times)
        
        return {
            'most_active_hour_posts': max(post_hour_dist, key=post_hour_dist.get) if post_hour_dist else 0,
            'most_active_hour_comments': max(comment_hour_dist, key=comment_hour_dist.get) if comment_hour_dist else 0,
            'total_posts': len(user_posts),
            'total_comments': len(user_comments),
            'avg_post_score': sum(post.score for post in user_posts) / len(user_posts) if user_posts else 0
        }
    
    def get_content_analytics(self) -> Dict[str, Any]:
        """Get content analysis and insights"""
        posts = self.db.get_posts(limit=1000)
        
        # Content length analysis
        content_lengths = [len(post.content) for post in posts]
        avg_content_length = sum(content_lengths) / len(content_lengths) if content_lengths else 0
        
        # Tag diversity
        all_tags = []
        for post in posts:
            all_tags.extend(post.tags)
        
        unique_tags = len(set(all_tags))
        avg_tags_per_post = len(all_tags) / len(posts) if posts else 0
        
        # Engagement by content length
        short_posts = [p for p in posts if len(p.content) < 100]
        medium_posts = [p for p in posts if 100 <= len(p.content) < 500]
        long_posts = [p for p in posts if len(p.content) >= 500]
        
        return {
            'avg_content_length': avg_content_length,
            'unique_tags': unique_tags,
            'avg_tags_per_post': avg_tags_per_post,
            'short_posts_count': len(short_posts),
            'medium_posts_count': len(medium_posts),
            'long_posts_count': len(long_posts),
            'short_posts_avg_score': sum(p.score for p in short_posts) / len(short_posts) if short_posts else 0,
            'medium_posts_avg_score': sum(p.score for p in medium_posts) / len(medium_posts) if medium_posts else 0,
            'long_posts_avg_score': sum(p.score for p in long_posts) / len(long_posts) if long_posts else 0
        }
