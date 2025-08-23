"""Jira operations for the MCP server."""

import logging
import httpx
import json
from typing import Dict, List, Optional, Any
from urllib.parse import quote

from .config import JiraConfig, get_jira_config

logger = logging.getLogger(__name__)


class JiraClient:
    """Client for interacting with Jira API."""

    def __init__(self, config: Optional[JiraConfig] = None):
        """Initialize the Jira client with configuration."""
        self.config = config or get_jira_config()
        self._session = None
        self._headers = {}
        
        # Configure authorization headers
        if self.config.personal_token:
            self._headers["Authorization"] = f"Bearer {self.config.personal_token}"
        elif self.config.username and self.config.api_token:
            from base64 import b64encode
            auth_str = f"{self.config.username}:{self.config.api_token}"
            auth_bytes = auth_str.encode('ascii')
            auth_base64 = b64encode(auth_bytes).decode('ascii')
            self._headers["Authorization"] = f"Basic {auth_base64}"
            
        # Common headers
        self._headers["Accept"] = "application/json"
        self._headers["Content-Type"] = "application/json"

    async def get_session(self) -> httpx.AsyncClient:
        """Get or create an HTTP session."""
        if self._session is None or self._session.is_closed:
            self._session = httpx.AsyncClient(
                verify=self.config.ssl_verify,
                headers=self._headers,
                follow_redirects=True,
                timeout=30.0
            )
        return self._session
        
    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.is_closed:
            await self._session.aclose()
            self._session = None
    
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the Jira API."""
        session = await self.get_session()
        url = f"{self.config.url}/rest/api/2/{path}"
        response = await session.get(url, params=params)
        response.raise_for_status()
        return response.json()
        
    async def post(self, path: str, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a POST request to the Jira API."""
        session = await self.get_session()
        url = f"{self.config.url}/rest/api/2/{path}"
        response = await session.post(url, json=data, params=params)
        response.raise_for_status()
        return response.json()
        
    async def put(self, path: str, data: Dict[str, Any], params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a PUT request to the Jira API."""
        session = await self.get_session()
        url = f"{self.config.url}/rest/api/2/{path}"
        response = await session.put(url, json=data, params=params)
        response.raise_for_status()
        if response.status_code == 204:  # No content
            return {}
        return response.json()

    async def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get an issue by its key."""
        fields = "summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype"
        return await self.get(f"issue/{issue_key}", params={"fields": fields})
    
    async def search_issues(self, jql: str, start: int = 0, max_results: int = 50) -> Dict[str, Any]:
        """Search for issues using JQL."""
        fields = "summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype"
        return await self.get("search", params={
            "jql": jql,
            "startAt": start,
            "maxResults": max_results,
            "fields": fields
        })
    
    async def create_issue(self, project_key: str, summary: str, issue_type: str, 
                          description: Optional[str] = None, 
                          assignee: Optional[str] = None) -> Dict[str, Any]:
        """Create a new issue."""
        data = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "issuetype": {"name": issue_type},
            }
        }
        
        if description:
            data["fields"]["description"] = description
            
        if assignee:
            data["fields"]["assignee"] = {"name": assignee}
            
        return await self.post("issue", data)
    
    async def update_issue(self, issue_key: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Update an issue."""
        data = {"fields": fields}
        return await self.put(f"issue/{issue_key}", data)
    
    async def add_comment(self, issue_key: str, comment: str) -> Dict[str, Any]:
        """Add a comment to an issue."""
        data = {"body": comment}
        return await self.post(f"issue/{issue_key}/comment", data)
    
    async def get_transitions(self, issue_key: str) -> Dict[str, Any]:
        """Get available transitions for an issue."""
        return await self.get(f"issue/{issue_key}/transitions")
    
    async def transition_issue(self, issue_key: str, transition_id: str) -> Dict[str, Any]:
        """Transition an issue to a new status."""
        data = {
            "transition": {"id": transition_id}
        }
        return await self.post(f"issue/{issue_key}/transitions", data)
        
    async def transition_issue_by_name(self, issue_key: str, transition_name: str) -> Dict[str, Any]:
        """
        Transition an issue to a new status by transition name.
        
        Args:
            issue_key: The issue key (e.g., 'PROJ-123')
            transition_name: Name of the transition (e.g., 'In Progress', 'Done', 'To Do')
            
        Returns:
            Dictionary with transition result and new status information
            
        Raises:
            ValueError: If transition name is not found or multiple matches exist
        """
        # Get available transitions
        transitions_response = await self.get_transitions(issue_key)
        available_transitions = transitions_response.get("transitions", [])
        
        if not available_transitions:
            raise ValueError(f"No transitions available for issue {issue_key}")
        
        # Find matching transition (case-insensitive)
        matching_transitions = []
        transition_name_lower = transition_name.lower().strip()
        
        for transition in available_transitions:
            trans_name = transition.get("name", "").lower().strip()
            trans_to_status = transition.get("to", {}).get("name", "").lower().strip()
            
            # Match by transition name or target status name
            if trans_name == transition_name_lower or trans_to_status == transition_name_lower:
                matching_transitions.append(transition)
        
        if not matching_transitions:
            # Provide helpful error message with available transitions
            available_names = [t.get("name", "Unknown") for t in available_transitions]
            raise ValueError(
                f"Transition '{transition_name}' not found for issue {issue_key}. "
                f"Available transitions: {', '.join(available_names)}"
            )
        
        if len(matching_transitions) > 1:
            trans_names = [t.get("name", "Unknown") for t in matching_transitions]
            raise ValueError(
                f"Multiple transitions match '{transition_name}' for issue {issue_key}: "
                f"{', '.join(trans_names)}. Please be more specific."
            )
        
        # Execute the transition
        transition_id = matching_transitions[0]["id"]
        transition_result = await self.transition_issue(issue_key, transition_id)
        
        # Get updated issue to return new status
        updated_issue = await self.get_issue(issue_key)
        new_status = updated_issue.get("fields", {}).get("status", {}).get("name", "Unknown")
        
        return {
            "transition_executed": matching_transitions[0]["name"],
            "new_status": new_status,
            "transition_id": transition_id,
            "issue_key": issue_key
        }
    
    async def get_project_versions(self, project_key: str) -> List[Dict[str, Any]]:
        """Get all versions for a project."""
        return await self.get(f"project/{project_key}/versions")
    
    async def get_current_user(self) -> Dict[str, Any]:
        """Get information about the current user."""
        return await self.get("myself")
    
    async def get_my_assigned_issues(self, max_results: int = 50, include_done: bool = False) -> Dict[str, Any]:
        """Get issues assigned to the current user, ordered by priority and date."""
        # Build JQL query for assigned issues
        jql_parts = ["assignee = currentUser()"]
        
        if not include_done:
            jql_parts.append('status not in ("Done", "Closed", "Resolved")')
        
        # Order by priority (highest first), then by created date (newest first)
        jql = " AND ".join(jql_parts) + " ORDER BY priority DESC, created DESC"
        
        fields = "summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype,duedate"
        return await self.get("search", params={
            "jql": jql,
            "startAt": 0,
            "maxResults": max_results,
            "fields": fields
        })
    
    async def summarize_issue(self, issue_key: str) -> Dict[str, Any]:
        """Get detailed information about an issue for summarization including comments and links."""
        # Get issue with expanded fields including comments
        issue_data = await self.get(f"issue/{issue_key}", params={
            "fields": "summary,description,status,assignee,reporter,labels,priority,created,updated,issuetype,duedate,comment",
            "expand": "changelog"
        })
        
        # Get remote links (including Confluence links)
        try:
            remote_links = await self.get(f"issue/{issue_key}/remotelink")
        except:
            remote_links = []
        
        # Combine issue data with remote links for easier processing
        issue_data["remoteLinks"] = remote_links
        
        return issue_data
        
    async def extract_confluence_links(self, issue_key: str) -> List[Dict[str, Any]]:
        """Extract Confluence links from an issue's description, comments, and remote links."""
        confluence_links = []
        
        try:
            # Get issue data with comments and remote links
            issue_data = await self.summarize_issue(issue_key)
            
            # Check remote links first (most reliable)
            if "remoteLinks" in issue_data:
                for link in issue_data["remoteLinks"]:
                    if link.get("object", {}).get("url", "").find("confluence") != -1:
                        confluence_links.append({
                            "type": "remote_link",
                            "title": link.get("object", {}).get("title", ""),
                            "url": link.get("object", {}).get("url", ""),
                            "summary": link.get("object", {}).get("summary", "")
                        })
            
            # Check description for Confluence URLs
            description = issue_data.get("fields", {}).get("description", "") or ""
            confluence_urls = self._extract_confluence_urls_from_text(description)
            for url in confluence_urls:
                confluence_links.append({
                    "type": "description_link",
                    "title": "Confluence Page",
                    "url": url,
                    "summary": "Found in issue description"
                })
            
            # Check comments for Confluence URLs
            comments = issue_data.get("fields", {}).get("comment", {}).get("comments", [])
            for comment in comments:
                comment_body = comment.get("body", "") or ""
                confluence_urls = self._extract_confluence_urls_from_text(comment_body)
                for url in confluence_urls:
                    confluence_links.append({
                        "type": "comment_link",
                        "title": "Confluence Page",
                        "url": url,
                        "summary": f"Found in comment by {comment.get('author', {}).get('displayName', 'Unknown')}"
                    })
            
        except Exception as e:
            logger.warning(f"Error extracting Confluence links from {issue_key}: {e}")
        
        return confluence_links
    
    def _extract_confluence_urls_from_text(self, text: str) -> List[str]:
        """Extract Confluence URLs from text using regex."""
        import re
        
        if not text:
            return []
        
        # Common Confluence URL patterns
        patterns = [
            r'https?://[^/\s]+/confluence/[^\s\)]+',  # Standard Confluence URLs
            r'https?://[^/\s]+/wiki/[^\s\)]+',        # Wiki-style URLs
            r'https?://[^/\s]+/display/[^\s\)]+',     # Display URLs
            r'https?://[^\.]+\.atlassian\.net/wiki/[^\s\)]+',  # Atlassian cloud
        ]
        
        urls = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            urls.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls
    
    def _extract_git_urls_from_text(self, text: str) -> List[str]:
        """Extract Git repository URLs from text using regex."""
        import re
        
        if not text:
            return []
        
        # Common Git repository URL patterns
        patterns = [
            r'https?://github\.com/[^/\s]+/[^/\s]+(?:\.git)?(?:/[^\s\)]*)?',  # GitHub
            r'https?://gitlab\.com/[^/\s]+/[^/\s]+(?:\.git)?(?:/[^\s\)]*)?',  # GitLab.com
            r'https?://bitbucket\.org/[^/\s]+/[^/\s]+(?:\.git)?(?:/[^\s\)]*)?',  # Bitbucket
            r'https?://[^/\s]+/gitlab/[^/\s]+/[^/\s]+(?:\.git)?(?:/[^\s\)]*)?',  # Self-hosted GitLab
            r'https?://[^/\s]+/bitbucket/[^/\s]+/[^/\s]+(?:\.git)?(?:/[^\s\)]*)?',  # Self-hosted Bitbucket
            r'git@[^:\s]+:[^/\s]+/[^/\s]+(?:\.git)?',  # SSH URLs
            r'https?://[^/\s]+\.visualstudio\.com/[^/\s]+/_git/[^/\s]+',  # Azure DevOps
            r'https?://dev\.azure\.com/[^/\s]+/[^/\s]+/_git/[^/\s]+',  # Azure DevOps new format
            r'https?://[^/\s]+/git/[^/\s]+/[^/\s]+(?:\.git)?(?:/[^\s\)]*)?',  # Generic Git hosting
        ]
        
        urls = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            urls.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_urls = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                unique_urls.append(url)
        
        return unique_urls
    
    async def extract_confluence_and_git_links(self, issue_key: str, include_git_urls: bool = True) -> List[Dict[str, Any]]:
        """Extract both Confluence and Git links from an issue's description, comments, and remote links."""
        all_links = []
        
        try:
            # Get issue data with comments and remote links
            issue_data = await self.summarize_issue(issue_key)
            
            # Check remote links first (most reliable)
            if "remoteLinks" in issue_data:
                for link in issue_data["remoteLinks"]:
                    url = link.get("object", {}).get("url", "")
                    title = link.get("object", {}).get("title", "")
                    summary = link.get("object", {}).get("summary", "")
                    
                    # Check if it's a Confluence link
                    if url.find("confluence") != -1 or url.find("wiki") != -1:
                        all_links.append({
                            "type": "remote_link",
                            "category": "confluence",
                            "title": title or "Confluence Page",
                            "url": url,
                            "summary": summary
                        })
                    # Check if it's a Git repository link
                    elif include_git_urls and any(pattern in url.lower() for pattern in ['github', 'gitlab', 'bitbucket', 'git', '_git']):
                        all_links.append({
                            "type": "remote_link", 
                            "category": "git",
                            "title": title or "Git Repository",
                            "url": url,
                            "summary": summary
                        })
            
            # Check description for Confluence and Git URLs
            description = issue_data.get("fields", {}).get("description", "") or ""
            
            confluence_urls = self._extract_confluence_urls_from_text(description)
            for url in confluence_urls:
                all_links.append({
                    "type": "description_link",
                    "category": "confluence",
                    "title": "Confluence Page",
                    "url": url,
                    "summary": "Found in issue description"
                })
            
            if include_git_urls:
                git_urls = self._extract_git_urls_from_text(description)
                for url in git_urls:
                    all_links.append({
                        "type": "description_link",
                        "category": "git", 
                        "title": "Git Repository",
                        "url": url,
                        "summary": "Found in issue description"
                    })
            
            # Check comments for Confluence and Git URLs
            comments = issue_data.get("fields", {}).get("comment", {}).get("comments", [])
            for comment in comments:
                comment_body = comment.get("body", "") or ""
                author = comment.get('author', {}).get('displayName', 'Unknown')
                
                confluence_urls = self._extract_confluence_urls_from_text(comment_body)
                for url in confluence_urls:
                    all_links.append({
                        "type": "comment_link",
                        "category": "confluence",
                        "title": "Confluence Page",
                        "url": url,
                        "summary": f"Found in comment by {author}"
                    })
                
                if include_git_urls:
                    git_urls = self._extract_git_urls_from_text(comment_body)
                    for url in git_urls:
                        all_links.append({
                            "type": "comment_link",
                            "category": "git",
                            "title": "Git Repository", 
                            "url": url,
                            "summary": f"Found in comment by {author}"
                        })
            
        except Exception as e:
            logger.warning(f"Error extracting links from {issue_key}: {e}")
        
        return all_links
    
    # Agile/Scrum Methods
    
    async def get_agile_boards(self, project_key: Optional[str] = None) -> Dict[str, Any]:
        """Get all agile boards or boards for a specific project."""
        try:
            # Use the agile API endpoint (modern Jira)
            params = {}
            if project_key:
                params["projectKeyOrId"] = project_key
            
            # Try to get boards via agile API
            session = await self.get_session()
            url = f"{self.config.url}/rest/agile/1.0/board"
            response = await session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Agile API not available, trying greenhopper: {e}")
            try:
                # Fallback to greenhopper API (older Jira versions)
                session = await self.get_session()
                url = f"{self.config.url}/rest/greenhopper/1.0/rapidviews/list"
                response = await session.get(url)
                response.raise_for_status()
                boards_data = response.json()
                
                # Convert greenhopper format to match agile API structure
                views = boards_data.get("views", [])
                converted_boards = []
                for view in views:
                    converted_boards.append({
                        "id": view.get("id"),
                        "name": view.get("name"),
                        "type": "scrum",  # Greenhopper boards are typically scrum
                        "location": {
                            "projectId": view.get("sprintSupportEnabled", False),
                            "name": "Unknown Project"
                        }
                    })
                
                return {
                    "maxResults": len(converted_boards),
                    "startAt": 0,
                    "total": len(converted_boards),
                    "isLast": True,
                    "values": converted_boards
                }
            except Exception as fallback_error:
                logger.error(f"Failed to get boards with both APIs: {fallback_error}")
                return {"values": [], "total": 0}
    
    async def get_board_sprints(self, board_id: str, state: str = "active") -> Dict[str, Any]:
        """
        Get sprints for a specific board.
        
        Args:
            board_id: The ID of the agile board
            state: Sprint state - 'active', 'closed', 'future', or 'all'
        """
        try:
            # Try modern agile API first
            params = {}
            if state != "all":
                params["state"] = state
            
            session = await self.get_session()
            url = f"{self.config.url}/rest/agile/1.0/board/{board_id}/sprint"
            response = await session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Agile API sprints not available, trying greenhopper: {e}")
            try:
                # Fallback to greenhopper API for older Jira versions
                session = await self.get_session()
                
                # Get sprints using greenhopper API
                url = f"{self.config.url}/rest/greenhopper/1.0/sprintquery/{board_id}"
                response = await session.get(url)
                response.raise_for_status()
                sprints_data = response.json()
                
                # Convert greenhopper format to agile API format
                sprints = sprints_data.get("sprints", [])
                filtered_sprints = []
                
                for sprint in sprints:
                    sprint_state = sprint.get("state", "").lower()
                    if state == "all" or sprint_state == state.lower():
                        filtered_sprints.append({
                            "id": sprint.get("id"),
                            "name": sprint.get("name"),
                            "state": sprint_state,
                            "startDate": sprint.get("startDate"),
                            "endDate": sprint.get("endDate"),
                            "goal": sprint.get("goal", "")
                        })
                
                return {
                    "maxResults": len(filtered_sprints),
                    "startAt": 0,
                    "total": len(filtered_sprints),
                    "isLast": True,
                    "values": filtered_sprints
                }
            except Exception as fallback_error:
                logger.error(f"Failed to get sprints for board {board_id} with both APIs: {fallback_error}")
                return {"values": [], "total": 0}
    
    async def get_sprint_issues(self, sprint_id: str) -> Dict[str, Any]:
        """Get all issues in a specific sprint."""
        try:
            # Try modern agile API first
            session = await self.get_session()
            url = f"{self.config.url}/rest/agile/1.0/sprint/{sprint_id}/issue"
            params = {
                "fields": "summary,status,assignee,priority,issuetype,customfield_10016,timeoriginalestimate,timeestimate,timespent,parent",
                "expand": "changelog"
            }
            response = await session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Agile API sprint issues not available, trying JQL search: {e}")
            try:
                # Fallback to JQL search for sprint issues
                jql = f"sprint = {sprint_id}"
                fields = "summary,status,assignee,priority,issuetype,customfield_10016,timeoriginalestimate,timeestimate,timespent,parent"
                return await self.search_issues(jql, max_results=1000)
            except Exception as fallback_error:
                logger.error(f"Failed to get issues for sprint {sprint_id} with both methods: {fallback_error}")
                return {"issues": [], "total": 0}
    
    async def get_daily_standup_summary(self, board_id: str) -> Dict[str, Any]:
        """
        Get a comprehensive daily standup summary for the active sprint.
        
        Returns sprint progress, team member status, blockers, and key metrics.
        """
        try:
            # Get active sprints for the board
            active_sprints = await self.get_board_sprints(board_id, "active")
            
            if not active_sprints.get("values"):
                return {
                    "status": "no_active_sprint",
                    "message": "No active sprint found for this board",
                    "board_id": board_id
                }
            
            active_sprint = active_sprints["values"][0]  # Get the first active sprint
            sprint_id = active_sprint["id"]
            sprint_name = active_sprint["name"]
            sprint_start = active_sprint.get("startDate", "Unknown")
            sprint_end = active_sprint.get("endDate", "Unknown")
            
            # Get all issues in the sprint
            sprint_issues = await self.get_sprint_issues(sprint_id)
            issues = sprint_issues.get("issues", [])
            
            # Analyze sprint progress
            status_breakdown = {}
            assignee_breakdown = {}
            story_points_total = 0
            story_points_completed = 0
            blockers = []
            in_progress_tasks = []
            completed_today = []
            
            for issue in issues:
                fields = issue.get("fields", {})
                key = issue.get("key", "")
                summary = fields.get("summary", "")
                status = fields.get("status", {}).get("name", "Unknown")
                assignee = fields.get("assignee", {}).get("displayName", "Unassigned")
                priority = fields.get("priority", {}).get("name", "Unknown")
                issue_type = fields.get("issuetype", {}).get("name", "Unknown")
                
                # Story points
                story_points = fields.get("customfield_10016", 0) or fields.get("storypoints", 0) or 0
                if isinstance(story_points, (int, float)):
                    story_points_total += story_points
                    if status.lower() in ["done", "closed", "resolved"]:
                        story_points_completed += story_points
                
                # Status breakdown
                status_breakdown[status] = status_breakdown.get(status, 0) + 1
                
                # Assignee breakdown
                if assignee not in assignee_breakdown:
                    assignee_breakdown[assignee] = {
                        "total": 0,
                        "in_progress": 0,
                        "completed": 0,
                        "todo": 0,
                        "issues": []
                    }
                
                assignee_breakdown[assignee]["total"] += 1
                assignee_breakdown[assignee]["issues"].append({
                    "key": key,
                    "summary": summary,
                    "status": status,
                    "priority": priority,
                    "story_points": story_points
                })
                
                if status.lower() in ["done", "closed", "resolved"]:
                    assignee_breakdown[assignee]["completed"] += 1
                elif status.lower() in ["in progress", "in review", "testing"]:
                    assignee_breakdown[assignee]["in_progress"] += 1
                    in_progress_tasks.append({
                        "key": key,
                        "summary": summary,
                        "assignee": assignee,
                        "status": status,
                        "priority": priority
                    })
                else:
                    assignee_breakdown[assignee]["todo"] += 1
                
                # Check for blockers (issues with high priority or specific labels)
                if priority.lower() in ["highest", "high", "blocker"] and status.lower() not in ["done", "closed", "resolved"]:
                    blockers.append({
                        "key": key,
                        "summary": summary,
                        "assignee": assignee,
                        "status": status,
                        "priority": priority
                    })
            
            # Calculate metrics
            completion_percentage = (story_points_completed / story_points_total * 100) if story_points_total > 0 else 0
            total_issues = len(issues)
            completed_issues = status_breakdown.get("Done", 0) + status_breakdown.get("Closed", 0) + status_breakdown.get("Resolved", 0)
            issue_completion_percentage = (completed_issues / total_issues * 100) if total_issues > 0 else 0
            
            return {
                "status": "success",
                "sprint": {
                    "id": sprint_id,
                    "name": sprint_name,
                    "start_date": sprint_start,
                    "end_date": sprint_end
                },
                "metrics": {
                    "total_issues": total_issues,
                    "completed_issues": completed_issues,
                    "issue_completion_percentage": round(issue_completion_percentage, 1),
                    "total_story_points": story_points_total,
                    "completed_story_points": story_points_completed,
                    "story_point_completion_percentage": round(completion_percentage, 1)
                },
                "status_breakdown": status_breakdown,
                "team_breakdown": assignee_breakdown,
                "in_progress_tasks": in_progress_tasks,
                "potential_blockers": blockers,
                "board_id": board_id
            }
            
        except Exception as e:
            logger.error(f"Failed to generate daily standup summary: {e}")
            return {
                "status": "error",
                "message": f"Failed to generate daily standup summary: {str(e)}",
                "board_id": board_id
            }
    
    async def get_task_assignment_recommendations(self, issue_key: str) -> Dict[str, Any]:
        """
        Get recommendations for who should be assigned to a task based on historical data.
        
        Analyzes similar issues, team member expertise, and workload.
        """
        try:
            # Get the issue details
            issue = await self.get_issue(issue_key)
            fields = issue.get("fields", {})
            issue_type = fields.get("issuetype", {}).get("name", "")
            summary = fields.get("summary", "")
            description = fields.get("description", "")
            component_names = [comp.get("name", "") for comp in fields.get("components", [])]
            labels = fields.get("labels", [])
            project_key = fields.get("project", {}).get("key", "")
            
            # Find similar issues based on type, components, and keywords
            jql_parts = [f'project = "{project_key}"']
            
            if issue_type:
                jql_parts.append(f'issuetype = "{issue_type}"')
            
            if component_names:
                component_query = " OR ".join([f'component = "{comp}"' for comp in component_names])
                jql_parts.append(f"({component_query})")
            
            # Look for resolved/closed issues to analyze successful assignments
            jql_parts.append('status in ("Done", "Closed", "Resolved")')
            
            # Search for similar issues in the last 6 months
            jql_parts.append('resolved >= -26w')
            
            jql = " AND ".join(jql_parts) + " ORDER BY resolved DESC"
            
            similar_issues = await self.search_issues(jql, max_results=50)
            
            # Analyze assignments
            assignee_scores = {}
            assignee_stats = {}
            
            for similar_issue in similar_issues.get("issues", []):
                similar_fields = similar_issue.get("fields", {})
                assignee = similar_fields.get("assignee")
                if not assignee:
                    continue
                
                assignee_name = assignee.get("displayName", "Unknown")
                assignee_key = assignee.get("key", assignee_name)
                
                if assignee_key not in assignee_scores:
                    assignee_scores[assignee_key] = {
                        "name": assignee_name,
                        "email": assignee.get("emailAddress", ""),
                        "score": 0,
                        "reasons": [],
                        "similar_issues_count": 0,
                        "avg_resolution_time": 0,
                        "total_resolution_time": 0
                    }
                    assignee_stats[assignee_key] = []
                
                # Calculate points based on similarity
                points = 1  # Base point for same project and type
                
                # Extra points for component match
                similar_components = [comp.get("name", "") for comp in similar_fields.get("components", [])]
                common_components = set(component_names) & set(similar_components)
                if common_components:
                    points += len(common_components) * 2
                    assignee_scores[assignee_key]["reasons"].append(f"Experience with {', '.join(common_components)}")
                
                # Extra points for label match
                similar_labels = similar_fields.get("labels", [])
                common_labels = set(labels) & set(similar_labels)
                if common_labels:
                    points += len(common_labels)
                    assignee_scores[assignee_key]["reasons"].append(f"Experience with {', '.join(common_labels)}")
                
                assignee_scores[assignee_key]["score"] += points
                assignee_scores[assignee_key]["similar_issues_count"] += 1
                
                # Calculate resolution time if available
                created = similar_fields.get("created")
                resolved = similar_fields.get("resolutiondate")
                if created and resolved:
                    try:
                        from datetime import datetime
                        created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                        resolved_dt = datetime.fromisoformat(resolved.replace('Z', '+00:00'))
                        resolution_time = (resolved_dt - created_dt).total_seconds() / 3600  # hours
                        assignee_stats[assignee_key].append(resolution_time)
                    except:
                        pass
            
            # Calculate average resolution times
            for assignee_key, times in assignee_stats.items():
                if times:
                    assignee_scores[assignee_key]["avg_resolution_time"] = sum(times) / len(times)
            
            # Get current workload for top candidates
            recommendations = []
            sorted_assignees = sorted(assignee_scores.items(), key=lambda x: x[1]["score"], reverse=True)
            
            for assignee_key, data in sorted_assignees[:5]:  # Top 5 candidates
                # Get current assigned issues
                current_workload_jql = f'assignee = "{assignee_key}" AND status not in ("Done", "Closed", "Resolved")'
                current_issues = await self.search_issues(current_workload_jql, max_results=100)
                current_workload = current_issues.get("total", 0)
                
                recommendations.append({
                    "assignee": data["name"],
                    "email": data["email"],
                    "score": data["score"],
                    "reasons": list(set(data["reasons"])),  # Remove duplicates
                    "similar_issues_handled": data["similar_issues_count"],
                    "avg_resolution_time_hours": round(data["avg_resolution_time"], 1) if data["avg_resolution_time"] > 0 else "N/A",
                    "current_workload": current_workload,
                    "recommendation_strength": "High" if data["score"] >= 5 else "Medium" if data["score"] >= 3 else "Low"
                })
            
            return {
                "status": "success",
                "issue_key": issue_key,
                "issue_summary": summary,
                "issue_type": issue_type,
                "analysis_based_on": len(similar_issues.get("issues", [])),
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Failed to get task assignment recommendations for {issue_key}: {e}")
            return {
                "status": "error",
                "message": f"Failed to analyze task assignment: {str(e)}",
                "issue_key": issue_key
            }
    
    async def estimate_story_points(self, issue_key: str) -> Dict[str, Any]:
        """
        Estimate story points for an issue based on complexity analysis and historical data.
        
        Analyzes issue complexity, similar issues, and provides recommendations.
        """
        try:
            # Get the issue details
            issue = await self.get_issue(issue_key)
            fields = issue.get("fields", {})
            issue_type = fields.get("issuetype", {}).get("name", "")
            summary = fields.get("summary", "")
            description = fields.get("description", "") or ""
            component_names = [comp.get("name", "") for comp in fields.get("components", [])]
            labels = fields.get("labels", [])
            project_key = fields.get("project", {}).get("key", "")
            
            # Analyze complexity factors
            complexity_factors = {
                "description_length": len(description),
                "title_length": len(summary),
                "has_components": len(component_names) > 0,
                "component_count": len(component_names),
                "has_labels": len(labels) > 0,
                "label_count": len(labels)
            }
            
            # Calculate base complexity score
            complexity_score = 0
            
            # Description length factor
            if complexity_factors["description_length"] > 1000:
                complexity_score += 3
            elif complexity_factors["description_length"] > 500:
                complexity_score += 2
            elif complexity_factors["description_length"] > 200:
                complexity_score += 1
            
            # Component complexity
            complexity_score += min(complexity_factors["component_count"], 3)
            
            # Label complexity
            complexity_score += min(complexity_factors["label_count"] // 2, 2)
            
            # Search for similar resolved issues with story points
            jql_parts = [
                f'project = "{project_key}"',
                'status in ("Done", "Closed", "Resolved")',
                '"Story Points" is not EMPTY',
                'resolved >= -52w'  # Last year
            ]
            
            if issue_type:
                jql_parts.append(f'issuetype = "{issue_type}"')
            
            if component_names:
                component_query = " OR ".join([f'component = "{comp}"' for comp in component_names])
                jql_parts.append(f"({component_query})")
            
            jql = " AND ".join(jql_parts) + " ORDER BY resolved DESC"
            
            similar_issues = await self.search_issues(jql, max_results=100)
            
            # Analyze story points from similar issues
            story_point_data = []
            story_point_field_names = ["customfield_10016", "storypoints", "Story Points"]
            
            for similar_issue in similar_issues.get("issues", []):
                similar_fields = similar_issue.get("fields", {})
                similar_summary = similar_fields.get("summary", "")
                similar_description = similar_fields.get("description", "") or ""
                
                # Try to find story points field
                story_points = None
                for field_name in story_point_field_names:
                    story_points = similar_fields.get(field_name)
                    if story_points is not None:
                        break
                
                if story_points and isinstance(story_points, (int, float)) and story_points > 0:
                    # Calculate similarity score
                    similarity_score = 0
                    
                    # Component similarity
                    similar_components = [comp.get("name", "") for comp in similar_fields.get("components", [])]
                    common_components = set(component_names) & set(similar_components)
                    if common_components:
                        similarity_score += len(common_components) * 2
                    
                    # Description length similarity
                    desc_length_diff = abs(len(description) - len(similar_description))
                    if desc_length_diff < 200:
                        similarity_score += 3
                    elif desc_length_diff < 500:
                        similarity_score += 2
                    elif desc_length_diff < 1000:
                        similarity_score += 1
                    
                    # Title length similarity
                    title_length_diff = abs(len(summary) - len(similar_summary))
                    if title_length_diff < 20:
                        similarity_score += 2
                    elif title_length_diff < 50:
                        similarity_score += 1
                    
                    story_point_data.append({
                        "story_points": story_points,
                        "similarity_score": similarity_score,
                        "issue_key": similar_issue.get("key", ""),
                        "summary": similar_summary[:100] + "..." if len(similar_summary) > 100 else similar_summary
                    })
            
            # Calculate recommendations
            if story_point_data:
                # Weight by similarity score
                weighted_points = []
                for data in story_point_data:
                    weight = max(1, data["similarity_score"])
                    weighted_points.extend([data["story_points"]] * weight)
                
                # Calculate statistics
                avg_points = sum(weighted_points) / len(weighted_points)
                median_points = sorted(weighted_points)[len(weighted_points) // 2]
                
                # Get distribution
                point_distribution = {}
                for points in weighted_points:
                    point_distribution[points] = point_distribution.get(points, 0) + 1
                
                # Most common points
                most_common_points = max(point_distribution.items(), key=lambda x: x[1])[0]
                
                # Adjust based on complexity score
                complexity_adjustment = complexity_score * 0.5
                
                recommended_points = round(avg_points + complexity_adjustment)
                recommended_points = max(1, min(recommended_points, 21))  # Cap between 1-21
                
                # Alternative recommendations
                alternatives = [
                    round(median_points),
                    most_common_points,
                    max(1, round(avg_points))
                ]
                alternatives = list(set([p for p in alternatives if 1 <= p <= 21]))
                
                return {
                    "status": "success",
                    "issue_key": issue_key,
                    "issue_summary": summary,
                    "issue_type": issue_type,
                    "complexity_analysis": {
                        "score": complexity_score,
                        "factors": complexity_factors,
                        "level": "High" if complexity_score >= 6 else "Medium" if complexity_score >= 3 else "Low"
                    },
                    "historical_analysis": {
                        "similar_issues_found": len(story_point_data),
                        "average_points": round(avg_points, 1),
                        "median_points": median_points,
                        "most_common_points": most_common_points,
                        "point_distribution": point_distribution
                    },
                    "recommendation": {
                        "primary": recommended_points,
                        "alternatives": sorted(alternatives),
                        "confidence": "High" if len(story_point_data) >= 10 else "Medium" if len(story_point_data) >= 5 else "Low"
                    },
                    "similar_issues": story_point_data[:5]  # Top 5 most similar
                }
            else:
                # No historical data available, use complexity-based estimation
                base_estimate = 1
                if complexity_score >= 8:
                    base_estimate = 8
                elif complexity_score >= 6:
                    base_estimate = 5
                elif complexity_score >= 4:
                    base_estimate = 3
                elif complexity_score >= 2:
                    base_estimate = 2
                
                return {
                    "status": "success",
                    "issue_key": issue_key,
                    "issue_summary": summary,
                    "issue_type": issue_type,
                    "complexity_analysis": {
                        "score": complexity_score,
                        "factors": complexity_factors,
                        "level": "High" if complexity_score >= 6 else "Medium" if complexity_score >= 3 else "Low"
                    },
                    "historical_analysis": {
                        "similar_issues_found": 0,
                        "note": "No similar resolved issues with story points found"
                    },
                    "recommendation": {
                        "primary": base_estimate,
                        "alternatives": [1, 2, 3, 5] if base_estimate <= 3 else [3, 5, 8, 13],
                        "confidence": "Low",
                        "note": "Based on complexity analysis only - consider team discussion"
                    },
                    "similar_issues": []
                }
            
        except Exception as e:
            logger.error(f"Failed to estimate story points for {issue_key}: {e}")
            return {
                "status": "error",
                "message": f"Failed to estimate story points: {str(e)}",
                "issue_key": issue_key
            }

# Instantiate a global client
jira_client = JiraClient()
