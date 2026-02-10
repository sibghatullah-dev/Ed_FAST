"""
Data Migration Script - JSON to Database
Migrates all existing JSON data to the new database structure.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_config import init_database
from database.models import User, Post, Comment, Vote
from auth.db_user_service import hash_password


class DataMigrator:
    """Handles migration of JSON data to database."""
    
    def __init__(self, db_type='sqlite'):
        """Initialize the migrator."""
        self.db_config = init_database(db_type=db_type, create_tables=True)
        self.migrated_users = {}  # Maps old username to new user_id
        self.migration_log = []
    
    def log(self, message: str):
        """Log migration progress."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        self.migration_log.append(log_message)
    
    def migrate_users(self, users_file='users.json'):
        """Migrate users from JSON to database."""
        self.log("=" * 60)
        self.log("Starting User Migration")
        self.log("=" * 60)
        
        if not os.path.exists(users_file):
            self.log(f"WARNING: {users_file} not found. Creating empty file.")
            with open(users_file, 'w') as f:
                json.dump([], f)
            return
        
        with open(users_file, 'r') as f:
            users_data = json.load(f)
        
        session = self.db_config.get_db_session()
        try:
            for user_data in users_data:
                try:
                    # Check if user already exists
                    existing_user = session.query(User).filter(
                        User.username == user_data['username']
                    ).first()
                    
                    if existing_user:
                        self.log(f"User '{user_data['username']}' already exists, skipping...")
                        self.migrated_users[user_data['username']] = existing_user.id
                        continue
                    
                    # Create new user
                    user = User(
                        username=user_data['username'],
                        password=hash_password(user_data.get('password', '')),
                        name=user_data.get('name', user_data['username']),
                        email=user_data.get('email', ''),
                        transcript_file=user_data.get('transcript_file', ''),
                        transcript_data=user_data.get('transcript_data', {}),
                        description=user_data.get('description', ''),
                        resume_data=user_data.get('resume_data', {})
                    )
                    
                    session.add(user)
                    session.flush()  # Get the user ID
                    
                    self.migrated_users[user_data['username']] = user.id
                    self.log(f"✓ Migrated user: {user_data['username']} (ID: {user.id})")
                    
                except Exception as e:
                    self.log(f"✗ Error migrating user {user_data.get('username', 'unknown')}: {str(e)}")
            
            session.commit()
            self.log(f"\nUser Migration Complete: {len(self.migrated_users)} users migrated")
            
        except Exception as e:
            session.rollback()
            self.log(f"CRITICAL ERROR in user migration: {str(e)}")
            raise
        finally:
            session.close()
    
    def migrate_peerhub_users(self, peerhub_users_file='peerhub_data/users.json'):
        """Migrate PeerHub users (merge with main users if needed)."""
        self.log("\n" + "=" * 60)
        self.log("Starting PeerHub Users Migration")
        self.log("=" * 60)
        
        if not os.path.exists(peerhub_users_file):
            self.log(f"WARNING: {peerhub_users_file} not found, skipping...")
            return
        
        with open(peerhub_users_file, 'r') as f:
            peerhub_users = json.load(f)
        
        session = self.db_config.get_db_session()
        try:
            for user_data in peerhub_users:
                try:
                    # Map PeerHub user_id to migrated user or create mapping
                    user_id = user_data['user_id']
                    username = user_data['username']
                    
                    # Check if this username exists in migrated users
                    if username in self.migrated_users:
                        # Update mapping
                        old_id = user_id
                        new_id = self.migrated_users[username]
                        self.migrated_users[old_id] = new_id  # Map old PeerHub ID to new ID
                        self.log(f"✓ Mapped PeerHub user {username}: {old_id} -> {new_id}")
                    else:
                        # PeerHub-only user, might not exist in main users.json
                        existing_user = session.query(User).filter(User.username == username).first()
                        if existing_user:
                            self.migrated_users[user_id] = existing_user.id
                            self.log(f"✓ Found existing user {username} for PeerHub ID {user_id}")
                        else:
                            self.log(f"⚠ PeerHub user {username} ({user_id}) not in main users, will need manual mapping")
                            self.migrated_users[user_id] = user_id  # Keep original ID for now
                            
                except Exception as e:
                    self.log(f"✗ Error processing PeerHub user {user_data.get('username', 'unknown')}: {str(e)}")
            
            self.log(f"\nPeerHub Users Processing Complete")
            
        except Exception as e:
            self.log(f"ERROR in PeerHub users migration: {str(e)}")
        finally:
            session.close()
    
    def migrate_posts(self, posts_file='peerhub_data/posts.json'):
        """Migrate posts from JSON to database."""
        self.log("\n" + "=" * 60)
        self.log("Starting Posts Migration")
        self.log("=" * 60)
        
        if not os.path.exists(posts_file):
            self.log(f"WARNING: {posts_file} not found, skipping...")
            return
        
        with open(posts_file, 'r') as f:
            posts_data = json.load(f)
        
        session = self.db_config.get_db_session()
        post_id_mapping = {}
        
        try:
            for post_data in posts_data:
                try:
                    old_post_id = post_data['post_id']
                    author_id = self.migrated_users.get(post_data['author_id'], post_data['author_id'])
                    
                    # Check if post already exists
                    existing_post = session.query(Post).filter(Post.id == old_post_id).first()
                    if existing_post:
                        self.log(f"Post '{old_post_id}' already exists, skipping...")
                        post_id_mapping[old_post_id] = existing_post.id
                        continue
                    
                    post = Post(
                        id=old_post_id,  # Preserve original ID
                        title=post_data['title'],
                        content=post_data['content'],
                        author_id=author_id,
                        tags=post_data.get('tags', []),
                        file_link=post_data.get('file_link', ''),
                        course_code=post_data.get('course_code'),
                        course_name=post_data.get('course_name'),
                        semester=post_data.get('semester'),
                        upvotes=post_data.get('upvotes', 0),
                        downvotes=post_data.get('downvotes', 0),
                        comments_count=post_data.get('comments_count', 0),
                        is_pinned=post_data.get('is_pinned', False),
                        is_deleted=post_data.get('is_deleted', False),
                        created_at=datetime.fromisoformat(post_data['created_at']),
                        updated_at=datetime.fromisoformat(post_data.get('updated_at', post_data['created_at']))
                    )
                    
                    session.add(post)
                    post_id_mapping[old_post_id] = old_post_id
                    self.log(f"✓ Migrated post: {post_data['title'][:50]}...")
                    
                except Exception as e:
                    self.log(f"✗ Error migrating post {post_data.get('post_id', 'unknown')}: {str(e)}")
            
            session.commit()
            self.log(f"\nPosts Migration Complete: {len(post_id_mapping)} posts migrated")
            self.post_id_mapping = post_id_mapping
            
        except Exception as e:
            session.rollback()
            self.log(f"CRITICAL ERROR in posts migration: {str(e)}")
            raise
        finally:
            session.close()
    
    def migrate_comments(self, comments_file='peerhub_data/comments.json'):
        """Migrate comments from JSON to database."""
        self.log("\n" + "=" * 60)
        self.log("Starting Comments Migration")
        self.log("=" * 60)
        
        if not os.path.exists(comments_file):
            self.log(f"WARNING: {comments_file} not found, skipping...")
            return
        
        with open(comments_file, 'r') as f:
            comments_data = json.load(f)
        
        session = self.db_config.get_db_session()
        
        try:
            for comment_data in comments_data:
                try:
                    author_id = self.migrated_users.get(comment_data['author_id'], comment_data['author_id'])
                    
                    # Check if comment already exists
                    existing_comment = session.query(Comment).filter(
                        Comment.id == comment_data['comment_id']
                    ).first()
                    
                    if existing_comment:
                        self.log(f"Comment '{comment_data['comment_id']}' already exists, skipping...")
                        continue
                    
                    comment = Comment(
                        id=comment_data['comment_id'],  # Preserve original ID
                        post_id=comment_data['post_id'],
                        author_id=author_id,
                        content=comment_data['content'],
                        parent_id=comment_data.get('parent_id'),
                        upvotes=comment_data.get('upvotes', 0),
                        downvotes=comment_data.get('downvotes', 0),
                        is_deleted=comment_data.get('is_deleted', False),
                        created_at=datetime.fromisoformat(comment_data['created_at']),
                        updated_at=datetime.fromisoformat(comment_data.get('updated_at', comment_data['created_at']))
                    )
                    
                    session.add(comment)
                    self.log(f"✓ Migrated comment for post {comment_data['post_id'][:8]}...")
                    
                except Exception as e:
                    self.log(f"✗ Error migrating comment {comment_data.get('comment_id', 'unknown')}: {str(e)}")
            
            session.commit()
            self.log(f"\nComments Migration Complete")
            
        except Exception as e:
            session.rollback()
            self.log(f"CRITICAL ERROR in comments migration: {str(e)}")
            raise
        finally:
            session.close()
    
    def migrate_votes(self, votes_file='peerhub_data/votes.json'):
        """Migrate votes from JSON to database."""
        self.log("\n" + "=" * 60)
        self.log("Starting Votes Migration")
        self.log("=" * 60)
        
        if not os.path.exists(votes_file):
            self.log(f"WARNING: {votes_file} not found, skipping...")
            return
        
        with open(votes_file, 'r') as f:
            votes_data = json.load(f)
        
        session = self.db_config.get_db_session()
        
        try:
            for vote_data in votes_data:
                try:
                    user_id = self.migrated_users.get(vote_data['user_id'], vote_data['user_id'])
                    
                    # Check if vote already exists
                    existing_vote = session.query(Vote).filter(Vote.id == vote_data['vote_id']).first()
                    if existing_vote:
                        self.log(f"Vote '{vote_data['vote_id']}' already exists, skipping...")
                        continue
                    
                    vote = Vote(
                        id=vote_data['vote_id'],  # Preserve original ID
                        user_id=user_id,
                        post_id=vote_data.get('target_id') if vote_data['target_type'] == 'post' else None,
                        comment_id=vote_data.get('target_id') if vote_data['target_type'] == 'comment' else None,
                        vote_type=vote_data['vote_type'],
                        created_at=datetime.fromisoformat(vote_data['created_at'])
                    )
                    
                    session.add(vote)
                    self.log(f"✓ Migrated {vote_data['vote_type']} for {vote_data['target_type']}")
                    
                except Exception as e:
                    self.log(f"✗ Error migrating vote {vote_data.get('vote_id', 'unknown')}: {str(e)}")
            
            session.commit()
            self.log(f"\nVotes Migration Complete")
            
        except Exception as e:
            session.rollback()
            self.log(f"CRITICAL ERROR in votes migration: {str(e)}")
            raise
        finally:
            session.close()
    
    def backup_json_files(self):
        """Create backups of JSON files before migration."""
        self.log("\n" + "=" * 60)
        self.log("Creating Backups of JSON Files")
        self.log("=" * 60)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"json_backup_{timestamp}"
        os.makedirs(backup_dir, exist_ok=True)
        
        files_to_backup = [
            'users.json',
            'peerhub_data/users.json',
            'peerhub_data/posts.json',
            'peerhub_data/comments.json',
            'peerhub_data/votes.json'
        ]
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                backup_path = os.path.join(backup_dir, file_path.replace('/', '_'))
                import shutil
                shutil.copy2(file_path, backup_path)
                self.log(f"✓ Backed up: {file_path} -> {backup_path}")
        
        self.log(f"\nBackup Complete: Files saved to {backup_dir}/")
        return backup_dir
    
    def save_migration_log(self, backup_dir):
        """Save migration log to file."""
        log_file = os.path.join(backup_dir, 'migration_log.txt')
        with open(log_file, 'w') as f:
            f.write('\n'.join(self.migration_log))
        self.log(f"\nMigration log saved to: {log_file}")
    
    def run_full_migration(self):
        """Run complete migration process."""
        print("\n" + "=" * 80)
        print(" " * 25 + "EdFast Data Migration")
        print(" " * 20 + "JSON Files → SQLite Database")
        print("=" * 80 + "\n")
        
        # Step 1: Backup
        backup_dir = self.backup_json_files()
        
        # Step 2: Migrate users
        self.migrate_users()
        
        # Step 3: Migrate PeerHub users (for ID mapping)
        self.migrate_peerhub_users()
        
        # Step 4: Migrate posts
        self.migrate_posts()
        
        # Step 5: Migrate comments
        self.migrate_comments()
        
        # Step 6: Migrate votes
        self.migrate_votes()
        
        # Step 7: Save log
        self.save_migration_log(backup_dir)
        
        self.log("\n" + "=" * 80)
        self.log(" " * 30 + "Migration Complete!")
        self.log("=" * 80)
        self.log("\nSummary:")
        self.log(f"  - Users migrated: {len(self.migrated_users)}")
        self.log(f"  - Backup directory: {backup_dir}")
        self.log(f"  - Database: edfast.db (SQLite)")
        self.log("\nNext steps:")
        self.log("  1. Verify the data in the database")
        self.log("  2. Update the application to use database services")
        self.log("  3. Test thoroughly before removing JSON files")
        self.log("\n" + "=" * 80)


def main():
    """Main migration entry point."""
    print("\nWelcome to EdFast Data Migration Tool")
    print("This will migrate all JSON data to a SQLite database.\n")
    
    response = input("Do you want to proceed? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Migration cancelled.")
        return
    
    migrator = DataMigrator(db_type='sqlite')
    migrator.run_full_migration()
    
    print("\n✓ Migration completed successfully!")
    print("You can now update your application to use the database services.")


if __name__ == "__main__":
    main()


