"""Pydantic models for request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class PullRequestInfo(BaseModel):
    """Complete pull request information."""

    title: str
    description: Optional[str] = None
    author: str
    state: str
    labels: list[str]
    changed_files_count: int
    additions: int
    deletions: int
    reviewers: list[str]
    pr_url: str
    created_at: datetime
    updated_at: datetime
    base_branch: str
    head_branch: str


class ChangedFile(BaseModel):
    """Information about a changed file in a PR."""

    filename: str
    status: str  # added, removed, modified
    additions: int
    deletions: int
    changes: int
    patch: Optional[str] = None


class ReviewSuggestion(BaseModel):
    """A single review suggestion."""

    file: Optional[str] = None
    severity: str  # critical, high, medium, low, info
    comment: str
    reasoning: str
    line_number: Optional[int] = None

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """Validate severity is one of allowed values."""
        allowed = {"critical", "high", "medium", "low", "info"}
        if v not in allowed:
            raise ValueError(f"severity must be one of {allowed}")
        return v


class ReviewSuggestions(BaseModel):
    """Collection of review suggestions."""

    pr_title: str
    pr_url: str
    risk_score: float = Field(ge=0, le=100)
    suggestions: list[ReviewSuggestion]
    summary: str


class ReleaseNotes(BaseModel):
    """Generated release notes."""

    version: str
    date: datetime
    features: list[str]
    fixes: list[str]
    refactors: list[str]
    documentation: list[str]
    breaking_changes: list[str]
    contributors: list[str]
    markdown: str


class DiffResponse(BaseModel):
    """Unified diff response."""

    pr_number: int
    total_files: int
    total_additions: int
    total_deletions: int
    diff_text: str


class ReviewCommentRequest(BaseModel):
    """Request to post a review comment."""

    body: str
    commit_id: Optional[str] = None
    path: Optional[str] = None
    line: Optional[int] = None


class ReviewCommentResponse(BaseModel):
    """Response from posting a review comment."""

    comment_id: int
    url: str
    created_at: datetime
