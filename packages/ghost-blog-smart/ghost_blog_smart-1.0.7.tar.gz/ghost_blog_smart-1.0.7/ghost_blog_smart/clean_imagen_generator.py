#!/usr/bin/env python3
"""
🎨 Google Imagen Generator - Clean Implementation
Using the latest Imagen model with only useful parameters
"""

import os
import time
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
from pathlib import Path
import sys

from google import genai
from google.genai import types
from PIL import Image
import io
from dotenv import load_dotenv

# Import blog to image prompt (also works for general image optimization)
from .blog_to_image_prompt import BLOG_TO_IMAGE_SYSTEM_PROMPT

# Model configuration constants
IMAGE_MODEL = "imagen-4.0-generate-001"  # Latest stable Imagen model
TEXT_MODEL = "gemini-2.5-flash"  # Model for prompt optimization


class CleanImagenGenerator:
    """
    Clean Google Imagen Generator
    Keeps only truly useful features and parameters
    """
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """
        Initialize the generator
        
        Args:
            api_key: Gemini API Key
            model_name: Optional custom model name (defaults to IMAGE_MODEL)
        """
        load_dotenv()
        
        # Basic configuration
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required")
        
        # Initialize client
        self.client = genai.Client(api_key=self.api_key)
        
        # Use specified model or default
        self.model_name = model_name or IMAGE_MODEL
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self.default_config = {
            'output_directory': './generated_images',
            'save_metadata': True,
            'image_prefix': 'imagen_'
        }
        
        # Statistics
        self.generation_count = 0
        
        self.logger.info(f"✅ Initialized with model: {self.model_name}")
    
    def optimize_prompt(self, prompt: str) -> str:
        """
        Optimize prompt using blog to image system prompt
        
        Args:
            prompt: Original prompt
            
        Returns:
            Optimized prompt
        """
        try:
            # Use blog to image prompt for optimization
            full_instruction = BLOG_TO_IMAGE_SYSTEM_PROMPT + f"\n\nBlog Title: Image Generation\n\nBlog Content:\n{prompt}"
            
            response = self.client.models.generate_content(
                model=TEXT_MODEL,
                contents=full_instruction
            )
            
            optimized = response.candidates[0].content.parts[0].text.strip()
            self.logger.info(f"🔧 Prompt optimized: {prompt[:30]}... -> {optimized[:50]}...")
            return optimized
            
        except Exception as e:
            self.logger.warning(f"Prompt optimization failed: {e}, using original prompt")
            return prompt
    
    def generate_image(self, 
                      prompt: str,
                      aspect_ratio: str = "16:9",
                      number_of_images: int = 1,
                      person_generation: str = "allow_adult",
                      optimize_prompt: bool = True,
                      output_directory: Optional[str] = None,
                      image_prefix: str = "imagen_") -> Dict[str, Any]:
        """
        Generate images - keeping only truly useful parameters
        
        Args:
            prompt: Image description
            aspect_ratio: Aspect ratio ("1:1", "3:4", "4:3", "9:16", "16:9")
            number_of_images: Number of images (1-4)
            person_generation: Person generation ("dont_allow", "allow_adult", "allow_all") 
            optimize_prompt: Whether to optimize prompt with AI
            output_directory: Output directory
            image_prefix: Filename prefix
            
        Returns:
            Generation result dictionary
        """
        
        if not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        # Parameter validation
        valid_ratios = ["1:1", "3:4", "4:3", "9:16", "16:9"]
        if aspect_ratio not in valid_ratios:
            raise ValueError(f"aspect_ratio must be one of: {valid_ratios}")
            
        if not 1 <= number_of_images <= 4:
            raise ValueError("number_of_images must be between 1-4")
        
        valid_person_gen = ["dont_allow", "allow_adult", "allow_all"]
        if person_generation not in valid_person_gen:
            raise ValueError(f"person_generation must be one of: {valid_person_gen}")
        
        # Use configuration
        output_dir = output_directory or self.default_config['output_directory']
        os.makedirs(output_dir, exist_ok=True)
        
        # Optimize prompt if requested
        final_prompt = self.optimize_prompt(prompt) if optimize_prompt else prompt
        
        try:
            start_time = time.time()
            self.logger.info(f"🎨 Starting generation of {number_of_images} image(s)...")
            
            # Call Imagen API
            response = self.client.models.generate_images(
                model=self.model_name,
                prompt=final_prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=number_of_images,
                    aspect_ratio=aspect_ratio,
                    person_generation=person_generation
                )
            )
            
            # Process results
            results = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for i, generated_image in enumerate(response.generated_images):
                # Open image
                image = Image.open(io.BytesIO(generated_image.image.image_bytes))
                
                # Generate filename
                if number_of_images > 1:
                    filename = f"{image_prefix}{timestamp}_{i+1:03d}.png"
                else:
                    filename = f"{image_prefix}{timestamp}.png"
                
                filepath = os.path.join(output_dir, filename)
                
                # Save image
                image.save(filepath)
                
                # Result information
                result = {
                    'filepath': filepath,
                    'filename': filename,
                    'original_prompt': prompt,
                    'final_prompt': final_prompt,
                    'image_size': image.size,
                    'aspect_ratio': aspect_ratio,
                    'generation_time': time.time() - start_time,
                    'model': self.model_name
                }
                
                # Save metadata
                if self.default_config['save_metadata']:
                    metadata_path = filepath.replace('.png', '_metadata.json')
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2, ensure_ascii=False, default=str)
                
                results.append(result)
                self.logger.info(f"✅ Image saved: {filename} ({image.size[0]}x{image.size[1]})")
            
            generation_time = time.time() - start_time
            self.generation_count += len(results)
            
            self.logger.info(f"🎉 Successfully generated {len(results)} image(s) in {generation_time:.1f}s")
            
            return {
                'success': True,
                'results': results,
                'generation_time': generation_time,
                'total_images': len(results)
            }
            
        except Exception as e:
            self.logger.error(f"Generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'prompt': prompt
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics"""
        return {
            'total_generated': self.generation_count,
            'model_used': self.model_name
        }


def main():
    """Usage example"""
    
    # Initialize generator
    generator = CleanImagenGenerator()
    
    # Generate example
    result = generator.generate_image(
        prompt="A cute robot working in a candy factory",
        aspect_ratio="16:9",
        number_of_images=2,
        optimize_prompt=True
    )
    
    if result['success']:
        print(f"✅ Successfully generated {result['total_images']} image(s)")
        for img in result['results']:
            print(f"📁 {img['filename']} - {img['image_size']}")
    else:
        print(f"❌ Failed: {result['error']}")


if __name__ == "__main__":
    main()