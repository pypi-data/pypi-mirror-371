from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from kreuzberg._extractors._presentation import PresentationExtractor
from kreuzberg.extraction import DEFAULT_CONFIG

if TYPE_CHECKING:
    from pathlib import Path

    from pytest_mock import MockerFixture


@pytest.fixture
def extractor() -> PresentationExtractor:
    return PresentationExtractor(
        mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", config=DEFAULT_CONFIG
    )


@pytest.mark.anyio
async def test_extract_pptx_with_notes(mocker: MockerFixture, extractor: PresentationExtractor) -> None:
    mock_presentation = mocker.MagicMock()
    mock_slide = mocker.MagicMock()
    mock_notes_slide = mocker.MagicMock()
    mock_text_frame = mocker.MagicMock()

    mock_presentation.slides = [mock_slide]
    mock_slide.has_notes_slide = True
    mock_slide.notes_slide = mock_notes_slide
    mock_notes_slide.notes_text_frame = mock_text_frame
    mock_text_frame.text = "Test note content"
    mock_slide.shapes = []

    mocker.patch("pptx.Presentation", return_value=mock_presentation)

    result = await extractor.extract_bytes_async(b"mock pptx content")

    assert "Test note content" in result.content
    assert result.mime_type == "text/markdown"


@pytest.mark.anyio
async def test_extract_path_async(mocker: MockerFixture, extractor: PresentationExtractor, tmp_path: Path) -> None:
    """Test async path extraction - covers lines 69-70."""

    mock_presentation = mocker.MagicMock()
    mock_presentation.slides = []
    mock_presentation.core_properties = mocker.MagicMock()
    mock_presentation.core_properties.author = None

    mocker.patch("pptx.Presentation", return_value=mock_presentation)

    test_file = tmp_path / "test.pptx"
    test_file.write_bytes(b"mock pptx content")

    result = await extractor.extract_path_async(test_file)

    assert result.mime_type == "text/markdown"


def test_extract_bytes_sync(mocker: MockerFixture, extractor: PresentationExtractor) -> None:
    """Test sync bytes extraction - covers line 82."""
    mock_presentation = mocker.MagicMock()
    mock_presentation.slides = []
    mock_presentation.core_properties = mocker.MagicMock()
    mock_presentation.core_properties.author = None

    mocker.patch("pptx.Presentation", return_value=mock_presentation)

    result = extractor.extract_bytes_sync(b"mock pptx content")

    assert result.mime_type == "text/markdown"


def test_extract_path_sync(mocker: MockerFixture, extractor: PresentationExtractor, tmp_path: Path) -> None:
    """Test sync path extraction - covers lines 94-95."""

    mock_presentation = mocker.MagicMock()
    mock_presentation.slides = []
    mock_presentation.core_properties = mocker.MagicMock()
    mock_presentation.core_properties.author = None

    mocker.patch("pptx.Presentation", return_value=mock_presentation)

    test_file = tmp_path / "test.pptx"
    test_file.write_bytes(b"mock pptx content")

    result = extractor.extract_path_sync(test_file)

    assert result.mime_type == "text/markdown"


def test_extract_pptx_with_slide_title(mocker: MockerFixture, extractor: PresentationExtractor) -> None:
    """Test extraction with slide title - covers line 131."""
    mock_presentation = mocker.MagicMock()
    mock_slide = mocker.MagicMock()
    mock_title_shape = mocker.MagicMock()
    mock_shapes = mocker.MagicMock()

    mock_shapes.title = mock_title_shape
    mock_slide.shapes = mock_shapes
    mock_slide.has_notes_slide = False
    mock_presentation.slides = [mock_slide]
    mock_presentation.core_properties = mocker.MagicMock()
    mock_presentation.core_properties.author = None

    mock_shapes.__iter__ = mocker.Mock(return_value=iter([mock_title_shape]))
    mock_title_shape.shape_type = mocker.MagicMock()
    mock_title_shape.has_text_frame = True
    mock_title_shape.text = "Test Title"

    mocker.patch("pptx.Presentation", return_value=mock_presentation)

    result = extractor.extract_bytes_sync(b"mock pptx content")

    assert "# Test Title" in result.content
    assert result.mime_type == "text/markdown"


def test_extract_pptx_with_shapes_no_shape_type(mocker: MockerFixture, extractor: PresentationExtractor) -> None:
    """Test extraction with shapes that don't have shape_type - covers lines 134-135."""
    mock_presentation = mocker.MagicMock()
    mock_slide = mocker.MagicMock()
    mock_shape_no_type = mocker.MagicMock()

    del mock_shape_no_type.shape_type

    mock_slide.shapes = [mock_shape_no_type]
    mock_slide.has_notes_slide = False
    mock_presentation.slides = [mock_slide]
    mock_presentation.core_properties = mocker.MagicMock()
    mock_presentation.core_properties.author = None

    mocker.patch("pptx.Presentation", return_value=mock_presentation)

    result = extractor.extract_bytes_sync(b"mock pptx content")

    assert result.mime_type == "text/markdown"


def test_extract_pptx_with_picture_shape(mocker: MockerFixture, extractor: PresentationExtractor) -> None:
    """Test extraction with picture shapes - covers lines 137-145."""
    from pptx.enum.shapes import MSO_SHAPE_TYPE

    mock_presentation = mocker.MagicMock()
    mock_slide = mocker.MagicMock()
    mock_picture_shape = mocker.MagicMock()

    mock_picture_shape.shape_type = MSO_SHAPE_TYPE.PICTURE
    mock_picture_shape.name = "test_image"

    mock_element = mocker.MagicMock()
    mock_nvXxPr = mocker.MagicMock()
    mock_cNvPr = mocker.MagicMock()
    mock_cNvPr.attrib = {"descr": "Test alt text"}
    mock_nvXxPr.cNvPr = mock_cNvPr
    mock_element._nvXxPr = mock_nvXxPr
    mock_picture_shape._element = mock_element

    mock_slide.shapes = [mock_picture_shape]
    mock_slide.has_notes_slide = False
    mock_presentation.slides = [mock_slide]
    mock_presentation.core_properties = mocker.MagicMock()
    mock_presentation.core_properties.author = None

    mocker.patch("pptx.Presentation", return_value=mock_presentation)

    result = extractor.extract_bytes_sync(b"mock pptx content")

    assert "![Test alt text](test_image.jpg)" in result.content
    assert result.mime_type == "text/markdown"


def test_extract_pptx_with_table_shape(mocker: MockerFixture, extractor: PresentationExtractor) -> None:
    """Test extraction with table shapes - covers lines 147-162."""
    from pptx.enum.shapes import MSO_SHAPE_TYPE

    mock_presentation = mocker.MagicMock()
    mock_slide = mocker.MagicMock()
    mock_table_shape = mocker.MagicMock()

    mock_table_shape.shape_type = MSO_SHAPE_TYPE.TABLE

    mock_table = mocker.MagicMock()
    mock_row1 = mocker.MagicMock()
    mock_row2 = mocker.MagicMock()

    mock_cell1 = mocker.MagicMock()
    mock_cell1.text = "Header1"
    mock_cell2 = mocker.MagicMock()
    mock_cell2.text = "Header2"
    mock_cell3 = mocker.MagicMock()
    mock_cell3.text = "Data1"
    mock_cell4 = mocker.MagicMock()
    mock_cell4.text = "Data2"

    mock_row1.cells = [mock_cell1, mock_cell2]
    mock_row2.cells = [mock_cell3, mock_cell4]
    mock_table.rows = [mock_row1, mock_row2]
    mock_table_shape.table = mock_table

    mock_slide.shapes = [mock_table_shape]
    mock_slide.has_notes_slide = False
    mock_presentation.slides = [mock_slide]
    mock_presentation.core_properties = mocker.MagicMock()
    mock_presentation.core_properties.author = None

    mocker.patch("pptx.Presentation", return_value=mock_presentation)

    result = extractor.extract_bytes_sync(b"mock pptx content")

    assert "<table>" in result.content
    assert "<th>Header1</th>" in result.content
    assert "<td>Data1</td>" in result.content
    assert result.mime_type == "text/markdown"


def test_extract_pptx_with_text_frame_shape(mocker: MockerFixture, extractor: PresentationExtractor) -> None:
    """Test extraction with text frame shapes - covers lines 164-165."""
    mock_presentation = mocker.MagicMock()
    mock_slide = mocker.MagicMock()
    mock_text_shape = mocker.MagicMock()

    mock_text_shape.shape_type = mocker.MagicMock()
    mock_text_shape.has_text_frame = True
    mock_text_shape.text = "  Some text content"

    mock_slide.shapes = [mock_text_shape]
    mock_slide.has_notes_slide = False
    mock_presentation.slides = [mock_slide]
    mock_presentation.core_properties = mocker.MagicMock()
    mock_presentation.core_properties.author = None

    mocker.patch("pptx.Presentation", return_value=mock_presentation)

    result = extractor.extract_bytes_sync(b"mock pptx content")

    assert "Some text content" in result.content
    assert result.mime_type == "text/markdown"


def test_extract_presentation_metadata(mocker: MockerFixture, extractor: PresentationExtractor) -> None:
    """Test metadata extraction - covers lines 210-231."""
    mock_presentation = mocker.MagicMock()
    mock_slide = mocker.MagicMock()

    mock_core_properties = mocker.MagicMock()
    mock_core_properties.author = "Test Author"
    mock_core_properties.title = "Test Title"
    mock_core_properties.subject = "Test Subject"
    mock_core_properties.language = "en-US"
    mock_core_properties.category = "Test Category"
    mock_core_properties.comments = None
    mock_core_properties.content_status = None
    mock_core_properties.created = None
    mock_core_properties.identifier = None
    mock_core_properties.keywords = None
    mock_core_properties.last_modified_by = None
    mock_core_properties.modified = None
    mock_core_properties.revision = None
    mock_core_properties.version = None

    mock_presentation.core_properties = mock_core_properties

    mock_shape = mocker.MagicMock()
    mock_text_frame = mocker.MagicMock()
    mock_paragraph = mocker.MagicMock()
    mock_run = mocker.MagicMock()
    mock_font = mocker.MagicMock()
    mock_font.name = "Arial"
    mock_run.font = mock_font
    mock_paragraph.runs = [mock_run]
    mock_text_frame.paragraphs = [mock_paragraph]
    mock_shape.text_frame = mock_text_frame

    mock_slide.shapes = [mock_shape]
    mock_presentation.slides = [mock_slide]

    mocker.patch("pptx.Presentation", return_value=mock_presentation)

    result = extractor.extract_bytes_sync(b"mock pptx content")

    assert result.metadata["authors"] == "Test Author"  # type: ignore[comparison-overlap]
    assert result.metadata["title"] == "Test Title"
    assert result.metadata["subject"] == "Test Subject"
    assert result.metadata["languages"] == ["en-US"]
    assert result.metadata["categories"] == ["Test Category"]
    assert result.metadata["fonts"] == ["Arial"]
    assert result.mime_type == "text/markdown"


def test_extract_presentation_metadata_no_text_frame(mocker: MockerFixture, extractor: PresentationExtractor) -> None:
    """Test metadata extraction with shapes that don't have text_frame - covers lines 222-223."""
    mock_presentation = mocker.MagicMock()
    mock_slide = mocker.MagicMock()

    mock_core_properties = mocker.MagicMock()
    mock_core_properties.author = None
    mock_core_properties.title = None
    mock_core_properties.language = None
    mock_core_properties.category = None
    mock_presentation.core_properties = mock_core_properties

    mock_shape = mocker.MagicMock()
    del mock_shape.text_frame

    mock_slide.shapes = [mock_shape]
    mock_presentation.slides = [mock_slide]

    mocker.patch("pptx.Presentation", return_value=mock_presentation)

    result = extractor.extract_bytes_sync(b"mock pptx content")

    assert "fonts" not in result.metadata
    assert result.mime_type == "text/markdown"


def test_extract_pptx_shape_without_text_frame(mocker: MockerFixture, extractor: PresentationExtractor) -> None:
    """Test extraction with shapes that don't have text_frame - covers branch 164->133."""
    mock_presentation = mocker.MagicMock()
    mock_slide = mocker.MagicMock()
    mock_shape = mocker.MagicMock()

    mock_shape.shape_type = mocker.MagicMock()
    mock_shape.has_text_frame = False

    mock_slide.shapes = [mock_shape]
    mock_slide.has_notes_slide = False
    mock_presentation.slides = [mock_slide]
    mock_presentation.core_properties = mocker.MagicMock()
    mock_presentation.core_properties.author = None

    mocker.patch("pptx.Presentation", return_value=mock_presentation)

    result = extractor.extract_bytes_sync(b"mock pptx content")

    assert result.mime_type == "text/markdown"


def test_extract_presentation_metadata_run_without_font(
    mocker: MockerFixture, extractor: PresentationExtractor
) -> None:
    """Test metadata extraction with runs that don't have font - covers branch 227->226."""
    mock_presentation = mocker.MagicMock()
    mock_slide = mocker.MagicMock()

    mock_core_properties = mocker.MagicMock()
    mock_core_properties.author = None
    mock_core_properties.language = None
    mock_core_properties.category = None
    mock_presentation.core_properties = mock_core_properties

    mock_shape = mocker.MagicMock()
    mock_text_frame = mocker.MagicMock()
    mock_paragraph = mocker.MagicMock()
    mock_run_no_font = mocker.MagicMock()

    del mock_run_no_font.font

    mock_paragraph.runs = [mock_run_no_font]
    mock_text_frame.paragraphs = [mock_paragraph]
    mock_shape.text_frame = mock_text_frame

    mock_slide.shapes = [mock_shape]
    mock_presentation.slides = [mock_slide]

    mocker.patch("pptx.Presentation", return_value=mock_presentation)

    result = extractor.extract_bytes_sync(b"mock pptx content")

    assert "fonts" not in result.metadata
    assert result.mime_type == "text/markdown"


def test_extract_presentation_metadata_font_without_name(
    mocker: MockerFixture, extractor: PresentationExtractor
) -> None:
    """Test metadata extraction with fonts that don't have name - covers branch 227->226."""
    mock_presentation = mocker.MagicMock()
    mock_slide = mocker.MagicMock()

    mock_core_properties = mocker.MagicMock()
    mock_core_properties.author = None
    mock_core_properties.language = None
    mock_core_properties.category = None
    mock_presentation.core_properties = mock_core_properties

    mock_shape = mocker.MagicMock()
    mock_text_frame = mocker.MagicMock()
    mock_paragraph = mocker.MagicMock()
    mock_run = mocker.MagicMock()
    mock_font = mocker.MagicMock()
    mock_font.name = None
    mock_run.font = mock_font
    mock_paragraph.runs = [mock_run]
    mock_text_frame.paragraphs = [mock_paragraph]
    mock_shape.text_frame = mock_text_frame

    mock_slide.shapes = [mock_shape]
    mock_presentation.slides = [mock_slide]

    mocker.patch("pptx.Presentation", return_value=mock_presentation)

    result = extractor.extract_bytes_sync(b"mock pptx content")

    assert "fonts" not in result.metadata
    assert result.mime_type == "text/markdown"


# =============================================================================
# COMPREHENSIVE TESTS (for improved coverage)
# =============================================================================


class TestPresentationExtractorComprehensiveScenarios:
    """Test comprehensive scenarios for presentation extraction."""

    def test_extract_pptx_picture_shape_no_alt_text(
        self, mocker: MockerFixture, extractor: PresentationExtractor
    ) -> None:
        """Test extraction with picture shapes that have no alt text - covers line 143-145."""
        from pptx.enum.shapes import MSO_SHAPE_TYPE

        mock_presentation = mocker.MagicMock()
        mock_slide = mocker.MagicMock()
        mock_picture_shape = mocker.MagicMock()

        mock_picture_shape.shape_type = MSO_SHAPE_TYPE.PICTURE
        mock_picture_shape.name = "test_image_no_alt"

        # Mock element structure that raises AttributeError for alt text
        mock_element = mocker.MagicMock()
        mock_element._nvXxPr.side_effect = AttributeError("No _nvXxPr attribute")
        mock_picture_shape._element = mock_element

        mock_slide.shapes = [mock_picture_shape]
        mock_slide.has_notes_slide = False
        mock_presentation.slides = [mock_slide]
        mock_presentation.core_properties = mocker.MagicMock()
        mock_presentation.core_properties.author = None

        mocker.patch("pptx.Presentation", return_value=mock_presentation)

        result = extractor.extract_bytes_sync(b"mock pptx content")

        # Should use shape.name when alt text is not available
        assert "![test_image_no_alt](test_image_no_alt.jpg)" in result.content
        assert result.mime_type == "text/markdown"

    def test_extract_pptx_placeholder_with_image(self, mocker: MockerFixture, extractor: PresentationExtractor) -> None:
        """Test extraction with placeholder shapes that have images - covers line 137-139."""
        from pptx.enum.shapes import MSO_SHAPE_TYPE

        mock_presentation = mocker.MagicMock()
        mock_slide = mocker.MagicMock()
        mock_placeholder_shape = mocker.MagicMock()

        mock_placeholder_shape.shape_type = MSO_SHAPE_TYPE.PLACEHOLDER
        mock_placeholder_shape.name = "placeholder_image"
        mock_placeholder_shape.image = mocker.MagicMock()  # Has image attribute

        # Mock alt text extraction
        mock_element = mocker.MagicMock()
        mock_nvXxPr = mocker.MagicMock()
        mock_cNvPr = mocker.MagicMock()
        mock_cNvPr.attrib = {"descr": "Placeholder alt text"}
        mock_nvXxPr.cNvPr = mock_cNvPr
        mock_element._nvXxPr = mock_nvXxPr
        mock_placeholder_shape._element = mock_element

        mock_slide.shapes = [mock_placeholder_shape]
        mock_slide.has_notes_slide = False
        mock_presentation.slides = [mock_slide]
        mock_presentation.core_properties = mocker.MagicMock()
        mock_presentation.core_properties.author = None

        mocker.patch("pptx.Presentation", return_value=mock_presentation)

        result = extractor.extract_bytes_sync(b"mock pptx content")

        assert "![Placeholder alt text](placeholderimage.jpg)" in result.content
        assert result.mime_type == "text/markdown"

    def test_extract_pptx_non_title_text_frame(self, mocker: MockerFixture, extractor: PresentationExtractor) -> None:
        """Test extraction with text frame that is not a title - covers line 165-166."""
        mock_presentation = mocker.MagicMock()
        mock_slide = mocker.MagicMock()
        mock_title_shape = mocker.MagicMock()
        mock_text_shape = mocker.MagicMock()
        mock_shapes = mocker.MagicMock()

        # Set up shapes with title and non-title text
        mock_shapes.title = mock_title_shape
        mock_slide.shapes = mock_shapes
        mock_slide.has_notes_slide = False
        mock_presentation.slides = [mock_slide]
        mock_presentation.core_properties = mocker.MagicMock()
        mock_presentation.core_properties.author = None

        # Configure both shapes
        mock_title_shape.shape_type = mocker.MagicMock()
        mock_title_shape.has_text_frame = True
        mock_title_shape.text = "  Title Text"

        mock_text_shape.shape_type = mocker.MagicMock()
        mock_text_shape.has_text_frame = True
        mock_text_shape.text = "Regular content text"

        # Mock iteration over shapes
        mock_shapes.__iter__ = mocker.Mock(return_value=iter([mock_title_shape, mock_text_shape]))

        mocker.patch("pptx.Presentation", return_value=mock_presentation)

        result = extractor.extract_bytes_sync(b"mock pptx content")

        # Title should be formatted as header, regular text as plain text
        assert "# Title Text" in result.content
        assert "Regular content text" in result.content
        assert result.mime_type == "text/markdown"

    def test_extract_pptx_notes_text_frame_none(self, mocker: MockerFixture, extractor: PresentationExtractor) -> None:
        """Test extraction when notes_text_frame is None - covers line 172-173."""
        mock_presentation = mocker.MagicMock()
        mock_slide = mocker.MagicMock()
        mock_notes_slide = mocker.MagicMock()

        mock_presentation.slides = [mock_slide]
        mock_slide.has_notes_slide = True
        mock_slide.notes_slide = mock_notes_slide
        mock_notes_slide.notes_text_frame = None  # Notes frame is None
        mock_slide.shapes = []

        mock_presentation.core_properties = mocker.MagicMock()
        mock_presentation.core_properties.author = None

        mocker.patch("pptx.Presentation", return_value=mock_presentation)

        result = extractor.extract_bytes_sync(b"mock pptx content")

        # Should have notes section but no content
        assert "### Notes:" in result.content
        assert result.mime_type == "text/markdown"

    def test_extract_pptx_shapes_no_title_attribute(
        self, mocker: MockerFixture, extractor: PresentationExtractor
    ) -> None:
        """Test extraction when slide.shapes has no title attribute - covers line 127-129."""
        mock_presentation = mocker.MagicMock()
        mock_slide = mocker.MagicMock()
        mock_text_shape = mocker.MagicMock()

        # Mock shapes without title attribute
        mock_shapes = mocker.MagicMock()
        del mock_shapes.title  # Remove title attribute
        mock_slide.shapes = mock_shapes
        mock_slide.has_notes_slide = False
        mock_presentation.slides = [mock_slide]

        mock_text_shape.shape_type = mocker.MagicMock()
        mock_text_shape.has_text_frame = True
        mock_text_shape.text = "Content without title"

        mock_shapes.__iter__ = mocker.Mock(return_value=iter([mock_text_shape]))

        mock_presentation.core_properties = mocker.MagicMock()
        mock_presentation.core_properties.author = None

        mocker.patch("pptx.Presentation", return_value=mock_presentation)

        result = extractor.extract_bytes_sync(b"mock pptx content")

        assert "Content without title" in result.content
        assert result.mime_type == "text/markdown"

    def test_extract_pptx_multiple_slides_comprehensive(
        self, mocker: MockerFixture, extractor: PresentationExtractor
    ) -> None:
        """Test extraction with multiple slides - covers slide numbering and content accumulation."""
        mock_presentation = mocker.MagicMock()

        # Create multiple slides
        mock_slide1 = mocker.MagicMock()
        mock_slide2 = mocker.MagicMock()
        mock_slide3 = mocker.MagicMock()

        mock_presentation.slides = [mock_slide1, mock_slide2, mock_slide3]

        # Configure slide 1
        mock_slide1.shapes = []
        mock_slide1.has_notes_slide = False

        # Configure slide 2 with content
        mock_text_shape = mocker.MagicMock()
        mock_text_shape.shape_type = mocker.MagicMock()
        mock_text_shape.has_text_frame = True
        mock_text_shape.text = "Slide 2 content"
        mock_slide2.shapes = [mock_text_shape]
        mock_slide2.has_notes_slide = False

        # Configure slide 3 with notes
        mock_slide3.shapes = []
        mock_slide3.has_notes_slide = True
        mock_notes_slide = mocker.MagicMock()
        mock_notes_text_frame = mocker.MagicMock()
        mock_notes_text_frame.text = "Notes for slide 3"
        mock_notes_slide.notes_text_frame = mock_notes_text_frame
        mock_slide3.notes_slide = mock_notes_slide

        mock_presentation.core_properties = mocker.MagicMock()
        mock_presentation.core_properties.author = None

        mocker.patch("pptx.Presentation", return_value=mock_presentation)

        result = extractor.extract_bytes_sync(b"mock pptx content")

        # Should contain slide numbers as comments
        assert "<!-- Slide number: 1 -->" in result.content
        assert "<!-- Slide number: 2 -->" in result.content
        assert "<!-- Slide number: 3 -->" in result.content
        assert "Slide 2 content" in result.content
        assert "### Notes:" in result.content
        assert "Notes for slide 3" in result.content
        assert result.mime_type == "text/markdown"


class TestPresentationExtractorMetadataComprehensive:
    """Test comprehensive metadata extraction scenarios."""

    def test_extract_presentation_metadata_all_properties(
        self, mocker: MockerFixture, extractor: PresentationExtractor
    ) -> None:
        """Test metadata extraction with all core properties populated."""
        from datetime import datetime, timezone

        mock_presentation = mocker.MagicMock()
        mock_slide = mocker.MagicMock()

        # Mock all core properties
        mock_core_properties = mocker.MagicMock()
        mock_core_properties.author = "Full Author"
        mock_core_properties.comments = "Full Comments"
        mock_core_properties.content_status = "Final"
        mock_core_properties.created = datetime(2023, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        mock_core_properties.identifier = "PRES-12345"
        mock_core_properties.keywords = "presentation, test, comprehensive"
        mock_core_properties.last_modified_by = "Editor User"
        mock_core_properties.modified = datetime(2023, 2, 20, 14, 45, 0, tzinfo=timezone.utc)
        mock_core_properties.revision = 5
        mock_core_properties.subject = "Comprehensive Test Subject"
        mock_core_properties.title = "Comprehensive Test Title"
        mock_core_properties.language = "en-GB"
        mock_core_properties.category = "Educational"

        mock_presentation.core_properties = mock_core_properties

        # Mock font extraction
        mock_shape = mocker.MagicMock()
        mock_text_frame = mocker.MagicMock()
        mock_paragraph = mocker.MagicMock()
        mock_run = mocker.MagicMock()
        mock_font = mocker.MagicMock()
        mock_font.name = "Calibri"
        mock_run.font = mock_font
        mock_paragraph.runs = [mock_run]
        mock_text_frame.paragraphs = [mock_paragraph]
        mock_shape.text_frame = mock_text_frame

        mock_slide.shapes = [mock_shape]
        mock_slide.has_notes_slide = True  # Slide with notes
        mock_presentation.slides = [mock_slide]

        mocker.patch("pptx.Presentation", return_value=mock_presentation)

        result = extractor.extract_bytes_sync(b"mock pptx content")

        metadata = result.metadata
        assert str(metadata["authors"]) == "Full Author"
        assert str(metadata["comments"]) == "Full Comments"
        assert str(metadata["status"]) == "Final"
        assert metadata["created_by"] == datetime(2023, 1, 15, 10, 30, 0, tzinfo=timezone.utc)
        assert str(metadata["identifier"]) == "PRES-12345"
        assert str(metadata["keywords"]) == "presentation, test, comprehensive"
        assert str(metadata["modified_by"]) == "Editor User"
        assert metadata["modified_at"] == datetime(2023, 2, 20, 14, 45, 0, tzinfo=timezone.utc)
        assert int(metadata["version"]) == 5
        assert metadata["subject"] == "Comprehensive Test Subject"
        assert metadata["title"] == "Comprehensive Test Title"
        assert metadata["languages"] == ["en-GB"]
        assert metadata["categories"] == ["Educational"]
        assert metadata["fonts"] == ["Calibri"]

        # Check structure info
        assert metadata["description"] == "Presentation with 1 slide, 1 with notes"
        assert "PowerPoint presentation with 1 slide" in metadata["summary"]
        assert "1 slide has notes" in metadata["summary"]
        assert "uses 1 font" in metadata["summary"]

    def test_extract_presentation_metadata_empty_presentation(
        self, mocker: MockerFixture, extractor: PresentationExtractor
    ) -> None:
        """Test metadata extraction with presentation that has no slides."""
        mock_presentation = mocker.MagicMock()
        mock_presentation.slides = []  # No slides
        mock_presentation.core_properties = mocker.MagicMock()
        mock_presentation.core_properties.author = None

        mocker.patch("pptx.Presentation", return_value=mock_presentation)

        result = extractor.extract_bytes_sync(b"mock pptx content")

        # Should not add structure info for empty presentation
        assert "description" not in result.metadata
        assert "summary" not in result.metadata
        assert result.mime_type == "text/markdown"

    def test_extract_presentation_metadata_multiple_fonts(
        self, mocker: MockerFixture, extractor: PresentationExtractor
    ) -> None:
        """Test metadata extraction with multiple unique fonts."""
        mock_presentation = mocker.MagicMock()
        mock_slide = mocker.MagicMock()

        mock_core_properties = mocker.MagicMock()
        mock_core_properties.author = None
        mock_core_properties.language = None
        mock_core_properties.category = None
        mock_presentation.core_properties = mock_core_properties

        # Create shapes with different fonts
        mock_shape1 = mocker.MagicMock()
        mock_text_frame1 = mocker.MagicMock()
        mock_paragraph1 = mocker.MagicMock()
        mock_run1 = mocker.MagicMock()
        mock_font1 = mocker.MagicMock()
        mock_font1.name = "Arial"
        mock_run1.font = mock_font1
        mock_paragraph1.runs = [mock_run1]
        mock_text_frame1.paragraphs = [mock_paragraph1]
        mock_shape1.text_frame = mock_text_frame1

        mock_shape2 = mocker.MagicMock()
        mock_text_frame2 = mocker.MagicMock()
        mock_paragraph2 = mocker.MagicMock()
        mock_run2a = mocker.MagicMock()
        mock_font2a = mocker.MagicMock()
        mock_font2a.name = "Calibri"
        mock_run2a.font = mock_font2a
        mock_run2b = mocker.MagicMock()
        mock_font2b = mocker.MagicMock()
        mock_font2b.name = "Arial"  # Duplicate font (should be deduplicated)
        mock_run2b.font = mock_font2b
        mock_paragraph2.runs = [mock_run2a, mock_run2b]
        mock_text_frame2.paragraphs = [mock_paragraph2]
        mock_shape2.text_frame = mock_text_frame2

        mock_slide.shapes = [mock_shape1, mock_shape2]
        mock_presentation.slides = [mock_slide]

        mocker.patch("pptx.Presentation", return_value=mock_presentation)

        result = extractor.extract_bytes_sync(b"mock pptx content")

        # Should have unique fonts sorted
        assert set(result.metadata["fonts"]) == {"Arial", "Calibri"}
        assert len(result.metadata["fonts"]) == 2
        assert "uses 2 fonts" in result.metadata["summary"]

    def test_extract_presentation_metadata_structure_single_vs_plural(
        self, mocker: MockerFixture, extractor: PresentationExtractor
    ) -> None:
        """Test metadata structure info with singular vs plural forms."""
        mock_presentation = mocker.MagicMock()

        # Create 3 slides, 2 with notes
        mock_slide1 = mocker.MagicMock()
        mock_slide1.shapes = []
        mock_slide1.has_notes_slide = True

        mock_slide2 = mocker.MagicMock()
        mock_slide2.shapes = []
        mock_slide2.has_notes_slide = False

        mock_slide3 = mocker.MagicMock()
        mock_slide3.shapes = []
        mock_slide3.has_notes_slide = True

        mock_presentation.slides = [mock_slide1, mock_slide2, mock_slide3]
        mock_presentation.core_properties = mocker.MagicMock()
        mock_presentation.core_properties.author = None

        mocker.patch("pptx.Presentation", return_value=mock_presentation)

        result = extractor.extract_bytes_sync(b"mock pptx content")

        # Should use plural for slides, and correctly count notes
        assert result.metadata["description"] == "Presentation with 3 slides, 2 with notes"
        assert "PowerPoint presentation with 3 slides" in result.metadata["summary"]
        assert "2 slides have notes" in result.metadata["summary"]

    def test_extract_presentation_metadata_existing_summary_preserved(
        self, mocker: MockerFixture, extractor: PresentationExtractor
    ) -> None:
        """Test that existing summary in metadata is preserved."""
        mock_presentation = mocker.MagicMock()
        mock_slide = mocker.MagicMock()
        mock_slide.shapes = []
        mock_slide.has_notes_slide = False
        mock_presentation.slides = [mock_slide]

        mock_core_properties = mocker.MagicMock()
        mock_core_properties.author = None
        mock_core_properties.comments = "Existing summary content"  # This should become summary
        mock_presentation.core_properties = mock_core_properties

        mocker.patch("pptx.Presentation", return_value=mock_presentation)

        # Create a custom metadata dict with existing summary
        original_extract_method = extractor._extract_presentation_metadata

        def mock_extract_with_existing_summary(presentation: Any) -> Any:
            metadata = original_extract_method(presentation)
            metadata["summary"] = "Pre-existing summary"  # Simulate existing summary
            return metadata

        mocker.patch.object(extractor, "_extract_presentation_metadata", side_effect=mock_extract_with_existing_summary)

        result = extractor.extract_bytes_sync(b"mock pptx content")

        # Should preserve the pre-existing summary
        assert result.metadata["summary"] == "Pre-existing summary"


class TestPresentationExtractorTableProcessingEdgeCases:
    """Test table processing edge cases."""

    def test_extract_pptx_table_with_html_content(
        self, mocker: MockerFixture, extractor: PresentationExtractor
    ) -> None:
        """Test table extraction with content that needs HTML escaping."""
        from pptx.enum.shapes import MSO_SHAPE_TYPE

        mock_presentation = mocker.MagicMock()
        mock_slide = mocker.MagicMock()
        mock_table_shape = mocker.MagicMock()

        mock_table_shape.shape_type = MSO_SHAPE_TYPE.TABLE

        mock_table = mocker.MagicMock()
        mock_row1 = mocker.MagicMock()
        mock_row2 = mocker.MagicMock()

        # Cells with content that needs HTML escaping
        mock_cell1 = mocker.MagicMock()
        mock_cell1.text = "Header <with> special & chars"
        mock_cell2 = mocker.MagicMock()
        mock_cell2.text = 'Header "with" quotes'
        mock_cell3 = mocker.MagicMock()
        mock_cell3.text = "Data <script>alert('xss')</script>"
        mock_cell4 = mocker.MagicMock()
        mock_cell4.text = 'Data & more "special" chars'

        mock_row1.cells = [mock_cell1, mock_cell2]
        mock_row2.cells = [mock_cell3, mock_cell4]
        mock_table.rows = [mock_row1, mock_row2]
        mock_table_shape.table = mock_table

        mock_slide.shapes = [mock_table_shape]
        mock_slide.has_notes_slide = False
        mock_presentation.slides = [mock_slide]
        mock_presentation.core_properties = mocker.MagicMock()
        mock_presentation.core_properties.author = None

        mocker.patch("pptx.Presentation", return_value=mock_presentation)

        result = extractor.extract_bytes_sync(b"mock pptx content")

        # Content should be HTML escaped
        assert "&lt;with&gt;" in result.content
        assert "&amp;" in result.content
        assert "&quot;with&quot;" in result.content
        assert "&lt;script&gt;" in result.content
        assert "<table>" in result.content
        assert "<th>" in result.content
        assert "<td>" in result.content
        assert result.mime_type == "text/markdown"

    def test_extract_pptx_table_empty_cells(self, mocker: MockerFixture, extractor: PresentationExtractor) -> None:
        """Test table extraction with empty cells."""
        from pptx.enum.shapes import MSO_SHAPE_TYPE

        mock_presentation = mocker.MagicMock()
        mock_slide = mocker.MagicMock()
        mock_table_shape = mocker.MagicMock()

        mock_table_shape.shape_type = MSO_SHAPE_TYPE.TABLE

        mock_table = mocker.MagicMock()
        mock_row1 = mocker.MagicMock()
        mock_row2 = mocker.MagicMock()

        # Mix of empty and filled cells
        mock_cell1 = mocker.MagicMock()
        mock_cell1.text = ""  # Empty cell
        mock_cell2 = mocker.MagicMock()
        mock_cell2.text = "Header2"
        mock_cell3 = mocker.MagicMock()
        mock_cell3.text = "Data1"
        mock_cell4 = mocker.MagicMock()
        mock_cell4.text = ""  # Empty cell

        mock_row1.cells = [mock_cell1, mock_cell2]
        mock_row2.cells = [mock_cell3, mock_cell4]
        mock_table.rows = [mock_row1, mock_row2]
        mock_table_shape.table = mock_table

        mock_slide.shapes = [mock_table_shape]
        mock_slide.has_notes_slide = False
        mock_presentation.slides = [mock_slide]
        mock_presentation.core_properties = mocker.MagicMock()
        mock_presentation.core_properties.author = None

        mocker.patch("pptx.Presentation", return_value=mock_presentation)

        result = extractor.extract_bytes_sync(b"mock pptx content")

        # Should handle empty cells properly
        assert "<th></th>" in result.content
        assert "<th>Header2</th>" in result.content
        assert "<td>Data1</td>" in result.content
        assert "<td></td>" in result.content
        assert result.mime_type == "text/markdown"


class TestPresentationExtractorImageProcessingEdgeCases:
    """Test image processing edge cases."""

    def test_extract_pptx_picture_shape_special_characters_in_name(
        self, mocker: MockerFixture, extractor: PresentationExtractor
    ) -> None:
        """Test picture extraction with special characters in shape name."""
        from pptx.enum.shapes import MSO_SHAPE_TYPE

        mock_presentation = mocker.MagicMock()
        mock_slide = mocker.MagicMock()
        mock_picture_shape = mocker.MagicMock()

        mock_picture_shape.shape_type = MSO_SHAPE_TYPE.PICTURE
        mock_picture_shape.name = "test-image_with@special#chars!"  # Contains non-word characters

        # Mock alt text extraction
        mock_element = mocker.MagicMock()
        mock_nvXxPr = mocker.MagicMock()
        mock_cNvPr = mocker.MagicMock()
        mock_cNvPr.attrib = {"descr": "Image with special chars"}
        mock_nvXxPr.cNvPr = mock_cNvPr
        mock_element._nvXxPr = mock_nvXxPr
        mock_picture_shape._element = mock_element

        mock_slide.shapes = [mock_picture_shape]
        mock_slide.has_notes_slide = False
        mock_presentation.slides = [mock_slide]
        mock_presentation.core_properties = mocker.MagicMock()
        mock_presentation.core_properties.author = None

        mocker.patch("pptx.Presentation", return_value=mock_presentation)

        result = extractor.extract_bytes_sync(b"mock pptx content")

        # Non-word characters should be removed from filename
        assert "![Image with special chars](testimagewithspecialchars.jpg)" in result.content
        assert result.mime_type == "text/markdown"

    def test_extract_pptx_placeholder_without_image_attribute(
        self, mocker: MockerFixture, extractor: PresentationExtractor
    ) -> None:
        """Test placeholder shapes without image attribute are not processed as images."""
        from pptx.enum.shapes import MSO_SHAPE_TYPE

        mock_presentation = mocker.MagicMock()
        mock_slide = mocker.MagicMock()
        mock_placeholder_shape = mocker.MagicMock()

        mock_placeholder_shape.shape_type = MSO_SHAPE_TYPE.PLACEHOLDER
        mock_placeholder_shape.name = "text_placeholder"
        # Placeholder does NOT have image attribute
        mock_placeholder_shape.has_text_frame = True
        mock_placeholder_shape.text = "Placeholder text content"

        mock_slide.shapes = [mock_placeholder_shape]
        mock_slide.has_notes_slide = False
        mock_presentation.slides = [mock_slide]
        mock_presentation.core_properties = mocker.MagicMock()
        mock_presentation.core_properties.author = None

        mocker.patch("pptx.Presentation", return_value=mock_presentation)

        result = extractor.extract_bytes_sync(b"mock pptx content")

        # Should be processed as text, not image
        assert "Placeholder text content" in result.content
        assert "![" not in result.content  # No image markdown
        assert result.mime_type == "text/markdown"
