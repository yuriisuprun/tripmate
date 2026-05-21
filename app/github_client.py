"""GitHub API client wrapper."""

from __future__ import annotations

import logging
from typing import Optional

import httpx
from github import Github, GithubException
from github.PullRequest import PullRequest
from github.Repository import Repository

from app.config import get_settings
from app.models import ChangedFile, PullRequestInfo

logger = logging.getLogger(__name__)


class GitHubClient:
    """Wrapper around GitHub API for PR operations."""

    def __init__(self) -> None:
        """Initialize GitHub client."""
        settings = get_settings()
        self.token = settings.github_token
        self.api_url = settings.github_api_url
        self.gh = Github(self.token, base_url=self.api_url)
        self.http_client = httpx.Client(
            headers={"Authorization": f"token {self.token}"},
            base_url=self.api_url,
        )

    def get_pull_request(self, owner: str, repo: str, pull_number: int) -> PullRequestInfo:
        """Fetch complete PR information."""
        try:
            repository: Repository = self.gh.get_user(owner).get_repo(repo)
            pr: PullRequest = repository.get_pull(pull_number)

            return PullRequestInfo(
                title=pr.title,
                description=pr.body,
                author=pr.user.login,
                state=pr.state,
                labels=[label.name for label in pr.labels],
                changed_files_count=pr.changed_files,
                additions=pr.additions,
                deletions=pr.deletions,
                reviewers=[reviewer.login for reviewer in pr.requested_reviewers],
                pr_url=pr.html_url,
                created_at=pr.created_at,
                updated_at=pr.updated_at,
                base_branch=pr.base.ref,
                head_branch=pr.head.ref,
            )
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise

    def list_changed_files(self, owner: str, repo: str, pull_number: int) -> list[ChangedFile]:
        """List all files modified in a pull request."""
        try:
            repository: Repository = self.gh.get_user(owner).get_repo(repo)
            pr: PullRequest = repository.get_pull(pull_number)

            files = []
            for file in pr.get_files():
                changed_file = ChangedFile(
                    filename=file.filename,
                    status=file.status,
                    additions=file.additions,
                    deletions=file.deletions,
                    changes=file.changes,
                    patch=file.patch,
                )
                files.append(changed_file)

            return files
        except GithubException as e:
            logger.error(f"GitHub API error: {e}")
            raise

    def get_diff(self, owner: str, repo: str, pull_number: int) -> str:
        """Get the complete unified diff for a PR."""
        try:
            repository: Repository = self.gh.get_user(owner).get_repo(repo)
            pr: PullRequest = repository.get_pull(pull_number)

            # Use the diff URL to get the unified diff
            response = self.http_client.get(
                f"/repos/{owner}/{repo}/pulls/{pull_number}.diff"
            )
            response.raise_for_status()
            return response.text
        except (GithubException, httpx.HTTPError) as e:
            logger.error(f"Error fetching diff: {e}")
            raise

    def post_review_comment(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        body: str,
        commit_id: Optional[str] = None,
        path: Optional[str] = None,
        line: Optional[int] = None,
    ) -> dict:
        """Post a review comment to a PR."""
        try:
            repository: Repository = self.gh.get_user(owner).get_repo(repo)
            pr: PullRequest = repository.get_pull(pull_number)

            if commit_id and path and line:
                # Post as a review comment on a specific line
                review = pr.create_review(
                    body=body,
                    commit=repository.get_commit(commit_id),
                    comments=[{"path": path, "position": line, "body": body}],
                )
                return {
                    "comment_id": review.id,
                    "url": review.html_url,
                    "created_at": review.submitted_at,
                }
            else:
                # Post as a general PR comment
                comment = pr.create_issue_comment(body)
                return {
                    "comment_id": comment.id,
                    "url": comment.html_url,
                    "created_at": comment.created_at,
                }
        except GithubException as e:
            logger.error(f"Error posting review comment: {e}")
            raise

    def get_commits_since(
        self, owner: str, repo: str, base_branch: str, head_branch: str
    ) -> list[dict]:
        """Get commits between two branches."""
        try:
            repository: Repository = self.gh.get_user(owner).get_repo(repo)
            comparison = repository.compare(base_branch, head_branch)

            commits = []
            for commit in comparison.commits:
                commits.append(
                    {
                        "sha": commit.sha,
                        "message": commit.commit.message,
                        "author": commit.commit.author.name,
                        "date": commit.commit.author.date,
                        "url": commit.html_url,
                    }
                )

            return commits
        except GithubException as e:
            logger.error(f"Error fetching commits: {e}")
            raise

    def close(self) -> None:
        """Close HTTP client."""
        self.http_client.close()
