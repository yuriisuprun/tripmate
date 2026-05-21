"""Risk analysis for pull requests."""

from __future__ import annotations

import logging
import re
from typing import Optional

from app.models import ChangedFile, ReviewSuggestion

logger = logging.getLogger(__name__)

# Patterns for risky files and changes
RISKY_FILE_PATTERNS = [
    r"auth.*\.py$",
    r"security.*\.py$",
    r"password.*\.py$",
    r"token.*\.py$",
    r"\.github/workflows/.*",
    r"Dockerfile",
    r"docker-compose.*",
    r"\.env.*",
    r"requirements\.txt$",
    r"setup\.py$",
    r"pyproject\.toml$",
    r"package\.json$",
    r"package-lock\.json$",
    r"migrations/.*\.py$",
    r"database.*\.py$",
    r"config.*\.py$",
    r"settings.*\.py$",
]

RISKY_KEYWORDS = [
    "eval",
    "exec",
    "pickle",
    "subprocess",
    "os.system",
    "shell=True",
    "DROP TABLE",
    "DELETE FROM",
    "TRUNCATE",
    "ALTER TABLE",
    "password",
    "secret",
    "api_key",
    "token",
]

TEST_FILE_PATTERNS = [
    r"test_.*\.py$",
    r".*_test\.py$",
    r"tests/.*\.py$",
    r"__tests__/.*",
]


def is_risky_file(filename: str) -> bool:
    """Check if a file is considered risky."""
    for pattern in RISKY_FILE_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            return True
    return False


def is_test_file(filename: str) -> bool:
    """Check if a file is a test file."""
    for pattern in TEST_FILE_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            return True
    return False


def contains_risky_keywords(content: Optional[str]) -> list[str]:
    """Check if content contains risky keywords."""
    if not content:
        return []

    found_keywords = []
    for keyword in RISKY_KEYWORDS:
        if re.search(rf"\b{re.escape(keyword)}\b", content, re.IGNORECASE):
            found_keywords.append(keyword)

    return found_keywords


def analyze_file_changes(files: list[ChangedFile]) -> tuple[list[ReviewSuggestion], float]:
    """Analyze file changes and generate review suggestions with risk score."""
    suggestions: list[ReviewSuggestion] = []
    risk_score = 0.0
    total_files = len(files)

    # Track metrics
    risky_files_count = 0
    large_changes_count = 0
    missing_tests = False
    test_files_modified = False

    for file in files:
        # Check for risky files
        if is_risky_file(file.filename):
            risky_files_count += 1
            severity = "critical" if "auth" in file.filename.lower() else "high"
            suggestions.append(
                ReviewSuggestion(
                    file=file.filename,
                    severity=severity,
                    comment=f"This is a sensitive file. Review changes carefully.",
                    reasoning=f"File matches risky pattern: {file.filename}",
                )
            )

        # Check for large changes
        if file.changes > 500:
            large_changes_count += 1
            suggestions.append(
                ReviewSuggestion(
                    file=file.filename,
                    severity="high",
                    comment=f"Large change ({file.changes} lines). Consider breaking into smaller PRs.",
                    reasoning="Large changes are harder to review and more prone to bugs.",
                )
            )
        elif file.changes > 200:
            suggestions.append(
                ReviewSuggestion(
                    file=file.filename,
                    severity="medium",
                    comment=f"Moderate change ({file.changes} lines). Ensure thorough review.",
                    reasoning="Medium-sized changes should be reviewed carefully.",
                )
            )

        # Check for risky keywords in patch
        if file.patch:
            risky_keywords = contains_risky_keywords(file.patch)
            if risky_keywords:
                suggestions.append(
                    ReviewSuggestion(
                        file=file.filename,
                        severity="high",
                        comment=f"Contains potentially risky keywords: {', '.join(risky_keywords)}",
                        reasoning="These keywords may indicate security or stability concerns.",
                    )
                )

        # Track test files
        if is_test_file(file.filename):
            test_files_modified = True

    # Check for missing tests
    non_test_files = [f for f in files if not is_test_file(f.filename)]
    if non_test_files and not test_files_modified:
        missing_tests = True
        suggestions.append(
            ReviewSuggestion(
                severity="medium",
                comment="No test files were modified. Consider adding tests for new functionality.",
                reasoning="Tests help ensure code quality and prevent regressions.",
            )
        )

    # Calculate risk score (0-100)
    risk_score = min(
        100.0,
        (risky_files_count * 20)
        + (large_changes_count * 15)
        + (20 if missing_tests else 0)
        + (len([s for s in suggestions if s.severity == "critical"]) * 10)
        + (len([s for s in suggestions if s.severity == "high"]) * 5),
    )

    return suggestions, risk_score


def generate_summary(suggestions: list[ReviewSuggestion], risk_score: float) -> str:
    """Generate a summary of the review."""
    if not suggestions:
        return "No issues detected. This PR looks good!"

    critical_count = len([s for s in suggestions if s.severity == "critical"])
    high_count = len([s for s in suggestions if s.severity == "high"])
    medium_count = len([s for s in suggestions if s.severity == "medium"])

    summary_parts = []

    if critical_count > 0:
        summary_parts.append(f"⚠️ {critical_count} critical issue(s) found")
    if high_count > 0:
        summary_parts.append(f"⚠️ {high_count} high-priority issue(s) found")
    if medium_count > 0:
        summary_parts.append(f"ℹ️ {medium_count} medium-priority issue(s) found")

    summary_parts.append(f"Risk score: {risk_score:.1f}/100")

    return ". ".join(summary_parts) + "."
