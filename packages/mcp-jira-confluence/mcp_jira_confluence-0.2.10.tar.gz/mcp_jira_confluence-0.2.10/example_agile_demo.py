#!/usr/bin/env python3
"""
Example demonstrating all agile/scrum tools in the MCP Jira & Confluence server.

This script shows how to use the new agile tools for scrum masters and development teams.
Set your environment variables before running:
  export JIRA_URL="https://yourcompany.atlassian.net"
  export JIRA_USERNAME="your-email@company.com" 
  export JIRA_API_TOKEN="your-api-token"
"""

import asyncio
import sys
import os
sys.path.insert(0, 'src')

from mcp_jira_confluence.jira import jira_client

async def demonstrate_agile_tools():
    """Demonstrate all agile/scrum functionality."""
    
    print("🚀 MCP Jira & Confluence - Agile/Scrum Tools Demo\n")
    
    # Check configuration
    if not os.getenv("JIRA_URL"):
        print("⚠️  Please set JIRA_URL, JIRA_USERNAME, and JIRA_API_TOKEN environment variables")
        print("   export JIRA_URL='https://yourcompany.atlassian.net'")
        print("   export JIRA_USERNAME='your-email@company.com'")
        print("   export JIRA_API_TOKEN='your-api-token'\n")
        return
    
    try:
        # 1. Get Agile Boards
        print("1️⃣ Getting Agile Boards...")
        boards_result = await jira_client.get_agile_boards()
        boards = boards_result.get("values", [])
        
        if boards:
            print(f"   Found {len(boards)} boards:")
            for board in boards[:3]:  # Show first 3
                print(f"   - {board.get('name', 'Unknown')} (ID: {board.get('id', 'N/A')}) - {board.get('type', 'Unknown')}")
            
            # Use the first board for subsequent demos
            board_id = boards[0].get("id")
            board_name = boards[0].get("name", "Unknown")
            print(f"   Using board '{board_name}' (ID: {board_id}) for demo...\n")
            
            # 2. Get Board Sprints
            print("2️⃣ Getting Board Sprints...")
            sprints_result = await jira_client.get_board_sprints(str(board_id), "all")
            sprints = sprints_result.get("values", [])
            
            if sprints:
                print(f"   Found {len(sprints)} sprints:")
                for sprint in sprints[:3]:  # Show first 3
                    print(f"   - {sprint.get('name', 'Unknown')} ({sprint.get('state', 'Unknown')})")
            else:
                print("   No sprints found for this board")
            print()
            
            # 3. Daily Standup Summary
            print("3️⃣ Getting Daily Standup Summary...")
            standup = await jira_client.get_daily_standup_summary(str(board_id))
            
            if standup.get("status") == "no_active_sprint":
                print("   No active sprint found for standup summary")
            elif standup.get("status") == "error":
                print(f"   Error: {standup.get('message', 'Unknown error')}")
            else:
                sprint = standup.get("sprint", {})
                metrics = standup.get("metrics", {})
                print(f"   Active Sprint: {sprint.get('name', 'Unknown')}")
                print(f"   Progress: {metrics.get('completed_issues', 0)}/{metrics.get('total_issues', 0)} issues")
                print(f"   Story Points: {metrics.get('completed_story_points', 0)}/{metrics.get('total_story_points', 0)}")
                
                blockers = standup.get("potential_blockers", [])
                if blockers:
                    print(f"   Potential Blockers: {len(blockers)} issues need attention")
            print()
            
        else:
            print("   No agile boards found\n")
        
        # 4. Task Assignment Recommendations (needs a real issue)
        print("4️⃣ Task Assignment Recommendations...")
        print("   (Requires a valid issue key - demo with placeholder)")
        print("   This tool analyzes historical data to recommend the best assignee")
        print("   Based on: expertise, workload, past performance, technology stack\n")
        
        # 5. Story Point Estimation (needs a real issue)
        print("5️⃣ Story Point Estimation...")
        print("   (Requires a valid issue key - demo with placeholder)")
        print("   This tool uses AI to estimate story points based on:")
        print("   - Issue complexity (description length, components, labels)")
        print("   - Historical data from similar resolved issues")
        print("   - Project-specific patterns and team velocity\n")
        
        print("✅ Demo completed! These tools provide comprehensive agile/scrum support:")
        print("   🏃‍♂️ Sprint management and board overview")
        print("   📊 Daily standup summaries with key metrics")  
        print("   🎯 AI-powered task assignment recommendations")
        print("   📏 Intelligent story point estimation")
        print("   🔄 Perfect for scrum masters and development teams!")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        print("   Make sure your Jira configuration is correct and you have access to boards/issues")

if __name__ == "__main__":
    asyncio.run(demonstrate_agile_tools())
