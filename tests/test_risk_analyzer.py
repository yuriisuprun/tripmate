"""Tests for risk analyzer."""

from __future__ import annotations

import pytest

from app.models import ChangedFile
from app.risk_analyzer import (
    analyze_file_changes,
    contains_risky_keywords,
    is_risky_file,
    is_test_file,
)


class TestFileClassification:
    """Test file classification logic."""

    def test_risky_file_auth(self) -> None:
        """Test detection of auth files."""
        assert is_risky_file("app/auth.py")
        assert is_risky_file("app/authentication.py")
        assert is_risky_file("auth_module.py")

    def test_risky_file_docker(self) -> None:
        """Test detection of Docker files."""
        assert is_risky_file("Dockerfile")
        assert is_risky_file("docker-compose.yml")

    def test_risky_file_config(self) -> None:
        """Test detection of config files."""
        assert is_risky_file("config.py")
        assert is_risky_file("settings.py")
        assert is_risky_file("pyproject.toml")

    def test_risky_file_migrations(self) -> None:
        """Test detection of migration files."""
        assert is_risky_file("migrations/0001_initial.py")

    def test_non_risky_file(self) -> None:
        """Test non-risky files."""
        assert not is_risky_file("app/utils.py")
        assert not is_risky_file("app/models.py")

    def test_test_file_detection(self) -> None:
        """Test detection of test files."""
        assert is_test_file("test_utils.py")
        assert is_test_file("utils_test.py")
        assert is_test_file("tests/test_models.py")
        assert is_test_file("__tests__/utils.test.js")

    def test_non_test_file(self) -> None:
        """Test non-test files."""
        assert not is_test_file("utils.py")
        assert not is_test_file("models.py")


class TestRiskyKeywords:
    """Test risky keyword detection."""

    def test_eval_keyword(self) -> None:
        """Test detection of eval."""
        assert "eval" in contains_risky_keywords("result = eval(user_input)")

    def test_subprocess_keyword(self) -> None:
        """Test detection of subprocess."""
        assert "subprocess" in contains_risky_keywords("subprocess.run(cmd, shell=True)")

    def test_password_keyword(self) -> None:
        """Test detection of password."""
        assert "password" in contains_risky_keywords("password = get_from_env()")

    def test_no_keywords(self) -> None:
        """Test content without risky keywords."""
        assert contains_risky_keywords("def add(a, b): return a + b") == []

    def test_empty_content(self) -> None:
        """Test empty content."""
        assert contains_risky_keywords("") == []
        assert contains_risky_keywords(None) == []


class TestFileAnalysis:
    """Test file change analysis."""

    def test_risky_file_detection(self) -> None:
        """Test detection of risky files in analysis."""
        files = [
            ChangedFile(
                filename="app/auth.py",
                status="modified",
                additions=10,
                deletions=5,
                changes=15,
            ),
        ]

        suggestions, risk_score = analyze_file_changes(files)

        assert len(suggestions) > 0
        assert any("sensitive" in s.comment.lower() for s in suggestions)
        assert risk_score > 0

    def test_large_file_detection(self) -> None:
        """Test detection of large file changes."""
        files = [
            ChangedFile(
                filename="app/utils.py",
                status="modified",
                additions=300,
                deletions=200,
                changes=600,
            ),
        ]

        suggestions, risk_score = analyze_file_changes(files)

        assert len(suggestions) > 0
        assert any("large" in s.comment.lower() for s in suggestions)

    def test_missing_tests_detection(self) -> None:
        """Test detection of missing tests."""
        files = [
            ChangedFile(
                filename="app/models.py",
                status="modified",
                additions=50,
                deletions=10,
                changes=60,
            ),
        ]

        suggestions, risk_score = analyze_file_changes(files)

        assert any("test" in s.comment.lower() for s in suggestions)

    def test_no_issues(self) -> None:
        """Test PR with no issues."""
        files = [
            ChangedFile(
                filename="app/utils.py",
                status="modified",
                additions=10,
                deletions=5,
                changes=15,
            ),
            ChangedFile(
                filename="tests/test_utils.py",
                status="modified",
                additions=20,
                deletions=0,
                changes=20,
            ),
        ]

        suggestions, risk_score = analyze_file_changes(files)

        # Should have minimal suggestions
        assert risk_score < 20

    def test_risky_keywords_in_patch(self) -> None:
        """Test detection of risky keywords in patch."""
        files = [
            ChangedFile(
                filename="app/utils.py",
                status="modified",
                additions=10,
                deletions=5,
                changes=15,
                patch="+    result = eval(user_input)",
            ),
        ]

        suggestions, risk_score = analyze_file_changes(files)

        assert any("eval" in s.comment.lower() for s in suggestions)
