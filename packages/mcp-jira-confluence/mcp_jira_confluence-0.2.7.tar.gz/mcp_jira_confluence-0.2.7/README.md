# MCP Server for Jira and Confluence

A Model Context Protocol (MCP) server that integrates with Atlassian's Jira and Confluence, enabling AI assistants to interact with these tools directly.

## Features

- **Jira Integration**
  - List recent issues
  - View issue details including comments
  - Create new issues
  - Add comments to issues
  - Transition issues between statuses
  - **Get assigned issues** - Retrieve your assigned tickets ordered by priority and date
  - **Summarize issues** - Get comprehensive issue summaries with comments and history
  - **Extract Confluence and Git links** - Find all Confluence page references and Git repository URLs in issues
  - **Agile/Scrum Support** - Board management, sprint tracking, daily standup summaries
  - **AI-Powered Assistance** - Smart task assignment recommendations and story point estimation

- **Confluence Integration**
  - List recent pages
  - View page content
  - Create new pages
  - Update existing pages
  - Add comments to pages
  - Search pages using CQL (Confluence Query Language)
  - Get specific pages by ID or title
  - Ask questions about page content

- **AI-Powered Prompts**
  - Summarize Jira issues
  - Create structured Jira issue descriptions
  - Summarize Confluence pages
  - Generate structured Confluence content

## Installation

1. Clone the repository
2. Install dependencies using `uv`:

```bash
pip install uv
uv pip install -e .
```

## Configuration

### Environment Variables

Set the following environment variables to configure the server:

#### Jira Configuration
- `JIRA_URL`: Base URL of your Jira instance (e.g., `https://yourcompany.atlassian.net`)
- `JIRA_USERNAME`: Your Jira username/email
- `JIRA_API_TOKEN`: Your Jira API token or password
- `JIRA_PERSONAL_TOKEN`: Personal access token (alternative to username/API token)

#### Confluence Configuration
- `CONFLUENCE_URL`: Base URL of your Confluence instance (e.g., `https://yourcompany.atlassian.net/wiki`)
- `CONFLUENCE_USERNAME`: Your Confluence username/email
- `CONFLUENCE_API_TOKEN`: Your Confluence API token or password
- `CONFLUENCE_PERSONAL_TOKEN`: Personal access token (alternative to username/API token)

### Quick Setup

1. Create API tokens from your Atlassian account settings
2. Set environment variables in your shell:

```bash
export JIRA_URL="https://yourcompany.atlassian.net"
export JIRA_USERNAME="your-email@company.com"
export JIRA_API_TOKEN="your-jira-api-token"

export CONFLUENCE_URL="https://yourcompany.atlassian.net/wiki"
export CONFLUENCE_USERNAME="your-email@company.com"
export CONFLUENCE_API_TOKEN="your-confluence-api-token"
```

3. Or use the provided `run.sh` script with environment variables

## Usage

### Starting the Server

Run the server directly:

```bash
python -m mcp_jira_confluence.server
```

### VSCode MCP Extension

If using with the VSCode MCP extension, the server is automatically configured via `.vscode/mcp.json`.

### Claude Desktop

To use with Claude Desktop, add the following configuration:

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  
```json
"mcpServers": {
  "mcp-jira-confluence": {
    "command": "uv",
    "args": [
      "--directory",
      "/Users/annmariyajoshy/vibecoding/mcp-jira-confluence",
      "run",
      "mcp-jira-confluence"
    ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  
```json
"mcpServers": {
  "mcp-jira-confluence": {
    "command": "uvx",
    "args": [
      "mcp-jira-confluence"
    ]
  }
}
```
</details>

## Resources

The server exposes the following types of resources:

- `jira://issue/{ISSUE_KEY}` - Jira issues
- `confluence://page/{PAGE_ID}` - Confluence pages
- `confluence://space/{SPACE_KEY}/page/{PAGE_ID}` - Confluence pages with space key

## Usage

### Available Tools

#### Jira Tools
- **`create-jira-issue`**: Create a new Jira issue
- **`comment-jira-issue`**: Add a comment to an issue
- **`transition-jira-issue`**: Change an issue's status (supports transition names like "In Progress", "Done")
- **`get-jira-transitions`**: Get available transitions for an issue
- **`get-jira-issue`**: Get detailed information about a specific Jira issue
- **`get-my-assigned-issues`**: Get issues assigned to you, ordered by priority and date
- **`summarize-jira-issue`**: Get comprehensive issue summary with comments and history
- **`extract-confluence-links`**: Find all Confluence and Git repository links in an issue

#### Agile/Scrum Tools (NEW!)
- **`get-agile-boards`**: Get all agile boards or filter by project - essential for scrum masters
- **`get-board-sprints`**: Get sprints for a specific board (active, closed, future, or all)
- **`get-daily-standup-summary`**: Comprehensive daily standup report with sprint progress, team status, and blockers
- **`get-task-assignment-recommendations`**: AI-powered assignment suggestions based on historical data and expertise
- **`estimate-story-points`**: AI-powered story point estimation using complexity analysis and historical patterns

#### Confluence Tools
- **`create-confluence-page`**: Create a new Confluence page
- **`update-confluence-page`**: Update an existing page (version auto-fetched if not provided)
- **`comment-confluence-page`**: Add a comment to a page
- **`get-confluence-page`**: Get a specific page with optional comments/history
- **`search-confluence`**: Search pages using CQL queries
- **`ask-confluence-page`**: Ask questions about page content

### Usage Examples

#### Getting Your Assigned Issues
```
Get issues assigned to you ordered by priority (highest first) and creation date (newest first):

Default (25 issues, exclude completed):
- No parameters needed

Custom parameters:
- max_results: 50 (max: 100)
- include_done: true (includes closed/resolved issues)

The tool returns issues with:
- Issue key, summary, status, priority
- Issue type, creation date, due date
- Formatted for easy reading
```

#### Getting a Specific Jira Issue
```
Get detailed information about any Jira issue by its key:

Basic issue info:
- issue_key: "PROJ-123" (required)
- include_comments: false (default)

With comments:
- issue_key: "PROJ-123"
- include_comments: true (includes last 3 comments)

Returns:
- Complete issue details (status, priority, assignee, dates)
- Full description
- Optional recent comments
- Formatted for easy reading
```

#### Summarizing a Jira Issue
```
Get comprehensive issue information including:
- Basic details (status, priority, assignee, dates)
- Full description
- Recent comments (last 5)
- Confluence page references
- Status history

Parameters:
- issue_key: "PROJ-123" (required)

Returns formatted markdown summary perfect for AI analysis.
```

#### Transitioning Issue Status
```
Change an issue's status using human-readable transition names:

Using transition name (recommended):
- issue_key: "PROJ-123"
- transition_name: "In Progress"  // or "Done", "To Do", etc.

Using transition ID (advanced):
- issue_key: "PROJ-123" 
- transition_id: "21"

The tool automatically:
- Finds the correct transition ID from the name
- Provides helpful error messages with available options
- Shows the new status after transition

Common transition names: "To Do", "In Progress", "Done", "Closed"
```

#### Getting Available Transitions
```
See what status changes are possible for an issue:

Parameters:
- issue_key: "PROJ-123" (required)

Returns:
- List of available transitions with names and target statuses
- Transition IDs for advanced usage
- Usage examples for each transition
- Clear formatting for easy reading

Use this before transitioning to see available options.
```

#### Extracting Links from Issues
```
Find all Confluence and Git repository links in a Jira issue from:
- Issue description text
- Comments from all users  
- Remote links attached to the issue

Parameters:
- issue_key: "PROJ-123" (required)
- include_git_urls: true (default, set to false to exclude Git links)

Supported Git platforms:
- GitHub, GitLab, Bitbucket (cloud and self-hosted)
- Azure DevOps / Visual Studio Team Services
- Generic Git hosting platforms
- SSH Git URLs (git@server:org/repo.git)

Returns:
- Confluence page links with titles and context
- Git repository URLs with source location
- Organized by category (Confluence vs Git)
- Source information (description, comment, remote link)
```

#### Agile Board Management
```
Get all agile boards or filter by project:

All boards:
- No parameters needed

Project-specific boards:
- project_key: "PROJ" (optional filter)

Returns:
- Board ID, name, type (Scrum/Kanban)
- Associated project information
- Essential for scrum masters managing multiple teams
```

#### Sprint Management
```
Get sprints for a specific agile board:

Active sprints only (default):
- board_id: "123" (required)

All sprint states:
- board_id: "123"
- state: "all" (options: "active", "closed", "future", "all")

Returns:
- Sprint ID, name, state, dates
- Sprint goals and progress information
- Perfect for sprint planning and retrospectives
```

#### Daily Standup Summary (Scrum Masters)
```
Get comprehensive daily standup report for active sprint:

Parameters:
- board_id: "123" (required - get from get-agile-boards)

Returns detailed analysis:
- Sprint progress (issues & story points completion %)
- Status breakdown (To Do, In Progress, Done, etc.)
- Team member workload and current tasks
- Potential blockers (high priority unresolved issues)
- In-progress tasks by assignee
- Key metrics for standup discussion

Perfect for scrum masters to quickly assess sprint health!
```

#### AI-Powered Task Assignment
```
Get smart recommendations for who should work on a task:

Parameters:
- issue_key: "PROJ-123" (required)

AI analyzes:
- Historical data from similar resolved issues
- Team member expertise in components/labels
- Current workload of potential assignees
- Average resolution times for similar work
- Component and technology experience

Returns:
- Ranked list of recommended assignees
- Confidence scores and reasoning
- Current workload information
- Historical performance data
```

#### AI-Powered Story Point Estimation
```
Get intelligent story point estimates based on complexity and history:

Parameters:
- issue_key: "PROJ-123" (required)

AI analyzes:
- Issue complexity (description length, components, labels)
- Historical data from similar resolved issues
- Story point patterns in your project
- Component and issue type complexity

Returns:
- Primary recommendation with confidence level
- Alternative estimates for team discussion
- Complexity analysis breakdown
- Similar issues for reference
- Historical patterns and distribution

Perfect for sprint planning and effort estimation!
```

#### Getting a Confluence Page
```
You can retrieve a page using either its ID or title + space key:

By ID:
- page_id: "123456789"
- include_comments: true
- include_history: false

By title and space:
- title: "API Documentation"
- space_key: "DEV"
- include_comments: false
```

#### Searching Confluence Pages
```
Search using CQL (Confluence Query Language):

Simple text search:
- query: "API Documentation"
- max_results: 10

Search by title:
- query: "title ~ 'API Documentation'"
- max_results: 10

Search in specific space:
- query: "space.key = 'DEV'"
- space_key: "DEV"
- max_results: 5

Recent pages:
- query: "lastmodified >= now('-7d')"

Note: The system automatically adds "type = page" to queries that don't specify a content type.
```

#### Asking Questions About Pages
```
Ask specific questions about page content:

- page_id: "123456789"
- question: "What are the main features described?"
- context_type: "summary" | "details" | "specific"

Or using title + space:
- title: "User Guide"
- space_key: "DOCS"
- question: "How do I configure authentication?"
- context_type: "details"
```

#### Common CQL Query Examples
- Simple text search: `"API Documentation"` (searches in content and title)
- Search by title: `title ~ "API Documentation"`
- Search in space: `space.key = "DEV"`
- Recent pages: `lastmodified >= now("-7d")`
- By author: `creator = "john.doe"`
- Combined: `title ~ "API" AND space.key = "DEV" AND lastmodified >= now("-30d")`
- Text in content: `text ~ "authentication method"`

Note: All queries automatically include `type = page` unless explicitly specified otherwise.

### Available Prompts

#### AI-Powered Analysis
- **`summarize-jira-issue`**: Create a summary of a Jira issue
- **`create-jira-description`**: Generate a structured issue description
- **`summarize-confluence-page`**: Create a summary of a Confluence page
- **`create-confluence-content`**: Generate structured Confluence content
- **`answer-confluence-question`**: Answer questions about specific page content

### Context Types for Question Answering
- **`summary`**: Quick answers using first 1000-1500 characters
- **`details`**: Comprehensive answers using full page content
- **`specific`**: Full content with enhanced filtering (future feature)

For detailed Confluence tool documentation and advanced CQL examples, see [CONFLUENCE_TOOLS.md](CONFLUENCE_TOOLS.md).

## Practical Examples

### Workflow: Research and Documentation
1. **Search for relevant pages**: Use `search-confluence` to find pages related to your topic
2. **Get page details**: Use `get-confluence-page` to retrieve full content with comments
3. **Ask specific questions**: Use `ask-confluence-page` to extract specific information
4. **Create summaries**: Use `summarize-confluence-page` prompt for quick overviews

### Common Use Cases

#### Finding Documentation
```
"Search for all API documentation in the DEV space that was updated in the last month"
→ Use search-confluence with query: "type = page AND space.key = 'DEV' AND title ~ 'API' AND lastmodified >= now('-30d')"
```

#### Getting Page Information
```
"Get the User Guide page from DOCS space with all comments"
→ Use get-confluence-page with title: "User Guide", space_key: "DOCS", include_comments: true
```

#### Content Analysis
```
"What authentication methods are supported according to the API documentation?"
→ Use ask-confluence-page with the API doc page ID and your specific question
```

#### Knowledge Extraction
```
"Summarize the key points from the deployment guide"
→ Use summarize-confluence-page prompt with the deployment guide page ID
```

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).


You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /Users/annmariyajoshy/vibecoding/mcp-jira-confluence run mcp-jira-confluence
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

## Changelog

### Version 0.2.7 (2025-08-22)

**Critical Agile API Fixes:**

- **🔧 Fixed Jira Agile API Endpoints** - Resolved 404 errors with legacy Jira instances:
  - **Corrected greenhopper URLs**: Fixed `/rest/api/2/greenhopper/1.0/rapidview` → `/rest/greenhopper/1.0/rapidviews/list`
  - **Added sprint query endpoint**: Implemented `/rest/greenhopper/1.0/sprintquery/{board_id}` for legacy Jira
  - **Enhanced API fallbacks**: Better error handling with graceful degradation from modern to legacy APIs
  - **Direct session calls**: Improved control over HTTP requests for agile endpoints
  - **JQL fallback**: Added JQL search fallback for sprint issues when agile API unavailable
  - **Response normalization**: Convert legacy API responses to modern format for consistency

**Technical Improvements:**

- Fixed argument validation in server.py to allow empty parameters for some tools
- Enhanced error messages with specific API endpoint information
- Added comprehensive API documentation (AGILE_API_FIX.md)
- Better compatibility with both Jira Cloud and Server instances
- Improved debugging information for API endpoint issues

### Version 0.2.6 (2025-08-22)

**Major Agile/Scrum Features:**

- **🏃‍♂️ Complete Agile/Scrum Toolset** - Full suite of tools for scrum masters and agile teams:
  - **`get-agile-boards`** - Get all agile boards or filter by project with board types and project info
  - **`get-board-sprints`** - Get sprints for any board (active, closed, future, or all) with goals and dates
  - **`get-daily-standup-summary`** - Comprehensive daily standup reports for scrum masters with:
    - Sprint progress metrics (issues & story points completion %)
    - Team status breakdown with current workloads
    - Potential blockers identification
    - In-progress tasks by assignee
  - **`get-task-assignment-recommendations`** - AI-powered assignment suggestions using:
    - Historical data from similar resolved issues
    - Team member expertise analysis
    - Current workload considerations
    - Component and technology experience
  - **`estimate-story-points`** - AI-powered story point estimation using:
    - Complexity analysis (description, components, labels)
    - Historical patterns from similar issues
    - Confidence scoring and alternatives
    - Reference to most similar resolved issues

**Technical Enhancements:**

- Added comprehensive agile API support with fallback to greenhopper for older Jira versions
- Implemented sophisticated AI analysis algorithms for assignment and estimation
- Enhanced error handling for cases with no active sprints or insufficient data
- Rich markdown formatting for all agile tool outputs
- Embedded resource support for better MCP integration

### Version 0.2.5 (2025-08-22)

**Enhanced Jira Transitions:**

- **Enhanced `transition-jira-issue`** - Now supports transition by name instead of cryptic IDs:
  - **Human-readable transitions** - Use "In Progress", "Done", "To Do" instead of numeric IDs
  - **Automatic ID resolution** - Finds the correct transition ID from user-friendly names
  - **Smart matching** - Matches both transition names and target status names
  - **Helpful error messages** - Shows available transitions when invalid names are used
  - **Backwards compatibility** - Still supports transition_id parameter for advanced users

- **New `get-jira-transitions` tool** - Discover available transitions for any issue:
  - **Complete transition list** - Shows all possible status changes for an issue
  - **Rich information** - Displays transition names, target statuses, and IDs
  - **Usage guidance** - Provides examples for using each transition
  - **User-friendly format** - Clear markdown formatting for easy reading

**Technical Improvements:**

- Added `transition_issue_by_name()` method with intelligent transition matching
- Enhanced error handling with available transitions in error messages  
- Case-insensitive transition name matching for better user experience
- Updated tool schemas to support both name and ID parameters
- Comprehensive validation and helpful error messages

### Version 0.2.4 (2025-07-27)

**Enhanced Confluence Search:**

- **Smart CQL Query Builder** - Automatically enhances simple search queries with proper CQL syntax:
  - **Simple text queries** - "API docs" becomes `(title ~ "API docs" OR text ~ "API docs")`
  - **Phrase detection** - Longer queries become `text ~ "your search phrase"`
  - **Advanced CQL preservation** - Complex queries with operators (AND, OR, ~, =) are used as-is
  - **Space integration** - Automatically adds space constraints when specified
  - **Query transparency** - Shows the enhanced CQL query in search results

**Technical Improvements:**

- Added `build_smart_cql_query()` function for intelligent query enhancement
- Enhanced search-confluence tool description to explain automatic query enhancement
- Better user experience with query transformation visibility
- Improved search accuracy for both novice and advanced users

### Version 0.2.3 (2025-07-27)

**Enhanced Link Extraction:**

- **Enhanced `extract-confluence-links`** - Now extracts both Confluence pages AND Git repository URLs:
  - **Git Repository Support** - Detects URLs from GitHub, GitLab, Bitbucket, Azure DevOps, and other Git platforms
  - **Smart Pattern Matching** - Uses regex patterns to identify repository URLs in issue descriptions, comments, and remote links
  - **Comprehensive Coverage** - Scans all issue text fields for both Confluence and Git references
  - **Rich Output** - Returns organized lists of both Confluence pages and Git repositories with context

**Technical Improvements:**

- Added `_extract_git_urls_from_text()` method with support for major Git platforms
- Enhanced URL extraction patterns for better accuracy
- Improved tool description and documentation
- Better organization of extracted links by type (Confluence vs Git)

### Version 0.2.2 (2025-07-27)

**New Jira Tools:**

- **`get-my-assigned-issues`** - Get issues assigned to you ordered by priority (highest first) and creation date (newest first)
  - Configurable max results (default: 25, max: 100)
  - Option to include completed/closed issues
  - Rich formatting with status, priority, type, dates
- **`summarize-jira-issue`** - Comprehensive issue analysis including:
  - Complete issue details (status, priority, assignee, dates)
  - Full description and recent comments (last 5)
  - Confluence page references from remote links
  - Formatted as markdown for easy AI processing
- **`extract-confluence-links`** - Find all Confluence page references in issues:
  - Scans issue description, all comments, and remote links
  - Supports multiple Confluence URL patterns (atlassian.net, custom domains)
  - Returns link titles, URLs, and source context

**Technical Enhancements:**

- Added `get_current_user()` API method for user context
- Enhanced JQL queries with proper field selection and ordering
- Robust URL extraction with regex pattern matching
- Improved error handling for missing or invalid issues
- Better date formatting for human readability

### Version 0.2.1 (2025-07-27)

**Formatting Fixes:**

- **Fixed 400 Bad Request errors** with complex markdown formatting in Confluence pages
- **Implemented intelligent complexity detection** - automatically chooses conversion strategy
- **Added robust error handling** with graceful fallbacks for conversion failures
- **Enhanced list processing** with proper HTML grouping and nesting

### Version 0.2.0 (2025-07-27)

**Major Improvements:**

- **Fixed EmbeddedResource validation errors** - All tools now use the correct MCP structure with `type: "resource"` and proper `TextResourceContents` format
- **Enhanced Confluence formatting** - Dramatically improved markdown to Confluence conversion:
  - Proper list handling (grouped `<ul>`/`<ol>` tags instead of individual ones)
  - Better code block formatting with language support
  - Improved inline formatting (bold, italic, code, links)
  - Smarter paragraph handling
  - More robust markdown detection patterns
- **Fixed HTTP 409 conflicts** - Made version parameter optional in `update-confluence-page` with automatic version fetching
- **Added missing Confluence tools** - Implemented `get-confluence-page` and `search-confluence-pages` with proper CQL support
- **Improved error handling** - Better error messages and validation throughout

**Technical Changes:**

- Rewrote `ConfluenceFormatter.markdown_to_confluence()` with line-by-line processing
- Added regex-based markdown detection with multiple pattern matching
- Enhanced `_process_inline_formatting()` helper for consistent formatting
- Improved version conflict resolution in page updates
- Added comprehensive logging for format detection and conversion

### Version 0.1.9 (2025-07-26)

- Initial PyPI release with basic Jira and Confluence functionality
- Fixed basic EmbeddedResource structure issues
- Added core tool implementations