"""
Data models for PeerHub - Peer Discussion Hub
Handles User, Post, Comment, and Vote data structures
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import uuid


class User:
    """User model for PeerHub"""
    
    def __init__(self, user_id: str, username: str, name: str, email: str = "", 
                 created_at: str = None, profile_pic: str = ""):
        self.user_id = user_id
        self.username = username
        self.name = name
        self.email = email
        self.created_at = created_at or datetime.now().isoformat()
        self.profile_pic = profile_pic
        self.reputation = 0
        self.posts_count = 0
        self.comments_count = 0
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'username': self.username,
            'name': self.name,
            'email': self.email,
            'created_at': self.created_at,
            'profile_pic': self.profile_pic,
            'reputation': self.reputation,
            'posts_count': self.posts_count,
            'comments_count': self.comments_count
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        user = cls(
            user_id=data['user_id'],
            username=data['username'],
            name=data['name'],
            email=data.get('email', ''),
            created_at=data.get('created_at'),
            profile_pic=data.get('profile_pic', '')
        )
        user.reputation = data.get('reputation', 0)
        user.posts_count = data.get('posts_count', 0)
        user.comments_count = data.get('comments_count', 0)
        return user


class Post:
    """Post model for PeerHub discussions"""
    
    def __init__(self, post_id: str, title: str, content: str, author_id: str, 
                 tags: List[str] = None, file_link: str = "", created_at: str = None,
                 updated_at: str = None, upvotes: int = 0, downvotes: int = 0,
                 comments_count: int = 0, is_pinned: bool = False, course_code: str = None,
                 course_name: str = None, semester: int = None):
        self.post_id = post_id
        self.title = title
        self.content = content
        self.author_id = author_id
        self.tags = tags or []
        self.file_link = file_link
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
        self.upvotes = upvotes
        self.downvotes = downvotes
        self.comments_count = comments_count
        self.is_pinned = is_pinned
        self.is_deleted = False
        self.course_code = course_code
        self.course_name = course_name
        self.semester = semester
    
    def to_dict(self):
        return {
            'post_id': self.post_id,
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'tags': self.tags,
            'file_link': self.file_link,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'upvotes': self.upvotes,
            'downvotes': self.downvotes,
            'comments_count': self.comments_count,
            'is_pinned': self.is_pinned,
            'is_deleted': self.is_deleted,
            'course_code': self.course_code,
            'course_name': self.course_name,
            'semester': self.semester
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        post = cls(
            post_id=data['post_id'],
            title=data['title'],
            content=data['content'],
            author_id=data['author_id'],
            tags=data.get('tags', []),
            file_link=data.get('file_link', ''),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            upvotes=data.get('upvotes', 0),
            downvotes=data.get('downvotes', 0),
            comments_count=data.get('comments_count', 0),
            is_pinned=data.get('is_pinned', False),
            course_code=data.get('course_code'),
            course_name=data.get('course_name'),
            semester=data.get('semester')
        )
        post.is_deleted = data.get('is_deleted', False)
        return post
    
    @property
    def score(self):
        return self.upvotes - self.downvotes


class Comment:
    """Comment model for PeerHub discussions"""
    
    def __init__(self, comment_id: str, post_id: str, content: str, author_id: str,
                 parent_id: str = None, created_at: str = None, updated_at: str = None,
                 upvotes: int = 0, downvotes: int = 0, is_deleted: bool = False):
        self.comment_id = comment_id
        self.post_id = post_id
        self.content = content
        self.author_id = author_id
        self.parent_id = parent_id  # For nested replies
        self.created_at = created_at or datetime.now().isoformat()
        self.updated_at = updated_at or datetime.now().isoformat()
        self.upvotes = upvotes
        self.downvotes = downvotes
        self.is_deleted = is_deleted
    
    def to_dict(self):
        return {
            'comment_id': self.comment_id,
            'post_id': self.post_id,
            'content': self.content,
            'author_id': self.author_id,
            'parent_id': self.parent_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'upvotes': self.upvotes,
            'downvotes': self.downvotes,
            'is_deleted': self.is_deleted
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        comment = cls(
            comment_id=data['comment_id'],
            post_id=data['post_id'],
            content=data['content'],
            author_id=data['author_id'],
            parent_id=data.get('parent_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            upvotes=data.get('upvotes', 0),
            downvotes=data.get('downvotes', 0)
        )
        comment.is_deleted = data.get('is_deleted', False)
        return comment
    
    @property
    def score(self):
        return self.upvotes - self.downvotes


class Vote:
    """Vote model for posts and comments"""
    
    def __init__(self, vote_id: str, user_id: str, target_type: str, target_id: str,
                 vote_type: str, created_at: str = None):  # vote_type: 'upvote' or 'downvote'
        self.vote_id = vote_id
        self.user_id = user_id
        self.target_type = target_type  # 'post' or 'comment'
        self.target_id = target_id
        self.vote_type = vote_type
        self.created_at = created_at or datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'vote_id': self.vote_id,
            'user_id': self.user_id,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'vote_type': self.vote_type,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            vote_id=data['vote_id'],
            user_id=data['user_id'],
            target_type=data['target_type'],
            target_id=data['target_id'],
            vote_type=data['vote_type'],
            created_at=data.get('created_at')
        )


class PeerHubDatabase:
    """Database manager for PeerHub using JSON files"""
    
    def __init__(self, data_dir: str = "peerhub_data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.posts_file = os.path.join(data_dir, "posts.json")
        self.comments_file = os.path.join(data_dir, "comments.json")
        self.votes_file = os.path.join(data_dir, "votes.json")
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize empty files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize empty JSON files if they don't exist"""
        files = [self.users_file, self.posts_file, self.comments_file, self.votes_file]
        for file_path in files:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump([], f)
    
    def _load_data(self, file_path: str) -> List[dict]:
        """Load data from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_data(self, file_path: str, data: List[dict]):
        """Save data to JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    # User operations
    def create_user(self, user: User) -> bool:
        """Create a new user"""
        users = self._load_data(self.users_file)
        if any(u['user_id'] == user.user_id for u in users):
            return False
        users.append(user.to_dict())
        self._save_data(self.users_file, users)
        return True
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        users = self._load_data(self.users_file)
        for user_data in users:
            if user_data['user_id'] == user_id:
                return User.from_dict(user_data)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        users = self._load_data(self.users_file)
        for user_data in users:
            if user_data['username'] == username:
                return User.from_dict(user_data)
        return None
    
    def update_user(self, user: User) -> bool:
        """Update user information"""
        users = self._load_data(self.users_file)
        for i, user_data in enumerate(users):
            if user_data['user_id'] == user.user_id:
                users[i] = user.to_dict()
                self._save_data(self.users_file, users)
                return True
        return False
    
    # Post operations
    def create_post(self, post: Post) -> bool:
        """Create a new post"""
        posts = self._load_data(self.posts_file)
        posts.append(post.to_dict())
        self._save_data(self.posts_file, posts)
        
        # Update user's post count
        user = self.get_user(post.author_id)
        if user:
            user.posts_count += 1
            self.update_user(user)
        
        return True
    
    def get_post(self, post_id: str) -> Optional[Post]:
        """Get post by ID"""
        posts = self._load_data(self.posts_file)
        for post_data in posts:
            if post_data['post_id'] == post_id and not post_data.get('is_deleted', False):
                return Post.from_dict(post_data)
        return None
    
    def get_posts(self, limit: int = 50, offset: int = 0, tag: str = None, 
                  author_id: str = None, course_code: str = None, sort_by: str = "created_at") -> List[Post]:
        """Get posts with filtering and sorting"""
        posts = self._load_data(self.posts_file)
        
        # Filter out deleted posts
        posts = [p for p in posts if not p.get('is_deleted', False)]
        
        # Apply filters
        if tag:
            posts = [p for p in posts if tag in p.get('tags', [])]
        if author_id:
            posts = [p for p in posts if p['author_id'] == author_id]
        if course_code:
            posts = [p for p in posts if p.get('course_code') == course_code]
        
        # Sort posts
        if sort_by == "created_at":
            posts.sort(key=lambda x: x['created_at'], reverse=True)
        elif sort_by == "score":
            posts.sort(key=lambda x: x['upvotes'] - x['downvotes'], reverse=True)
        elif sort_by == "comments":
            posts.sort(key=lambda x: x['comments_count'], reverse=True)
        
        # Apply pagination
        posts = posts[offset:offset + limit]
        
        return [Post.from_dict(p) for p in posts]
    
    def update_post(self, post: Post) -> bool:
        """Update post"""
        posts = self._load_data(self.posts_file)
        for i, post_data in enumerate(posts):
            if post_data['post_id'] == post.post_id:
                posts[i] = post.to_dict()
                self._save_data(self.posts_file, posts)
                return True
        return False
    
    def delete_post(self, post_id: str) -> bool:
        """Soft delete post"""
        posts = self._load_data(self.posts_file)
        for i, post_data in enumerate(posts):
            if post_data['post_id'] == post_id:
                posts[i]['is_deleted'] = True
                posts[i]['updated_at'] = datetime.now().isoformat()
                self._save_data(self.posts_file, posts)
                
                # Update user's post count
                user = self.get_user(post_data['author_id'])
                if user:
                    user.posts_count = max(0, user.posts_count - 1)
                    self.update_user(user)
                
                return True
        return False
    
    # Comment operations
    def create_comment(self, comment: Comment) -> bool:
        """Create a new comment"""
        comments = self._load_data(self.comments_file)
        comments.append(comment.to_dict())
        self._save_data(self.comments_file, comments)
        
        # Update post's comment count
        post = self.get_post(comment.post_id)
        if post:
            post.comments_count += 1
            self.update_post(post)
        
        # Update user's comment count
        user = self.get_user(comment.author_id)
        if user:
            user.comments_count += 1
            self.update_user(user)
        
        return True
    
    def get_comments(self, post_id: str) -> List[Comment]:
        """Get comments for a post (with nested structure)"""
        comments = self._load_data(self.comments_file)
        post_comments = [c for c in comments if c['post_id'] == post_id and not c.get('is_deleted', False)]
        
        # Sort by creation time
        post_comments.sort(key=lambda x: x['created_at'])
        
        return [Comment.from_dict(c) for c in post_comments]
    
    def get_comment(self, comment_id: str) -> Optional[Comment]:
        """Get comment by ID"""
        comments = self._load_data(self.comments_file)
        for comment_data in comments:
            if comment_data['comment_id'] == comment_id and not comment_data.get('is_deleted', False):
                return Comment.from_dict(comment_data)
        return None
    
    def update_comment(self, comment: Comment) -> bool:
        """Update comment"""
        comments = self._load_data(self.comments_file)
        for i, comment_data in enumerate(comments):
            if comment_data['comment_id'] == comment.comment_id:
                comments[i] = comment.to_dict()
                self._save_data(self.comments_file, comments)
                return True
        return False
    
    def delete_comment(self, comment_id: str) -> bool:
        """Soft delete comment"""
        comments = self._load_data(self.comments_file)
        for i, comment_data in enumerate(comments):
            if comment_data['comment_id'] == comment_id:
                comments[i]['is_deleted'] = True
                comments[i]['updated_at'] = datetime.now().isoformat()
                self._save_data(self.comments_file, comments)
                
                # Update post's comment count
                post = self.get_post(comment_data['post_id'])
                if post:
                    post.comments_count = max(0, post.comments_count - 1)
                    self.update_post(post)
                
                # Update user's comment count
                user = self.get_user(comment_data['author_id'])
                if user:
                    user.comments_count = max(0, user.comments_count - 1)
                    self.update_user(user)
                
                return True
        return False
    
    # Vote operations
    def create_vote(self, vote: Vote) -> bool:
        """Create a new vote"""
        votes = self._load_data(self.votes_file)
        
        # Check if user already voted on this target
        existing_vote = None
        for i, v in enumerate(votes):
            if (v['user_id'] == vote.user_id and 
                v['target_type'] == vote.target_type and 
                v['target_id'] == vote.target_id):
                existing_vote = i
                break
        
        if existing_vote is not None:
            # Update existing vote
            votes[existing_vote] = vote.to_dict()
        else:
            # Create new vote
            votes.append(vote.to_dict())
        
        self._save_data(self.votes_file, votes)
        
        # Update target's vote counts
        self._update_vote_counts(vote.target_type, vote.target_id)
        
        return True
    
    def get_user_vote(self, user_id: str, target_type: str, target_id: str) -> Optional[Vote]:
        """Get user's vote on a target"""
        votes = self._load_data(self.votes_file)
        for vote_data in votes:
            if (vote_data['user_id'] == user_id and 
                vote_data['target_type'] == target_type and 
                vote_data['target_id'] == target_id):
                return Vote.from_dict(vote_data)
        return None
    
    def _update_vote_counts(self, target_type: str, target_id: str):
        """Update vote counts for a target"""
        votes = self._load_data(self.votes_file)
        target_votes = [v for v in votes if v['target_type'] == target_type and v['target_id'] == target_id]
        
        upvotes = len([v for v in target_votes if v['vote_type'] == 'upvote'])
        downvotes = len([v for v in target_votes if v['vote_type'] == 'downvote'])
        
        if target_type == 'post':
            posts = self._load_data(self.posts_file)
            for i, post in enumerate(posts):
                if post['post_id'] == target_id:
                    posts[i]['upvotes'] = upvotes
                    posts[i]['downvotes'] = downvotes
                    self._save_data(self.posts_file, posts)
                    break
        elif target_type == 'comment':
            comments = self._load_data(self.comments_file)
            for i, comment in enumerate(comments):
                if comment['comment_id'] == target_id:
                    comments[i]['upvotes'] = upvotes
                    comments[i]['downvotes'] = downvotes
                    self._save_data(self.comments_file, comments)
                    break
