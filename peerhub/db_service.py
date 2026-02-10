"""
Database-backed PeerHub service.
Replaces JSON-based service with SQLAlchemy database operations.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy import or_, and_, func, desc, String
from sqlalchemy.exc import IntegrityError

from database.models import User, Post, Comment, Vote
from database.db_config import get_session


class PeerHubDBService:
    """Database-backed service for PeerHub operations."""
    
    def __init__(self):
        """Initialize the PeerHub service."""
        pass
    
    # ==================== User Operations ====================
    
    def create_user(self, user_id: str, username: str, name: str, email: str = "") -> Optional[User]:
        """Create a new PeerHub user profile."""
        session = get_session()
        try:
            # Check if user already exists
            existing_user = session.query(User).filter(User.id == user_id).first()
            if existing_user:
                return existing_user
            
            user = User(
                id=user_id,
                username=username,
                name=name,
                email=email
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except IntegrityError:
            session.rollback()
            return None
        finally:
            session.close()
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        session = get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        session = get_session()
        try:
            return session.query(User).filter(User.username == username).first()
        finally:
            session.close()
    
    # ==================== Post Operations ====================
    
    def create_post(self, title: str, content: str, author_id: str, tags: List[str] = None,
                   file_link: str = "", course_code: str = None, course_name: str = None,
                   semester: int = None) -> Optional[Post]:
        """Create a new post."""
        session = get_session()
        try:
            post = Post(
                title=title,
                content=content,
                author_id=author_id,
                tags=tags or [],
                file_link=file_link,
                course_code=course_code,
                course_name=course_name,
                semester=semester
            )
            session.add(post)
            session.commit()
            session.refresh(post)
            return post
        except Exception as e:
            session.rollback()
            print(f"Error creating post: {e}")
            return None
        finally:
            session.close()
    
    def get_post(self, post_id: str) -> Optional[Post]:
        """Get post by ID."""
        session = get_session()
        try:
            return session.query(Post).filter(
                Post.id == post_id,
                Post.is_deleted == False
            ).first()
        finally:
            session.close()
    
    def get_posts(self, limit: int = 50, offset: int = 0, tag: str = None,
                 author_id: str = None, course_code: str = None,
                 sort_by: str = "created_at") -> List[Post]:
        """Get posts with filtering and sorting."""
        session = get_session()
        try:
            query = session.query(Post).filter(Post.is_deleted == False)
            
            # Apply filters
            if tag:
                query = query.filter(Post.tags.contains([tag]))
            if author_id:
                query = query.filter(Post.author_id == author_id)
            if course_code:
                query = query.filter(Post.course_code == course_code)
            
            # Apply sorting
            if sort_by == "created_at":
                query = query.order_by(desc(Post.created_at))
            elif sort_by == "score":
                query = query.order_by(desc(Post.upvotes - Post.downvotes))
            elif sort_by == "comments":
                query = query.order_by(desc(Post.comments_count))
            
            # Apply pagination
            posts = query.offset(offset).limit(limit).all()
            return posts
        finally:
            session.close()
    
    def update_post(self, post: Post) -> bool:
        """Update an existing post."""
        session = get_session()
        try:
            existing_post = session.query(Post).filter(Post.id == post.id).first()
            if existing_post:
                existing_post.title = post.title
                existing_post.content = post.content
                existing_post.tags = post.tags
                existing_post.file_link = post.file_link
                existing_post.updated_at = datetime.utcnow()
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def delete_post(self, post_id: str, user_id: str) -> bool:
        """Soft delete a post."""
        session = get_session()
        try:
            post = session.query(Post).filter(Post.id == post_id).first()
            if post and post.author_id == user_id:
                post.is_deleted = True
                post.updated_at = datetime.utcnow()
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def search_posts(self, query: str, limit: int = 20, search_type: str = "all") -> List[Post]:
        """Search posts by query."""
        session = get_session()
        try:
            search_query = session.query(Post).filter(Post.is_deleted == False)
            
            query_lower = query.lower()
            
            if search_type == "title":
                search_query = search_query.filter(func.lower(Post.title).contains(query_lower))
            elif search_type == "content":
                search_query = search_query.filter(func.lower(Post.content).contains(query_lower))
            elif search_type == "tags":
                # PostgreSQL JSON contains, fallback for SQLite
                search_query = search_query.filter(
                    func.lower(func.cast(Post.tags, String)).contains(query_lower)
                )
            else:  # "all"
                search_query = search_query.filter(
                    or_(
                        func.lower(Post.title).contains(query_lower),
                        func.lower(Post.content).contains(query_lower)
                    )
                )
            
            posts = search_query.order_by(desc(Post.created_at)).limit(limit).all()
            return posts
        finally:
            session.close()
    
    def advanced_search(self, query: str = None, tags: List[str] = None, author_id: str = None,
                       date_from: datetime = None, date_to: datetime = None,
                       min_score: int = None, sort_by: str = "relevance") -> List[Post]:
        """Advanced search with multiple filters."""
        session = get_session()
        try:
            search_query = session.query(Post).filter(Post.is_deleted == False)
            
            # Text search
            if query:
                query_lower = query.lower()
                search_query = search_query.filter(
                    or_(
                        func.lower(Post.title).contains(query_lower),
                        func.lower(Post.content).contains(query_lower)
                    )
                )
            
            # Tag filter
            if tags:
                for tag in tags:
                    search_query = search_query.filter(Post.tags.contains([tag]))
            
            # Author filter
            if author_id:
                search_query = search_query.filter(Post.author_id == author_id)
            
            # Date range filter
            if date_from:
                search_query = search_query.filter(Post.created_at >= date_from)
            if date_to:
                search_query = search_query.filter(Post.created_at <= date_to)
            
            # Score filter
            if min_score is not None:
                search_query = search_query.filter((Post.upvotes - Post.downvotes) >= min_score)
            
            # Sorting
            if sort_by == "date":
                search_query = search_query.order_by(desc(Post.created_at))
            elif sort_by == "score":
                search_query = search_query.order_by(desc(Post.upvotes - Post.downvotes))
            elif sort_by == "comments":
                search_query = search_query.order_by(desc(Post.comments_count))
            else:  # relevance
                search_query = search_query.order_by(desc(Post.created_at))
            
            return search_query.limit(100).all()
        finally:
            session.close()
    
    def get_trending_posts(self, limit: int = 10, days: int = 7) -> List[Post]:
        """Get trending posts based on recent engagement."""
        session = get_session()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            posts = session.query(Post).filter(
                Post.is_deleted == False,
                Post.created_at >= cutoff_date
            ).order_by(
                desc((Post.upvotes - Post.downvotes) + Post.comments_count)
            ).limit(limit).all()
            return posts
        finally:
            session.close()
    
    def get_popular_tags(self, limit: int = 20) -> List[Dict]:
        """Get popular tags with counts."""
        session = get_session()
        try:
            # This is a simplified version - for production, consider a dedicated tags table
            posts = session.query(Post).filter(Post.is_deleted == False).all()
            tag_counts = {}
            
            for post in posts:
                if post.tags:
                    for tag in post.tags:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            return [{"tag": tag, "count": count} for tag, count in sorted_tags[:limit]]
        finally:
            session.close()
    
    # ==================== Comment Operations ====================
    
    def create_comment(self, post_id: str, content: str, author_id: str,
                      parent_id: str = None) -> Optional[Comment]:
        """Create a new comment."""
        session = get_session()
        try:
            comment = Comment(
                post_id=post_id,
                content=content,
                author_id=author_id,
                parent_id=parent_id
            )
            session.add(comment)
            
            # Update post comment count
            post = session.query(Post).filter(Post.id == post_id).first()
            if post:
                post.comments_count += 1
            
            session.commit()
            session.refresh(comment)
            return comment
        except Exception as e:
            session.rollback()
            print(f"Error creating comment: {e}")
            return None
        finally:
            session.close()
    
    def get_comments(self, post_id: str) -> List[Comment]:
        """Get all comments for a post."""
        session = get_session()
        try:
            return session.query(Comment).filter(
                Comment.post_id == post_id,
                Comment.is_deleted == False
            ).order_by(Comment.created_at).all()
        finally:
            session.close()
    
    def get_comment(self, comment_id: str) -> Optional[Comment]:
        """Get a specific comment."""
        session = get_session()
        try:
            return session.query(Comment).filter(
                Comment.id == comment_id,
                Comment.is_deleted == False
            ).first()
        finally:
            session.close()
    
    def update_comment(self, comment: Comment) -> bool:
        """Update a comment."""
        session = get_session()
        try:
            existing_comment = session.query(Comment).filter(Comment.id == comment.id).first()
            if existing_comment:
                existing_comment.content = comment.content
                existing_comment.updated_at = datetime.utcnow()
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def delete_comment(self, comment_id: str, user_id: str) -> bool:
        """Soft delete a comment."""
        session = get_session()
        try:
            comment = session.query(Comment).filter(Comment.id == comment_id).first()
            if comment and comment.author_id == user_id:
                comment.is_deleted = True
                comment.updated_at = datetime.utcnow()
                
                # Update post comment count
                post = session.query(Post).filter(Post.id == comment.post_id).first()
                if post and post.comments_count > 0:
                    post.comments_count -= 1
                
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    # ==================== Vote Operations ====================
    
    def vote(self, user_id: str, target_type: str, target_id: str, vote_type: str) -> bool:
        """Cast or update a vote."""
        session = get_session()
        try:
            # Check for existing vote
            if target_type == "post":
                existing_vote = session.query(Vote).filter(
                    Vote.user_id == user_id,
                    Vote.post_id == target_id
                ).first()
            else:
                existing_vote = session.query(Vote).filter(
                    Vote.user_id == user_id,
                    Vote.comment_id == target_id
                ).first()
            
            if existing_vote:
                # Update existing vote
                old_vote_type = existing_vote.vote_type
                existing_vote.vote_type = vote_type
                existing_vote.created_at = datetime.utcnow()
            else:
                # Create new vote
                vote = Vote(
                    user_id=user_id,
                    post_id=target_id if target_type == "post" else None,
                    comment_id=target_id if target_type == "comment" else None,
                    vote_type=vote_type
                )
                session.add(vote)
                old_vote_type = None
            
            # Update vote counts
            if target_type == "post":
                target = session.query(Post).filter(Post.id == target_id).first()
            else:
                target = session.query(Comment).filter(Comment.id == target_id).first()
            
            if target:
                # Remove old vote count
                if old_vote_type == "upvote":
                    target.upvotes = max(0, target.upvotes - 1)
                elif old_vote_type == "downvote":
                    target.downvotes = max(0, target.downvotes - 1)
                
                # Add new vote count
                if vote_type == "upvote":
                    target.upvotes += 1
                elif vote_type == "downvote":
                    target.downvotes += 1
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error voting: {e}")
            return False
        finally:
            session.close()
    
    def get_user_vote(self, user_id: str, target_type: str, target_id: str) -> Optional[Vote]:
        """Get user's vote on a target."""
        session = get_session()
        try:
            if target_type == "post":
                return session.query(Vote).filter(
                    Vote.user_id == user_id,
                    Vote.post_id == target_id
                ).first()
            else:
                return session.query(Vote).filter(
                    Vote.user_id == user_id,
                    Vote.comment_id == target_id
                ).first()
        finally:
            session.close()
    
    def remove_vote(self, user_id: str, target_type: str, target_id: str) -> bool:
        """Remove a user's vote."""
        session = get_session()
        try:
            if target_type == "post":
                vote = session.query(Vote).filter(
                    Vote.user_id == user_id,
                    Vote.post_id == target_id
                ).first()
            else:
                vote = session.query(Vote).filter(
                    Vote.user_id == user_id,
                    Vote.comment_id == target_id
                ).first()
            
            if vote:
                # Update vote counts
                if target_type == "post":
                    target = session.query(Post).filter(Post.id == target_id).first()
                else:
                    target = session.query(Comment).filter(Comment.id == target_id).first()
                
                if target:
                    if vote.vote_type == "upvote":
                        target.upvotes = max(0, target.upvotes - 1)
                    elif vote.vote_type == "downvote":
                        target.downvotes = max(0, target.downvotes - 1)
                
                session.delete(vote)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    # ==================== Analytics Operations ====================
    
    def get_platform_stats(self) -> Dict:
        """Get platform-wide statistics."""
        session = get_session()
        try:
            total_posts = session.query(Post).filter(Post.is_deleted == False).count()
            total_users = session.query(User).count()
            total_comments = session.query(Comment).filter(Comment.is_deleted == False).count()
            total_votes = session.query(Vote).count()
            
            # Calculate engagement metrics
            upvotes = session.query(func.sum(Post.upvotes)).scalar() or 0
            downvotes = session.query(func.sum(Post.downvotes)).scalar() or 0
            
            return {
                'total_posts': total_posts,
                'total_users': total_users,
                'total_comments': total_comments,
                'total_votes': total_votes,
                'total_upvotes': upvotes,
                'total_downvotes': downvotes,
                'net_score': upvotes - downvotes
            }
        finally:
            session.close()
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get user statistics."""
        session = get_session()
        try:
            posts_count = session.query(Post).filter(
                Post.author_id == user_id,
                Post.is_deleted == False
            ).count()
            
            comments_count = session.query(Comment).filter(
                Comment.author_id == user_id,
                Comment.is_deleted == False
            ).count()
            
            total_upvotes = session.query(func.sum(Post.upvotes)).filter(
                Post.author_id == user_id,
                Post.is_deleted == False
            ).scalar() or 0
            
            return {
                'posts_count': posts_count,
                'comments_count': comments_count,
                'total_upvotes': total_upvotes,
                'reputation': total_upvotes  # Simplified reputation
            }
        finally:
            session.close()

