"""Generate release notes from commits and PRs."""

from __future__ import annotations

import logging
import re
from datetime import datetime

from app.models import ReleaseNotes

logger = logging.getLogger(__name__)

# Patterns to categorize commits
FEATURE_PATTERNS = [
    r"^feat(\(.+\))?:",
    r"^feature:",
    r"^add:",
    r"^new:",
]

FIX_PATTERNS = [
    r"^fix(\(.+\))?:",
    r"^bugfix:",
    r"^bug:",
    r"^hotfix:",
]

REFACTOR_PATTERNS = [
    r"^refactor(\(.+\))?:",
    r"^refactoring:",
    r"^cleanup:",
]

DOCS_PATTERNS = [
    r"^docs(\(.+\))?:",
    r"^documentation:",
    r"^doc:",
]

BREAKING_PATTERNS = [
    r"^breaking(\(.+\))?:",
    r"breaking:",
    r"BREAKING CHANGE",
]


def categorize_commit(message: str) -> str:
    """Categorize a commit message."""
    message_lower = message.lower()

    # Check breaking changes first (can appear anywhere in message)
    if "breaking change" in message_lower or re.search(
        r"^breaking(\(.+\))?:", message_lower
    ):
        return "breaking"
    if any(re.search(pattern, message_lower) for pattern in FEATURE_PATTERNS):
        return "feature"
    if any(re.search(pattern, message_lower) for pattern in FIX_PATTERNS):
        return "fix"
    if any(re.search(pattern, message_lower) for pattern in REFACTOR_PATTERNS):
        return "refactor"
    if any(re.search(pattern, message_lower) for pattern in DOCS_PATTERNS):
        return "docs"

    return "other"


def extract_title(message: str) -> str:
    """Extract the first line of a commit message."""
    lines = message.split("\n")
    title = lines[0].strip()

    # Remove conventional commit prefix
    title = re.sub(r"^(feat|fix|refactor|docs|chore|test|style|perf)(\(.+\))?:\s*", "", title)

    return title


def generate_release_notes(
    version: str,
    commits: list[dict],
    contributors: list[str] | None = None,
) -> ReleaseNotes:
    """Generate release notes from commits."""
    features: list[str] = []
    fixes: list[str] = []
    refactors: list[str] = []
    documentation: list[str] = []
    breaking_changes: list[str] = []

    seen_messages = set()

    for commit in commits:
        message = commit.get("message", "")
        category = categorize_commit(message)
        title = extract_title(message)

        # Avoid duplicates
        if title in seen_messages:
            continue
        seen_messages.add(title)

        if category == "breaking":
            breaking_changes.append(title)
        elif category == "feature":
            features.append(title)
        elif category == "fix":
            fixes.append(title)
        elif category == "refactor":
            refactors.append(title)
        elif category == "docs":
            documentation.append(title)

    # Generate markdown
    markdown_parts = [f"# Release {version}\n"]
    markdown_parts.append(f"*Released on {datetime.now().strftime('%Y-%m-%d')}*\n")

    if breaking_changes:
        markdown_parts.append("## ⚠️ Breaking Changes\n")
        for change in breaking_changes:
            markdown_parts.append(f"- {change}\n")
        markdown_parts.append("")

    if features:
        markdown_parts.append("## ✨ Features\n")
        for feature in features:
            markdown_parts.append(f"- {feature}\n")
        markdown_parts.append("")

    if fixes:
        markdown_parts.append("## 🐛 Fixes\n")
        for fix in fixes:
            markdown_parts.append(f"- {fix}\n")
        markdown_parts.append("")

    if refactors:
        markdown_parts.append("## 🔄 Refactors\n")
        for refactor in refactors:
            markdown_parts.append(f"- {refactor}\n")
        markdown_parts.append("")

    if documentation:
        markdown_parts.append("## 📚 Documentation\n")
        for doc in documentation:
            markdown_parts.append(f"- {doc}\n")
        markdown_parts.append("")

    if contributors:
        markdown_parts.append("## 👥 Contributors\n")
        for contributor in sorted(set(contributors)):
            markdown_parts.append(f"- @{contributor}\n")

    markdown = "".join(markdown_parts)

    return ReleaseNotes(
        version=version,
        date=datetime.now(),
        features=features,
        fixes=fixes,
        refactors=refactors,
        documentation=documentation,
        breaking_changes=breaking_changes,
        contributors=list(set(contributors or [])),
        markdown=markdown,
    )
