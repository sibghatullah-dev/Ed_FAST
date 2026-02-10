# Authentication package for EdFast application

# Import functions from db_user_service (database-backed implementation)
from .db_user_service import (
    user_exists,
    validate_login,
    add_user,
    get_user_name,
    get_user_transcript,
    update_user_transcript,
    update_user_description,
    get_user_resume_data,
    update_user_resume_data,
    get_user_description,
    UserService
)

# Also import from user_management for backward compatibility
from .user_management import (
    create_user_storage_if_not_exists
)

__all__ = [
    'user_exists',
    'validate_login', 
    'add_user',
    'get_user_name',
    'get_user_transcript',
    'update_user_transcript',
    'update_user_description',
    'get_user_resume_data',
    'update_user_resume_data',
    'get_user_description',
    'UserService',
    'create_user_storage_if_not_exists'
] 