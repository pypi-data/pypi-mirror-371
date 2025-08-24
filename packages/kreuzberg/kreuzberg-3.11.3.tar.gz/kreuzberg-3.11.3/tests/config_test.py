"""Tests for configuration discovery and loading."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

from kreuzberg._config import (
    _build_ocr_config_from_cli,
    _configure_gmft,
    _configure_ocr_backend,
    _merge_cli_args,
    _merge_file_config,
    build_extraction_config,
    build_extraction_config_from_dict,
    discover_and_load_config,
    find_config_file,
    find_default_config,
    load_config_from_file,
    load_config_from_path,
    load_default_config,
    merge_configs,
    parse_ocr_backend_config,
    try_discover_config,
)
from kreuzberg._gmft import GMFTConfig
from kreuzberg._ocr._easyocr import EasyOCRConfig
from kreuzberg._ocr._paddleocr import PaddleOCRConfig
from kreuzberg._ocr._tesseract import PSMMode, TesseractConfig
from kreuzberg._types import ExtractionConfig
from kreuzberg.exceptions import ValidationError


class TestConfigFileLoading:
    """Test configuration file loading functionality."""

    def test_load_kreuzberg_toml(self, tmp_path: Path) -> None:
        """Test loading from kreuzberg.toml file."""
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("""
force_ocr = true
chunk_content = false
extract_tables = true
max_chars = 1000
""")

        result = load_config_from_file(config_file)
        assert result == {
            "force_ocr": True,
            "chunk_content": False,
            "extract_tables": True,
            "max_chars": 1000,
        }

    def test_load_pyproject_toml(self, tmp_path: Path) -> None:
        """Test loading from pyproject.toml with [tool.kreuzberg] section."""
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text("""
[build-system]
requires = ["hatchling"]

[tool.kreuzberg]
force_ocr = true
ocr_backend = "tesseract"
""")

        result = load_config_from_file(config_file)
        assert result == {"force_ocr": True, "ocr_backend": "tesseract"}

    def test_load_pyproject_toml_no_kreuzberg_section(self, tmp_path: Path) -> None:
        """Test loading from pyproject.toml without [tool.kreuzberg] section."""
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text("""
[build-system]
requires = ["hatchling"]
""")

        result = load_config_from_file(config_file)
        assert result == {}

    def test_load_missing_file(self, tmp_path: Path) -> None:
        """Test error when config file doesn't exist."""
        config_file = tmp_path / "nonexistent.toml"

        with pytest.raises(ValidationError, match="Configuration file not found"):
            load_config_from_file(config_file)

    def test_load_invalid_toml(self, tmp_path: Path) -> None:
        """Test error when TOML file is invalid."""
        config_file = tmp_path / "invalid.toml"
        config_file.write_text("invalid [ toml")

        with pytest.raises(ValidationError, match="Invalid TOML"):
            load_config_from_file(config_file)

    def test_load_nested_config(self, tmp_path: Path) -> None:
        """Test loading nested configuration."""
        config_path = tmp_path / "kreuzberg.toml"
        config_content = """
ocr_backend = "tesseract"
extract_tables = true

[tesseract]
language = "eng+fra"
psm = 6
config = "--oem 1"

[gmft]
verbosity = 2
detector_base_threshold = 0.7
"""
        config_path.write_text(config_content)

        result = load_config_from_file(config_path)

        assert result["ocr_backend"] == "tesseract"
        assert result["extract_tables"] is True
        assert result["tesseract"]["language"] == "eng+fra"
        assert result["tesseract"]["psm"] == 6
        assert result["gmft"]["verbosity"] == 2


class TestConfigDiscovery:
    """Test configuration file discovery functionality."""

    def test_find_kreuzberg_toml(self, tmp_path: Path) -> None:
        """Test finding kreuzberg.toml file."""
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("force_ocr = true")

        result = find_config_file(tmp_path)
        assert result == config_file

    def test_find_pyproject_toml_with_kreuzberg_section(self, tmp_path: Path) -> None:
        """Test finding pyproject.toml with [tool.kreuzberg] section."""
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text("""
[tool.kreuzberg]
force_ocr = true
""")

        result = find_config_file(tmp_path)
        assert result == config_file

    def test_find_pyproject_toml_without_kreuzberg_section(self, tmp_path: Path) -> None:
        """Test that pyproject.toml without [tool.kreuzberg] is ignored."""
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text("""
[build-system]
requires = ["hatchling"]
""")

        result = find_config_file(tmp_path)
        assert result is None

    def test_find_config_prefers_kreuzberg_toml(self, tmp_path: Path) -> None:
        """Test that kreuzberg.toml is preferred over pyproject.toml."""
        kreuzberg_file = tmp_path / "kreuzberg.toml"
        pyproject_file = tmp_path / "pyproject.toml"

        kreuzberg_file.write_text("force_ocr = true")
        pyproject_file.write_text("""
[tool.kreuzberg]
force_ocr = false
""")

        result = find_config_file(tmp_path)
        assert result == kreuzberg_file

    def test_find_config_searches_up_tree(self, tmp_path: Path) -> None:
        """Test that config search goes up directory tree."""
        # Create config in parent directory
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("force_ocr = true")

        # Search from subdirectory
        subdir = tmp_path / "subdir" / "deep"
        subdir.mkdir(parents=True)

        result = find_config_file(subdir)
        assert result == config_file

    def test_find_config_no_file_found(self, tmp_path: Path) -> None:
        """Test when no config file is found."""
        result = find_config_file(tmp_path)
        assert result is None

    def test_find_config_stops_at_git_root(self, tmp_path: Path) -> None:
        """Test that config search stops at .git directory."""
        # Create .git directory
        git_dir = tmp_path / ".git"
        git_dir.mkdir()

        # Search from subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        result = find_config_file(subdir)
        assert result is None

    def test_find_config_default_start_path(self) -> None:
        """Test find_config_file with default start path."""
        with patch("pathlib.Path.cwd") as mock_cwd:
            mock_cwd.return_value = Path("/fake/path")

            # Mock the file system traversal
            with patch.object(Path, "exists", return_value=False):
                result = find_config_file()
                assert result is None

    def test_find_config_invalid_pyproject_toml(self, tmp_path: Path) -> None:
        """Test handling invalid pyproject.toml file."""
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text("invalid [ toml")

        # Should skip invalid pyproject.toml
        result = find_config_file(tmp_path)
        assert result is None


class TestConfigParsing:
    """Test configuration parsing functionality."""

    def test_merge_configs_simple(self) -> None:
        """Test merging simple configurations."""
        base = {"force_ocr": False, "max_chars": 1000}
        override = {"force_ocr": True, "chunk_content": True}

        result = merge_configs(base, override)
        assert result == {
            "force_ocr": True,
            "max_chars": 1000,
            "chunk_content": True,
        }

    def test_merge_configs_nested(self) -> None:
        """Test merging nested configurations."""
        base = {"tesseract": {"lang": "eng", "psm": 3}}
        override = {"tesseract": {"psm": 6, "oem": 1}}

        result = merge_configs(base, override)
        assert result == {"tesseract": {"lang": "eng", "psm": 6, "oem": 1}}

    def test_merge_configs_empty_base(self) -> None:
        """Test merging with empty base config."""
        base: dict[str, Any] = {}
        override = {"force_ocr": True, "max_chars": 1000}

        result = merge_configs(base, override)
        assert result == override

    def test_merge_configs_empty_override(self) -> None:
        """Test merging with empty override config."""
        base = {"force_ocr": True, "max_chars": 1000}
        override: dict[str, Any] = {}

        result = merge_configs(base, override)
        assert result == base

    def test_merge_configs_deep_nesting(self) -> None:
        """Test merging deeply nested configurations."""
        base = {"level1": {"level2": {"level3": {"value1": "base", "value2": "keep"}}}}
        override = {"level1": {"level2": {"level3": {"value1": "override", "value3": "new"}}}}

        result = merge_configs(base, override)
        assert result == {"level1": {"level2": {"level3": {"value1": "override", "value2": "keep", "value3": "new"}}}}

    def test_parse_tesseract_config(self) -> None:
        """Test parsing Tesseract OCR configuration."""
        config_dict = {"tesseract": {"language": "eng", "psm": 6}}

        result = parse_ocr_backend_config(config_dict, "tesseract")
        assert isinstance(result, TesseractConfig)
        assert result.language == "eng"
        assert result.psm.value == 6

    def test_parse_tesseract_config_with_all_fields(self) -> None:
        """Test parsing Tesseract configuration with all fields."""
        config_dict = {
            "tesseract": {
                "language": "eng+fra",
                "psm": 6,
                "tessedit_char_whitelist": "0123456789",
            }
        }

        result = parse_ocr_backend_config(config_dict, "tesseract")
        assert isinstance(result, TesseractConfig)
        assert result.language == "eng+fra"
        assert result.psm == PSMMode.SINGLE_BLOCK
        assert result.tessedit_char_whitelist == "0123456789"

    def test_parse_easyocr_config(self) -> None:
        """Test parsing EasyOCR configuration."""
        config_dict = {
            "easyocr": {
                "language": ["en", "fr"],
            }
        }

        result = parse_ocr_backend_config(config_dict, "easyocr")
        assert isinstance(result, EasyOCRConfig)
        assert result.language == ["en", "fr"]

    def test_parse_paddleocr_config(self) -> None:
        """Test parsing PaddleOCR configuration."""
        config_dict = {
            "paddleocr": {
                "language": "en",
                "use_angle_cls": True,
                "use_gpu": False,
            }
        }

        result = parse_ocr_backend_config(config_dict, "paddleocr")
        assert isinstance(result, PaddleOCRConfig)
        assert result.language == "en"
        assert result.use_angle_cls is True
        assert result.use_gpu is False

    def test_parse_ocr_config_missing_backend(self) -> None:
        """Test parsing when OCR backend config is missing."""
        config_dict = {"other_setting": "value"}

        result = parse_ocr_backend_config(config_dict, "tesseract")
        assert result is None

    def test_parse_ocr_config_invalid_type(self) -> None:
        """Test parsing when OCR backend config is not a dict."""
        config_dict = {"tesseract": "invalid"}

        result = parse_ocr_backend_config(config_dict, "tesseract")
        assert result is None

    def test_parse_ocr_config_invalid_backend(self) -> None:
        """Test parsing with invalid backend name."""
        config_dict = {"tesseract": {"language": "eng"}}

        result = parse_ocr_backend_config(config_dict, "invalid_backend")  # type: ignore[arg-type]
        assert result is None


class TestExtractionConfigBuilder:
    """Test ExtractionConfig building functionality."""


# Additional functional tests for better coverage
def test_merge_configs_deep_merge() -> None:
    """Test deep merging of configuration dictionaries."""
    base = {
        "force_ocr": False,
        "tesseract": {"language": "eng", "psm": 6},
        "nested": {"deep": {"value": "base"}},
    }
    override = {
        "force_ocr": True,
        "tesseract": {"psm": 3},
        "nested": {"deep": {"value": "override", "new": "added"}},
        "new_key": "new_value",
    }

    result = merge_configs(base, override)

    assert result["force_ocr"] is True
    assert result["tesseract"]["language"] == "eng"  # Preserved from base
    assert result["tesseract"]["psm"] == 3  # Overridden
    assert result["nested"]["deep"]["value"] == "override"
    assert result["nested"]["deep"]["new"] == "added"
    assert result["new_key"] == "new_value"


def test_build_extraction_config_from_dict_with_all_options() -> None:
    """Test building ExtractionConfig with all available options."""
    config_dict = {
        "force_ocr": True,
        "chunk_content": True,
        "max_chars": 500,
        "max_overlap": 50,
        "extract_tables": True,
        "extract_entities": True,
        "extract_keywords": True,
        "keyword_count": 15,
        "auto_detect_document_type": True,
        "document_type_confidence_threshold": 0.8,
        "auto_detect_language": True,
        "ocr_backend": "tesseract",
        "tesseract": {"language": "fra", "psm": 6},
        "gmft": {"verbosity": 2, "formatter_base_threshold": 0.4},
    }

    config = build_extraction_config_from_dict(config_dict)

    assert config.force_ocr is True
    assert config.chunk_content is True
    assert config.max_chars == 500
    assert config.max_overlap == 50
    assert config.extract_tables is True
    assert config.extract_entities is True
    assert config.extract_keywords is True
    assert config.keyword_count == 15
    assert config.auto_detect_document_type is True
    assert config.document_type_confidence_threshold == 0.8
    assert config.auto_detect_language is True
    assert config.ocr_backend == "tesseract"


def test_build_extraction_config_from_dict_invalid_ocr_backend() -> None:
    """Test handling of invalid OCR backend in config."""
    config_dict = {
        "ocr_backend": "invalid_backend",
    }

    with pytest.raises(ValidationError, match="Invalid OCR backend"):
        build_extraction_config_from_dict(config_dict)


def test_find_config_file_with_pyproject_toml(tmp_path: Path) -> None:
    """Test finding config in pyproject.toml file."""
    pyproject_file = tmp_path / "pyproject.toml"
    pyproject_file.write_text("""
[tool.kreuzberg]
force_ocr = true
chunk_content = false
""")

    result = find_config_file(tmp_path)
    assert result == pyproject_file


def test_find_config_file_no_config(tmp_path: Path) -> None:
    """Test when no config file exists."""
    result = find_config_file(tmp_path)
    assert result is None


def test_load_config_from_path_string() -> None:
    """Test loading config from string path."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write("force_ocr = true\nchunk_content = false\n")
        f.flush()
        temp_path = f.name

    try:
        config = load_config_from_path(temp_path)
        assert config.force_ocr is True
        assert config.chunk_content is False
    finally:
        Path(temp_path).unlink()


def test_discover_and_load_config_with_default(tmp_path: Path) -> None:
    """Test discovery that raises error when no config found."""
    with pytest.raises(ValidationError, match="No configuration file found"):
        discover_and_load_config(str(tmp_path))


def test_try_discover_config_returns_none(tmp_path: Path) -> None:
    """Test try_discover_config returns None when no config found."""
    result = try_discover_config(str(tmp_path))
    assert result is None


def test_build_extraction_config_comprehensive() -> None:
    """Test building ExtractionConfig with comprehensive options."""
    config_dict = {
        "force_ocr": True,
        "chunk_content": False,
        "extract_tables": True,
        "max_chars": 2000,
        "auto_detect_document_type": True,
    }

    config = build_extraction_config_from_dict(config_dict)

    assert config.force_ocr is True
    assert config.chunk_content is False
    assert config.extract_tables is True
    assert config.max_chars == 2000
    assert config.auto_detect_document_type is True


def test_build_from_dict_with_ocr_config() -> None:
    """Test building ExtractionConfig with OCR configuration."""
    config_dict = {
        "force_ocr": True,
        "ocr_backend": "tesseract",
        "tesseract": {"language": "eng", "psm": 6},
    }

    result = build_extraction_config_from_dict(config_dict)
    assert result.ocr_backend == "tesseract"
    assert isinstance(result.ocr_config, TesseractConfig)
    assert result.ocr_config.language == "eng"


def test_build_from_dict_ocr_backend_none() -> None:
    """Test building ExtractionConfig with OCR backend set to 'none'."""
    config_dict = {"ocr_backend": "none"}

    result = build_extraction_config_from_dict(config_dict)
    assert result.ocr_backend is None


def test_merge_cli_args_with_boolean_flags() -> None:
    """Test merging CLI args with boolean flags."""
    base_config = {"force_ocr": False, "chunk_content": True}
    cli_args = {"force_ocr": True, "extract_tables": True}

    _merge_cli_args(base_config, cli_args)

    assert base_config["force_ocr"] is True
    assert base_config["chunk_content"] is True  # Preserved
    assert base_config["extract_tables"] is True  # Added


def test_merge_file_config_with_missing_keys() -> None:
    """Test merging file config when some keys are missing."""
    base_config = {"force_ocr": False, "chunk_content": True}
    file_config = {"chunk_content": False}  # Missing force_ocr

    _merge_file_config(base_config, file_config)

    assert base_config["force_ocr"] is False  # Preserved from base
    assert base_config["chunk_content"] is False  # Overridden


def test_build_from_dict_with_gmft_config() -> None:
    """Test building ExtractionConfig with GMFT configuration."""
    config_dict = {
        "extract_tables": True,
        "gmft": {
            "verbosity": 2,
            "detector_base_threshold": 0.7,
        },
    }

    result = build_extraction_config_from_dict(config_dict)
    assert result.extract_tables is True
    assert isinstance(result.gmft_config, GMFTConfig)
    assert result.gmft_config.verbosity == 2


def test_build_extraction_config_file_cli_merge() -> None:
    """Test building ExtractionConfig with file and CLI argument merging."""
    file_config = {
        "max_chars": 1000,
        "tesseract": {"language": "eng"},
    }
    cli_args = {
        "force_ocr": True,
        "ocr_backend": "tesseract",
    }

    result = build_extraction_config(file_config, cli_args)
    assert result.force_ocr is True  # CLI overrides file
    assert result.max_chars == 1000  # File value preserved
    assert result.ocr_backend == "tesseract"


def test_build_extraction_config_complete() -> None:
    """Test building ExtractionConfig with all supported fields."""
    config_dict = {
        "force_ocr": True,
        "chunk_content": True,
        "extract_tables": True,
        "max_chars": 4000,
        "max_overlap": 200,
        "language_detection_threshold": 0.8,
        "auto_detect_language": True,
        "document_classification_mode": "text",
        "document_type_confidence_threshold": 0.7,
        "ocr_backend": "tesseract",
        "tesseract": {"language": "eng+fra"},
        "gmft": {"verbosity": 1},
    }

    result = build_extraction_config_from_dict(config_dict)
    assert result.force_ocr is True
    assert result.chunk_content is True
    assert result.extract_tables is True
    assert result.max_chars == 4000
    assert result.max_overlap == 200
    assert result.auto_detect_language is True
    assert result.ocr_backend == "tesseract"


class TestHighLevelAPI:
    """Test high-level configuration API."""

    def test_load_config_from_path(self, tmp_path: Path) -> None:
        """Test loading configuration from specific path."""
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("""
force_ocr = true
chunk_content = false
""")

        result = load_config_from_path(config_file)
        assert isinstance(result, ExtractionConfig)
        assert result.force_ocr is True
        assert result.chunk_content is False

    def test_discover_and_load_config(self, tmp_path: Path) -> None:
        """Test discovering and loading configuration."""
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("force_ocr = true")

        result = discover_and_load_config(tmp_path)
        assert isinstance(result, ExtractionConfig)
        assert result.force_ocr is True

    def test_discover_and_load_config_not_found(self, tmp_path: Path) -> None:
        """Test error when no config file is discovered."""
        with pytest.raises(ValidationError, match="No configuration file found"):
            discover_and_load_config(tmp_path)

    def test_discover_and_load_config_empty(self, tmp_path: Path) -> None:
        """Test error when config file exists but is empty."""
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text("""
[build-system]
requires = ["hatchling"]
""")

        with pytest.raises(ValidationError, match="No configuration file found"):
            discover_and_load_config(tmp_path)

    def test_try_discover_config_success(self, tmp_path: Path) -> None:
        """Test try_discover_config with successful discovery."""
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("force_ocr = true")

        result = try_discover_config(tmp_path)
        assert isinstance(result, ExtractionConfig)
        assert result.force_ocr is True

    def test_try_discover_config_not_found(self, tmp_path: Path) -> None:
        """Test try_discover_config when no config is found."""
        result = try_discover_config(tmp_path)
        assert result is None

    def test_try_discover_config_invalid(self, tmp_path: Path) -> None:
        """Test try_discover_config with invalid config."""
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("invalid [ toml")

        result = try_discover_config(tmp_path)
        assert result is None

    def test_load_default_config(self, tmp_path: Path) -> None:
        """Test deprecated load_default_config function."""
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("force_ocr = true")

        with patch("kreuzberg._config.find_config_file") as mock_find:
            mock_find.return_value = config_file

            result = load_default_config()

            assert isinstance(result, ExtractionConfig)
            assert result.force_ocr is True


class TestLegacyFunctions:
    """Test legacy/internal configuration functions."""

    def test_merge_file_config(self) -> None:
        """Test _merge_file_config function."""
        config_dict: dict[str, Any] = {"existing": "value"}
        file_config = {
            "force_ocr": True,
            "max_chars": 1000,
            "chunk_content": False,
            "unknown_field": "ignored",
        }

        _merge_file_config(config_dict, file_config)

        assert config_dict["force_ocr"] is True
        assert config_dict["chunk_content"] is False
        assert "unknown_field" not in config_dict
        assert config_dict["existing"] == "value"

    def test_merge_file_config_empty(self) -> None:
        """Test _merge_file_config with empty file config."""
        config_dict: dict[str, Any] = {"existing": "value"}

        _merge_file_config(config_dict, {})

        assert config_dict == {"existing": "value"}

    def test_merge_cli_args(self) -> None:
        """Test _merge_cli_args function."""
        config_dict: dict[str, Any] = {}
        cli_args: dict[str, Any] = {
            "force_ocr": True,
            "chunk_content": None,  # Should be ignored
            "max_chars": 2000,
            "extract_tables": True,
            "ocr_backend": "tesseract",
        }

        _merge_cli_args(config_dict, cli_args)

        assert config_dict["force_ocr"] is True
        assert "chunk_content" not in config_dict
        assert config_dict["max_chars"] == 2000
        assert config_dict["extract_tables"] is True
        assert config_dict["ocr_backend"] == "tesseract"

    def test_build_ocr_config_from_cli_tesseract(self) -> None:
        """Test _build_ocr_config_from_cli with Tesseract config."""
        cli_args = {"tesseract_config": {"language": "eng", "psm": 6}}

        result = _build_ocr_config_from_cli("tesseract", cli_args)

        assert isinstance(result, TesseractConfig)
        assert result.language == "eng"
        assert result.psm == 6  # type: ignore[comparison-overlap]  # PSM value is not converted to enum in _build_ocr_config_from_cli

    def test_build_ocr_config_from_cli_easyocr(self) -> None:
        """Test _build_ocr_config_from_cli with EasyOCR config."""
        cli_args = {"easyocr_config": {"language": ["en", "fr"]}}

        result = _build_ocr_config_from_cli("easyocr", cli_args)

        assert isinstance(result, EasyOCRConfig)
        assert result.language == ["en", "fr"]

    def test_build_ocr_config_from_cli_paddleocr(self) -> None:
        """Test _build_ocr_config_from_cli with PaddleOCR config."""
        cli_args = {"paddleocr_config": {"language": "en", "use_gpu": False}}

        result = _build_ocr_config_from_cli("paddleocr", cli_args)

        assert isinstance(result, PaddleOCRConfig)
        assert result.language == "en"
        assert result.use_gpu is False

    def test_build_ocr_config_from_cli_no_config(self) -> None:
        """Test _build_ocr_config_from_cli with no config."""
        cli_args: dict[str, Any] = {}

        result = _build_ocr_config_from_cli("tesseract", cli_args)

        assert result is None

    def test_configure_ocr_backend(self) -> None:
        """Test _configure_ocr_backend function."""
        config_dict = {"ocr_backend": "tesseract"}
        file_config: dict[str, Any] = {"tesseract": {"language": "eng", "psm": 3}}
        cli_args: dict[str, Any] = {}

        _configure_ocr_backend(config_dict, file_config, cli_args)

        assert "ocr_config" in config_dict
        assert isinstance(config_dict["ocr_config"], TesseractConfig)

    def test_configure_ocr_backend_cli_priority(self) -> None:
        """Test that CLI config takes priority over file config."""
        config_dict = {"ocr_backend": "tesseract"}
        file_config: dict[str, Any] = {"tesseract": {"language": "eng"}}
        cli_args: dict[str, Any] = {"tesseract_config": {"language": "fra"}}

        _configure_ocr_backend(config_dict, file_config, cli_args)

        assert isinstance(config_dict["ocr_config"], TesseractConfig)
        assert config_dict["ocr_config"].language == "fra"

    def test_configure_ocr_backend_none(self) -> None:
        """Test OCR backend configuration when backend is None."""
        config_dict = {"ocr_backend": None}
        file_config: dict[str, Any] = {}
        cli_args: dict[str, Any] = {}

        _configure_ocr_backend(config_dict, file_config, cli_args)

        assert "ocr_config" not in config_dict

    def test_configure_gmft(self) -> None:
        """Test _configure_gmft function."""
        config_dict = {"extract_tables": True}
        file_config: dict[str, Any] = {"gmft": {"verbosity": 2, "detector_base_threshold": 0.7}}
        cli_args: dict[str, Any] = {}

        _configure_gmft(config_dict, file_config, cli_args)

        assert "gmft_config" in config_dict
        assert isinstance(config_dict["gmft_config"], GMFTConfig)
        assert config_dict["gmft_config"].verbosity == 2

    def test_configure_gmft_cli_priority(self) -> None:
        """Test that CLI GMFT config takes priority."""
        config_dict = {"extract_tables": True}
        file_config: dict[str, Any] = {"gmft": {"detector_base_threshold": 0.5}}
        cli_args: dict[str, Any] = {"gmft_config": {"detector_base_threshold": 0.9}}

        _configure_gmft(config_dict, file_config, cli_args)

        assert isinstance(config_dict["gmft_config"], GMFTConfig)
        assert config_dict["gmft_config"].detector_base_threshold == 0.9

    def test_configure_gmft_no_extract_tables(self) -> None:
        """Test GMFT configuration when extract_tables is False."""
        config_dict = {"extract_tables": False}
        file_config: dict[str, Any] = {"gmft": {"verbosity": 2}}
        cli_args: dict[str, Any] = {}

        _configure_gmft(config_dict, file_config, cli_args)

        assert "gmft_config" not in config_dict

    def test_build_extraction_config_integration(self) -> None:
        """Test full integration of build_extraction_config."""
        file_config = {
            "force_ocr": False,
            "max_chars": 1000,
            "ocr_backend": "tesseract",
            "tesseract": {"language": "eng", "psm": 3},
            "gmft": {"verbosity": 1},
        }
        cli_args = {
            "force_ocr": True,
            "extract_tables": True,
            "tesseract_config": {"language": "fra"},
        }

        result = build_extraction_config(file_config, cli_args)

        assert result.force_ocr is True  # CLI override
        assert result.max_chars == 1000  # File value
        assert result.ocr_backend == "tesseract"  # File value
        assert result.extract_tables is True  # CLI value
        assert result.ocr_config is not None
        assert isinstance(result.ocr_config, TesseractConfig)
        assert result.ocr_config.language == "fra"  # CLI override

    def test_find_default_config_deprecated(self) -> None:
        """Test deprecated find_default_config function."""
        with patch("kreuzberg._config.find_config_file") as mock_find:
            mock_find.return_value = Path("/fake/config.toml")

            result = find_default_config()

            assert result == Path("/fake/config.toml")
            mock_find.assert_called_once_with()


class TestConfigIntegration:
    """Test configuration system integration scenarios."""

    def test_real_world_pyproject_toml(self, tmp_path: Path) -> None:
        """Test with realistic pyproject.toml configuration."""
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text("""
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-project"
version = "1.0.0"

[tool.kreuzberg]
force_ocr = false
chunk_content = true
extract_tables = true
max_chars = 4000
max_overlap = 200
ocr_backend = "tesseract"
auto_detect_language = true

[tool.kreuzberg.tesseract]
language = "eng+fra"
psm = 6

[tool.kreuzberg.gmft]
verbosity = 1
""")

        config = load_config_from_path(config_file)
        assert config.force_ocr is False
        assert config.chunk_content is True
        assert config.extract_tables is True
        assert config.max_chars == 4000
        assert config.max_overlap == 200
        assert config.ocr_backend == "tesseract"
        assert config.auto_detect_language is True

        # Check nested OCR config
        assert isinstance(config.ocr_config, TesseractConfig)
        assert config.ocr_config.language == "eng+fra"
        assert config.ocr_config.psm.value == 6

    def test_config_discovery_with_cwd(self) -> None:
        """Test config discovery using current working directory."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            config_file = tmp_path / "kreuzberg.toml"
            config_file.write_text("force_ocr = true")

            # Change to temp directory and test discovery
            import os

            original_cwd = Path.cwd()
            try:
                os.chdir(tmp_dir)
                result = try_discover_config()
                assert result is not None
                assert result.force_ocr is True
            finally:
                os.chdir(str(original_cwd))

    def test_config_priority_kreuzberg_over_pyproject(self, tmp_path: Path) -> None:
        """Test that kreuzberg.toml takes priority over pyproject.toml."""
        # Create both files with different settings
        kreuzberg_file = tmp_path / "kreuzberg.toml"
        kreuzberg_file.write_text("force_ocr = true")

        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text("""
[tool.kreuzberg]
force_ocr = false
""")

        config = discover_and_load_config(tmp_path)
        assert config.force_ocr is True  # Should use kreuzberg.toml value

    def test_complex_config_merging(self) -> None:
        """Test complex configuration merging scenario."""
        # File config (from kreuzberg.toml)
        file_config = {
            "force_ocr": False,
            "chunk_content": True,
            "max_chars": 1000,
            "ocr_backend": "tesseract",
            "tesseract": {"language": "eng", "psm": 3},
            "gmft": {"verbosity": 1, "detector_base_threshold": 0.5},
        }

        # CLI arguments override
        cli_args = {
            "force_ocr": True,  # Override
            "extract_tables": True,  # New setting
            "tesseract_config": {
                "language": "eng+fra"  # Override
            },
            "gmft_config": {
                "verbosity": 2  # Override
            },
        }

        result = build_extraction_config(file_config, cli_args)

        # Check CLI overrides
        assert result.force_ocr is True
        assert result.extract_tables is True

        # Check file values preserved
        assert result.chunk_content is True
        assert result.max_chars == 1000

        # Check OCR config merging
        assert isinstance(result.ocr_config, TesseractConfig)
        assert result.ocr_config.language == "eng+fra"  # CLI override
        assert result.ocr_config.psm.value == 3  # File value

        # Check GMFT config
        assert isinstance(result.gmft_config, GMFTConfig)
        assert result.gmft_config.verbosity == 2  # CLI override
        # Note: detector_base_threshold defaults to 0.9 when not specified


# =============================================================================
# COMPREHENSIVE TESTS (for improved coverage)
# =============================================================================


class TestConfigFileLoadingComprehensive:
    """Comprehensive tests for configuration file loading."""

    def test_load_arbitrary_toml_file(self, tmp_path: Path) -> None:
        """Test loading from arbitrary .toml file (not kreuzberg.toml or pyproject.toml)."""
        config_file = tmp_path / "custom.toml"
        config_file.write_text("""
force_ocr = true
chunk_content = false
ocr_backend = "tesseract"
""")

        result: dict[str, Any] = load_config_from_file(config_file)
        # Should load as root-level config
        assert result == {
            "force_ocr": True,
            "chunk_content": False,
            "ocr_backend": "tesseract",
        }

    def test_load_pyproject_toml_with_tool_no_kreuzberg(self, tmp_path: Path) -> None:
        """Test loading pyproject.toml with [tool] section but no [tool.kreuzberg]."""
        config_file = tmp_path / "pyproject.toml"
        config_file.write_text("""
[tool.black]
line-length = 88

[tool.mypy]
strict = true
""")

        result = load_config_from_file(config_file)
        assert result == {}

    def test_load_empty_config_file(self, tmp_path: Path) -> None:
        """Test loading empty configuration file."""
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("")

        result = load_config_from_file(config_file)
        assert result == {}

    def test_load_config_with_comments(self, tmp_path: Path) -> None:
        """Test loading config with comments and complex formatting."""
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("""
# Main configuration
force_ocr = true  # Force OCR processing

# OCR settings
ocr_backend = "tesseract"

[tesseract]
# Language settings
language = "eng+fra"  # English and French
psm = 6
tessedit_char_whitelist = "0123456789"
""")

        result = load_config_from_file(config_file)
        assert result["force_ocr"] is True
        assert result["ocr_backend"] == "tesseract"
        assert result["tesseract"]["language"] == "eng+fra"
        assert result["tesseract"]["tessedit_char_whitelist"] == "0123456789"


class TestConfigDiscoveryComprehensive:
    """Comprehensive tests for configuration discovery."""

    def test_find_config_handles_permission_error(self, tmp_path: Path) -> None:
        """Test that permission errors in pyproject.toml are silently handled."""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text("""
[tool.kreuzberg]
force_ocr = true
""")

        with patch("pathlib.Path.open", side_effect=PermissionError("No access")):
            result = find_config_file(tmp_path)
            assert result is None

    def test_find_config_handles_generic_exception(self, tmp_path: Path) -> None:
        """Test that generic exceptions in pyproject.toml are handled."""
        pyproject_file = tmp_path / "pyproject.toml"
        pyproject_file.write_text("""
[tool.kreuzberg]
force_ocr = true
""")

        with patch("kreuzberg._config.tomllib.load", side_effect=Exception("Unexpected error")):
            result = find_config_file(tmp_path)
            assert result is None

    def test_find_config_at_root_directory(self) -> None:
        """Test config discovery when reaching root directory."""
        # Mock a path that's already at root
        with patch("pathlib.Path.parent", new_callable=lambda: property(lambda self: self)):
            root_path = Path("/")
            result = find_config_file(root_path)
            assert result is None


class TestConfigParsingComprehensive:
    """Comprehensive tests for configuration parsing."""

    def test_parse_tesseract_config_psm_enum_conversion(self) -> None:
        """Test that PSM integer values are converted to enum."""
        config_dict = {
            "tesseract": {
                "language": "eng",
                "psm": 0,  # Should convert to PSMMode.OSD_ONLY
            }
        }

        result = parse_ocr_backend_config(config_dict, "tesseract")
        assert isinstance(result, TesseractConfig)
        assert result.psm == PSMMode.OSD_ONLY

    def test_parse_tesseract_config_all_psm_modes(self) -> None:
        """Test all PSM mode conversions."""
        for psm_value in range(11):  # PSM modes 0-10
            config_dict = {"tesseract": {"psm": psm_value}}
            result = parse_ocr_backend_config(config_dict, "tesseract")
            assert isinstance(result, TesseractConfig)
            assert result.psm.value == psm_value

    def test_parse_tesseract_config_with_boolean_fields(self) -> None:
        """Test Tesseract config with boolean fields."""
        config_dict = {
            "tesseract": {
                "language": "eng",
                "tessedit_enable_dict_correction": False,
                "tessedit_use_primary_params_model": False,
                "textord_space_size_is_variable": False,
            }
        }

        result = parse_ocr_backend_config(config_dict, "tesseract")
        assert isinstance(result, TesseractConfig)
        assert result.tessedit_enable_dict_correction is False
        assert result.tessedit_use_primary_params_model is False
        assert result.textord_space_size_is_variable is False

    def test_parse_paddleocr_config_all_fields(self) -> None:
        """Test PaddleOCR config with all supported fields."""
        config_dict = {
            "paddleocr": {
                "language": "ch",
                "use_gpu": True,
                "use_angle_cls": False,
                "det_db_box_thresh": 0.6,
                "det_db_thresh": 0.4,
                "det_db_unclip_ratio": 2.5,
                "max_text_length": 100,
                "use_space_char": False,
                "drop_score": 0.3,
                "enable_mkldnn": True,
                "gpu_mem": 4000,
                "rec": False,
                "table": False,
                "device": "cuda",
                "gpu_memory_limit": 4.0,
                "fallback_to_cpu": False,
            }
        }

        result = parse_ocr_backend_config(config_dict, "paddleocr")
        assert isinstance(result, PaddleOCRConfig)
        assert result.language == "ch"
        assert result.use_gpu is True
        assert result.use_angle_cls is False
        assert result.det_db_box_thresh == 0.6
        assert result.det_db_thresh == 0.4
        assert result.det_db_unclip_ratio == 2.5
        assert result.max_text_length == 100
        assert result.use_space_char is False
        assert result.drop_score == 0.3
        assert result.enable_mkldnn is True
        assert result.gpu_mem == 4000
        assert result.rec is False
        assert result.table is False
        assert result.device == "cuda"
        assert result.gpu_memory_limit == 4.0
        assert result.fallback_to_cpu is False

    def test_parse_easyocr_config_all_fields(self) -> None:
        """Test EasyOCR config with all supported fields."""
        config_dict = {
            "easyocr": {
                "language": ["en", "fr", "de"],
                "add_margin": 0.2,
                "adjust_contrast": 0.7,
                "beam_width": 10,
                "canvas_size": 3000,
                "contrast_ths": 0.2,
                "decoder": "beamsearch",
                "height_ths": 0.6,
                "link_threshold": 0.5,
                "low_text": 0.5,
                "mag_ratio": 1.5,
                "min_size": 20,
                "rotation_info": [0, 90, 180, 270],
                "slope_ths": 0.2,
                "use_gpu": False,
                "device": "cpu",
            }
        }

        result = parse_ocr_backend_config(config_dict, "easyocr")
        assert isinstance(result, EasyOCRConfig)
        assert result.language == ["en", "fr", "de"]
        assert result.add_margin == 0.2
        assert result.adjust_contrast == 0.7
        assert result.beam_width == 10
        assert result.canvas_size == 3000
        assert result.contrast_ths == 0.2
        assert result.decoder == "beamsearch"
        assert result.height_ths == 0.6
        assert result.link_threshold == 0.5
        assert result.low_text == 0.5
        assert result.mag_ratio == 1.5
        assert result.min_size == 20
        assert result.rotation_info == [0, 90, 180, 270]
        assert result.slope_ths == 0.2
        assert result.use_gpu is False
        assert result.device == "cpu"

    def test_merge_configs_non_dict_override(self) -> None:
        """Test merge_configs when override value is not a dict."""
        base = {"nested": {"key": "value"}}
        override = {"nested": "string_value"}  # Replace dict with string

        result = merge_configs(base, override)
        assert result["nested"] == "string_value"

    def test_merge_configs_mixed_types(self) -> None:
        """Test merge_configs with mixed data types."""
        base = {
            "string": "base",
            "number": 100,
            "bool": False,
            "list": [1, 2, 3],
            "dict": {"inner": "base"},
        }
        override = {
            "string": "override",
            "number": 200,
            "bool": True,
            "list": [4, 5],
            "dict": {"inner": "override", "new": "value"},
        }

        result = merge_configs(base, override)
        assert result["string"] == "override"
        assert result["number"] == 200
        assert result["bool"] is True
        assert result["list"] == [4, 5]
        assert result["dict"] == {"inner": "override", "new": "value"}


class TestExtractionConfigBuilderComprehensive:
    """Comprehensive tests for ExtractionConfig building."""

    def test_build_config_with_all_basic_fields(self) -> None:
        """Test building config with all basic fields."""
        config_dict = {
            "force_ocr": True,
            "chunk_content": True,
            "extract_tables": True,
            "max_chars": 3000,
            "max_overlap": 300,
            "ocr_backend": "tesseract",
            "extract_entities": True,
            "extract_keywords": True,
            "auto_detect_language": True,
            "enable_quality_processing": False,
            "auto_detect_document_type": False,
            "document_type_confidence_threshold": 0.9,
            "document_classification_mode": "vision",
            "keyword_count": 20,
        }

        result = build_extraction_config_from_dict(config_dict)

        assert result.force_ocr is True
        assert result.chunk_content is True
        assert result.extract_tables is True
        assert result.max_chars == 3000
        assert result.max_overlap == 300
        assert result.ocr_backend == "tesseract"
        assert result.extract_entities is True
        assert result.extract_keywords is True
        assert result.auto_detect_language is True
        assert result.enable_quality_processing is False
        assert result.auto_detect_document_type is False
        assert result.document_type_confidence_threshold == 0.9
        assert result.document_classification_mode == "vision"
        assert result.keyword_count == 20

    def test_build_config_without_ocr_backend_config(self) -> None:
        """Test building config when OCR backend has no specific config."""
        config_dict = {
            "ocr_backend": "tesseract",
            # No tesseract section
        }

        result = build_extraction_config_from_dict(config_dict)
        assert result.ocr_backend == "tesseract"
        assert result.ocr_config is None

    def test_build_config_with_gmft_but_no_extract_tables(self) -> None:
        """Test that GMFT config is ignored when extract_tables is False."""
        config_dict = {
            "extract_tables": False,
            "gmft": {
                "verbosity": 2,
                "detector_base_threshold": 0.8,
            },
        }

        result = build_extraction_config_from_dict(config_dict)
        assert result.extract_tables is False
        assert result.gmft_config is None

    def test_build_config_with_extract_tables_but_no_gmft(self) -> None:
        """Test extract_tables without GMFT config."""
        config_dict = {
            "extract_tables": True,
            # No gmft section
        }

        result = build_extraction_config_from_dict(config_dict)
        assert result.extract_tables is True
        assert result.gmft_config is None

    def test_build_config_with_invalid_gmft_config(self) -> None:
        """Test handling invalid GMFT config."""
        config_dict = {
            "extract_tables": True,
            "gmft": "not_a_dict",  # Invalid
        }

        result = build_extraction_config_from_dict(config_dict)
        assert result.extract_tables is True
        assert result.gmft_config is None

    def test_build_config_minimal(self) -> None:
        """Test building config with minimal settings."""
        config_dict: dict[str, Any] = {}  # Empty config

        result = build_extraction_config_from_dict(config_dict)
        # Should use all defaults
        assert result.force_ocr is False
        assert result.chunk_content is False
        assert result.ocr_backend == "tesseract"

    def test_build_config_validation_context(self) -> None:
        """Test that validation error includes proper context."""
        config_dict = {
            "ocr_backend": "invalid_ocr",
        }

        with pytest.raises(ValidationError) as exc_info:
            build_extraction_config_from_dict(config_dict)

        assert exc_info.value.context["provided"] == "invalid_ocr"
        assert "easyocr" in exc_info.value.context["valid"]
        assert "paddleocr" in exc_info.value.context["valid"]
        assert "tesseract" in exc_info.value.context["valid"]


class TestHighLevelAPIComprehensive:
    """Comprehensive tests for high-level API functions."""

    def test_load_default_config_no_file(self) -> None:
        """Test load_default_config when no config file exists."""
        with patch("kreuzberg._config.find_config_file", return_value=None):
            result = load_default_config()
            assert result is None

    def test_load_default_config_with_error(self, tmp_path: Path) -> None:
        """Test load_default_config silently handles errors."""
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("invalid [ toml")

        with patch("kreuzberg._config.find_config_file", return_value=config_file):
            result = load_default_config()
            assert result is None

    def test_load_default_config_empty_dict(self, tmp_path: Path) -> None:
        """Test load_default_config with empty config dict."""
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("")  # Empty file

        with patch("kreuzberg._config.find_config_file", return_value=config_file):
            result = load_default_config()
            assert result is None

    def test_discover_and_load_config_with_string_path(self, tmp_path: Path) -> None:
        """Test discover_and_load_config with string path."""
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("force_ocr = true")

        result = discover_and_load_config(str(tmp_path))
        assert result.force_ocr is True

    def test_discover_and_load_config_empty_file_error(self, tmp_path: Path) -> None:
        """Test error when discovered config file is empty."""
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("")  # Empty file

        with pytest.raises(ValidationError, match="contains no Kreuzberg configuration"):
            discover_and_load_config(tmp_path)

    def test_try_discover_config_with_string_path(self, tmp_path: Path) -> None:
        """Test try_discover_config with string path."""
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("chunk_content = true")

        result = try_discover_config(str(tmp_path))
        assert result is not None
        assert result.chunk_content is True


class TestLegacyFunctionsComprehensive:
    """Comprehensive tests for legacy/internal functions."""

    def test_merge_file_config_with_none_values(self) -> None:
        """Test _merge_file_config handles None values correctly."""
        config_dict: dict[str, Any] = {}
        file_config = {
            "force_ocr": None,  # Should still be copied
            "chunk_content": True,
            "max_chars": 0,  # Falsy but valid
        }

        _merge_file_config(config_dict, file_config)

        assert config_dict["force_ocr"] is None
        assert config_dict["chunk_content"] is True
        assert config_dict["max_chars"] == 0

    def test_merge_cli_args_with_empty_dict(self) -> None:
        """Test _merge_cli_args with empty config dict."""
        config_dict: dict[str, Any] = {}
        cli_args = {
            "force_ocr": False,  # Falsy but should be included
            "chunk_content": None,  # Should be ignored
            "extract_tables": True,
            "unknown_field": "ignored",  # Not in _CONFIG_FIELDS
        }

        _merge_cli_args(config_dict, cli_args)

        assert config_dict["force_ocr"] is False
        assert "chunk_content" not in config_dict
        assert config_dict["extract_tables"] is True
        assert "unknown_field" not in config_dict

    def test_build_ocr_config_from_cli_invalid_backend(self) -> None:
        """Test _build_ocr_config_from_cli with invalid backend."""
        cli_args = {"tesseract_config": {"language": "eng"}}

        result = _build_ocr_config_from_cli("invalid_backend", cli_args)
        assert result is None

    def test_configure_ocr_backend_with_none_string(self) -> None:
        """Test _configure_ocr_backend when backend is 'none' string."""
        config_dict = {"ocr_backend": "none"}
        file_config: dict[str, Any] = {}
        cli_args: dict[str, Any] = {}

        _configure_ocr_backend(config_dict, file_config, cli_args)

        assert "ocr_config" not in config_dict

    def test_configure_ocr_backend_no_config_available(self) -> None:
        """Test _configure_ocr_backend when no config is available."""
        config_dict = {"ocr_backend": "tesseract"}
        file_config: dict[str, Any] = {}  # No tesseract config
        cli_args: dict[str, Any] = {}  # No CLI config

        _configure_ocr_backend(config_dict, file_config, cli_args)

        assert "ocr_config" not in config_dict

    def test_configure_gmft_with_none_values(self) -> None:
        """Test _configure_gmft handles None values."""
        config_dict = {"extract_tables": None}  # Falsy
        file_config: dict[str, Any] = {"gmft": {"verbosity": 2}}
        cli_args: dict[str, Any] = {}

        _configure_gmft(config_dict, file_config, cli_args)

        assert "gmft_config" not in config_dict

    def test_build_extraction_config_none_to_null_conversion(self) -> None:
        """Test build_extraction_config converts 'none' to None."""
        file_config = {"ocr_backend": "none"}
        cli_args: dict[str, Any] = {}

        result = build_extraction_config(file_config, cli_args)

        assert result.ocr_backend is None

    def test_build_extraction_config_complex_override(self) -> None:
        """Test complex configuration override scenarios."""
        file_config = {
            "force_ocr": True,
            "chunk_content": False,
            "max_chars": 1000,
            "ocr_backend": "tesseract",
            "tesseract": {"language": "eng", "psm": 3},
            "extract_tables": True,
            "gmft": {"verbosity": 1, "detector_base_threshold": 0.5},
        }

        cli_args = {
            "force_ocr": None,  # Should be ignored
            "chunk_content": True,  # Override
            "max_overlap": 100,  # New value
            "tesseract_config": {"psm": 6},  # Partial override
            "gmft_config": None,  # Should be ignored
            "unused_arg": "ignored",
        }

        result = build_extraction_config(file_config, cli_args)

        assert result.force_ocr is True  # File value preserved
        assert result.chunk_content is True  # CLI override
        assert result.max_chars == 1000  # File value preserved
        assert result.max_overlap == 100  # CLI value
        assert result.ocr_backend == "tesseract"
        assert isinstance(result.ocr_config, TesseractConfig)
        assert result.ocr_config.psm == 6  # type: ignore[comparison-overlap]  # CLI override
        assert result.ocr_config.language == "eng"  # Default, not from file


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling."""

    def test_load_config_from_path_with_pathlib_path(self, tmp_path: Path) -> None:
        """Test load_config_from_path accepts pathlib.Path."""
        config_file = tmp_path / "config.toml"
        config_file.write_text("extract_entities = true")

        result = load_config_from_path(config_file)
        assert result.extract_entities is True

    def test_discover_config_search_path_context(self, tmp_path: Path) -> None:
        """Test that discovery error includes search path in context."""
        with pytest.raises(ValidationError) as exc_info:
            discover_and_load_config(tmp_path)

        assert "search_path" in exc_info.value.context
        assert str(tmp_path) in exc_info.value.context["search_path"]

    def test_discover_config_file_path_context(self, tmp_path: Path) -> None:
        """Test that empty config error includes file path in context."""
        config_file = tmp_path / "kreuzberg.toml"
        config_file.write_text("")

        with pytest.raises(ValidationError) as exc_info:
            discover_and_load_config(tmp_path)

        assert "config_path" in exc_info.value.context
        assert str(config_file) in exc_info.value.context["config_path"]

    def test_gmft_config_with_all_parameters(self) -> None:
        """Test GMFT config with all possible parameters."""
        config_dict = {
            "extract_tables": True,
            "gmft": {
                "verbosity": 3,
                "detector_base_threshold": 0.6,
                "formatter_base_threshold": 0.5,
                "cell_required_confidence": {0: 0.1, 1: 0.2, 2: 0.3, 3: 0.4, 4: 0.5, 5: 0.6, 6: 0.9},
                "remove_null_rows": False,
            },
        }

        result = build_extraction_config_from_dict(config_dict)
        assert result.gmft_config is not None
        assert result.gmft_config.verbosity == 3
        assert result.gmft_config.detector_base_threshold == 0.6
        assert result.gmft_config.formatter_base_threshold == 0.5
        assert result.gmft_config.cell_required_confidence == {0: 0.1, 1: 0.2, 2: 0.3, 3: 0.4, 4: 0.5, 5: 0.6, 6: 0.9}
        assert result.gmft_config.remove_null_rows is False
