"""
Ghost Blog Smart - A powerful Python API for creating Ghost CMS blog posts with AI-powered features
"""

__version__ = "1.0.9"
__author__ = "leowang.net"
__email__ = "me@leowang.net"

# Import main functions for easy access
from .main_functions import (
    create_ghost_blog_post,
    update_ghost_post_image,
    get_ghost_posts,
    delete_ghost_post,
    generate_ghost_headers
)

from .post_management import (
    get_ghost_post_details,
    get_ghost_posts_advanced,
    get_posts_summary,
    batch_get_post_details,
    find_posts_by_date_pattern
)

from .smart_gateway import (
    smart_blog_gateway
)

from .clean_imagen_generator import (
    CleanImagenGenerator
)

from .blog_post_refine_prompt import (
    BLOG_POST_REFINE_SYSTEM_PROMPT,
    get_refine_prompt_with_language
)

from .blog_to_image_prompt import (
    BLOG_TO_IMAGE_SYSTEM_PROMPT,
    generate_blog_image_prompt
)

__all__ = [
    # Main functions
    'create_ghost_blog_post',
    'update_ghost_post_image',
    'get_ghost_posts',
    'delete_ghost_post',
    'generate_ghost_headers',
    
    # Post management
    'get_ghost_post_details',
    'get_ghost_posts_advanced',
    'get_posts_summary',
    'batch_get_post_details',
    'find_posts_by_date_pattern',
    
    # Classes
    'CleanImagenGenerator',
    
    # Smart Gateway
    'smart_blog_gateway',
    
    # Prompts
    'BLOG_POST_REFINE_SYSTEM_PROMPT',
    'get_refine_prompt_with_language',
    'BLOG_TO_IMAGE_SYSTEM_PROMPT',
    'generate_blog_image_prompt',
]