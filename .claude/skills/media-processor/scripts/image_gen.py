#!/usr/bin/env python3
"""
Generate images using Gemini API.

Supports two modes:
- generate: Standard image generation (gemini-2.5-flash-image)
- generate-hq: High-quality image generation (gemini-3-pro-image-preview)
"""

import argparse
import os
import sys
import time
from pathlib import Path
from typing import Optional

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("Error: google-genai package not installed")
    print("Install with: pip install google-genai")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

MODEL_ROUTING = {
    "generate": "gemini-2.5-flash-image",
    "generate-hq": "gemini-3-pro-image-preview",
}

MODELS_PAGE_URL = "https://ai.google.dev/gemini-api/docs/models"

_SKILL_ENV = Path(__file__).parent.parent / '.env'
if load_dotenv and _SKILL_ENV.exists():
    load_dotenv(_SKILL_ENV)


def find_api_key() -> Optional[str]:
    """Find Gemini API key from environment or skill .env."""
    return os.getenv('GEMINI_API_KEY')


def get_mime_type(file_path: str) -> str:
    """Determine MIME type from file extension."""
    ext = Path(file_path).suffix.lower()

    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
        '.heic': 'image/heic',
        '.heif': 'image/heif',
    }

    return mime_types.get(ext, 'application/octet-stream')


def generate_image(
    client: genai.Client,
    prompt: str,
    model: str,
    output: str,
    input_file: Optional[str] = None,
    aspect_ratio: Optional[str] = None,
    verbose: bool = False,
    max_retries: int = 3
) -> dict:
    """Generate an image with retry logic."""

    for attempt in range(max_retries):
        try:
            if input_file:
                input_path = Path(input_file)
                with open(input_path, 'rb') as f:
                    file_bytes = f.read()
                mime_type = get_mime_type(str(input_path))
                content = [
                    prompt,
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
                ]
            else:
                content = [prompt]

            config_args = {'response_modalities': ['Image']}
            if aspect_ratio:
                config_args['image_config'] = types.ImageConfig(
                    aspect_ratio=aspect_ratio
                )

            config = types.GenerateContentConfig(**config_args)

            response = client.models.generate_content(
                model=model,
                contents=content,
                config=config
            )

            if hasattr(response, 'candidates') and response.candidates:
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        output_path = Path(output)
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(output_path, 'wb') as f:
                            f.write(part.inline_data.data)
                        if verbose:
                            print(f"Saved image to: {output_path}")
                        return {
                            'status': 'success',
                            'output': str(output_path),
                        }

            return {
                'status': 'error',
                'error': 'No image data in response',
            }

        except Exception as e:
            error_str = str(e)

            if '404' in error_str or 'not found' in error_str.lower():
                print(f"Warning: Model '{model}' not found or unavailable.")
                print(f"  Check available models at: {MODELS_PAGE_URL}")
                return {
                    'status': 'error',
                    'error': f"Model not found: {model}. See {MODELS_PAGE_URL}"
                }

            if attempt == max_retries - 1:
                return {
                    'status': 'error',
                    'error': error_str
                }

            wait_time = 2 ** attempt
            if verbose:
                print(f"  Retry {attempt + 1} after {wait_time}s: {e}")
            time.sleep(wait_time)


def main():
    parser = argparse.ArgumentParser(
        description='Generate images with Gemini API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate an image
  %(prog)s --prompt "A mountain landscape" --output landscape.png

  # High-quality generation
  %(prog)s --prompt "Detailed cityscape" --output city.png --mode generate-hq

  # With aspect ratio
  %(prog)s --prompt "Wide banner" --output banner.png --aspect-ratio 16:9

  # Edit an existing image
  %(prog)s --prompt "Make the sky sunset colors" --input photo.jpg --output edited.png
        """
    )

    parser.add_argument('--prompt', required=True,
                       help='Text prompt for image generation')
    parser.add_argument('--output', required=True,
                       help='Output file path for generated image')
    parser.add_argument('--mode', default='generate',
                       choices=['generate', 'generate-hq'],
                       help='Generation mode (default: generate)')
    parser.add_argument('--aspect-ratio',
                       choices=['1:1', '16:9', '9:16', '4:3', '3:4'],
                       help='Aspect ratio for generated image')
    parser.add_argument('--input',
                       help='Optional input image for editing')
    parser.add_argument('--model', default=None,
                       help='Gemini model override (default: auto-selected per mode)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    api_key = find_api_key()
    if not api_key:
        print("Error: GEMINI_API_KEY not found")
        print("Set via: export GEMINI_API_KEY='your-key'")
        print("Or create .env file with: GEMINI_API_KEY=your-key")
        sys.exit(1)

    if args.model is None:
        args.model = MODEL_ROUTING.get(args.mode, 'gemini-2.5-flash-image')

    if args.verbose:
        print(f"Mode: {args.mode}")
        print(f"Model: {args.model}")
        print(f"Prompt: {args.prompt}")
        if args.input:
            print(f"Input: {args.input}")
        if args.aspect_ratio:
            print(f"Aspect ratio: {args.aspect_ratio}")

    client = genai.Client(api_key=api_key)

    result = generate_image(
        client=client,
        prompt=args.prompt,
        model=args.model,
        output=args.output,
        input_file=args.input,
        aspect_ratio=args.aspect_ratio,
        verbose=args.verbose
    )

    if result['status'] == 'success':
        print(f"Image saved to: {result['output']}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
