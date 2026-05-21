"""Tests for release notes generator."""

from __future__ import annotations

import pytest

from app.release_notes_generator import (
    categorize_commit,
    extract_title,
    generate_release_notes,
)


class TestCommitCategorization:
    """Test commit message categorization."""

    def test_feature_commit(self) -> None:
        """Test feature commit detection."""
        assert categorize_commit("feat: add new feature") == "feature"
        assert categorize_commit("feat(api): add endpoint") == "feature"
        assert categorize_commit("feature: new functionality") == "feature"

    def test_fix_commit(self) -> None:
        """Test fix commit detection."""
        assert categorize_commit("fix: resolve bug") == "fix"
        assert categorize_commit("fix(auth): fix login") == "fix"
        assert categorize_commit("bugfix: resolve issue") == "fix"

    def test_refactor_commit(self) -> None:
        """Test refactor commit detection."""
        assert categorize_commit("refactor: improve code") == "refactor"
        assert categorize_commit("refactor(api): restructure") == "refactor"

    def test_docs_commit(self) -> None:
        """Test docs commit detection."""
        assert categorize_commit("docs: update readme") == "docs"
        assert categorize_commit("docs(api): add examples") == "docs"

    def test_breaking_change(self) -> None:
        """Test breaking change detection."""
        assert categorize_commit("BREAKING CHANGE: remove old API") == "breaking"
        assert categorize_commit("breaking: change behavior") == "breaking"

    def test_other_commit(self) -> None:
        """Test other commit type."""
        assert categorize_commit("chore: update deps") == "other"
        assert categorize_commit("random commit message") == "other"


class TestTitleExtraction:
    """Test commit title extraction."""

    def test_extract_simple_title(self) -> None:
        """Test extraction of simple title."""
        assert extract_title("feat: add feature") == "add feature"
        assert extract_title("fix(auth): fix bug") == "fix bug"

    def test_extract_multiline_title(self) -> None:
        """Test extraction from multiline message."""
        message = "feat: add feature\n\nThis is a longer description"
        assert extract_title(message) == "add feature"

    def test_extract_title_without_prefix(self) -> None:
        """Test extraction of title without prefix."""
        assert extract_title("Update documentation") == "Update documentation"


class TestReleaseNotesGeneration:
    """Test release notes generation."""

    def test_generate_basic_release_notes(self) -> None:
        """Test basic release notes generation."""
        commits = [
            {
                "sha": "abc123",
                "message": "feat: add new feature",
                "author": "Alice",
                "date": "2024-01-01",
                "url": "https://github.com/repo/commit/abc123",
            },
            {
                "sha": "def456",
                "message": "fix: resolve bug",
                "author": "Bob",
                "date": "2024-01-02",
                "url": "https://github.com/repo/commit/def456",
            },
        ]

        release_notes = generate_release_notes("1.0.0", commits)

        assert release_notes.version == "1.0.0"
        assert len(release_notes.features) == 1
        assert len(release_notes.fixes) == 1
        assert "add new feature" in release_notes.features[0]
        assert "resolve bug" in release_notes.fixes[0]

    def test_generate_with_breaking_changes(self) -> None:
        """Test release notes with breaking changes."""
        commits = [
            {
                "sha": "abc123",
                "message": "BREAKING CHANGE: remove old API",
                "author": "Alice",
                "date": "2024-01-01",
                "url": "https://github.com/repo/commit/abc123",
            },
        ]

        release_notes = generate_release_notes("2.0.0", commits)

        assert len(release_notes.breaking_changes) == 1
        assert "remove old API" in release_notes.breaking_changes[0]

    def test_generate_with_contributors(self) -> None:
        """Test release notes with contributors."""
        commits = [
            {
                "sha": "abc123",
                "message": "feat: feature 1",
                "author": "Alice",
                "date": "2024-01-01",
                "url": "https://github.com/repo/commit/abc123",
            },
            {
                "sha": "def456",
                "message": "fix: fix 1",
                "author": "Bob",
                "date": "2024-01-02",
                "url": "https://github.com/repo/commit/def456",
            },
        ]

        release_notes = generate_release_notes("1.0.0", commits, ["Alice", "Bob"])

        assert "Alice" in release_notes.contributors
        assert "Bob" in release_notes.contributors

    def test_markdown_generation(self) -> None:
        """Test markdown generation."""
        commits = [
            {
                "sha": "abc123",
                "message": "feat: add feature",
                "author": "Alice",
                "date": "2024-01-01",
                "url": "https://github.com/repo/commit/abc123",
            },
        ]

        release_notes = generate_release_notes("1.0.0", commits)

        assert "# Release 1.0.0" in release_notes.markdown
        assert "## ✨ Features" in release_notes.markdown
        assert "add feature" in release_notes.markdown

    def test_duplicate_removal(self) -> None:
        """Test that duplicate commits are removed."""
        commits = [
            {
                "sha": "abc123",
                "message": "feat: add feature",
                "author": "Alice",
                "date": "2024-01-01",
                "url": "https://github.com/repo/commit/abc123",
            },
            {
                "sha": "def456",
                "message": "feat: add feature",
                "author": "Bob",
                "date": "2024-01-02",
                "url": "https://github.com/repo/commit/def456",
            },
        ]

        release_notes = generate_release_notes("1.0.0", commits)

        # Should only have one feature (duplicates removed)
        assert len(release_notes.features) == 1
