#!/usr/bin/env python3
"""
Batch process multiple media files using Gemini API.

Supports all Gemini modalities:
- Audio: Transcription, analysis, summarization
- Image: Captioning, detection, OCR, analysis
- Video: Summarization, Q&A, scene detection
- Document: PDF extraction, structured output
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import csv

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
    "transcribe": "gemini-3-flash-preview",
    "analyze": "gemini-3-flash-preview",
    "extract": "gemini-2.5-flash",
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
        # Audio
        '.mp3': 'audio/mp3',
        '.wav': 'audio/wav',
        '.aac': 'audio/aac',
        '.flac': 'audio/flac',
        '.ogg': 'audio/ogg',
        '.aiff': 'audio/aiff',
        # Image
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
        '.heic': 'image/heic',
        '.heif': 'image/heif',
        # Video
        '.mp4': 'video/mp4',
        '.mpeg': 'video/mpeg',
        '.mov': 'video/quicktime',
        '.avi': 'video/x-msvideo',
        '.flv': 'video/x-flv',
        '.mpg': 'video/mpeg',
        '.webm': 'video/webm',
        '.wmv': 'video/x-ms-wmv',
        '.3gpp': 'video/3gpp',
        # Document
        '.pdf': 'application/pdf',
        '.txt': 'text/plain',
        '.html': 'text/html',
        '.md': 'text/markdown',
    }

    return mime_types.get(ext, 'application/octet-stream')


def upload_file(client: genai.Client, file_path: str, verbose: bool = False) -> Any:
    """Upload file to Gemini File API."""
    if verbose:
        print(f"Uploading {file_path}...")

    myfile = client.files.upload(file=file_path)

    mime_type = get_mime_type(file_path)
    if mime_type.startswith('video/') or mime_type.startswith('audio/'):
        max_wait = 300
        elapsed = 0
        while myfile.state.name == 'PROCESSING' and elapsed < max_wait:
            time.sleep(2)
            myfile = client.files.get(name=myfile.name)
            elapsed += 2
            if verbose and elapsed % 10 == 0:
                print(f"  Processing... {elapsed}s")

        if myfile.state.name == 'FAILED':
            raise ValueError(f"File processing failed: {file_path}")

        if myfile.state.name == 'PROCESSING':
            raise TimeoutError(f"Processing timeout after {max_wait}s: {file_path}")

    if verbose:
        print(f"  Uploaded: {myfile.name}")

    return myfile


def process_file(
    client: genai.Client,
    file_path: str,
    prompt: str,
    model: str,
    task: str,
    format_output: str,
    verbose: bool = False,
    max_retries: int = 3
) -> Dict[str, Any]:
    """Process a single file with retry logic."""

    for attempt in range(max_retries):
        try:
            file_path_obj = Path(file_path)
            file_size = file_path_obj.stat().st_size
            use_file_api = file_size > 20 * 1024 * 1024

            if use_file_api:
                myfile = upload_file(client, str(file_path_obj), verbose)
                content = [prompt, myfile]
            else:
                with open(file_path_obj, 'rb') as f:
                    file_bytes = f.read()

                mime_type = get_mime_type(str(file_path_obj))
                content = [
                    prompt,
                    types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
                ]

            config_args = {}
            if format_output == 'json':
                config_args['response_mime_type'] = 'application/json'

            config = types.GenerateContentConfig(**config_args) if config_args else None

            response = client.models.generate_content(
                model=model,
                contents=content,
                config=config
            )

            return {
                'file': str(file_path),
                'status': 'success',
                'response': response.text if hasattr(response, 'text') else None
            }

        except Exception as e:
            error_str = str(e)

            if '404' in error_str or 'not found' in error_str.lower():
                print(f"Warning: Model '{model}' not found or unavailable.")
                print(f"  Check available models at: {MODELS_PAGE_URL}")
                return {
                    'file': str(file_path),
                    'status': 'error',
                    'error': f"Model not found: {model}. See {MODELS_PAGE_URL}"
                }

            if attempt == max_retries - 1:
                return {
                    'file': str(file_path),
                    'status': 'error',
                    'error': error_str
                }

            wait_time = 2 ** attempt
            if verbose:
                print(f"  Retry {attempt + 1} after {wait_time}s: {e}")
            time.sleep(wait_time)


def batch_process(
    files: List[str],
    prompt: str,
    model: str,
    task: str,
    format_output: str,
    output_file: Optional[str] = None,
    verbose: bool = False,
    dry_run: bool = False
) -> List[Dict[str, Any]]:
    """Batch process multiple files."""
    api_key = find_api_key()
    if not api_key:
        print("Error: GEMINI_API_KEY not found")
        print("Set via: export GEMINI_API_KEY='your-key'")
        print("Or create .env file with: GEMINI_API_KEY=your-key")
        sys.exit(1)

    if dry_run:
        print("DRY RUN MODE - No API calls will be made")
        print(f"Files to process: {len(files)}")
        print(f"Model: {model}")
        print(f"Task: {task}")
        print(f"Prompt: {prompt}")
        return []

    client = genai.Client(api_key=api_key)
    results = []

    for i, file_path in enumerate(files, 1):
        if verbose:
            print(f"\n[{i}/{len(files)}] Processing: {file_path}")

        result = process_file(
            client=client,
            file_path=file_path,
            prompt=prompt,
            model=model,
            task=task,
            format_output=format_output,
            verbose=verbose
        )

        results.append(result)

        if verbose:
            status = result.get('status', 'unknown')
            print(f"  Status: {status}")

    if output_file:
        save_results(results, output_file, format_output)

    return results


def save_results(results: List[Dict[str, Any]], output_file: str, format_output: str):
    """Save results to file."""
    output_path = Path(output_file)

    if format_output == 'json':
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)
    elif format_output == 'csv':
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['file', 'status', 'response', 'error']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for result in results:
                writer.writerow({
                    'file': result.get('file', ''),
                    'status': result.get('status', ''),
                    'response': result.get('response', ''),
                    'error': result.get('error', '')
                })
    else:  # markdown
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Batch Processing Results\n\n")
            for i, result in enumerate(results, 1):
                f.write(f"## {i}. {result.get('file', 'Unknown')}\n\n")
                f.write(f"**Status**: {result.get('status', 'unknown')}\n\n")
                if result.get('response'):
                    f.write(f"**Response**:\n\n{result['response']}\n\n")
                if result.get('error'):
                    f.write(f"**Error**: {result['error']}\n\n")


def main():
    parser = argparse.ArgumentParser(
        description='Batch process media files with Gemini API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Transcribe audio (auto-selects gemini-3-flash-preview)
  %(prog)s --files *.mp3 --task transcribe

  # Analyze images
  %(prog)s --files *.jpg --task analyze --prompt "Describe this image"

  # Process PDFs to JSON
  %(prog)s --files *.pdf --task extract --prompt "Extract data as JSON" \\
    --format json --output results.json
        """
    )

    parser.add_argument('--files', nargs='+', required=True,
                       help='Input files to process')
    parser.add_argument('--task', required=True,
                       choices=['transcribe', 'analyze', 'extract'],
                       help='Task to perform')
    parser.add_argument('--prompt', help='Prompt for analysis/extraction')
    parser.add_argument('--model', default=None,
                       help='Gemini model to use (default: auto-selected per task)')
    parser.add_argument('--format', dest='format_output', default='text',
                       choices=['text', 'json', 'csv', 'markdown'],
                       help='Output format (default: text)')
    parser.add_argument('--output', help='Output file for results')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making API calls')

    args = parser.parse_args()

    if args.model is None:
        args.model = MODEL_ROUTING.get(args.task, 'gemini-2.5-flash')

    if not args.prompt:
        if args.task == 'transcribe':
            args.prompt = 'Generate a transcript with timestamps'
        elif args.task == 'analyze':
            args.prompt = 'Analyze this content'
        elif args.task == 'extract':
            args.prompt = 'Extract key information'

    results = batch_process(
        files=args.files,
        prompt=args.prompt,
        model=args.model,
        task=args.task,
        format_output=args.format_output,
        output_file=args.output,
        verbose=args.verbose,
        dry_run=args.dry_run
    )

    if not args.dry_run and results:
        success = sum(1 for r in results if r.get('status') == 'success')
        failed = len(results) - success
        print(f"\n{'='*50}")
        print(f"Processed: {len(results)} files")
        print(f"Success: {success}")
        print(f"Failed: {failed}")
        if args.output:
            print(f"Results saved to: {args.output}")


if __name__ == '__main__':
    main()
