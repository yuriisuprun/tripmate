# Repo Assistant MCP - Usage Examples

This document provides practical examples of how to use the repo-assistant-mcp server with various AI assistants and tools.

## Example 1: Review a Pull Request

### Prompt
```
Please review the pull request at owner/repo#123. 
Use the suggest_review_comments tool to analyze the changes and provide feedback.
```

### Expected Output
```json
{
  "pr_title": "Add authentication module",
  "pr_url": "https://github.com/owner/repo/pull/123",
  "risk_score": 45.5,
  "suggestions": [
    {
      "file": "app/auth.py",
      "severity": "critical",
      "comment": "This is a sensitive file. Review changes carefully.",
      "reasoning": "File matches risky pattern: auth module"
    },
    {
      "file": "app/auth.py",
      "severity": "high",
      "comment": "Contains potentially risky keywords: password, token",
      "reasoning": "These keywords may indicate security or stability concerns."
    },
    {
      "severity": "medium",
      "comment": "No test files were modified. Consider adding tests for new functionality.",
      "reasoning": "Tests help ensure code quality and prevent regressions."
    }
  ],
  "summary": "⚠️ 1 critical issue(s) found. ⚠️ 1 high-priority issue(s) found. ℹ️ 1 medium-priority issue(s) found. Risk score: 45.5/100."
}
```

## Example 2: Get Pull Request Details

### Prompt
```
Fetch the details of pull request #42 in the owner/repo repository.
```

### Tool Call
```json
{
  "tool": "get_pull_request",
  "arguments": {
    "owner": "owner",
    "repo": "repo",
    "pull_number": 42
  }
}
```

### Expected Output
```json
{
  "title": "Add new feature",
  "description": "This PR adds a new feature to improve user experience",
  "author": "alice",
  "state": "open",
  "labels": ["feature", "enhancement"],
  "changed_files_count": 5,
  "additions": 150,
  "deletions": 30,
  "reviewers": ["bob", "charlie"],
  "pr_url": "https://github.com/owner/repo/pull/42",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T14:20:00",
  "base_branch": "main",
  "head_branch": "feature/new-feature"
}
```

## Example 3: List Changed Files

### Prompt
```
Show me all the files that were changed in pull request #42 of owner/repo.
```

### Tool Call
```json
{
  "tool": "list_changed_files",
  "arguments": {
    "owner": "owner",
    "repo": "repo",
    "pull_number": 42
  }
}
```

### Expected Output
```json
[
  {
    "filename": "app/models.py",
    "status": "modified",
    "additions": 50,
    "deletions": 10,
    "changes": 60,
    "patch": "diff --git a/app/models.py b/app/models.py\n..."
  },
  {
    "filename": "tests/test_models.py",
    "status": "modified",
    "additions": 75,
    "deletions": 5,
    "changes": 80,
    "patch": "diff --git a/tests/test_models.py b/tests/test_models.py\n..."
  },
  {
    "filename": "README.md",
    "status": "modified",
    "additions": 25,
    "deletions": 0,
    "changes": 25,
    "patch": "diff --git a/README.md b/README.md\n..."
  }
]
```

## Example 4: Get Full Diff

### Prompt
```
Show me the complete diff for pull request #42 in owner/repo.
```

### Tool Call
```json
{
  "tool": "get_diff",
  "arguments": {
    "owner": "owner",
    "repo": "repo",
    "pull_number": 42
  }
}
```

### Expected Output
```json
{
  "pr_number": 42,
  "total_files": 3,
  "total_additions": 150,
  "total_deletions": 15,
  "diff_text": "diff --git a/app/models.py b/app/models.py\nindex abc123..def456 100644\n--- a/app/models.py\n+++ b/app/models.py\n@@ -1,5 +1,10 @@\n..."
}
```

## Example 5: Post a Review Comment

### Prompt
```
Post a review comment to pull request #42 in owner/repo suggesting improvements.
```

### Tool Call
```json
{
  "tool": "post_review_comment",
  "arguments": {
    "owner": "owner",
    "repo": "repo",
    "pull_number": 42,
    "body": "Great work! I have a few suggestions:\n\n1. Consider adding error handling for edge cases\n2. Add docstrings to new functions\n3. Run the test suite before merging"
  }
}
```

### Expected Output
```json
{
  "comment_id": 1234567890,
  "url": "https://github.com/owner/repo/pull/42#issuecomment-1234567890",
  "created_at": "2024-01-15T15:30:00"
}
```

## Example 6: Generate Release Notes

### Prompt
```
Generate release notes for version 1.0.0 from commits between main and develop branches in owner/repo.
```

### Tool Call
```json
{
  "tool": "generate_release_notes",
  "arguments": {
    "owner": "owner",
    "repo": "repo",
    "base_branch": "main",
    "head_branch": "develop",
    "version": "1.0.0"
  }
}
```

### Expected Output
```json
{
  "version": "1.0.0",
  "date": "2024-01-15T15:30:00",
  "features": [
    "Add authentication module",
    "Implement user dashboard",
    "Add API rate limiting"
  ],
  "fixes": [
    "Fix login redirect bug",
    "Fix memory leak in cache"
  ],
  "refactors": [
    "Restructure API endpoints",
    "Improve error handling"
  ],
  "documentation": [
    "Update API documentation",
    "Add deployment guide"
  ],
  "breaking_changes": [
    "Remove deprecated /api/v1 endpoints"
  ],
  "contributors": [
    "alice",
    "bob",
    "charlie"
  ],
  "markdown": "# Release 1.0.0\n\n*Released on 2024-01-15*\n\n## ⚠️ Breaking Changes\n\n- Remove deprecated /api/v1 endpoints\n\n## ✨ Features\n\n- Add authentication module\n- Implement user dashboard\n- Add API rate limiting\n\n## 🐛 Fixes\n\n- Fix login redirect bug\n- Fix memory leak in cache\n\n## 🔄 Refactors\n\n- Restructure API endpoints\n- Improve error handling\n\n## 📚 Documentation\n\n- Update API documentation\n- Add deployment guide\n\n## 👥 Contributors\n\n- @alice\n- @bob\n- @charlie\n"
}
```

## Example 7: Complex Review Workflow

### Prompt
```
I need to review pull request #100 in owner/repo. Please:
1. Get the PR details
2. List all changed files
3. Analyze the changes for risks
4. Post a comprehensive review comment

Then generate release notes for version 2.0.0 from main to develop.
```

### Workflow
1. Call `get_pull_request` to understand the PR scope
2. Call `list_changed_files` to see what was modified
3. Call `suggest_review_comments` to get risk analysis
4. Call `post_review_comment` with detailed feedback
5. Call `generate_release_notes` for the release

## Example 8: Risk Analysis for Large PR

### Prompt
```
Analyze pull request #50 in owner/repo for potential risks and security concerns.
```

### Analysis Output
The `suggest_review_comments` tool will identify:

- **Risky Files**: Auth modules, Docker files, config files, migrations
- **Large Changes**: Files with >200 lines changed
- **Missing Tests**: PRs without test file modifications
- **Risky Keywords**: eval, exec, pickle, subprocess, password, secret, etc.
- **Risk Score**: 0-100 scale indicating overall PR risk

Example risk score interpretation:
- 0-20: Low risk - routine changes
- 21-40: Medium risk - review recommended
- 41-60: High risk - careful review needed
- 61-100: Critical risk - requires thorough review

## Integration with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "repo-assistant": {
      "command": "python",
      "args": ["/path/to/repo-assistant-mcp/main.py"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

Then use prompts like:
```
Review the pull request at owner/repo#123 and suggest improvements.
```

## Integration with Cline (VS Code)

Add to your Cline settings:

```json
{
  "mcpServers": {
    "repo-assistant": {
      "command": "python",
      "args": ["/path/to/repo-assistant-mcp/main.py"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

## Tips for Best Results

1. **Be Specific**: Include owner, repo, and PR number in your prompts
2. **Use Conventional Commits**: For better release notes, use conventional commit format (feat:, fix:, etc.)
3. **Review Risk Scores**: Pay attention to risk scores - higher scores need more careful review
4. **Check Test Coverage**: Always verify that tests were added for new functionality
5. **Security First**: Prioritize reviewing changes to auth, config, and infrastructure files

## Troubleshooting

### "GitHub API error: 401"
- Check that your GITHUB_TOKEN is valid
- Ensure the token has `repo` scope

### "GitHub API error: 404"
- Verify the owner, repo, and PR number are correct
- Check that the PR exists and is accessible

### "No test files were modified"
- This is a warning, not an error
- Consider adding tests for new functionality

### Large PR Analysis Takes Time
- Large PRs (>300 files) may take longer to analyze
- This is normal - the tool is analyzing all changes
