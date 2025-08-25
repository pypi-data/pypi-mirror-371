#!/usr/bin/env python3
"""
Smart Gateway for Ghost Blog Creation
Intelligently routes blog creation through two paths:
1. Direct publish - when all parameters are complete
2. Rewrite & publish - when content needs enhancement or parameters are missing
"""

import os
import json
import time
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Import our existing blog creation function
from main_functions import create_ghost_blog_post

# Load environment variables
load_dotenv()

# Configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
GEMINI_MODEL = 'gemini-2.0-flash-exp'

# ================================================================================
# STRUCTURED OUTPUT SCHEMA - For blog rewriting
# ================================================================================

BLOG_STRUCTURE_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "Engaging, SEO-friendly blog title"
        },
        "content": {
            "type": "string",
            "description": "Full blog content in markdown format with proper structure"
        },
        "excerpt": {
            "type": "string",
            "description": "Brief summary (max 299 chars) for previews and search results"
        },
        "tags": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Relevant tags for categorization",
            "minItems": 1,
            "maxItems": 5
        },
        "target_language": {
            "type": "string",
            "description": "Target language for the content (e.g., 'English', 'Chinese')"
        },
        "use_ai_image": {
            "type": "boolean",
            "description": "Whether to generate AI feature image"
        },
        "image_prompt": {
            "type": "string",
            "description": "Custom prompt for AI image generation if use_ai_image is true"
        }
    },
    "required": ["title", "content", "excerpt", "tags"]
}

# System prompt for structured output - Combines blog refinement and image generation
BLOG_REWRITE_SYSTEM_PROMPT = """You are an expert blog writer, content strategist, and visual designer. Your task is to transform user input into a COMPLETE, PUBLICATION-READY blog post with all necessary components.

## YOUR MISSION
Create a single, perfect output that requires NO further AI processing. Everything must be done in this one step.

## CONTENT TRANSFORMATION RULES

### 1. TITLE GENERATION
- **NEVER include title in the content body** - Title is handled separately by the system
- Create an engaging, SEO-friendly title that captures the essence
- Should be memorable and click-worthy
- Maximum 60 characters for optimal display

### 2. CONTENT STRUCTURE & FORMATTING

#### For Scattered Ideas/Fragments:
- **Expand Ideas**: Transform bullet points into full, informative paragraphs with context
- **Add Transitions**: Connect thoughts with smooth, logical transitions
- **Provide Context**: Add necessary background information for clarity
- **Include Examples**: Add relevant, concrete examples to illustrate points
- **Create Structure**: Organize into logical sections with clear narrative flow

#### Markdown Formatting Requirements:
- Start directly with engaging content (NO title in body)
- Use `##` for main sections (NOT for title)
- Use `###` for subsections
- Use **bold** for key concepts and important terms
- Use *italic* for emphasis and foreign words
- Use `inline code` for technical terms, commands, special terminology
- Use bullet points (`-`) for unordered lists
- Use numbered lists (`1.` `2.`) for sequential steps
- Use `>` blockquotes for important statements
- Include code blocks with language specification when relevant
- Add `---` horizontal rules between major sections
- Ensure proper spacing between paragraphs

#### Content Requirements:
- **Introduction**: Hook the reader immediately with a compelling opening
- **Main Body**: 
  * Organize into 3-5 clear sections with headers
  * Each section should have substantial content (200+ words)
  * Include specific details, data, or examples
  * Maintain logical flow between sections
- **Conclusion**: Strong ending with actionable takeaways or thought-provoking summary
- **Total Length**: Aim for 800-1500 words for comprehensive coverage

### 3. EXCERPT CREATION
- Craft a compelling summary in under 299 characters
- Must capture the core value proposition
- Should entice readers to click and read more
- Include the most interesting or surprising element

### 4. TAG GENERATION
- Select 1-5 highly relevant tags
- Mix broad and specific tags for better discoverability
- Consider SEO value and search intent
- Use proper capitalization (e.g., "Machine Learning", not "machine learning")

### 5. LANGUAGE HANDLING
- Detect the primary language of user input
- Set target_language to match the detected language
- Maintain absolute consistency in the chosen language
- If translation is needed, ensure professional quality
- Preserve cultural context and idioms appropriately

### 6. IMAGE PROMPT GENERATION (CRITICAL)

#### Core Focus Noun Extraction:
- Identify ONE SINGLE CONCRETE NOUN that represents the blog's essence
- Must be visually compelling and instantly recognizable
- Examples:
  * Silicon Valley → "Stanford Tower" or "Golden Gate Bridge"
  * Google article → "Google Logo" or "Googleplex Building"
  * AI healthcare → "Robot Doctor" or "MRI Scanner"
  * Success story → "Trophy" or "Mountain Peak"

#### Image Prompt Structure:
Your image_prompt must follow this exact format:

"**Core Focus: [Concrete Noun]** - [Detailed description of the noun as the central focal point, taking up 40-60% of the frame]. [Art style: photorealistic/3D rendered/illustrated]. [Color palette focusing on making the noun pop]. [Supporting elements that enhance but don't compete]. [Lighting that dramatically highlights the main noun]. Professional blog header image, high resolution, sharp focus on main subject, no text or words in image."

#### Image Generation Rules:
- Set use_ai_image to true ONLY if visual content enhances the post
- The noun MUST be instantly recognizable
- NO abstract concepts - must be photographable/renderable
- Think "magazine cover" - what single image would make someone click?
- Focus on the most SPECIFIC and RECOGNIZABLE version of the noun

## CRITICAL OUTPUT RULES

⚠️ The content field must be the ACTUAL blog post content, ready to publish
⚠️ NO title in the content body - title is a separate field
⚠️ NO code block wrapping around the content
⚠️ NO meta-commentary about what you're doing
⚠️ Start content directly with an engaging opening paragraph
⚠️ Everything must be complete in this single output - no further processing needed

## QUALITY CHECKLIST
Before outputting, ensure:
✓ Title is catchy and under 60 characters
✓ Content is well-structured with clear sections
✓ Content is 800+ words with substantive information
✓ Excerpt is compelling and under 299 characters
✓ Tags are relevant and properly capitalized
✓ Image prompt has a concrete focal noun (if use_ai_image is true)
✓ All text is in consistent language
✓ Content is engaging and informative
✓ Markdown formatting is correct
✓ NO title appears in the content body

Remember: This is your ONLY chance to create the content. Make it perfect."""

# ================================================================================
# FUNCTION DECLARATIONS - For Gemini Function Calling
# ================================================================================

function_declarations = [
    {
        "name": "direct_publish_blog",
        "description": "Directly publish a blog post when all required parameters are complete and content is well-structured. Use this when the user provides clear title, content, and the blog is ready for publication.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "The blog post title"
                },
                "content": {
                    "type": "string",
                    "description": "The blog post content (markdown or plain text)"
                },
                "excerpt": {
                    "type": "string",
                    "description": "Brief summary of the post (optional, max 299 chars)"
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Tags for the post",
                    "default": ["Blog"]
                },
                "status": {
                    "type": "string",
                    "enum": ["draft", "published"],
                    "description": "Publishing status",
                    "default": "published"
                },
                "use_generated_feature_image": {
                    "type": "boolean",
                    "description": "Generate AI feature image",
                    "default": False
                },
                "target_language": {
                    "type": "string",
                    "description": "Target language for content translation (optional)"
                }
            },
            "required": ["title", "content"]
        }
    },
    {
        "name": "rewrite_and_publish_blog",
        "description": "Rewrite and enhance blog content when it needs improvement or is missing key parameters. Use this when: 1) Content is fragmented or needs restructuring, 2) Missing title or excerpt, 3) Content needs professional enhancement before publishing.",
        "parameters": {
            "type": "object",
            "properties": {
                "raw_content": {
                    "type": "string",
                    "description": "The raw content or ideas that need to be rewritten into a blog post"
                },
                "guidance": {
                    "type": "string",
                    "description": "Additional guidance for rewriting (tone, style, focus areas)",
                    "default": ""
                },
                "preferred_language": {
                    "type": "string",
                    "description": "Preferred language for the final blog post",
                    "default": ""
                },
                "status": {
                    "type": "string",
                    "enum": ["draft", "published"],
                    "description": "Publishing status after rewriting",
                    "default": "published"
                }
            },
            "required": ["raw_content"]
        }
    }
]

# ================================================================================
# CORE FUNCTIONS
# ================================================================================

def direct_publish_blog(**kwargs) -> Dict[str, Any]:
    """
    Directly publish a blog post using the existing create_ghost_blog_post function.
    This is called when content is complete and ready for publication.
    """
    try:
        # Remove any gateway-specific parameters before passing to create function
        publish_params = {
            'title': kwargs.get('title'),
            'content': kwargs.get('content'),
            'excerpt': kwargs.get('excerpt', ''),
            'tags': kwargs.get('tags', ['Blog']),
            'status': kwargs.get('status', 'published'),
            'use_generated_feature_image': kwargs.get('use_generated_feature_image', False),
            'target_language': kwargs.get('target_language'),
            'auto_format': True
        }
        
        # Remove None values
        publish_params = {k: v for k, v in publish_params.items() if v is not None}
        
        # Call the actual blog creation function
        result = create_ghost_blog_post(**publish_params)
        
        if result['success']:
            return {
                'success': True,
                'response': f"✅ Blog post published successfully!\n🔗 URL: {result['url']}\n📝 Post ID: {result['post_id']}",
                'url': result['url'],
                'post_id': result['post_id']
            }
        else:
            return {
                'success': False,
                'response': f"❌ Failed to publish: {result.get('message', 'Unknown error')}"
            }
            
    except Exception as e:
        return {
            'success': False,
            'response': f"❌ Error in direct publish: {str(e)}"
        }


def rewrite_and_publish_blog(**kwargs) -> Dict[str, Any]:
    """
    Rewrite content using structured output, then publish.
    This is called when content needs enhancement or parameters are missing.
    """
    try:
        raw_content = kwargs.get('raw_content', '')
        guidance = kwargs.get('guidance', '')
        preferred_language = kwargs.get('preferred_language', '')
        status = kwargs.get('status', 'published')
        
        # Prepare the user content for structured output
        user_input = f"""Please transform this into a complete blog post:

Content/Ideas:
{raw_content}

{f"Additional Guidance: {guidance}" if guidance else ""}
{f"Target Language: {preferred_language}" if preferred_language else ""}
"""
        
        print("🔄 Rewriting content with AI enhancement...")
        
        # Generate structured output
        structured_result = gemini_structured_output_with_schema(
            user_content=user_input,
            system_prompt=BLOG_REWRITE_SYSTEM_PROMPT,
            json_schema=BLOG_STRUCTURE_SCHEMA,
            api_key=GEMINI_API_KEY,
            model=GEMINI_MODEL
        )
        
        if not structured_result['success']:
            return {
                'success': False,
                'response': f"❌ Failed to rewrite content: {structured_result['message']}"
            }
        
        # Extract the rewritten blog data
        blog_data = structured_result['data']
        
        print("✅ Content rewritten successfully")
        print(f"📝 Title: {blog_data['title']}")
        print(f"📄 Excerpt: {blog_data['excerpt']}")
        print(f"🏷️ Tags: {', '.join(blog_data['tags'])}")
        
        # Prepare parameters for publishing
        publish_params = {
            'title': blog_data['title'],
            'content': blog_data['content'],
            'excerpt': blog_data['excerpt'],
            'tags': blog_data['tags'],
            'status': status,
            'auto_format': False  # CRITICAL: Content is already perfectly formatted by AI
        }
        
        # Handle image generation
        if blog_data.get('use_ai_image', False):
            # Use the AI-generated image prompt directly (no further AI processing needed)
            publish_params['use_generated_feature_image'] = True
            if blog_data.get('image_prompt'):
                # Pass the complete, optimized prompt directly to image generation
                publish_params['image_generation_prompt'] = blog_data['image_prompt']
                # Disable any auto-generation of image prompt since we have a perfect one
                publish_params['auto_generate_image_prompt'] = False
        else:
            publish_params['use_generated_feature_image'] = False
        
        # Set target language if specified (but no translation needed - content is already in correct language)
        if blog_data.get('target_language'):
            publish_params['target_language'] = blog_data['target_language']
        
        # Publish the rewritten blog
        print("📤 Publishing blog post...")
        result = create_ghost_blog_post(**publish_params)
        
        if result['success']:
            return {
                'success': True,
                'response': f"✅ Blog rewritten and published successfully!\n🔗 URL: {result['url']}\n📝 Post ID: {result['post_id']}\n📊 Rewrote {len(raw_content)} chars → {len(blog_data['content'])} chars",
                'url': result['url'],
                'post_id': result['post_id'],
                'rewritten_data': blog_data
            }
        else:
            return {
                'success': False,
                'response': f"❌ Failed to publish rewritten blog: {result.get('message', 'Unknown error')}"
            }
            
    except Exception as e:
        return {
            'success': False,
            'response': f"❌ Error in rewrite and publish: {str(e)}"
        }


def gemini_structured_output_with_schema(
    user_content: str, 
    system_prompt: str, 
    json_schema: dict,
    model: str = None,
    api_key: str = None,
    max_retries: int = 3
) -> Dict[str, Any]:
    """
    Generate structured output using Gemini that conforms to JSON Schema.
    Adapted from the reference implementation.
    """
    if not model:
        model = GEMINI_MODEL
    
    if not api_key:
        api_key = GEMINI_API_KEY
        if not api_key:
            return {
                'success': False,
                'data': None,
                'message': 'GEMINI_API_KEY not found',
                'response_time': 0,
                'retries_used': 0
            }
    
    # Build complete prompt with JSON Schema
    full_prompt = f"""{system_prompt}

You must respond with a valid JSON object that strictly conforms to the following JSON Schema:

{json.dumps(json_schema, indent=2, ensure_ascii=False)}

IMPORTANT:
- Your response must be ONLY the JSON object, no additional text
- All required fields must be present
- Follow the exact data types and structure specified
- Use proper JSON formatting

User Input:
{user_content}"""
    
    start_time = time.time()
    
    for attempt in range(max_retries):
        try:
            # Configure and create model
            genai.configure(api_key=api_key)
            model_instance = genai.GenerativeModel(model)
            
            # Generate response
            response = model_instance.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    top_p=0.9,
                )
            )
            
            if response and hasattr(response, 'text') and response.text:
                try:
                    # Clean markdown code blocks if present
                    response_text = response.text.strip()
                    if response_text.startswith('```json'):
                        response_text = response_text[7:]
                        if response_text.endswith('```'):
                            response_text = response_text[:-3]
                    elif response_text.startswith('```'):
                        response_text = response_text[3:]
                        if response_text.endswith('```'):
                            response_text = response_text[:-3]
                    
                    # Parse JSON
                    result_data = json.loads(response_text.strip())
                    
                    response_time = time.time() - start_time
                    return {
                        'success': True,
                        'data': result_data,
                        'message': f'Successfully generated structured output',
                        'response_time': response_time,
                        'retries_used': attempt
                    }
                    
                except json.JSONDecodeError as e:
                    if attempt == max_retries - 1:
                        response_time = time.time() - start_time
                        return {
                            'success': False,
                            'data': None,
                            'message': f'JSON parsing failed: {str(e)}',
                            'response_time': response_time,
                            'retries_used': attempt + 1
                        }
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                    
        except Exception as e:
            if attempt == max_retries - 1:
                response_time = time.time() - start_time
                return {
                    'success': False,
                    'data': None,
                    'message': f'API error: {str(e)}',
                    'response_time': response_time,
                    'retries_used': attempt + 1
                }
            time.sleep(2 ** attempt)
            continue
    
    return {
        'success': False,
        'data': None,
        'message': 'All attempts failed',
        'response_time': time.time() - start_time,
        'retries_used': max_retries
    }


# ================================================================================
# MAIN SMART GATEWAY FUNCTION
# ================================================================================

def smart_blog_gateway(user_input: str, **kwargs) -> Dict[str, Any]:
    """
    Smart Gateway for blog creation.
    Analyzes user input and routes to appropriate processing path.
    
    Args:
        user_input: User's blog content or request
        **kwargs: Additional parameters like status, preferred_language, etc.
        
    Returns:
        Dictionary with success status and response message
    """
    try:
        # Available functions for Gemini to call
        available_functions = {
            "direct_publish_blog": direct_publish_blog,
            "rewrite_and_publish_blog": rewrite_and_publish_blog
        }
        
        # Configure Gemini
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Create tool configuration
        tool = genai.types.Tool(function_declarations=function_declarations)
        config = genai.types.GenerateContentConfig(
            tools=[tool],
            temperature=0.1  # Low temperature for consistent routing
        )
        
        # Prepare the analysis prompt
        analysis_prompt = f"""Analyze this blog creation request and determine the best processing path:

User Input:
{user_input}

Additional Context:
- Status preference: {kwargs.get('status', 'published')}
- Language preference: {kwargs.get('preferred_language', 'auto-detect')}

DECISION CRITERIA:
1. Use 'direct_publish_blog' when:
   - User provides clear title and well-structured content
   - Content is publication-ready
   - Only minor formatting might be needed

2. Use 'rewrite_and_publish_blog' when:
   - Content is fragmented or ideas are scattered
   - Missing title or excerpt
   - Content needs significant restructuring or enhancement
   - User explicitly asks for rewriting or improvement

Choose the appropriate function and provide the necessary parameters."""
        
        print("🤖 Analyzing blog request...")
        
        # Generate response with function calling
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=analysis_prompt,
            config=config
        )
        
        # Process the response
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call') and part.function_call:
                function_call = part.function_call
                func_name = function_call.name
                func_args = dict(function_call.args)
                
                print(f"📌 Routing to: {func_name}")
                
                if func_name in available_functions:
                    # Add any additional kwargs to function arguments
                    if func_name == "rewrite_and_publish_blog":
                        func_args['status'] = kwargs.get('status', 'published')
                        if 'preferred_language' in kwargs:
                            func_args['preferred_language'] = kwargs['preferred_language']
                    elif func_name == "direct_publish_blog":
                        func_args['status'] = kwargs.get('status', 'published')
                    
                    # Execute the selected function
                    result = available_functions[func_name](**func_args)
                    return result
                else:
                    return {
                        'success': False,
                        'response': f"❌ Unknown function: {func_name}"
                    }
        
        # If no function was called (shouldn't happen)
        return {
            'success': False,
            'response': "❌ No processing path was selected. Please provide clearer blog content."
        }
        
    except Exception as e:
        return {
            'success': False,
            'response': f"❌ Gateway error: {str(e)}"
        }


# ================================================================================
# UTILITY FUNCTIONS
# ================================================================================

def analyze_content_completeness(content: str) -> Dict[str, Any]:
    """
    Analyze if content has all necessary components for a blog post.
    This is a helper function for understanding content structure.
    """
    analysis = {
        'has_title': False,
        'has_structure': False,
        'word_count': len(content.split()),
        'has_paragraphs': '\n\n' in content or '\n' in content,
        'needs_rewrite': False,
        'missing_components': []
    }
    
    # Check for title (usually first line or # header)
    lines = content.strip().split('\n')
    if lines and (lines[0].startswith('#') or len(lines[0]) < 100):
        analysis['has_title'] = True
    else:
        analysis['missing_components'].append('title')
    
    # Check for structure
    if any(line.startswith('#') for line in lines):
        analysis['has_structure'] = True
    
    # Determine if rewrite is needed
    if analysis['word_count'] < 50:
        analysis['needs_rewrite'] = True
        analysis['missing_components'].append('content too brief')
    
    if not analysis['has_paragraphs']:
        analysis['needs_rewrite'] = True
        analysis['missing_components'].append('proper paragraphs')
    
    return analysis


# ================================================================================
# MAIN EXECUTION
# ================================================================================

if __name__ == "__main__":
    # Test examples
    print("=" * 80)
    print("🎯 GHOST BLOG SMART GATEWAY - Test Examples")
    print("=" * 80)
    
    # Example 1: Complete blog (should route to direct publish)
    example1 = """
# The Future of AI in Healthcare

Artificial intelligence is revolutionizing healthcare delivery worldwide.

## Current Applications
AI is being used for early disease detection, personalized treatment plans, 
and improving diagnostic accuracy.

## Future Prospects
The next decade will see even more integration of AI in medical practice,
potentially saving millions of lives.

## Conclusion
The AI healthcare revolution is just beginning.
"""
    
    # Example 2: Scattered ideas (should route to rewrite)
    example2 = """
AI healthcare. Better diagnosis. Saves lives. 
Need to write about machine learning in hospitals.
Maybe mention radiology and drug discovery?
"""
    
    # Example 3: Good content but missing title
    example3 = """
Technology companies are increasingly investing in renewable energy sources.
Apple has committed to carbon neutrality across its entire supply chain by 2030.
Google has been carbon neutral since 2007 and aims to run on carbon-free energy 24/7 by 2030.
Microsoft has pledged to be carbon negative by 2030.
These commitments show that big tech is taking climate change seriously.
"""
    
    print("\nChoose an example to test:")
    print("1. Complete blog post (should use direct publish)")
    print("2. Scattered ideas (should use rewrite)")
    print("3. Good content without title (should use rewrite)")
    print("4. Enter custom content")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == '1':
        test_content = example1
    elif choice == '2':
        test_content = example2
    elif choice == '3':
        test_content = example3
    elif choice == '4':
        test_content = input("\nEnter your blog content:\n")
    else:
        print("Invalid choice")
        exit(1)
    
    # Test the smart gateway
    print("\n" + "=" * 80)
    print("🚀 Processing through Smart Gateway...")
    print("=" * 80)
    
    result = smart_blog_gateway(
        test_content,
        status='draft',  # Create as draft for testing
        preferred_language='English'
    )
    
    print("\n" + "=" * 80)
    print("📊 RESULT:")
    print("=" * 80)
    print(result['response'])
    
    if result['success'] and 'rewritten_data' in result:
        print("\n📝 Rewritten Content Preview:")
        print("-" * 40)
        print(f"Title: {result['rewritten_data']['title']}")
        print(f"Excerpt: {result['rewritten_data']['excerpt']}")
        print(f"Tags: {', '.join(result['rewritten_data']['tags'])}")
        print(f"Content Length: {len(result['rewritten_data']['content'])} characters")