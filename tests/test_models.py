"""Tests for Pydantic models."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models import (
    ChangedFile,
    PullRequestInfo,
    ReviewSuggestion,
    ReviewSuggestions,
)


class TestChangedFile:
    """Test ChangedFile model."""

    def test_valid_changed_file(self) -> None:
        """Test creating a valid ChangedFile."""
        file = ChangedFile(
            filename="app/utils.py",
            status="modified",
            additions=10,
            deletions=5,
            changes=15,
        )

        assert file.filename == "app/utils.py"
        assert file.status == "modified"
        assert file.additions == 10

    def test_changed_file_with_patch(self) -> None:
        """Test ChangedFile with patch."""
        file = ChangedFile(
            filename="app/utils.py",
            status="modified",
            additions=10,
            deletions=5,
            changes=15,
            patch="+def new_function():\n+    pass",
        )

        assert file.patch is not None
        assert "new_function" in file.patch


class TestReviewSuggestion:
    """Test ReviewSuggestion model."""

    def test_valid_suggestion(self) -> None:
        """Test creating a valid suggestion."""
        suggestion = ReviewSuggestion(
            file="app/auth.py",
            severity="high",
            comment="This is a sensitive file",
            reasoning="Auth files need careful review",
        )

        assert suggestion.file == "app/auth.py"
        assert suggestion.severity == "high"

    def test_suggestion_without_file(self) -> None:
        """Test suggestion without file (general comment)."""
        suggestion = ReviewSuggestion(
            severity="medium",
            comment="No test files modified",
            reasoning="Tests help prevent regressions",
        )

        assert suggestion.file is None

    def test_invalid_severity(self) -> None:
        """Test that invalid severity is rejected."""
        with pytest.raises(ValidationError):
            ReviewSuggestion(
                severity="invalid",
                comment="Test",
                reasoning="Test",
            )


class TestReviewSuggestions:
    """Test ReviewSuggestions model."""

    def test_valid_review_suggestions(self) -> None:
        """Test creating valid review suggestions."""
        suggestions = ReviewSuggestions(
            pr_title="Add new feature",
            pr_url="https://github.com/repo/pull/1",
            risk_score=25.5,
            suggestions=[
                ReviewSuggestion(
                    severity="medium",
                    comment="No tests",
                    reasoning="Tests needed",
                )
            ],
            summary="1 medium issue found",
        )

        assert suggestions.pr_title == "Add new feature"
        assert suggestions.risk_score == 25.5
        assert len(suggestions.suggestions) == 1

    def test_risk_score_bounds(self) -> None:
        """Test risk score validation."""
        # Valid scores
        ReviewSuggestions(
            pr_title="Test",
            pr_url="https://github.com/repo/pull/1",
            risk_score=0,
            suggestions=[],
            summary="No issues",
        )

        ReviewSuggestions(
            pr_title="Test",
            pr_url="https://github.com/repo/pull/1",
            risk_score=100,
            suggestions=[],
            summary="Critical issues",
        )

        # Invalid scores
        with pytest.raises(ValidationError):
            ReviewSuggestions(
                pr_title="Test",
                pr_url="https://github.com/repo/pull/1",
                risk_score=-1,
                suggestions=[],
                summary="Invalid",
            )

        with pytest.raises(ValidationError):
            ReviewSuggestions(
                pr_title="Test",
                pr_url="https://github.com/repo/pull/1",
                risk_score=101,
                suggestions=[],
                summary="Invalid",
            )


class TestPullRequestInfo:
    """Test PullRequestInfo model."""

    def test_valid_pr_info(self) -> None:
        """Test creating valid PR info."""
        now = datetime.now()
        pr = PullRequestInfo(
            title="Add new feature",
            description="This PR adds a new feature",
            author="alice",
            state="open",
            labels=["feature", "enhancement"],
            changed_files_count=5,
            additions=100,
            deletions=20,
            reviewers=["bob", "charlie"],
            pr_url="https://github.com/repo/pull/1",
            created_at=now,
            updated_at=now,
            base_branch="main",
            head_branch="feature/new-feature",
        )

        assert pr.title == "Add new feature"
        assert pr.author == "alice"
        assert len(pr.labels) == 2
        assert len(pr.reviewers) == 2
