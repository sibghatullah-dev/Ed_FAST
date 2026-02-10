"""
UI Components for PeerHub - Peer Discussion Hub
Streamlit components for the discussion platform
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional
from .service import PeerHubService
from .models import User, Post, Comment


class PeerHubUI:
    """UI class for PeerHub components"""
    
    def __init__(self):
        self.service = PeerHubService()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize PeerHub session state variables"""
        if 'peerhub_current_user' not in st.session_state:
            st.session_state.peerhub_current_user = None
        if 'peerhub_selected_post' not in st.session_state:
            st.session_state.peerhub_selected_post = None
        if 'peerhub_view_mode' not in st.session_state:
            st.session_state.peerhub_view_mode = 'list'  # 'list', 'post', 'new_post'
        if 'peerhub_search_query' not in st.session_state:
            st.session_state.peerhub_search_query = ''
        if 'peerhub_selected_tag' not in st.session_state:
            st.session_state.peerhub_selected_tag = None
        if 'peerhub_selected_course' not in st.session_state:
            st.session_state.peerhub_selected_course = None
        if 'peerhub_sort_by' not in st.session_state:
            st.session_state.peerhub_sort_by = 'created_at'
    
    def render_peerhub_main(self):
        """Render the main PeerHub interface"""
        st.markdown("""
        <style>
        .peerhub-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 2rem;
            color: white;
            margin-bottom: 2rem;
            text-align: center;
        }
        .peerhub-title {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }
        .peerhub-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        .post-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid #E5E7EB;
            transition: transform 0.2s ease;
        }
        .post-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
        }
        .post-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #1F2937;
            margin-bottom: 0.5rem;
        }
        .post-content {
            color: #6B7280;
            margin-bottom: 1rem;
            line-height: 1.6;
        }
        .post-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9rem;
            color: #9CA3AF;
        }
        .post-tags {
            margin-top: 0.5rem;
        }
        .tag {
            display: inline-block;
            background: #E0E7FF;
            color: #3730A3;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            margin-right: 0.5rem;
            margin-bottom: 0.5rem;
        }
        .vote-section {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .vote-btn {
            background: #F3F4F6;
            border: 1px solid #D1D5DB;
            border-radius: 6px;
            padding: 0.25rem 0.5rem;
            cursor: pointer;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }
        .vote-btn:hover {
            background: #E5E7EB;
        }
        .vote-btn.upvoted {
            background: #10B981;
            color: white;
            border-color: #059669;
        }
        .vote-btn.downvoted {
            background: #EF4444;
            color: white;
            border-color: #DC2626;
        }
        .vote-btn.upvoted:hover {
            background: #059669;
        }
        .vote-btn.downvoted:hover {
            background: #DC2626;
        }
        .vote-count {
            font-weight: 600;
            color: #374151;
        }
        .comment-section {
            background: #F9FAFB;
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1rem;
        }
        .comment {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 0.5rem;
            border-left: 3px solid #E0E7FF;
        }
        .comment-author {
            font-weight: 600;
            color: #374151;
            font-size: 0.9rem;
        }
        .comment-content {
            color: #6B7280;
            margin-top: 0.25rem;
        }
        .comment-meta {
            font-size: 0.8rem;
            color: #9CA3AF;
            margin-top: 0.5rem;
        }
        .new-post-form {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid #E5E7EB;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-label {
            font-weight: 600;
            color: #374151;
            margin-bottom: 0.5rem;
            display: block;
        }
        .form-input {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #D1D5DB;
            border-radius: 8px;
            font-size: 1rem;
        }
        .form-textarea {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #D1D5DB;
            border-radius: 8px;
            font-size: 1rem;
            min-height: 120px;
            resize: vertical;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        .btn-primary:hover {
            transform: translateY(-1px);
        }
        .btn-secondary {
            background: #F3F4F6;
            color: #374151;
            border: 1px solid #D1D5DB;
            border-radius: 8px;
            padding: 0.75rem 1.5rem;
            font-weight: 600;
            cursor: pointer;
        }
        .stats-card {
            background: white;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .stats-number {
            font-size: 2rem;
            font-weight: 800;
            color: #667eea;
        }
        .stats-label {
            color: #6B7280;
            font-size: 0.9rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Header
        st.markdown("""
        <div class="peerhub-header">
            <div class="peerhub-title">💬 PeerHub</div>
            <div class="peerhub-subtitle">Connect, Discuss, Learn Together</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Check if user is logged in
        if not st.session_state.get('user_logged_in', False):
            self._render_login_prompt()
            return
        
        # Initialize current user
        self._initialize_current_user()
        
        # Course selection section
        self._render_course_selection()
        
        # Main content based on view mode
        if st.session_state.peerhub_view_mode == 'list':
            # Only show general posts list if no course is selected
            if not st.session_state.peerhub_selected_course:
                self._render_posts_list()
        elif st.session_state.peerhub_view_mode == 'post':
            self._render_single_post()
        elif st.session_state.peerhub_view_mode == 'new_post':
            self._render_new_post_form()
        elif st.session_state.peerhub_view_mode == 'edit_post':
            self._render_edit_post_form()
    
    def _render_login_prompt(self):
        """Render login prompt for non-authenticated users"""
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: #F9FAFB; border-radius: 12px;">
            <h3 style="color: #374151; margin-bottom: 1rem;">🔐 Authentication Required</h3>
            <p style="color: #6B7280; margin-bottom: 2rem;">Please log in to access PeerHub discussions</p>
            <p style="color: #9CA3AF;">Use the login form in the sidebar to get started</p>
        </div>
        """, unsafe_allow_html=True)
    
    def _initialize_current_user(self):
        """Initialize current user for PeerHub"""
        if not st.session_state.peerhub_current_user:
            username = st.session_state.get('username', '')
            if username:
                user = self.service.get_user_by_username(username)
                if not user:
                    # Create user if doesn't exist in PeerHub
                    user = self.service.create_user(
                        username=username,
                        name=username,  # Use username as name for now
                        email=""
                    )
                st.session_state.peerhub_current_user = user
    
    def _render_course_selection(self):
        """Render elective course selection interface"""
        st.markdown("### 📚 Elective Courses")
        st.markdown("Select an elective course to view and participate in discussions:")
        
        # Get available courses
        courses = self.service.get_available_courses()
        
        if not courses:
            st.warning("No elective courses available. Please check the elective_courses.txt file.")
            return
        
        # Display courses in a grid layout
        cols = st.columns(3)
        for i, course in enumerate(courses):
            with cols[i % 3]:
                # Create a card for each course
                with st.container():
                    st.markdown(f"""
                    <div style="
                        border: 1px solid #ddd;
                        border-radius: 8px;
                        padding: 1rem;
                        margin: 0.5rem 0;
                        background: {'#f0f8ff' if st.session_state.peerhub_selected_course == course['code'] else 'white'};
                        cursor: pointer;
                        transition: all 0.3s ease;
                    ">
                        <h4 style="margin: 0 0 0.5rem 0; color: #333;">{course['name']}</h4>
                        <p style="margin: 0; color: #666; font-size: 0.9rem;">{course['code']}</p>
                        <p style="margin: 0.5rem 0 0 0; color: #888; font-size: 0.8rem;">
                            Posts: {course['posts_count']} | Recent: {course['recent_activity']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Add click functionality
                    if st.button(f"Select {course['name']}", key=f"select_{course['code']}", use_container_width=True):
                        st.session_state.peerhub_selected_course = course['code']
                        st.rerun()
        
        # Show selected course info and chat interface
        if st.session_state.peerhub_selected_course:
            course_info = next((c for c in courses if c['code'] == st.session_state.peerhub_selected_course), None)
            if course_info:
                st.success(f"📖 **Selected:** {course_info['name']} ({course_info['code']})")
                
                # Show course stats
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Posts", course_info['posts_count'])
                with col2:
                    st.metric("Recent Activity", course_info['recent_activity'])
                with col3:
                    if st.button("📊 Detailed Stats", use_container_width=True):
                        self._render_course_stats()
                with col4:
                    if st.button("🔄 View All Courses", use_container_width=True):
                        st.session_state.peerhub_selected_course = None
                        st.rerun()
                
                st.markdown("---")
                
                # Show chat interface for the selected course
                self._render_course_chat_interface(course_info)
        
        st.markdown("---")
    
    def _render_course_stats(self):
        """Render course statistics"""
        if not st.session_state.peerhub_selected_course:
            return
        
        stats = self.service.get_course_stats(st.session_state.peerhub_selected_course)
        
        st.markdown("### 📊 Course Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Posts", stats['count'])
        with col2:
            st.metric("Total Score", stats['total_score'])
        with col3:
            st.metric("Average Score", f"{stats['avg_score']:.1f}")
        with col4:
            st.metric("Semester", stats['semester'])
        
        st.markdown(f"**Course:** {stats['course_name']} ({stats['course_code']})")
        st.markdown(f"**Program:** {stats['program']}")
        
        if stats['recent_posts']:
            st.markdown("#### Recent Posts")
            for post in stats['recent_posts']:
                with st.expander(f"{post.title} (Score: {post.score})"):
                    st.write(post.content[:200] + "..." if len(post.content) > 200 else post.content)
                    st.write(f"**Author:** {post.author_id} | **Created:** {post.created_at}")
        
        if st.button("← Back to Course Selection"):
            st.session_state.peerhub_view_mode = 'list'
            st.rerun()
    
    def _render_course_chat_interface(self, course_info):
        """Render chat interface for selected course"""
        st.markdown(f"### 💬 {course_info['name']} Discussions")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📝 View Posts", "✍️ Create Post", "🔍 Search Posts"])
        
        with tab1:
            self._render_course_posts(course_info)
        
        with tab2:
            self._render_course_new_post_form(course_info)
        
        with tab3:
            self._render_course_search(course_info)
    
    def _render_course_posts(self, course_info):
        """Render posts for the selected course"""
        posts = self.service.get_posts_by_course(course_info['code'])
        
        if not posts:
            st.info(f"No discussions yet for {course_info['name']}. Be the first to start a discussion!")
            return
        
        # Sort options
        col1, col2 = st.columns([1, 3])
        with col1:
            sort_by = st.selectbox("Sort by", ["created_at", "score", "comments"], key="course_sort")
        
        # Sort posts
        if sort_by == "created_at":
            posts.sort(key=lambda x: x.created_at, reverse=True)
        elif sort_by == "score":
            posts.sort(key=lambda x: x.score, reverse=True)
        elif sort_by == "comments":
            posts.sort(key=lambda x: x.comments_count, reverse=True)
        
        # Display posts
        for post in posts:
            self._render_course_post_card(post)
    
    def _render_course_post_card(self, post):
        """Render a post card for course discussions"""
        author = self.service.get_user(post.author_id)
        author_name = author.name if author else "Unknown User"
        
        # Format time
        post_time = datetime.fromisoformat(post.created_at)
        time_str = post_time.strftime("%b %d, %Y at %I:%M %p")
        
        # Create expandable post card
        with st.expander(f"💬 {post.title} by {author_name} (Score: {post.score})", expanded=False):
            st.write(post.content)
            
            # Tags
            if post.tags:
                st.write("**Tags:**", ", ".join(post.tags))
            
            # Meta information
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.caption(f"Posted by **{author_name}** on {time_str}")
            with col2:
                st.caption(f"💬 {post.comments_count} comments")
            with col3:
                st.caption(f"⭐ Score: {post.score}")
            
            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("👁️ View", key=f"view_course_{post.post_id}"):
                    st.session_state.peerhub_selected_post = post.post_id
                    st.session_state.peerhub_view_mode = 'post'
                    st.rerun()
            
            with col2:
                if st.button(f"👍 {post.upvotes}", key=f"upvote_course_{post.post_id}"):
                    self._handle_vote(post.post_id, 'post', 'upvote')
                    st.rerun()
            
            with col3:
                if st.button(f"👎 {post.downvotes}", key=f"downvote_course_{post.post_id}"):
                    self._handle_vote(post.post_id, 'post', 'downvote')
                    st.rerun()
            
            # Author-only actions
            is_author = (st.session_state.peerhub_current_user and 
                        st.session_state.peerhub_current_user.user_id == post.author_id)
            
            if is_author:
                with col4:
                    if st.button("✏️ Edit", key=f"edit_course_{post.post_id}"):
                        st.session_state.peerhub_editing_post = post.post_id
                        st.session_state.peerhub_view_mode = 'edit_post'
                        st.rerun()
    
    def _render_course_new_post_form(self, course_info):
        """Render new post form for course"""
        st.markdown(f"### ✍️ Create New Discussion for {course_info['name']}")
        
        with st.form("course_new_post_form"):
            title = st.text_input("Title", placeholder="Enter a descriptive title...")
            content = st.text_area("Content", placeholder="Share your thoughts, questions, or ideas about this course...", height=200)
            
            # Enhanced tag input with suggestions
            tags_input = st.text_input("Tags (comma-separated)", placeholder="e.g., assignment, exam, project, question")
            
            file_link = st.text_input("File Link (optional)", placeholder="Link to relevant files or resources...")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit = st.form_submit_button("📤 Post Discussion", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if submit:
                if title and content:
                    tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                    
                    post = self.service.create_post(
                        title=title,
                        content=content,
                        author_id=st.session_state.peerhub_current_user.user_id,
                        tags=tags,
                        file_link=file_link,
                        course_code=course_info['code'],
                        course_name=course_info['name'],
                        semester=course_info['semester']
                    )
                    
                    if post:
                        st.success("Discussion posted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to create post. Please try again.")
                else:
                    st.warning("Please fill in the title and content fields.")
    
    def _render_course_search(self, course_info):
        """Render search interface for course posts"""
        st.markdown(f"### 🔍 Search Discussions in {course_info['name']}")
        
        search_query = st.text_input("Search posts", placeholder="Enter keywords to search...")
        
        if search_query:
            posts = self.service.search_posts(search_query)
            # Filter by course
            course_posts = [p for p in posts if p.course_code == course_info['code']]
            
            if course_posts:
                st.write(f"Found {len(course_posts)} posts matching '{search_query}':")
                for post in course_posts:
                    self._render_course_post_card(post)
            else:
                st.info(f"No posts found matching '{search_query}' in {course_info['name']}")
        else:
            st.info("Enter a search term to find relevant discussions.")
    
    def _render_posts_list(self):
        """Render the posts list view"""
        # Filters and controls
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            search_query = st.text_input("🔍 Search discussions", 
                                       value=st.session_state.peerhub_search_query,
                                       placeholder="Search by title, content, or tags...")
            if search_query != st.session_state.peerhub_search_query:
                st.session_state.peerhub_search_query = search_query
                st.rerun()
        
        with col2:
            sort_by = st.selectbox("Sort by", 
                                 ["created_at", "score", "comments"],
                                 index=["created_at", "score", "comments"].index(st.session_state.peerhub_sort_by))
            if sort_by != st.session_state.peerhub_sort_by:
                st.session_state.peerhub_sort_by = sort_by
                st.rerun()
        
        with col3:
            if st.button("📝 New Post", use_container_width=True):
                st.session_state.peerhub_view_mode = 'new_post'
                st.rerun()
        
        with col4:
            if st.button("📊 Stats", use_container_width=True):
                self._render_platform_stats()
                return
        
        # Add management buttons
        col5, col6 = st.columns([1, 1])
        
        with col5:
            if st.button("🏷️ Manage Tags", use_container_width=True):
                self._render_tag_management()
                return
        
        with col6:
            if st.button("👤 My Profile", use_container_width=True):
                self._render_user_profile()
                return
        
        # Advanced Search and Filtering
        self._render_advanced_search_filters()
        
        # Get and display posts using advanced search
        if st.session_state.peerhub_advanced_search['query'] or any(st.session_state.peerhub_advanced_search.values()):
            # Use advanced search
            posts = self.service.advanced_search(
                query=st.session_state.peerhub_advanced_search['query'],
                tags=st.session_state.peerhub_advanced_search['tags'],
                author_id=st.session_state.peerhub_advanced_search['author_id'],
                date_from=st.session_state.peerhub_advanced_search['date_from'],
                date_to=st.session_state.peerhub_advanced_search['date_to'],
                min_score=st.session_state.peerhub_advanced_search['min_score'],
                sort_by=st.session_state.peerhub_advanced_search['sort_by']
            )
            # Filter by course if selected
            if st.session_state.peerhub_selected_course:
                posts = [p for p in posts if p.course_code == st.session_state.peerhub_selected_course]
        elif st.session_state.peerhub_search_query:
            # Use basic search
            posts = self.service.search_posts(st.session_state.peerhub_search_query)
            # Filter by course if selected
            if st.session_state.peerhub_selected_course:
                posts = [p for p in posts if p.course_code == st.session_state.peerhub_selected_course]
        else:
            # Use default posts with course filtering
            posts = self.service.get_posts(
                tag=st.session_state.peerhub_selected_tag,
                course_code=st.session_state.peerhub_selected_course,
                sort_by=st.session_state.peerhub_sort_by
            )
        
        if not posts:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; color: #6B7280;">
                <h3>No discussions found</h3>
                <p>Be the first to start a discussion!</p>
            </div>
            """, unsafe_allow_html=True)
            return
        
        # Display posts
        for post in posts:
            self._render_post_card(post)
    
    def _render_post_card(self, post: Post):
        """Render a single post card"""
        author = self.service.get_user(post.author_id)
        author_name = author.name if author else "Unknown User"
        
        # Format time
        post_time = datetime.fromisoformat(post.created_at)
        time_str = post_time.strftime("%b %d, %Y at %I:%M %p")
        
        # Course info display
        if post.course_code:
            course_display = post.course_code
            if post.course_name:
                course_display += f" - {post.course_name}"
            if post.semester:
                course_display += f" (Sem {post.semester})"
            
            st.markdown(f"""
            <div style='background: #E0F2FE; color: #0277BD; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem; margin-bottom: 0.5rem; display: inline-block;'>
                {course_display}
            </div>
            """, unsafe_allow_html=True)
        
        # Post content using Streamlit components instead of raw HTML
        with st.container():
            st.markdown(f"### {post.title}")
            st.write(post.content[:200] + ('...' if len(post.content) > 200 else ''))
            
            # Tags
            if post.tags:
                tag_cols = st.columns(min(len(post.tags), 5))
                for i, tag in enumerate(post.tags[:5]):
                    with tag_cols[i]:
                        st.markdown(f"`{tag}`")
            
            # Meta information
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"**{author_name}** • {time_str} • {post.comments_count} comments")
            with col2:
                st.caption(f"Score: {post.score}")
        
        st.markdown("---")
        
        # Action buttons
        is_author = (st.session_state.peerhub_current_user and 
                    st.session_state.peerhub_current_user.user_id == post.author_id)
        
        if is_author:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        else:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 0, 0])
        
        with col1:
            if st.button("👁️ View", key=f"view_{post.post_id}"):
                st.session_state.peerhub_selected_post = post.post_id
                st.session_state.peerhub_view_mode = 'post'
                st.rerun()
        
        with col2:
            # Get user's vote status for visual feedback
            user_vote = None
            if st.session_state.peerhub_current_user:
                user_vote = self.service.get_user_vote(
                    st.session_state.peerhub_current_user.user_id, 
                    'post', 
                    post.post_id
                )
            
            if st.button(f"👍 {post.upvotes}", key=f"upvote_{post.post_id}", 
                        help="Upvote this post"):
                self._handle_vote(post.post_id, 'post', 'upvote')
                st.rerun()
        
        with col3:
            if st.button(f"👎 {post.downvotes}", key=f"downvote_{post.post_id}",
                        help="Downvote this post"):
                self._handle_vote(post.post_id, 'post', 'downvote')
                st.rerun()
        
        # Author-only actions
        if is_author:
            with col4:
                if st.button("✏️ Edit", key=f"edit_{post.post_id}", 
                           help="Edit this post"):
                    st.session_state.peerhub_editing_post = post.post_id
                    st.session_state.peerhub_view_mode = 'edit_post'
                    st.rerun()
            
            with col5:
                if st.button("🗑️ Delete", key=f"delete_{post.post_id}", 
                           help="Delete this post"):
                    if self.service.delete_post(post.post_id, st.session_state.peerhub_current_user.user_id):
                        st.success("Post deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete post")
        
        st.markdown("---")
    
    def _render_single_post(self):
        """Render single post view with comments"""
        if not st.session_state.peerhub_selected_post:
            st.session_state.peerhub_view_mode = 'list'
            st.rerun()
            return
        
        post = self.service.get_post(st.session_state.peerhub_selected_post)
        if not post:
            st.error("Post not found")
            st.session_state.peerhub_view_mode = 'list'
            st.rerun()
            return
        
        author = self.service.get_user(post.author_id)
        author_name = author.name if author else "Unknown User"
        
        # Back button
        if st.button("← Back to Discussions"):
            st.session_state.peerhub_view_mode = 'list'
            st.session_state.peerhub_selected_post = None
            st.rerun()
        
        # Post content
        post_time = datetime.fromisoformat(post.created_at)
        time_str = post_time.strftime("%b %d, %Y at %I:%M %p")
        
        # Course info display
        if post.course_code:
            course_display = f"📚 **Course:** {post.course_code}"
            if post.course_name:
                course_display += f" - {post.course_name}"
            if post.semester:
                course_display += f" (Semester {post.semester})"
            
            st.info(course_display)
        
        # Post content using Streamlit components
        st.markdown(f"## {post.title}")
        st.write(post.content)
        
        # Tags
        if post.tags:
            st.write("**Tags:**", ", ".join(post.tags))
        
        # Meta information
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(f"Posted by **{author_name}** on {time_str}")
        with col2:
            st.caption(f"Score: {post.score}")
        
        st.markdown("---")
        
        # Vote buttons
        col1, col2, col3 = st.columns([1, 1, 8])
        
        # Get user's vote status for visual feedback
        user_vote = None
        if st.session_state.peerhub_current_user:
            user_vote = self.service.get_user_vote(
                st.session_state.peerhub_current_user.user_id, 
                'post', 
                post.post_id
            )
        
        with col1:
            if st.button(f"👍 {post.upvotes}", key=f"post_upvote_{post.post_id}",
                        help="Upvote this post"):
                self._handle_vote(post.post_id, 'post', 'upvote')
                st.rerun()
        with col2:
            if st.button(f"👎 {post.downvotes}", key=f"post_downvote_{post.post_id}",
                        help="Downvote this post"):
                self._handle_vote(post.post_id, 'post', 'downvote')
                st.rerun()
        
        # Comments section
        st.markdown("### 💬 Comments")
        
        # Add comment form
        with st.expander("Add a comment", expanded=False):
            comment_content = st.text_area("Your comment", height=100)
            if st.button("Post Comment"):
                if comment_content.strip():
                    self.service.create_comment(
                        post_id=post.post_id,
                        content=comment_content,
                        author_id=st.session_state.peerhub_current_user.user_id
                    )
                    st.success("Comment posted!")
                    st.rerun()
                else:
                    st.warning("Please enter a comment")
        
        # Display comments
        comments = self.service.get_nested_comments(post.post_id)
        if not comments:
            st.markdown("*No comments yet. Be the first to comment!*")
        else:
            for comment_group in comments:
                self._render_comment_group(comment_group)
    
    def _render_comment_group(self, comment_group: Dict[str, Any]):
        """Render a comment and its replies"""
        comment = comment_group['comment']
        replies = comment_group['replies']
        
        author = self.service.get_user(comment.author_id)
        author_name = author.name if author else "Unknown User"
        
        comment_time = datetime.fromisoformat(comment.created_at)
        time_str = comment_time.strftime("%b %d, %Y at %I:%M %p")
        
        st.markdown(f"""
        <div class="comment">
            <div class="comment-author">{author_name}</div>
            <div class="comment-content">{comment.content}</div>
            <div class="comment-meta">
                {time_str} • Score: {comment.score}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Comment vote buttons
        col1, col2 = st.columns([1, 9])
        
        # Get user's vote status for this comment
        user_vote = None
        if st.session_state.peerhub_current_user:
            user_vote = self.service.get_user_vote(
                st.session_state.peerhub_current_user.user_id, 
                'comment', 
                comment.comment_id
            )
        
        with col1:
            if st.button(f"👍 {comment.upvotes}", key=f"comment_upvote_{comment.comment_id}",
                        help="Upvote this comment"):
                self._handle_vote(comment.comment_id, 'comment', 'upvote')
                st.rerun()
        with col2:
            if st.button(f"👎 {comment.downvotes}", key=f"comment_downvote_{comment.comment_id}",
                        help="Downvote this comment"):
                self._handle_vote(comment.comment_id, 'comment', 'downvote')
                st.rerun()
        
        # Render replies
        if replies:
            st.markdown('<div style="margin-left: 2rem;">', unsafe_allow_html=True)
            for reply in replies:
                self._render_comment_group({'comment': reply, 'replies': []})
            st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_new_post_form(self):
        """Render new post form"""
        st.markdown("### 📝 Create New Discussion")
        
        with st.form("new_post_form"):
            title = st.text_input("Title", placeholder="Enter a descriptive title...")
            content = st.text_area("Content", placeholder="Share your thoughts, questions, or ideas...", height=200)
            
            # Course selection
            courses = self.service.get_available_courses()
            course_options = [""] + [f"{course['code']} - {course['name']} (Sem {course['semester']})" 
                                   for course in courses]
            
            selected_course_display = st.selectbox(
                "Course (optional)",
                course_options,
                help="Select a course if this discussion is related to a specific course"
            )
            
            selected_course_code = None
            selected_course_name = None
            selected_semester = None
            
            if selected_course_display:
                selected_course_code = selected_course_display.split(' - ')[0]
                course_info = next((c for c in courses if c['code'] == selected_course_code), None)
                if course_info:
                    selected_course_name = course_info['name']
                    selected_semester = course_info['semester']
            
            # Enhanced tag input with suggestions
            tags_input = st.text_input("Tags (comma-separated)", placeholder="e.g., programming, career, study-tips")
            
            # Show tag suggestions
            if tags_input:
                current_tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                if current_tags:
                    last_tag = current_tags[-1]
                    if last_tag:
                        suggestions = self.service.get_tag_suggestions(last_tag)
                        if suggestions:
                            st.write("**Tag suggestions:**")
                            suggestion_cols = st.columns(min(len(suggestions), 5))
                            for i, suggestion in enumerate(suggestions[:5]):
                                with suggestion_cols[i]:
                                    if st.button(suggestion, key=f"suggestion_{suggestion}"):
                                        # Add suggestion to tags
                                        new_tags = current_tags[:-1] + [suggestion]
                                        st.session_state.suggested_tags = ", ".join(new_tags)
                                        st.rerun()
            
            file_link = st.text_input("File Link (optional)", placeholder="Link to relevant files or resources...")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit = st.form_submit_button("📤 Post Discussion", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if cancel:
                st.session_state.peerhub_view_mode = 'list'
                st.rerun()
            
            if submit:
                if title and content:
                    tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                    
                    post = self.service.create_post(
                        title=title,
                        content=content,
                        author_id=st.session_state.peerhub_current_user.user_id,
                        tags=tags,
                        file_link=file_link,
                        course_code=selected_course_code,
                        course_name=selected_course_name,
                        semester=selected_semester
                    )
                    
                    if post:
                        st.success("Discussion posted successfully!")
                        st.session_state.peerhub_view_mode = 'list'
                        st.rerun()
                    else:
                        st.error("Failed to create post. Please try again.")
                else:
                    st.warning("Please fill in the title and content fields.")
    
    def _render_edit_post_form(self):
        """Render edit post form"""
        if not st.session_state.get('peerhub_editing_post'):
            st.error("No post selected for editing")
            st.session_state.peerhub_view_mode = 'list'
            st.rerun()
            return
        
        post = self.service.get_post(st.session_state.peerhub_editing_post)
        if not post:
            st.error("Post not found")
            st.session_state.peerhub_view_mode = 'list'
            st.rerun()
            return
        
        # Check if user is the author
        if not (st.session_state.peerhub_current_user and 
                st.session_state.peerhub_current_user.user_id == post.author_id):
            st.error("You can only edit your own posts")
            st.session_state.peerhub_view_mode = 'list'
            st.rerun()
            return
        
        st.markdown("### ✏️ Edit Discussion")
        
        with st.form("edit_post_form"):
            title = st.text_input("Title", value=post.title, placeholder="Enter a descriptive title...")
            content = st.text_area("Content", value=post.content, placeholder="Share your thoughts, questions, or ideas...", height=200)
            
            # Course selection
            courses = self.service.get_available_courses()
            course_options = [""] + [f"{course['code']} - {course['name']} (Sem {course['semester']})" 
                                   for course in courses]
            
            # Find current course selection
            current_course_display = ""
            if post.course_code:
                current_course_display = f"{post.course_code} - {post.course_name or 'Unknown Course'}"
                if post.semester:
                    current_course_display += f" (Sem {post.semester})"
            
            selected_course_display = st.selectbox(
                "Course (optional)",
                course_options,
                index=course_options.index(current_course_display) if current_course_display in course_options else 0,
                help="Select a course if this discussion is related to a specific course"
            )
            
            selected_course_code = None
            selected_course_name = None
            selected_semester = None
            
            if selected_course_display:
                selected_course_code = selected_course_display.split(' - ')[0]
                course_info = next((c for c in courses if c['code'] == selected_course_code), None)
                if course_info:
                    selected_course_name = course_info['name']
                    selected_semester = course_info['semester']
            
            tags_input = st.text_input("Tags (comma-separated)", value=", ".join(post.tags), placeholder="e.g., programming, career, study-tips")
            file_link = st.text_input("File Link (optional)", value=post.file_link, placeholder="Link to relevant files or resources...")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                submit = st.form_submit_button("💾 Save Changes", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if cancel:
                st.session_state.peerhub_view_mode = 'list'
                st.session_state.peerhub_editing_post = None
                st.rerun()
            
            if submit:
                if title and content:
                    tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
                    
                    # Update post
                    post.title = title
                    post.content = content
                    post.tags = tags
                    post.file_link = file_link
                    post.course_code = selected_course_code
                    post.course_name = selected_course_name
                    post.semester = selected_semester
                    
                    if self.service.update_post(post):
                        st.success("Post updated successfully!")
                        st.session_state.peerhub_view_mode = 'list'
                        st.session_state.peerhub_editing_post = None
                        st.rerun()
                    else:
                        st.error("Failed to update post. Please try again.")
                else:
                    st.warning("Please fill in the title and content fields.")
    
    def _render_platform_stats(self):
        """Render comprehensive platform statistics"""
        stats = self.service.get_platform_stats()
        trending_analytics = self.service.get_trending_analytics(10)
        content_analytics = self.service.get_content_analytics()
        
        st.markdown("### 📊 Platform Analytics Dashboard")
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Posts", stats['total_posts'])
            st.metric("Active Users (30d)", stats['active_users'])
        with col2:
            st.metric("Total Users", stats['total_users'])
            st.metric("Total Votes", stats['total_votes'])
        with col3:
            st.metric("Total Comments", stats['total_comments'])
            st.metric("Net Score", stats['net_score'])
        with col4:
            st.metric("Avg Score", f"{stats['average_score']:.1f}")
            st.metric("Engagement Rate", f"{stats['engagement_rate']:.1f}")
        
        # Detailed analytics tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Engagement", "🔥 Trending", "📝 Content", "👥 Users"])
        
        with tab1:
            st.markdown("#### 📈 Engagement Analytics")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Upvotes", stats['total_upvotes'])
                st.metric("Total Downvotes", stats['total_downvotes'])
            with col2:
                st.metric("Posts Last 7 Days", stats['recent_activity']['posts_last_7_days'])
                st.metric("Avg Posts/Day", f"{stats['recent_activity']['avg_posts_per_day']:.1f}")
            
            st.write(f"**Most Active Day:** {stats['recent_activity']['most_active_day']}")
        
        with tab2:
            st.markdown("#### 🔥 Trending Content")
            
            if trending_analytics['trending_posts']:
                st.write(f"**Average Trending Score:** {trending_analytics['avg_trending_score']:.1f}")
                
                st.markdown("**Top Trending Posts:**")
                for i, post in enumerate(trending_analytics['trending_posts'][:5], 1):
                    st.write(f"{i}. **{post.title}** (Score: {post.score})")
                
                if trending_analytics['trending_tags']:
                    st.markdown("**Trending Tags:**")
                    for tag, count in trending_analytics['trending_tags'].items():
                        st.write(f"• **{tag}** ({count} posts)")
            else:
                st.info("No trending content yet.")
        
        with tab3:
            st.markdown("#### 📝 Content Analytics")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Avg Content Length", f"{content_analytics['avg_content_length']:.0f} chars")
                st.metric("Unique Tags", content_analytics['unique_tags'])
            with col2:
                st.metric("Avg Tags/Post", f"{content_analytics['avg_tags_per_post']:.1f}")
                st.metric("Tag Diversity", f"{content_analytics['unique_tags']/max(1, stats['total_posts']):.2f}")
            
            # Content length distribution
            st.markdown("**Content Length Distribution:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Short Posts (<100)", content_analytics['short_posts_count'])
                st.metric("Avg Score", f"{content_analytics['short_posts_avg_score']:.1f}")
            with col2:
                st.metric("Medium Posts (100-500)", content_analytics['medium_posts_count'])
                st.metric("Avg Score", f"{content_analytics['medium_posts_avg_score']:.1f}")
            with col3:
                st.metric("Long Posts (500+)", content_analytics['long_posts_count'])
                st.metric("Avg Score", f"{content_analytics['long_posts_avg_score']:.1f}")
        
        with tab4:
            st.markdown("#### 👥 User Analytics")
            
            # User engagement patterns for current user
            if st.session_state.peerhub_current_user:
                user_patterns = self.service.get_user_engagement_patterns(
                    st.session_state.peerhub_current_user.user_id
                )
                
                st.markdown("**Your Engagement Patterns:**")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Your Posts", user_patterns['total_posts'])
                    st.metric("Your Comments", user_patterns['total_comments'])
                with col2:
                    st.metric("Most Active Hour (Posts)", f"{user_patterns['most_active_hour_posts']}:00")
                    st.metric("Most Active Hour (Comments)", f"{user_patterns['most_active_hour_comments']}:00")
                
                st.metric("Your Avg Post Score", f"{user_patterns['avg_post_score']:.1f}")
            else:
                st.info("Log in to see your engagement patterns.")
        
        # Popular tags section
        if stats['popular_tags']:
            st.markdown("#### 🏷️ Popular Tags")
            tag_cols = st.columns(min(len(stats['popular_tags']), 5))
            for i, tag_info in enumerate(stats['popular_tags'][:5]):
                with tag_cols[i]:
                    st.markdown(f"""
                    <div style="text-align: center; padding: 1rem; background: #F3F4F6; border-radius: 8px; margin: 0.5rem 0;">
                        <div style="font-size: 1.5rem; font-weight: bold; color: #1F2937;">{tag_info['count']}</div>
                        <div style="font-size: 0.9rem; color: #6B7280;">{tag_info['tag']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Back button
        if st.button("← Back to Discussions"):
            st.session_state.peerhub_view_mode = 'list'
            st.rerun()
    
    def _render_tag_management(self):
        """Render tag management interface"""
        st.markdown("### 🏷️ Tag Management")
        
        # Tag statistics
        all_tags = self.service.get_all_tags()
        popular_tags = self.service.get_popular_tags(20)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 📊 Tag Statistics")
            if all_tags:
                st.write(f"**Total unique tags:** {len(all_tags)}")
                
                # Show top tags
                st.markdown("**Most Popular Tags:**")
                for i, tag_info in enumerate(popular_tags[:10], 1):
                    st.write(f"{i}. **{tag_info['tag']}** ({tag_info['count']} posts)")
            else:
                st.info("No tags found yet.")
        
        with col2:
            st.markdown("#### 🔍 Tag Search")
            search_query = st.text_input("Search tags", placeholder="Type to search for tags...")
            
            if search_query:
                matching_tags = self.service.search_tags(search_query)
                if matching_tags:
                    st.write("**Matching tags:**")
                    for tag in matching_tags:
                        tag_stats = self.service.get_tag_stats(tag)
                        st.write(f"• **{tag}** ({tag_stats['count']} posts)")
                else:
                    st.info("No matching tags found.")
        
        # Tag operations
        st.markdown("#### ⚙️ Tag Operations")
        
        tab1, tab2, tab3 = st.tabs(["🔍 Search Posts by Tag", "🔄 Merge Tags", "📈 Tag Analytics"])
        
        with tab1:
            st.markdown("**Search posts by specific tag:**")
            selected_tag = st.selectbox("Select a tag", [""] + all_tags)
            
            if selected_tag:
                posts = self.service.get_posts_by_tag(selected_tag)
                if posts:
                    st.write(f"**Found {len(posts)} posts with tag '{selected_tag}':**")
                    for post in posts:
                        with st.expander(f"{post.title} (Score: {post.score})"):
                            st.write(post.content[:200] + "..." if len(post.content) > 200 else post.content)
                            st.write(f"**Author:** {post.author_id} | **Created:** {post.created_at}")
                else:
                    st.info(f"No posts found with tag '{selected_tag}'")
        
        with tab2:
            st.markdown("**Merge two tags (rename old tag to new tag):**")
            col1, col2 = st.columns([1, 1])
            
            with col1:
                old_tag = st.selectbox("Old tag to rename", [""] + all_tags)
            with col2:
                new_tag = st.text_input("New tag name", placeholder="Enter new tag name...")
            
            if old_tag and new_tag and st.button("🔄 Merge Tags"):
                if old_tag != new_tag:
                    if self.service.merge_tags(old_tag, new_tag):
                        st.success(f"Successfully merged '{old_tag}' into '{new_tag}'")
                        st.rerun()
                    else:
                        st.error("Failed to merge tags")
                else:
                    st.warning("Old and new tags cannot be the same")
        
        with tab3:
            st.markdown("**Detailed tag analytics:**")
            selected_tag = st.selectbox("Select tag for analytics", [""] + all_tags, key="analytics_tag")
            
            if selected_tag:
                tag_stats = self.service.get_tag_stats(selected_tag)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Posts", tag_stats['count'])
                with col2:
                    st.metric("Total Score", tag_stats['total_score'])
                with col3:
                    st.metric("Avg Score", f"{tag_stats['avg_score']:.1f}")
                with col4:
                    st.metric("Tag", selected_tag)
                
                if tag_stats['recent_posts']:
                    st.markdown("**Recent posts with this tag:**")
                    for post in tag_stats['recent_posts']:
                        st.write(f"• [{post.title}]({post.post_id}) (Score: {post.score})")
        
        # Back button
        if st.button("← Back to Discussions"):
            st.session_state.peerhub_view_mode = 'list'
            st.rerun()
    
    def _render_user_profile(self):
        """Render user profile management"""
        if not st.session_state.peerhub_current_user:
            st.error("Please log in to view your profile")
            return
        
        user = st.session_state.peerhub_current_user
        user_stats = self.service.get_user_stats(user.user_id)
        
        st.markdown("### 👤 My Profile")
        
        # User information
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 📊 Your Statistics")
            st.metric("Posts", user_stats.get('posts_count', 0))
            st.metric("Comments", user_stats.get('comments_count', 0))
            st.metric("Total Score", user_stats.get('total_score', 0))
            st.metric("Reputation", user_stats.get('reputation', 0))
        
        with col2:
            st.markdown("#### ℹ️ Profile Information")
            st.write(f"**Username:** {user.username}")
            st.write(f"**Name:** {user.name}")
            st.write(f"**Email:** {user.email if user.email else 'Not provided'}")
            st.write(f"**Member since:** {user.created_at}")
        
        # User's posts
        st.markdown("#### 📝 Your Posts")
        user_posts = self.service.get_posts(author_id=user.user_id, limit=20)
        
        if user_posts:
            for post in user_posts:
                with st.expander(f"{post.title} (Score: {post.score}, {post.comments_count} comments)"):
                    st.write(post.content[:300] + "..." if len(post.content) > 300 else post.content)
                    st.write(f"**Tags:** {', '.join(post.tags)}")
                    st.write(f"**Created:** {post.created_at}")
                    
                    # Quick actions for user's posts
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col1:
                        if st.button("👁️ View", key=f"view_my_{post.post_id}"):
                            st.session_state.peerhub_selected_post = post.post_id
                            st.session_state.peerhub_view_mode = 'post'
                            st.rerun()
                    with col2:
                        if st.button("✏️ Edit", key=f"edit_my_{post.post_id}"):
                            st.session_state.peerhub_editing_post = post.post_id
                            st.session_state.peerhub_view_mode = 'edit_post'
                            st.rerun()
                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_my_{post.post_id}"):
                            if self.service.delete_post(post.post_id, user.user_id):
                                st.success("Post deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete post")
        else:
            st.info("You haven't created any posts yet.")
        
        # User's recent activity
        st.markdown("#### 📈 Recent Activity")
        recent_posts = user_stats.get('recent_posts', [])
        if recent_posts:
            st.write("**Your recent posts:**")
            for post in recent_posts[:5]:
                st.write(f"• [{post.title}]({post.post_id}) - Score: {post.score}")
        else:
            st.info("No recent activity.")
        
        # Back button
        if st.button("← Back to Discussions"):
            st.session_state.peerhub_view_mode = 'list'
            st.rerun()
    
    def _render_advanced_search_filters(self):
        """Render advanced search and filtering interface"""
        st.markdown("### 🔍 Advanced Search & Filtering")
        
        # Initialize session state for advanced search
        if 'peerhub_advanced_search' not in st.session_state:
            st.session_state.peerhub_advanced_search = {
                'query': '',
                'tags': [],
                'author_id': None,
                'date_from': None,
                'date_to': None,
                'min_score': None,
                'sort_by': 'relevance'
            }
        
        # Get available filter options
        filter_options = self.service.get_advanced_filters()
        
        # Create search interface
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Text search with suggestions
            search_query = st.text_input(
                "🔍 Search across titles, content, and tags",
                value=st.session_state.peerhub_advanced_search['query'],
                placeholder="Enter search terms...",
                key="advanced_search_query"
            )
            
            # Show search suggestions
            if search_query and len(search_query) > 2:
                suggestions = self.service.get_search_suggestions(search_query)
                if suggestions:
                    st.write("**Suggestions:**")
                    suggestion_cols = st.columns(min(len(suggestions), 5))
                    for i, suggestion in enumerate(suggestions[:5]):
                        with suggestion_cols[i]:
                            if st.button(suggestion, key=f"suggestion_{suggestion}"):
                                st.session_state.peerhub_advanced_search['query'] = suggestion
                                st.rerun()
        
        with col2:
            # Quick filter buttons
            if st.button("🔥 Trending", use_container_width=True):
                st.session_state.peerhub_advanced_search['sort_by'] = 'score'
                st.session_state.peerhub_advanced_search['min_score'] = 5
                st.rerun()
            
            if st.button("📅 Recent", use_container_width=True):
                st.session_state.peerhub_advanced_search['sort_by'] = 'date'
                st.rerun()
        
        # Advanced filters in expandable section
        with st.expander("🔧 Advanced Filters", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Tag filtering
                st.markdown("**🏷️ Filter by Tags:**")
                selected_tags = st.multiselect(
                    "Select tags",
                    filter_options['available_tags'],
                    default=st.session_state.peerhub_advanced_search['tags'],
                    key="advanced_tags"
                )
                
                # Author filtering
                st.markdown("**👤 Filter by Author:**")
                author_options = [""] + [f"{author['name']} ({author['posts_count']} posts)" 
                                       for author in filter_options['available_authors'][:10]]
                selected_author = st.selectbox(
                    "Select author",
                    author_options,
                    key="advanced_author"
                )
            
            with col2:
                # Date filtering
                st.markdown("**📅 Filter by Date:**")
                date_from = st.date_input(
                    "From date",
                    value=None,
                    key="advanced_date_from"
                )
                date_to = st.date_input(
                    "To date", 
                    value=None,
                    key="advanced_date_to"
                )
            
            with col3:
                # Score filtering
                st.markdown("**⭐ Filter by Score:**")
                min_score = st.number_input(
                    "Minimum score",
                    min_value=0,
                    value=st.session_state.peerhub_advanced_search['min_score'] or 0,
                    key="advanced_min_score"
                )
                
                # Sort options
                st.markdown("**📊 Sort by:**")
                sort_options = {opt['label']: opt['value'] for opt in filter_options['sort_options']}
                selected_sort = st.selectbox(
                    "Sort order",
                    list(sort_options.keys()),
                    index=list(sort_options.values()).index(st.session_state.peerhub_advanced_search['sort_by']),
                    key="advanced_sort"
                )
        
        # Apply filters button
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("🔍 Apply Filters", use_container_width=True):
                # Update session state with current filter values
                st.session_state.peerhub_advanced_search.update({
                    'query': search_query,
                    'tags': selected_tags,
                    'author_id': filter_options['available_authors'][author_options.index(selected_author)-1]['user_id'] if selected_author and selected_author != "" else None,
                    'date_from': date_from.isoformat() if date_from else None,
                    'date_to': date_to.isoformat() if date_to else None,
                    'min_score': min_score if min_score > 0 else None,
                    'sort_by': sort_options[selected_sort]
                })
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset Filters", use_container_width=True):
                st.session_state.peerhub_advanced_search = {
                    'query': '',
                    'tags': [],
                    'author_id': None,
                    'date_from': None,
                    'date_to': None,
                    'min_score': None,
                    'sort_by': 'relevance'
                }
                st.rerun()
        
        with col3:
            if st.button("💾 Save Search", use_container_width=True):
                st.info("Search saved! (Feature coming soon)")
        
        # Display current active filters
        active_filters = []
        if st.session_state.peerhub_advanced_search['query']:
            active_filters.append(f"Text: '{st.session_state.peerhub_advanced_search['query']}'")
        if st.session_state.peerhub_advanced_search['tags']:
            active_filters.append(f"Tags: {', '.join(st.session_state.peerhub_advanced_search['tags'])}")
        if st.session_state.peerhub_advanced_search['author_id']:
            author_name = next((a['name'] for a in filter_options['available_authors'] 
                              if a['user_id'] == st.session_state.peerhub_advanced_search['author_id']), "Unknown")
            active_filters.append(f"Author: {author_name}")
        if st.session_state.peerhub_advanced_search['min_score']:
            active_filters.append(f"Min Score: {st.session_state.peerhub_advanced_search['min_score']}")
        
        if active_filters:
            st.markdown("**Active Filters:** " + " | ".join(active_filters))
    
    def _handle_vote(self, target_id: str, target_type: str, vote_type: str):
        """Handle voting on posts or comments"""
        if not st.session_state.peerhub_current_user:
            st.warning("Please log in to vote")
            return
        
        user_id = st.session_state.peerhub_current_user.user_id
        
        # Check if user already voted
        existing_vote = self.service.get_user_vote(user_id, target_type, target_id)
        
        if existing_vote:
            if existing_vote.vote_type == vote_type:
                # Remove vote if clicking same vote type
                self.service.remove_vote(user_id, target_type, target_id)
            else:
                # Change vote type
                self.service.vote(user_id, target_type, target_id, vote_type)
        else:
            # New vote
            self.service.vote(user_id, target_type, target_id, vote_type)
