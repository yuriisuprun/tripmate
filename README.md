# Repo Assistant MCP

A production-quality MCP (Model Context Protocol) server for GitHub pull request review workflows. Integrates with the GitHub API to provide AI assistants with tools for analyzing, reviewing, and managing pull requests.

## Features

- **Pull Request Analysis** - Fetch complete PR information and metadata
- **File Change Tracking** - List all modified files with detailed statistics
- **Diff Viewing** - Get unified diffs for entire PRs or specific files
- **AI Review Suggestions** - Automated risk analysis and code review recommendations
- **Review Comments** - Post comments directly to GitHub PRs
- **Release Notes Generation** - Create formatted release notes from commits

## Quick Start

### Prerequisites

- Python 3.12 or higher
- GitHub Personal Access Token (with `repo` scope)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/repo-assistant-mcp.git
cd repo-assistant-mcp
```

2. Create and activate a virtual environment:
```bash
# On Windows
python -m venv .venv
.venv\Scripts\activate

# On macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GitHub token
```

5. Run the server:
```bash
python main.py
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Required: GitHub Personal Access Token
GITHUB_TOKEN=ghp_your_token_here

# Optional: GitHub API base URL (for GitHub Enterprise)
# GITHUB_API_URL=https://api.github.com

# Optional: Logging level (default: INFO)
LOG_LEVEL=INFO

# Optional: Environment (dev or prod)
APP_ENV=dev
```

### Getting a GitHub Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token" → "Generate new token (classic)"
3. Select scopes: `repo` (full control of private repositories)
4. Copy the token and add it to your `.env` file

## MCP Tools

### 1. get_pull_request

Fetch complete pull request information.

**Input:**
- `owner` (string): Repository owner
- `repo` (string): Repository name
- `pull_number` (integer): PR number

**Output:**
```json
{
  "title": "Add new feature",
  "description": "This PR adds...",
  "author": "alice",
  "state": "open",
  "labels": ["feature", "enhancement"],
  "changed_files_count": 5,
  "additions": 150,
  "deletions": 30,
  "reviewers": ["bob"],
  "pr_url": "https://github.com/owner/repo/pull/123",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T14:20:00",
  "base_branch": "main",
  "head_branch": "feature/new-feature"
}
```

### 2. list_changed_files

List all files modified in a pull request.

**Input:**
- `owner` (string): Repository owner
- `repo` (string): Repository name
- `pull_number` (integer): PR number

**Output:**
```json
[
  {
    "filename": "app/utils.py",
    "status": "modified",
    "additions": 50,
    "deletions": 10,
    "changes": 60,
    "patch": "... unified diff patch ..."
  }
]
```

### 3. get_diff

Get the complete unified diff for a pull request.

**Input:**
- `owner` (string): Repository owner
- `repo` (string): Repository name
- `pull_number` (integer): PR number

**Output:**
```json
{
  "pr_number": 123,
  "total_files": 5,
  "total_additions": 150,
  "total_deletions": 30,
  "diff_text": "diff --git a/app/utils.py b/app/utils.py\n..."
}
```

### 4. suggest_review_comments

Analyze PR changes and generate AI review suggestions.

**Input:**
- `owner` (string): Repository owner
- `repo` (string): Repository name
- `pull_number` (integer): PR number

**Output:**
```json
{
  "pr_title": "Add new feature",
  "pr_url": "https://github.com/owner/repo/pull/123",
  "risk_score": 35.5,
  "suggestions": [
    {
      "file": "app/auth.py",
      "severity": "high",
      "comment": "This is a sensitive file. Review changes carefully.",
      "reasoning": "File matches risky pattern: auth module"
    }
  ],
  "summary": "1 high-priority issue found. Risk score: 35.5/100."
}
```

### 5. post_review_comment

Post a review comment to a GitHub pull request.

**Input:**
- `owner` (string): Repository owner
- `repo` (string): Repository name
- `pull_number` (integer): PR number
- `body` (string): Comment body (markdown supported)
- `commit_id` (string, optional): Commit SHA for line-specific comments
- `path` (string, optional): File path for line-specific comments
- `line` (integer, optional): Line number for line-specific comments

**Output:**
```json
{
  "comment_id": 1234567,
  "url": "https://github.com/owner/repo/pull/123#issuecomment-1234567",
  "created_at": "2024-01-15T15:30:00"
}
```

### 6. generate_release_notes

Generate release notes from commits between two branches.

**Input:**
- `owner` (string): Repository owner
- `repo` (string): Repository name
- `base_branch` (string): Base branch (e.g., 'main')
- `head_branch` (string): Head branch (e.g., 'develop')
- `version` (string): Version number (e.g., '1.0.0')

**Output:**
```json
{
  "version": "1.0.0",
  "date": "2024-01-15T15:30:00",
  "features": ["Add new feature", "Improve performance"],
  "fixes": ["Fix login bug"],
  "refactors": ["Restructure API"],
  "documentation": ["Update README"],
  "breaking_changes": [],
  "contributors": ["alice", "bob"],
  "markdown": "# Release 1.0.0\n..."
}
```

## Integration Examples

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "repo-assistant": {
      "command": "python",
      "args": ["/path/to/repo-assistant-mcp/main.py"],
      "env": {
        "GITHUB_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Cline (VS Code)

Add to your Cline settings:

```json
{
  "mcpServers": {
    "repo-assistant": {
      "command": "python",
      "args": ["/path/to/repo-assistant-mcp/main.py"],
      "env": {
        "GITHUB_TOKEN": "your_token_here"
      }
    }
  }
}
```

### Direct HTTP Usage

The server can also be run as an HTTP server:

```bash
uvicorn app.server:app --host 0.0.0.0 --port 8000
```

## Example Prompts

### Review a Pull Request
```
Please review the pull request at owner/repo#123. 
Use the suggest_review_comments tool to analyze the changes and provide feedback.
```

### Generate Release Notes
```
Generate release notes for version 1.0.0 from the commits between main and develop branches 
in the owner/repo repository.
```

### Post a Review Comment
```
Please post a review comment to owner/repo#123 suggesting improvements to the code.
```

## Development

### Running Tests

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_risk_analyzer.py -v

# Run with coverage
pytest --cov=app tests/
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
ruff check app/ tests/

# Type checking
mypy app/
```

### Project Structure

```
repo-assistant-mcp/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── github_client.py       # GitHub API wrapper
│   ├── models.py              # Pydantic models
│   ├── risk_analyzer.py       # Risk analysis logic
│   ├── release_notes_generator.py  # Release notes generation
│   └── server.py              # MCP server implementation
├── tests/
│   ├── test_models.py
│   ├── test_risk_analyzer.py
│   └── test_release_notes.py
├── main.py                    # Entry point
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## Risk Analysis

The `suggest_review_comments` tool analyzes PRs for:

- **Risky Files**: Auth modules, Docker files, config files, migrations
- **Large Changes**: Files with >200 lines changed
- **Missing Tests**: PRs without test file modifications
- **Risky Keywords**: eval, exec, pickle, subprocess, password, secret, etc.
- **Sensitive Operations**: Database migrations, infrastructure changes

Risk scores range from 0-100, with higher scores indicating more review attention needed.

## Error Handling

The server includes comprehensive error handling:

- GitHub API errors are logged and returned as JSON
- Validation errors provide detailed feedback
- Missing environment variables are caught at startup
- Rate limiting is handled gracefully

## Performance Considerations

- GitHub API calls are made directly (no caching)
- Large diffs are returned as-is (consider pagination for very large PRs)
- Risk analysis is performed locally without external API calls
- Async operations are used where appropriate

## Limitations

- GitHub API rate limits apply (60 requests/hour unauthenticated, 5000/hour authenticated)
- Large PRs (>300 files) may take longer to analyze
- Release notes generation requires commits to follow conventional commit format for best results

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or suggestions, please open an issue on GitHub.
