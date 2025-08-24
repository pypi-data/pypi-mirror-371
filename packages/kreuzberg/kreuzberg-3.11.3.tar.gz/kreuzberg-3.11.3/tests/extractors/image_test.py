from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from kreuzberg._extractors._image import ImageExtractor
from kreuzberg._types import ExtractionConfig, ExtractionResult
from kreuzberg.exceptions import ValidationError

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def extractor() -> ImageExtractor:
    config = ExtractionConfig(ocr_backend="tesseract")
    return ImageExtractor(mime_type="image/png", config=config)


@pytest.fixture
def mock_ocr_backend() -> Generator[MagicMock, None, None]:
    backend = MagicMock()
    backend.process_file = AsyncMock()
    backend.process_file_sync = MagicMock()
    backend.process_batch_sync = MagicMock()

    with patch("kreuzberg._extractors._image.get_ocr_backend", return_value=backend):
        yield backend


@pytest.mark.anyio
async def test_extract_path_async_no_ocr_backend() -> None:
    config = ExtractionConfig(ocr_backend=None)
    extractor = ImageExtractor(mime_type="image/png", config=config)

    with pytest.raises(ValidationError) as excinfo:
        await extractor.extract_path_async(Path("dummy_path"))

    assert "ocr_backend is None" in str(excinfo.value)


@pytest.mark.anyio
async def test_extract_path_async(mock_ocr_backend: MagicMock, tmp_path: Path) -> None:
    config = ExtractionConfig(ocr_backend="tesseract")
    extractor = ImageExtractor(mime_type="image/png", config=config)

    image_path = tmp_path / "test.png"
    image_path.write_bytes(b"dummy image content")

    expected_result = ExtractionResult(
        content="extracted text", chunks=[], mime_type="text/plain", metadata={"quality_score": 1.0}
    )
    mock_ocr_backend.process_file.return_value = expected_result

    result = await extractor.extract_path_async(image_path)

    mock_ocr_backend.process_file.assert_called_once()
    assert result == expected_result


def test_extract_path_sync(mock_ocr_backend: MagicMock, tmp_path: Path) -> None:
    config = ExtractionConfig(ocr_backend="tesseract")
    extractor = ImageExtractor(mime_type="image/png", config=config)

    image_path = tmp_path / "test.png"
    image_path.write_bytes(b"dummy image content")

    expected_result = ExtractionResult(
        content="extracted text", chunks=[], mime_type="text/plain", metadata={"quality_score": 1.0}
    )
    mock_ocr_backend.process_file_sync.return_value = expected_result

    result = extractor.extract_path_sync(image_path)

    mock_ocr_backend.process_file_sync.assert_called_once()
    assert result == expected_result


def test_extract_bytes_sync(mock_ocr_backend: MagicMock) -> None:
    config = ExtractionConfig(ocr_backend="tesseract")
    extractor = ImageExtractor(mime_type="image/png", config=config)

    expected_result = ExtractionResult(
        content="extracted text", chunks=[], mime_type="text/plain", metadata={"quality_score": 1.0}
    )

    with patch.object(extractor, "extract_path_sync") as mock_extract_path:
        mock_extract_path.return_value = expected_result
        result = extractor.extract_bytes_sync(b"dummy image content")

        mock_extract_path.assert_called_once()
        assert result == expected_result


@pytest.mark.parametrize(
    "mime_type,expected_extension",
    [
        ("image/png", "png"),
        ("image/jpeg", "jpg"),
        ("image/gif", "gif"),
        ("image/bmp", "bmp"),
        ("image/tiff", "tiff"),
        ("image/webp", "webp"),
    ],
)
def test_get_extension_from_mime_type(mime_type: str, expected_extension: str) -> None:
    config = ExtractionConfig(ocr_backend="tesseract")
    extractor = ImageExtractor(mime_type=mime_type, config=config)

    extension = extractor._get_extension_from_mime_type(mime_type)
    assert extension == expected_extension


def test_get_extension_from_partial_mime_type() -> None:
    config = ExtractionConfig(ocr_backend="tesseract")
    extractor = ImageExtractor(mime_type="image/jpeg", config=config)

    extension = extractor._get_extension_from_mime_type("image")
    assert extension == "bmp"


def test_get_extension_from_unsupported_mime_type() -> None:
    config = ExtractionConfig(ocr_backend="tesseract")
    extractor = ImageExtractor(mime_type="image/png", config=config)

    with pytest.raises(ValidationError) as excinfo:
        extractor._get_extension_from_mime_type("application/unsupported")

    assert "unsupported mimetype" in str(excinfo.value)
    assert "application/unsupported" in str(excinfo.value)


@pytest.mark.anyio
async def test_extract_bytes_async(mock_ocr_backend: MagicMock) -> None:
    config = ExtractionConfig(ocr_backend="tesseract")
    extractor = ImageExtractor(mime_type="image/png", config=config)

    expected_result = ExtractionResult(
        content="extracted text", chunks=[], mime_type="text/plain", metadata={"quality_score": 1.0}
    )
    mock_ocr_backend.process_file.return_value = expected_result

    mock_path = MagicMock()
    mock_unlink = AsyncMock()

    with patch("kreuzberg._extractors._image.create_temp_file") as mock_create_temp:
        mock_create_temp.return_value = (mock_path, mock_unlink)

        with patch("kreuzberg._extractors._image.AsyncPath") as mock_async_path:
            mock_async_path_instance = MagicMock()
            mock_async_path_instance.write_bytes = AsyncMock()
            mock_async_path.return_value = mock_async_path_instance

            result = await extractor.extract_bytes_async(b"dummy image content")

            mock_create_temp.assert_called_once_with(".png")

            mock_async_path_instance.write_bytes.assert_called_once_with(b"dummy image content")

            mock_ocr_backend.process_file.assert_called_once_with(mock_path, **config.get_config_dict())

            mock_unlink.assert_called_once()

            assert result == expected_result


def test_ocr_backend_none_validation_error() -> None:
    """Test validation error when OCR backend is None."""
    config = ExtractionConfig(ocr_backend=None)
    extractor = ImageExtractor(mime_type="image/png", config=config)

    with pytest.raises(ValidationError, match="ocr_backend is None"):
        extractor.extract_path_sync(Path("dummy.png"))


@pytest.mark.anyio
async def test_ocr_backend_none_validation_error_async() -> None:
    """Test validation error when OCR backend is None in async mode."""
    config = ExtractionConfig(ocr_backend=None)
    extractor = ImageExtractor(mime_type="image/png", config=config)

    with pytest.raises(ValidationError, match="ocr_backend is None"):
        await extractor.extract_path_async(Path("dummy.png"))


def test_extract_bytes_temp_file_cleanup_on_error() -> None:
    """Test that temp files are cleaned up even when processing fails."""
    config = ExtractionConfig(ocr_backend="tesseract")
    extractor = ImageExtractor(mime_type="image/png", config=config)

    with patch("tempfile.mkstemp") as mock_mkstemp:
        mock_fd = 42
        mock_temp_path = "/tmp/test_image.png"
        mock_mkstemp.return_value = (mock_fd, mock_temp_path)

        with patch("os.fdopen") as mock_fdopen:
            mock_file = MagicMock()
            mock_fdopen.return_value.__enter__.return_value = mock_file

            with patch.object(extractor, "extract_path_sync") as mock_extract:
                mock_extract.side_effect = Exception("Processing failed")

                with patch("pathlib.Path.unlink") as mock_unlink:
                    with pytest.raises(Exception, match="Processing failed"):
                        extractor.extract_bytes_sync(b"image data")

                    # Verify temp file was still cleaned up
                    mock_unlink.assert_called_once()


def test_extract_path_sync_no_ocr_backend() -> None:
    """Test sync path extraction when ocr_backend is None."""
    config = ExtractionConfig(ocr_backend=None)
    extractor = ImageExtractor(mime_type="image/png", config=config)

    with pytest.raises(ValidationError) as excinfo:
        extractor.extract_path_sync(Path("dummy_path"))

    assert "ocr_backend is None" in str(excinfo.value)


def test_extract_bytes_with_different_mime_types() -> None:
    """Test extract_bytes_sync with different image MIME types."""
    config = ExtractionConfig(ocr_backend="tesseract")

    # Test different MIME types
    mime_types = ["image/png", "image/jpeg", "image/tiff", "image/webp"]

    for mime_type in mime_types:
        extractor = ImageExtractor(mime_type=mime_type, config=config)
        assert extractor.mime_type == mime_type
        assert mime_type in extractor.SUPPORTED_MIME_TYPES


def test_extract_bytes_sync_with_ocr_config() -> None:
    """Test extract_bytes_sync with specific OCR configuration."""
    from kreuzberg._ocr._tesseract import PSMMode, TesseractConfig

    tesseract_config = TesseractConfig(
        language="fra",
        psm=PSMMode.SINGLE_BLOCK,
    )
    config = ExtractionConfig(ocr_backend="tesseract", ocr_config=tesseract_config)
    extractor = ImageExtractor(mime_type="image/png", config=config)

    with patch("tempfile.mkstemp") as mock_mkstemp:
        mock_fd = 42
        mock_temp_path = "/tmp/test_image.png"
        mock_mkstemp.return_value = (mock_fd, mock_temp_path)

        with patch("os.fdopen") as mock_fdopen:
            mock_file = MagicMock()
            mock_fdopen.return_value.__enter__.return_value = mock_file

            with patch.object(extractor, "extract_path_sync") as mock_extract:
                expected_result = ExtractionResult(
                    content="extracted French text",
                    mime_type="text/plain",
                    metadata={},
                )
                mock_extract.return_value = expected_result

                result = extractor.extract_bytes_sync(b"fake image data")

                assert result.content == "extracted French text"
                mock_file.write.assert_called_once_with(b"fake image data")


def test_extract_bytes_sync_temp_file_creation() -> None:
    """Test that temporary files are created and cleaned up properly."""
    config = ExtractionConfig(ocr_backend="tesseract")
    extractor = ImageExtractor(mime_type="image/png", config=config)

    with patch("tempfile.mkstemp") as mock_mkstemp:
        mock_fd = 42
        mock_temp_path = "/tmp/test_image.png"
        mock_mkstemp.return_value = (mock_fd, mock_temp_path)

        with patch("os.fdopen") as mock_fdopen:
            mock_file = MagicMock()
            mock_fdopen.return_value.__enter__.return_value = mock_file

            with patch.object(extractor, "extract_path_sync") as mock_extract:
                expected_result = ExtractionResult(
                    content="extracted text",
                    mime_type="text/plain",
                    metadata={},
                )
                mock_extract.return_value = expected_result

                with patch("pathlib.Path.unlink") as mock_unlink:
                    result = extractor.extract_bytes_sync(b"fake image data")

                    assert result.content == "extracted text"
                    # Verify temp file was created with correct suffix
                    mock_mkstemp.assert_called_once_with(suffix=".png")
                    # Verify file was written
                    mock_file.write.assert_called_once_with(b"fake image data")
                    # Verify file was cleaned up
                    mock_unlink.assert_called_once()


@pytest.mark.anyio
async def test_extract_bytes_async_delegation() -> None:
    """Test that async extraction properly delegates through extract_path_async."""
    config = ExtractionConfig(ocr_backend="tesseract")
    extractor = ImageExtractor(mime_type="image/png", config=config)

    with patch.object(extractor, "extract_path_async") as mock_async:
        expected_result = ExtractionResult(
            content="async extracted text",
            mime_type="text/plain",
            metadata={},
        )
        mock_async.return_value = expected_result

        result = await extractor.extract_bytes_async(b"fake image data")

        assert result.content == "async extracted text"
        mock_async.assert_called_once()
        # Verify it was called with a Path object
        assert isinstance(mock_async.call_args[0][0], Path)


@pytest.mark.anyio
async def test_extract_path_async_delegation(mock_ocr_backend: MagicMock) -> None:
    """Test that async path extraction properly uses OCR backend."""
    config = ExtractionConfig(ocr_backend="tesseract")
    extractor = ImageExtractor(mime_type="image/png", config=config)

    test_path = Path("test_image.png")

    expected_result = ExtractionResult(
        content="async path extracted text",
        mime_type="text/plain",
        metadata={},
    )
    mock_ocr_backend.process_file.return_value = expected_result

    result = await extractor.extract_path_async(test_path)

    assert result.content == "async path extracted text"
    mock_ocr_backend.process_file.assert_called_once_with(test_path, **config.get_config_dict())


def test_extract_path_sync_with_tesseract_config(mock_ocr_backend: MagicMock) -> None:
    """Test sync path extraction with TesseractConfig."""
    from kreuzberg._ocr._tesseract import TesseractConfig

    tesseract_config = TesseractConfig()
    config = ExtractionConfig(ocr_backend="tesseract", ocr_config=tesseract_config)
    extractor = ImageExtractor(mime_type="image/png", config=config)

    image_path = Path("test.png")

    expected_result = ExtractionResult(
        content="extracted text", chunks=[], mime_type="text/plain", metadata={"quality_score": 1.0}
    )
    mock_ocr_backend.process_file_sync.return_value = expected_result

    result = extractor.extract_path_sync(image_path)

    mock_ocr_backend.process_file_sync.assert_called_once()
    assert result == expected_result


def test_extract_path_sync_with_paddleocr_config(mock_ocr_backend: MagicMock) -> None:
    """Test sync path extraction with PaddleOCRConfig."""
    from kreuzberg._ocr._paddleocr import PaddleOCRConfig

    paddle_config = PaddleOCRConfig()
    config = ExtractionConfig(ocr_backend="paddleocr", ocr_config=paddle_config)
    extractor = ImageExtractor(mime_type="image/png", config=config)

    image_path = Path("test.png")

    expected_result = ExtractionResult(
        content="extracted text", chunks=[], mime_type="text/plain", metadata={"quality_score": 1.0}
    )
    mock_ocr_backend.process_file_sync.return_value = expected_result

    result = extractor.extract_path_sync(image_path)

    mock_ocr_backend.process_file_sync.assert_called_once()
    assert result == expected_result


def test_extract_path_sync_with_easyocr_config(mock_ocr_backend: MagicMock) -> None:
    """Test sync path extraction with EasyOCRConfig."""
    from kreuzberg._ocr._easyocr import EasyOCRConfig

    easy_config = EasyOCRConfig()
    config = ExtractionConfig(ocr_backend="easyocr", ocr_config=easy_config)
    extractor = ImageExtractor(mime_type="image/png", config=config)

    image_path = Path("test.png")

    expected_result = ExtractionResult(
        content="extracted text", chunks=[], mime_type="text/plain", metadata={"quality_score": 1.0}
    )
    mock_ocr_backend.process_file_sync.return_value = expected_result

    result = extractor.extract_path_sync(image_path)

    mock_ocr_backend.process_file_sync.assert_called_once()
    assert result == expected_result


# Integration Tests - These test with real images and OCR
@pytest.mark.anyio
async def test_extract_real_image_integration() -> None:
    """Integration test with real image and OCR."""
    test_image_path = Path(__file__).parent.parent / "test_source_files" / "images" / "test_hello_world.png"
    if not test_image_path.exists():
        pytest.skip("Test image not found")

    config = ExtractionConfig(ocr_backend="tesseract")
    extractor = ImageExtractor(mime_type="image/png", config=config)

    result = await extractor.extract_path_async(test_image_path)

    assert isinstance(result, ExtractionResult)
    assert result.mime_type == "text/plain"
    assert len(result.content) > 0  # Should extract some text


def test_extract_real_image_sync_integration() -> None:
    """Integration test with real image and OCR (sync)."""
    test_image_path = Path(__file__).parent.parent / "test_source_files" / "images" / "test_hello_world.png"
    if not test_image_path.exists():
        pytest.skip("Test image not found")

    config = ExtractionConfig(ocr_backend="tesseract")
    extractor = ImageExtractor(mime_type="image/png", config=config)

    result = extractor.extract_path_sync(test_image_path)

    assert isinstance(result, ExtractionResult)
    assert result.mime_type == "text/plain"
    assert len(result.content) > 0  # Should extract some text


# =============================================================================
# COMPREHENSIVE TESTS (for improved coverage)
# =============================================================================


class TestImageExtractorComprehensiveMimeTypes:
    """Test comprehensive MIME type handling."""

    @pytest.mark.parametrize(
        "mime_type,expected_extension",
        [
            # Test all mappings in IMAGE_MIME_TYPE_EXT_MAP
            ("image/bmp", "bmp"),
            ("image/x-bmp", "bmp"),
            ("image/x-ms-bmp", "bmp"),
            ("image/gif", "gif"),
            ("image/jpeg", "jpg"),
            ("image/pjpeg", "jpg"),
            ("image/png", "png"),
            ("image/tiff", "tiff"),
            ("image/x-tiff", "tiff"),
            ("image/jp2", "jp2"),
            ("image/jpx", "jpx"),
            ("image/jpm", "jpm"),
            ("image/mj2", "mj2"),
            ("image/webp", "webp"),
            ("image/x-portable-anymap", "pnm"),
            ("image/x-portable-bitmap", "pbm"),
            ("image/x-portable-graymap", "pgm"),
            ("image/x-portable-pixmap", "ppm"),
        ],
    )
    def test_all_mime_type_mappings(self, mime_type: str, expected_extension: str) -> None:
        """Test all MIME type to extension mappings."""
        config = ExtractionConfig(ocr_backend="tesseract")
        extractor = ImageExtractor(mime_type=mime_type, config=config)

        extension = extractor._get_extension_from_mime_type(mime_type)
        assert extension == expected_extension

    def test_partial_mime_type_matching_all_cases(self) -> None:
        """Test partial MIME type matching for all types."""
        config = ExtractionConfig(ocr_backend="tesseract")
        extractor = ImageExtractor(mime_type="image/png", config=config)

        # Test that a partial match finds the first matching key
        # Since the dict iteration order is preserved in Python 3.7+,
        # "image" should match "image/bmp" first
        extension = extractor._get_extension_from_mime_type("image")
        assert extension == "bmp"

        # Test other partial matches
        extension = extractor._get_extension_from_mime_type("image/x")
        assert extension in ["bmp", "tiff", "pnm", "pbm", "pgm", "ppm"]  # Any x- prefix type

        # Test exact prefix match
        extension = extractor._get_extension_from_mime_type("image/x-portable")
        assert extension in ["pnm", "pbm", "pgm", "ppm"]  # Any portable type

    def test_mime_type_case_sensitivity(self) -> None:
        """Test that MIME type matching is case-sensitive."""
        config = ExtractionConfig(ocr_backend="tesseract")
        extractor = ImageExtractor(mime_type="image/png", config=config)

        # These should fail as the mapping is case-sensitive
        with pytest.raises(ValidationError, match="unsupported mimetype"):
            extractor._get_extension_from_mime_type("IMAGE/PNG")

        with pytest.raises(ValidationError, match="unsupported mimetype"):
            extractor._get_extension_from_mime_type("Image/Png")


class TestImageExtractorSyncPathExtractionComprehensive:
    """Test comprehensive sync path extraction scenarios."""

    def test_extract_path_sync_unknown_ocr_backend(self, mock_ocr_backend: MagicMock) -> None:
        """Test sync path extraction with unknown OCR backend."""
        config = ExtractionConfig(ocr_backend="unknown_backend")  # type: ignore[arg-type]
        extractor = ImageExtractor(mime_type="image/png", config=config)

        with pytest.raises(NotImplementedError, match="Sync OCR not implemented for unknown_backend"):
            extractor.extract_path_sync(Path("test.png"))

    def test_extract_path_sync_with_default_tesseract_config(self, mock_ocr_backend: MagicMock) -> None:
        """Test sync path extraction when ocr_config is None (uses default)."""
        # Use None config to trigger default creation
        config = ExtractionConfig(ocr_backend="tesseract", ocr_config=None)
        extractor = ImageExtractor(mime_type="image/png", config=config)

        expected_result = ExtractionResult(content="extracted text", chunks=[], mime_type="text/plain", metadata={})
        mock_ocr_backend.process_file_sync.return_value = expected_result

        result = extractor.extract_path_sync(Path("test.png"))

        # Should create default TesseractConfig
        mock_ocr_backend.process_file_sync.assert_called_once()
        # Quality processing adds metadata
        assert result.content == expected_result.content
        assert result.mime_type == expected_result.mime_type

    def test_extract_path_sync_with_default_paddleocr_config(self, mock_ocr_backend: MagicMock) -> None:
        """Test sync path extraction when ocr_config is None (uses default)."""
        # Use None config to trigger default creation
        config = ExtractionConfig(ocr_backend="paddleocr", ocr_config=None)
        extractor = ImageExtractor(mime_type="image/png", config=config)

        expected_result = ExtractionResult(content="extracted text", chunks=[], mime_type="text/plain", metadata={})
        mock_ocr_backend.process_file_sync.return_value = expected_result

        result = extractor.extract_path_sync(Path("test.png"))

        # Should create default PaddleOCRConfig
        mock_ocr_backend.process_file_sync.assert_called_once()
        # Quality processing adds metadata
        assert result.content == expected_result.content
        assert result.mime_type == expected_result.mime_type

    def test_extract_path_sync_with_default_easyocr_config(self, mock_ocr_backend: MagicMock) -> None:
        """Test sync path extraction when ocr_config is None (uses default)."""
        # Use None config to trigger default creation
        config = ExtractionConfig(ocr_backend="easyocr", ocr_config=None)
        extractor = ImageExtractor(mime_type="image/png", config=config)

        expected_result = ExtractionResult(content="extracted text", chunks=[], mime_type="text/plain", metadata={})
        mock_ocr_backend.process_file_sync.return_value = expected_result

        result = extractor.extract_path_sync(Path("test.png"))

        # Should create default EasyOCRConfig
        mock_ocr_backend.process_file_sync.assert_called_once()
        # Quality processing adds metadata
        assert result.content == expected_result.content
        assert result.mime_type == expected_result.mime_type

    def test_extract_path_sync_with_custom_ocr_configs(self, mock_ocr_backend: MagicMock) -> None:
        """Test sync path extraction with custom OCR configurations."""
        from kreuzberg._ocr._tesseract import PSMMode, TesseractConfig

        # Test with custom Tesseract config
        tesseract_config = TesseractConfig(
            language="deu+fra",
            psm=PSMMode.SINGLE_COLUMN,
            tessedit_char_whitelist="0123456789",
            tessedit_enable_dict_correction=False,
            language_model_ngram_on=True,
        )
        config = ExtractionConfig(ocr_backend="tesseract", ocr_config=tesseract_config)
        extractor = ImageExtractor(mime_type="image/png", config=config)

        expected_result = ExtractionResult(content="German text", mime_type="text/plain", metadata={})
        mock_ocr_backend.process_file_sync.return_value = expected_result

        result = extractor.extract_path_sync(Path("test.png"))
        assert result.content == "German text"

        # Verify the config was passed correctly
        call_args = mock_ocr_backend.process_file_sync.call_args[1]
        assert call_args["language"] == "deu+fra"
        assert call_args["psm"] == PSMMode.SINGLE_COLUMN
        assert call_args["tessedit_char_whitelist"] == "0123456789"
        assert call_args["tessedit_enable_dict_correction"] is False
        assert call_args["language_model_ngram_on"] is True


class TestImageExtractorTempFileHandlingComprehensive:
    """Test comprehensive temporary file handling scenarios."""

    def test_extract_bytes_sync_fd_close_error(self) -> None:
        """Test handling when file descriptor close fails."""
        config = ExtractionConfig(ocr_backend="tesseract")
        extractor = ImageExtractor(mime_type="image/png", config=config)

        with patch("tempfile.mkstemp") as mock_mkstemp:
            mock_fd = 42
            mock_temp_path = "/tmp/test_image.png"
            mock_mkstemp.return_value = (mock_fd, mock_temp_path)

            with patch("os.fdopen") as mock_fdopen:
                # Simulate fdopen failure
                mock_fdopen.side_effect = OSError("Cannot open file descriptor")

                with patch("pathlib.Path.unlink") as mock_unlink:
                    with pytest.raises(OSError, match="Cannot open file descriptor"):
                        extractor.extract_bytes_sync(b"image data")

                    # Verify cleanup still attempted
                    mock_unlink.assert_called_once()

    def test_extract_bytes_sync_unlink_error_suppressed(self) -> None:
        """Test that unlink errors are suppressed."""
        config = ExtractionConfig(ocr_backend="tesseract")
        extractor = ImageExtractor(mime_type="image/png", config=config)

        with patch("tempfile.mkstemp") as mock_mkstemp:
            mock_fd = 42
            mock_temp_path = "/tmp/test_image.png"
            mock_mkstemp.return_value = (mock_fd, mock_temp_path)

            with patch("os.fdopen") as mock_fdopen:
                mock_file = MagicMock()
                mock_fdopen.return_value.__enter__.return_value = mock_file

                with patch.object(extractor, "extract_path_sync") as mock_extract:
                    expected_result = ExtractionResult(content="text", mime_type="text/plain", metadata={})
                    mock_extract.return_value = expected_result

                    with patch("pathlib.Path.unlink") as mock_unlink:
                        # Unlink fails but should be suppressed
                        mock_unlink.side_effect = OSError("Cannot unlink")

                        # Should not raise
                        result = extractor.extract_bytes_sync(b"image data")
                        assert result == expected_result

    @pytest.mark.anyio
    async def test_extract_bytes_async_temp_file_cleanup(self) -> None:
        """Test async temp file cleanup on error."""
        config = ExtractionConfig(ocr_backend="tesseract")
        extractor = ImageExtractor(mime_type="image/png", config=config)

        mock_path = Path("/tmp/test.png")
        mock_unlink = AsyncMock()

        with patch("kreuzberg._extractors._image.create_temp_file") as mock_create_temp:
            mock_create_temp.return_value = (mock_path, mock_unlink)

            with patch("kreuzberg._extractors._image.AsyncPath") as mock_async_path:
                mock_async_path_instance = MagicMock()
                mock_async_path_instance.write_bytes = AsyncMock()
                mock_async_path.return_value = mock_async_path_instance

                with patch.object(extractor, "extract_path_async") as mock_extract:
                    # Simulate extraction failure
                    mock_extract.side_effect = Exception("OCR failed")

                    with pytest.raises(Exception, match="OCR failed"):
                        await extractor.extract_bytes_async(b"image data")

                    # Verify cleanup was called
                    mock_unlink.assert_called_once()


class TestImageExtractorEdgeCases:
    """Test edge cases and error conditions."""

    def test_supported_mime_types_constant(self) -> None:
        """Test that SUPPORTED_MIME_TYPES matches expected set."""
        config = ExtractionConfig(ocr_backend="tesseract")
        extractor = ImageExtractor(mime_type="image/png", config=config)

        # Verify it includes all mapped types
        for mime_type in extractor.IMAGE_MIME_TYPE_EXT_MAP:
            assert mime_type in extractor.SUPPORTED_MIME_TYPES

    def test_extract_bytes_sync_with_all_mime_types(self) -> None:
        """Test extract_bytes_sync with all supported MIME types."""
        config = ExtractionConfig(ocr_backend="tesseract")

        # Mock the extraction to avoid actual OCR
        for mime_type in ImageExtractor.IMAGE_MIME_TYPE_EXT_MAP:
            extractor = ImageExtractor(mime_type=mime_type, config=config)

            with patch.object(extractor, "extract_path_sync") as mock_extract:
                expected_result = ExtractionResult(
                    content=f"Extracted from {mime_type}", mime_type="text/plain", metadata={}
                )
                mock_extract.return_value = expected_result

                result = extractor.extract_bytes_sync(b"fake image data")
                assert result.content == f"Extracted from {mime_type}"
                # Metadata is mocked, so we can't check specific keys

    def test_mime_type_validation_context(self) -> None:
        """Test that ValidationError includes proper context."""
        config = ExtractionConfig(ocr_backend="tesseract")
        extractor = ImageExtractor(mime_type="image/png", config=config)

        with pytest.raises(ValidationError) as exc_info:
            extractor._get_extension_from_mime_type("video/mp4")

        # Check error message and context
        assert "unsupported mimetype" in str(exc_info.value)
        assert exc_info.value.context == {"mime_type": "video/mp4"}

    def test_quality_processing_applied(self, mock_ocr_backend: MagicMock) -> None:
        """Test that quality processing is applied to results."""
        config = ExtractionConfig(ocr_backend="tesseract", enable_quality_processing=True)
        extractor = ImageExtractor(mime_type="image/png", config=config)

        # Create a result that would be modified by quality processing
        raw_result = ExtractionResult(
            content="Low quality text with ████ artifacts", mime_type="text/plain", metadata={}
        )
        mock_ocr_backend.process_file_sync.return_value = raw_result

        result = extractor.extract_path_sync(Path("test.png"))

        # Quality processing should be applied
        assert result != raw_result  # Result should be modified

    @pytest.mark.anyio
    async def test_async_path_delegation_preserves_config(self, mock_ocr_backend: MagicMock) -> None:
        """Test that async path extraction preserves all config options."""
        from kreuzberg._ocr._tesseract import PSMMode, TesseractConfig

        tesseract_config = TesseractConfig(language="jpn", psm=PSMMode.SINGLE_WORD, textord_space_size_is_variable=True)
        config = ExtractionConfig(ocr_backend="tesseract", ocr_config=tesseract_config, enable_quality_processing=True)
        extractor = ImageExtractor(mime_type="image/png", config=config)

        expected_result = ExtractionResult(content="日本語", mime_type="text/plain", metadata={})
        mock_ocr_backend.process_file.return_value = expected_result

        await extractor.extract_path_async(Path("japanese.png"))

        # Verify all OCR config was passed
        mock_ocr_backend.process_file.assert_called_once()
        call_kwargs = mock_ocr_backend.process_file.call_args[1]
        assert "language" in call_kwargs
        assert call_kwargs["language"] == "jpn"
        assert "psm" in call_kwargs
        assert call_kwargs["psm"] == PSMMode.SINGLE_WORD
        assert "textord_space_size_is_variable" in call_kwargs
        assert call_kwargs["textord_space_size_is_variable"] is True
