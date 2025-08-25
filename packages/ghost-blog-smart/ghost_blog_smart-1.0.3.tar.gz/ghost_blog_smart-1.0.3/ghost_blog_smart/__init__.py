"""
Ghost Blog Smart - A powerful Python API for creating Ghost CMS blog posts with AI-powered features
"""

__version__ = "1.0.3"
__author__ = "preangelleo"
__email__ = "admin@animagent.ai"

# Import main functions for easy access
from .main_functions import (
    create_ghost_blog_post,
    update_ghost_post_image,
    regenerate_feature_image_for_post,
    generate_blog_image_with_ai,
    generate_blog_content_with_ai,
    convert_html_to_markdown
)

from .post_management import (
    get_ghost_post_details,
    update_ghost_post,
    delete_ghost_post,
    list_ghost_posts
)

from .smart_gateway import (
    SmartGateway
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
    'regenerate_feature_image_for_post',
    'generate_blog_image_with_ai',
    'generate_blog_content_with_ai',
    'convert_html_to_markdown',
    
    # Post management
    'get_ghost_post_details',
    'update_ghost_post',
    'delete_ghost_post',
    'list_ghost_posts',
    
    # Classes
    'SmartGateway',
    'CleanImagenGenerator',
    
    # Prompts
    'BLOG_POST_REFINE_SYSTEM_PROMPT',
    'get_refine_prompt_with_language',
    'BLOG_TO_IMAGE_SYSTEM_PROMPT',
    'generate_blog_image_prompt',
]