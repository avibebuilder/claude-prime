"""
Tests for gemini_batch_process.py
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

import gemini_batch_process as gbp


class TestAPIKeyFinder:
    """Test API key detection."""

    def test_find_api_key_from_env(self, monkeypatch):
        """Test finding API key from environment variable."""
        monkeypatch.setenv('GEMINI_API_KEY', 'test_key_123')
        assert gbp.find_api_key() == 'test_key_123'

    def test_find_api_key_not_found(self, monkeypatch):
        """Test when API key is not found."""
        monkeypatch.delenv('GEMINI_API_KEY', raising=False)
        assert gbp.find_api_key() is None


class TestMimeTypeDetection:
    """Test MIME type detection."""

    def test_audio_mime_types(self):
        """Test audio file MIME types."""
        assert gbp.get_mime_type('test.mp3') == 'audio/mp3'
        assert gbp.get_mime_type('test.wav') == 'audio/wav'
        assert gbp.get_mime_type('test.aac') == 'audio/aac'
        assert gbp.get_mime_type('test.flac') == 'audio/flac'

    def test_image_mime_types(self):
        """Test image file MIME types."""
        assert gbp.get_mime_type('test.jpg') == 'image/jpeg'
        assert gbp.get_mime_type('test.jpeg') == 'image/jpeg'
        assert gbp.get_mime_type('test.png') == 'image/png'
        assert gbp.get_mime_type('test.webp') == 'image/webp'

    def test_video_mime_types(self):
        """Test video file MIME types."""
        assert gbp.get_mime_type('test.mp4') == 'video/mp4'
        assert gbp.get_mime_type('test.mov') == 'video/quicktime'
        assert gbp.get_mime_type('test.avi') == 'video/x-msvideo'

    def test_document_mime_types(self):
        """Test document file MIME types."""
        assert gbp.get_mime_type('test.pdf') == 'application/pdf'
        assert gbp.get_mime_type('test.txt') == 'text/plain'

    def test_unknown_mime_type(self):
        """Test unknown file extension."""
        assert gbp.get_mime_type('test.xyz') == 'application/octet-stream'

    def test_case_insensitive(self):
        """Test case-insensitive extension matching."""
        assert gbp.get_mime_type('TEST.MP3') == 'audio/mp3'
        assert gbp.get_mime_type('Test.JPG') == 'image/jpeg'


class TestFileUpload:
    """Test file upload functionality."""

    @patch('gemini_batch_process.genai.Client')
    def test_upload_file_success(self, mock_client_class):
        """Test successful file upload."""
        mock_client = Mock()
        mock_file = Mock()
        mock_file.state.name = 'ACTIVE'
        mock_file.name = 'test_file'
        mock_client.files.upload.return_value = mock_file

        result = gbp.upload_file(mock_client, 'test.jpg', verbose=False)

        assert result == mock_file
        mock_client.files.upload.assert_called_once_with(file='test.jpg')

    @patch('gemini_batch_process.genai.Client')
    @patch('gemini_batch_process.time.sleep')
    def test_upload_video_with_processing(self, mock_sleep, mock_client_class):
        """Test video upload with processing wait."""
        mock_client = Mock()

        mock_file_processing = Mock()
        mock_file_processing.state.name = 'PROCESSING'
        mock_file_processing.name = 'test_video'

        mock_file_active = Mock()
        mock_file_active.state.name = 'ACTIVE'
        mock_file_active.name = 'test_video'

        mock_client.files.upload.return_value = mock_file_processing
        mock_client.files.get.return_value = mock_file_active

        result = gbp.upload_file(mock_client, 'test.mp4', verbose=False)

        assert result.state.name == 'ACTIVE'

    @patch('gemini_batch_process.genai.Client')
    def test_upload_file_failed(self, mock_client_class):
        """Test failed file upload."""
        mock_client = Mock()
        mock_file = Mock()
        mock_file.state.name = 'FAILED'
        mock_client.files.upload.return_value = mock_file
        mock_client.files.get.return_value = mock_file

        with pytest.raises(ValueError, match="File processing failed"):
            gbp.upload_file(mock_client, 'test.mp4', verbose=False)


class TestProcessFile:
    """Test file processing functionality."""

    @patch('gemini_batch_process.genai.Client')
    @patch('builtins.open', create=True)
    @patch('pathlib.Path.stat')
    def test_process_small_file_inline(self, mock_stat, mock_open, mock_client_class):
        """Test processing small file with inline data."""
        mock_stat.return_value.st_size = 10 * 1024 * 1024

        mock_open.return_value.__enter__.return_value.read.return_value = b'test_data'

        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = 'Test response'
        mock_client.models.generate_content.return_value = mock_response

        result = gbp.process_file(
            client=mock_client,
            file_path='test.jpg',
            prompt='Describe this image',
            model='gemini-2.5-flash',
            task='analyze',
            format_output='text',
            verbose=False
        )

        assert result['status'] == 'success'
        assert result['response'] == 'Test response'

    @patch('gemini_batch_process.upload_file')
    @patch('gemini_batch_process.genai.Client')
    @patch('pathlib.Path.stat')
    def test_process_large_file_api(self, mock_stat, mock_client_class, mock_upload):
        """Test processing large file with File API."""
        mock_stat.return_value.st_size = 50 * 1024 * 1024

        mock_file = Mock()
        mock_upload.return_value = mock_file

        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = 'Test response'
        mock_client.models.generate_content.return_value = mock_response

        result = gbp.process_file(
            client=mock_client,
            file_path='test.mp4',
            prompt='Summarize this video',
            model='gemini-2.5-flash',
            task='analyze',
            format_output='text',
            verbose=False
        )

        assert result['status'] == 'success'
        mock_upload.assert_called_once()

    @patch('gemini_batch_process.genai.Client')
    @patch('builtins.open', create=True)
    @patch('pathlib.Path.stat')
    def test_process_file_error_handling(self, mock_stat, mock_open, mock_client_class):
        """Test error handling in file processing."""
        mock_stat.return_value.st_size = 1024

        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = b'test_data'
        mock_open.return_value = mock_file

        mock_client = Mock()
        mock_client.models.generate_content.side_effect = Exception("API Error")

        result = gbp.process_file(
            client=mock_client,
            file_path='test.jpg',
            prompt='Test',
            model='gemini-2.5-flash',
            task='analyze',
            format_output='text',
            verbose=False,
            max_retries=1
        )

        assert result['status'] == 'error'
        assert 'API Error' in result['error']


class TestBatchProcessing:
    """Test batch processing functionality."""

    @patch('gemini_batch_process.find_api_key')
    @patch('gemini_batch_process.process_file')
    @patch('gemini_batch_process.genai.Client')
    def test_batch_process_success(self, mock_client_class, mock_process, mock_find_key):
        """Test successful batch processing."""
        mock_find_key.return_value = 'test_key'
        mock_process.return_value = {'status': 'success', 'response': 'Test'}

        results = gbp.batch_process(
            files=['test1.jpg', 'test2.jpg'],
            prompt='Analyze',
            model='gemini-2.5-flash',
            task='analyze',
            format_output='text',
            verbose=False,
            dry_run=False
        )

        assert len(results) == 2
        assert all(r['status'] == 'success' for r in results)

    @patch('gemini_batch_process.find_api_key')
    def test_batch_process_no_api_key(self, mock_find_key):
        """Test batch processing without API key."""
        mock_find_key.return_value = None

        with pytest.raises(SystemExit):
            gbp.batch_process(
                files=['test.jpg'],
                prompt='Test',
                model='gemini-2.5-flash',
                task='analyze',
                format_output='text',
                verbose=False,
                dry_run=False
            )

    @patch('gemini_batch_process.find_api_key')
    def test_batch_process_dry_run(self, mock_find_key):
        """Test dry run mode."""
        mock_find_key.return_value = 'test_key'

        results = gbp.batch_process(
            files=['test1.jpg', 'test2.jpg'],
            prompt='Test',
            model='gemini-2.5-flash',
            task='analyze',
            format_output='text',
            verbose=False,
            dry_run=True
        )

        assert results == []


class TestModelRouting:
    """Test MODEL_ROUTING and auto-model selection."""

    def test_model_routing_has_all_tasks(self):
        """Test that MODEL_ROUTING covers all expected tasks."""
        expected_tasks = {'transcribe', 'analyze', 'extract'}
        assert expected_tasks == set(gbp.MODEL_ROUTING.keys())

    def test_transcribe_uses_flash_model(self):
        """Test that transcribe routes to gemini-3-flash-preview."""
        assert gbp.MODEL_ROUTING['transcribe'] == 'gemini-3-flash-preview'

    def test_analyze_uses_flash_model(self):
        """Test that analyze routes to gemini-3-flash-preview."""
        assert gbp.MODEL_ROUTING['analyze'] == 'gemini-3-flash-preview'

    def test_extract_uses_flash_model(self):
        """Test that extract routes to gemini-2.5-flash."""
        assert gbp.MODEL_ROUTING['extract'] == 'gemini-2.5-flash'


class TestResultsSaving:
    """Test results saving functionality."""

    @patch('builtins.open', create=True)
    @patch('json.dump')
    def test_save_results_json(self, mock_json_dump, mock_open):
        """Test saving results as JSON."""
        results = [
            {'file': 'test1.jpg', 'status': 'success', 'response': 'Test1'},
            {'file': 'test2.jpg', 'status': 'success', 'response': 'Test2'}
        ]

        gbp.save_results(results, 'output.json', 'json')

        mock_json_dump.assert_called_once()

    @patch('builtins.open', create=True)
    @patch('csv.DictWriter')
    def test_save_results_csv(self, mock_csv_writer, mock_open):
        """Test saving results as CSV."""
        results = [
            {'file': 'test1.jpg', 'status': 'success', 'response': 'Test1'},
            {'file': 'test2.jpg', 'status': 'success', 'response': 'Test2'}
        ]

        gbp.save_results(results, 'output.csv', 'csv')

        mock_csv_writer.assert_called_once()

    @patch('builtins.open', create=True)
    def test_save_results_markdown(self, mock_open):
        """Test saving results as Markdown."""
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        results = [
            {'file': 'test1.jpg', 'status': 'success', 'response': 'Test1'},
            {'file': 'test2.jpg', 'status': 'error', 'error': 'Failed'}
        ]

        gbp.save_results(results, 'output.md', 'markdown')

        assert mock_file.write.call_count > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=gemini_batch_process', '--cov-report=term-missing'])
