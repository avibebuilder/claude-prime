"""
Tests for image_gen.py
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

import image_gen as ig


class TestAPIKeyFinder:
    """Test API key detection."""

    def test_find_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv('GEMINI_API_KEY', 'test_key_123')
        assert ig.find_api_key() == 'test_key_123'

    def test_find_api_key_not_found(self, monkeypatch):
        monkeypatch.delenv('GEMINI_API_KEY', raising=False)
        assert ig.find_api_key() is None


class TestModelRouting:
    """Test MODEL_ROUTING and auto-model selection."""

    def test_model_routing_has_all_modes(self):
        expected_modes = {'generate', 'generate-hq'}
        assert expected_modes == set(ig.MODEL_ROUTING.keys())

    def test_generate_routes_to_flash_image(self):
        assert ig.MODEL_ROUTING['generate'] == 'gemini-2.5-flash-image'

    def test_generate_hq_routes_to_pro_image(self):
        assert ig.MODEL_ROUTING['generate-hq'] == 'gemini-3-pro-image-preview'


class TestMimeTypeDetection:
    """Test MIME type detection for image formats."""

    def test_jpeg_mime_types(self):
        assert ig.get_mime_type('photo.jpg') == 'image/jpeg'
        assert ig.get_mime_type('photo.jpeg') == 'image/jpeg'

    def test_png_mime_type(self):
        assert ig.get_mime_type('image.png') == 'image/png'

    def test_webp_mime_type(self):
        assert ig.get_mime_type('image.webp') == 'image/webp'

    def test_heic_heif_mime_types(self):
        assert ig.get_mime_type('photo.heic') == 'image/heic'
        assert ig.get_mime_type('photo.heif') == 'image/heif'

    def test_unknown_mime_type(self):
        assert ig.get_mime_type('file.xyz') == 'application/octet-stream'

    def test_case_insensitive(self):
        assert ig.get_mime_type('PHOTO.JPG') == 'image/jpeg'
        assert ig.get_mime_type('Image.PNG') == 'image/png'


class TestGenerateImage:
    """Test image generation functionality."""

    def _make_response_with_image(self, image_data=b'\x89PNG_data'):
        """Build a mock Gemini response containing inline image data."""
        mock_inline_data = Mock()
        mock_inline_data.data = image_data

        mock_part = Mock()
        mock_part.inline_data = mock_inline_data

        mock_content = Mock()
        mock_content.parts = [mock_part]

        mock_candidate = Mock()
        mock_candidate.content = mock_content

        mock_response = Mock()
        mock_response.candidates = [mock_candidate]
        return mock_response

    def _make_response_no_image(self):
        """Build a mock Gemini response with no inline image data."""
        mock_part = Mock()
        mock_part.inline_data = None

        mock_content = Mock()
        mock_content.parts = [mock_part]

        mock_candidate = Mock()
        mock_candidate.content = mock_content

        mock_response = Mock()
        mock_response.candidates = [mock_candidate]
        return mock_response

    @patch('builtins.open', create=True)
    @patch('pathlib.Path.mkdir')
    def test_generate_image_success(self, mock_mkdir, mock_open):
        mock_client = Mock()
        mock_client.models.generate_content.return_value = self._make_response_with_image()

        result = ig.generate_image(
            client=mock_client,
            prompt='A mountain landscape',
            model='gemini-2.5-flash-image',
            output='output.png',
            verbose=False
        )

        assert result['status'] == 'success'
        assert result['output'] == 'output.png'
        mock_client.models.generate_content.assert_called_once()

    @patch('builtins.open', create=True)
    @patch('pathlib.Path.mkdir')
    def test_generate_image_with_aspect_ratio(self, mock_mkdir, mock_open):
        mock_client = Mock()
        mock_client.models.generate_content.return_value = self._make_response_with_image()

        result = ig.generate_image(
            client=mock_client,
            prompt='Wide banner image',
            model='gemini-2.5-flash-image',
            output='banner.png',
            aspect_ratio='16:9',
            verbose=False
        )

        assert result['status'] == 'success'
        call_kwargs = mock_client.models.generate_content.call_args
        config = call_kwargs.kwargs.get('config') or call_kwargs[1].get('config')
        assert config is not None

    @patch('builtins.open', create=True)
    @patch('pathlib.Path.mkdir')
    def test_generate_image_with_input_file(self, mock_mkdir, mock_open):
        mock_client = Mock()
        mock_client.models.generate_content.return_value = self._make_response_with_image()

        mock_open.return_value.__enter__.return_value.read.return_value = b'input_image_bytes'

        result = ig.generate_image(
            client=mock_client,
            prompt='Make the sky sunset colors',
            model='gemini-2.5-flash-image',
            output='edited.png',
            input_file='photo.jpg',
            verbose=False
        )

        assert result['status'] == 'success'
        call_args = mock_client.models.generate_content.call_args
        contents = call_args.kwargs.get('contents') or call_args[1].get('contents')
        assert len(contents) == 2

    def test_generate_image_no_image_in_response(self):
        mock_client = Mock()
        mock_client.models.generate_content.return_value = self._make_response_no_image()

        result = ig.generate_image(
            client=mock_client,
            prompt='Test prompt',
            model='gemini-2.5-flash-image',
            output='output.png',
            verbose=False
        )

        assert result['status'] == 'error'
        assert 'No image data' in result['error']

    def test_generate_image_empty_candidates(self):
        mock_client = Mock()
        mock_response = Mock()
        mock_response.candidates = []
        mock_client.models.generate_content.return_value = mock_response

        result = ig.generate_image(
            client=mock_client,
            prompt='Test prompt',
            model='gemini-2.5-flash-image',
            output='output.png',
            verbose=False
        )

        assert result['status'] == 'error'

    def test_generate_image_model_not_found(self):
        mock_client = Mock()
        mock_client.models.generate_content.side_effect = Exception("404 model not found")

        result = ig.generate_image(
            client=mock_client,
            prompt='Test',
            model='nonexistent-model',
            output='output.png',
            verbose=False
        )

        assert result['status'] == 'error'
        assert 'Model not found' in result['error']
        assert ig.MODELS_PAGE_URL in result['error']

    @patch('image_gen.time.sleep')
    def test_generate_image_retry_on_error(self, mock_sleep):
        mock_client = Mock()
        mock_client.models.generate_content.side_effect = Exception("Temporary API Error")

        result = ig.generate_image(
            client=mock_client,
            prompt='Test',
            model='gemini-2.5-flash-image',
            output='output.png',
            verbose=False,
            max_retries=3
        )

        assert result['status'] == 'error'
        assert 'Temporary API Error' in result['error']
        assert mock_client.models.generate_content.call_count == 3
        assert mock_sleep.call_count == 2

    @patch('image_gen.time.sleep')
    @patch('builtins.open', create=True)
    @patch('pathlib.Path.mkdir')
    def test_generate_image_retry_then_success(self, mock_mkdir, mock_open, mock_sleep):
        mock_client = Mock()
        mock_response = self._make_response_with_image()
        mock_client.models.generate_content.side_effect = [
            Exception("Temporary error"),
            mock_response
        ]

        result = ig.generate_image(
            client=mock_client,
            prompt='Test',
            model='gemini-2.5-flash-image',
            output='output.png',
            verbose=False,
            max_retries=3
        )

        assert result['status'] == 'success'
        assert mock_client.models.generate_content.call_count == 2
        mock_sleep.assert_called_once_with(1)

    @patch('builtins.open', create=True)
    @patch('pathlib.Path.mkdir')
    def test_generate_image_creates_output_directory(self, mock_mkdir, mock_open):
        mock_client = Mock()
        mock_client.models.generate_content.return_value = self._make_response_with_image()

        result = ig.generate_image(
            client=mock_client,
            prompt='Test',
            model='gemini-2.5-flash-image',
            output='nested/dir/output.png',
            verbose=False
        )

        assert result['status'] == 'success'
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch('builtins.open', create=True)
    @patch('pathlib.Path.mkdir')
    def test_generate_image_writes_binary_data(self, mock_mkdir, mock_open):
        image_data = b'\x89PNG_test_image_data'
        mock_client = Mock()
        mock_client.models.generate_content.return_value = self._make_response_with_image(image_data)

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        ig.generate_image(
            client=mock_client,
            prompt='Test',
            model='gemini-2.5-flash-image',
            output='output.png',
            verbose=False
        )

        write_calls = [c for c in mock_file.method_calls if c[0] == 'write']
        assert len(write_calls) == 1
        assert write_calls[0][1][0] == image_data


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
