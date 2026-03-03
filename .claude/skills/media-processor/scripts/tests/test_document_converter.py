"""
Tests for document_converter.py
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open

sys.path.insert(0, str(Path(__file__).parent.parent))

import document_converter as dc


class TestAPIKeyFinder:
    """Test API key finding logic."""

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key-from-env'})
    def test_find_api_key_from_env(self):
        """Test finding API key from environment."""
        api_key = dc.find_api_key()
        assert api_key == 'test-key-from-env'

    def test_find_api_key_no_key(self, monkeypatch):
        """Test when no API key is available."""
        monkeypatch.delenv('GEMINI_API_KEY', raising=False)
        assert dc.find_api_key() is None


class TestProjectRoot:
    """Test project root finding."""

    @patch('pathlib.Path.exists')
    def test_find_project_root_with_git(self, mock_exists):
        """Test finding project root with .git directory."""
        root = dc.find_project_root()
        assert isinstance(root, Path)


class TestMimeType:
    """Test MIME type detection."""

    def test_pdf_mime_type(self):
        """Test PDF MIME type."""
        assert dc.get_mime_type('document.pdf') == 'application/pdf'

    def test_image_mime_types(self):
        """Test image MIME types."""
        assert dc.get_mime_type('image.jpg') == 'image/jpeg'
        assert dc.get_mime_type('image.png') == 'image/png'

    def test_unknown_mime_type(self):
        """Test unknown file extension."""
        assert dc.get_mime_type('file.unknown') == 'application/octet-stream'


class TestFileUpload:
    """Test file upload to Gemini API."""

    def test_upload_file_success(self):
        """Test successful file upload."""
        mock_client = Mock()
        mock_file = Mock()
        mock_file.state.name = 'ACTIVE'
        mock_file.name = 'uploaded_doc'
        mock_client.files.upload.return_value = mock_file

        result = dc.upload_file(mock_client, 'test.pdf', verbose=False)

        assert result == mock_file
        mock_client.files.upload.assert_called_once_with(file='test.pdf')

    @patch('document_converter.time.sleep')
    def test_upload_file_waits_for_processing(self, mock_sleep):
        """Test that upload waits for PROCESSING state to resolve."""
        mock_client = Mock()

        mock_processing = Mock()
        mock_processing.state.name = 'PROCESSING'
        mock_processing.name = 'doc_file'

        mock_active = Mock()
        mock_active.state.name = 'ACTIVE'
        mock_active.name = 'doc_file'

        mock_client.files.upload.return_value = mock_processing
        mock_client.files.get.return_value = mock_active

        result = dc.upload_file(mock_client, 'large.pdf', verbose=False)
        assert result.state.name == 'ACTIVE'

    def test_upload_file_failed_state(self):
        """Test upload raises on FAILED state."""
        mock_client = Mock()
        mock_file = Mock()
        mock_file.state.name = 'FAILED'
        mock_client.files.upload.return_value = mock_file

        with pytest.raises(ValueError, match="File processing failed"):
            dc.upload_file(mock_client, 'bad.pdf', verbose=False)


class TestConvertToMarkdown:
    """Test convert_to_markdown function (Gemini API calls)."""

    @patch('builtins.open', create=True)
    @patch('pathlib.Path.stat')
    def test_convert_small_file_inline(self, mock_stat, mock_open):
        """Test converting a small file uses inline data."""
        mock_stat.return_value.st_size = 1024  # 1KB - small file

        mock_open.return_value.__enter__.return_value.read.return_value = b'%PDF-1.4 test'

        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = '# Heading\n\nParagraph text.'
        mock_client.models.generate_content.return_value = mock_response

        result = dc.convert_to_markdown(
            client=mock_client,
            file_path='small.pdf',
            model='gemini-2.5-flash',
            verbose=False,
            max_retries=1
        )

        assert result['status'] == 'success'
        assert result['markdown'] == '# Heading\n\nParagraph text.'
        assert result['file'] == 'small.pdf'

    @patch('document_converter.upload_file')
    @patch('pathlib.Path.stat')
    def test_convert_large_file_uses_file_api(self, mock_stat, mock_upload):
        """Test converting a large file uses Gemini File API upload."""
        mock_stat.return_value.st_size = 50 * 1024 * 1024  # 50MB

        mock_uploaded = Mock()
        mock_upload.return_value = mock_uploaded

        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = '# Large Document Content'
        mock_client.models.generate_content.return_value = mock_response

        result = dc.convert_to_markdown(
            client=mock_client,
            file_path='large.pdf',
            model='gemini-2.5-flash',
            verbose=False,
            max_retries=1
        )

        assert result['status'] == 'success'
        mock_upload.assert_called_once()

    @patch('builtins.open', create=True)
    @patch('pathlib.Path.stat')
    def test_convert_with_custom_prompt(self, mock_stat, mock_open):
        """Test conversion with custom prompt."""
        mock_stat.return_value.st_size = 1024
        mock_open.return_value.__enter__.return_value.read.return_value = b'data'

        mock_client = Mock()
        mock_response = Mock()
        mock_response.text = '| Col1 | Col2 |\n|------|------|\n| A | B |'
        mock_client.models.generate_content.return_value = mock_response

        result = dc.convert_to_markdown(
            client=mock_client,
            file_path='spreadsheet.xlsx',
            custom_prompt='Extract only the tables as markdown',
            verbose=False,
            max_retries=1
        )

        assert result['status'] == 'success'
        assert '| Col1 |' in result['markdown']

    @patch('builtins.open', create=True)
    @patch('pathlib.Path.stat')
    def test_convert_error_handling(self, mock_stat, mock_open):
        """Test error handling when API call fails."""
        mock_stat.return_value.st_size = 1024
        mock_open.return_value.__enter__.return_value.read.return_value = b'data'

        mock_client = Mock()
        mock_client.models.generate_content.side_effect = Exception("API quota exceeded")

        result = dc.convert_to_markdown(
            client=mock_client,
            file_path='doc.pdf',
            verbose=False,
            max_retries=1
        )

        assert result['status'] == 'error'
        assert 'API quota exceeded' in result['error']
        assert result['markdown'] is None


class TestBatchConvert:
    """Test batch_convert function."""

    @patch('document_converter.find_api_key')
    @patch('document_converter.convert_to_markdown')
    @patch('document_converter.genai.Client')
    @patch('document_converter.find_project_root')
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', create=True)
    def test_batch_convert_success(self, mock_open, mock_mkdir, mock_root,
                                    mock_client_class, mock_convert, mock_key):
        """Test successful batch conversion of multiple files."""
        mock_key.return_value = 'test_key'
        mock_root.return_value = Path('/project')
        mock_convert.return_value = {
            'file': 'doc.pdf',
            'status': 'success',
            'markdown': '# Content'
        }

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        results = dc.batch_convert(
            files=['doc1.pdf', 'doc2.pdf'],
            output_file='/tmp/test_output.md',
            verbose=False
        )

        assert len(results) == 2
        assert all(r['status'] == 'success' for r in results)
        assert mock_convert.call_count == 2

    @patch('document_converter.find_api_key')
    def test_batch_convert_no_api_key(self, mock_key):
        """Test batch convert exits when no API key found."""
        mock_key.return_value = None

        with pytest.raises(SystemExit):
            dc.batch_convert(files=['doc.pdf'], verbose=False)

    @patch('document_converter.find_api_key')
    @patch('document_converter.convert_to_markdown')
    @patch('document_converter.genai.Client')
    @patch('document_converter.find_project_root')
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', create=True)
    def test_batch_convert_writes_output(self, mock_open, mock_mkdir, mock_root,
                                          mock_client_class, mock_convert, mock_key):
        """Test that batch_convert writes markdown output file."""
        mock_key.return_value = 'test_key'
        mock_root.return_value = Path('/project')
        mock_convert.return_value = {
            'file': 'doc.pdf',
            'status': 'success',
            'markdown': '# Result content'
        }

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        dc.batch_convert(
            files=['doc.pdf'],
            output_file='/tmp/output.md',
            verbose=False
        )

        # Verify file was written with header and content
        write_calls = mock_file.write.call_args_list
        written_text = ''.join(call.args[0] for call in write_calls)
        assert '# Document Extraction Results' in written_text
        assert '# Result content' in written_text


class TestMimeTypeExtended:
    """Extended MIME type tests for office document formats."""

    def test_office_mime_types(self):
        """Test office document MIME types."""
        assert dc.get_mime_type('doc.docx') == \
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        assert dc.get_mime_type('sheet.xlsx') == \
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert dc.get_mime_type('slides.pptx') == \
            'application/vnd.openxmlformats-officedocument.presentationml.presentation'

    def test_text_format_mime_types(self):
        """Test text format MIME types."""
        assert dc.get_mime_type('page.html') == 'text/html'
        assert dc.get_mime_type('page.htm') == 'text/html'
        assert dc.get_mime_type('data.csv') == 'text/csv'
        assert dc.get_mime_type('readme.md') == 'text/markdown'

    def test_image_mime_types_extended(self):
        """Test HEIC/HEIF image MIME types."""
        assert dc.get_mime_type('photo.heic') == 'image/heic'
        assert dc.get_mime_type('photo.heif') == 'image/heif'
        assert dc.get_mime_type('photo.webp') == 'image/webp'


class TestIntegration:
    """Integration tests."""

    def test_mime_type_integration(self):
        """Test MIME type detection with various extensions."""
        test_cases = [
            ('document.pdf', 'application/pdf'),
            ('image.jpg', 'image/jpeg'),
            ('unknown.xyz', 'application/octet-stream'),
        ]
        for file_path, expected_mime in test_cases:
            assert dc.get_mime_type(file_path) == expected_mime


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=document_converter', '--cov-report=term-missing'])
