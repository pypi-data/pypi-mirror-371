# Jira Agile API Endpoints - Corrected Documentation

## Issue Fixed
The original greenhopper API endpoint was incorrect:
- ❌ **Wrong**: `/rest/api/2/greenhopper/1.0/rapidview`
- ✅ **Correct**: `/rest/greenhopper/1.0/rapidviews/list`

## API Endpoints Reference

### Modern Jira (Agile API - Preferred)
```
Base URL: {jira_url}/rest/agile/1.0/
```

1. **Get Boards**: `GET /board`
   - Query params: `projectKeyOrId` (optional)
   - Response format: `{"values": [...], "total": N}`

2. **Get Board Sprints**: `GET /board/{board_id}/sprint`
   - Query params: `state` (active, closed, future)
   - Response format: `{"values": [...], "total": N}`

3. **Get Sprint Issues**: `GET /sprint/{sprint_id}/issue`
   - Query params: `fields`, `expand`
   - Response format: `{"issues": [...], "total": N}`

### Legacy Jira (Greenhopper API - Fallback)
```
Base URL: {jira_url}/rest/greenhopper/1.0/
```

1. **Get Boards**: `GET /rapidviews/list`
   - Response format: `{"views": [...]}`
   - Convert to: `{"values": [...], "total": N}`

2. **Get Board Sprints**: `GET /sprintquery/{board_id}`
   - Response format: `{"sprints": [...]}`
   - Convert to: `{"values": [...], "total": N}`

3. **Get Sprint Issues**: Use JQL search instead
   - JQL: `sprint = {sprint_id}`
   - Via: `/rest/api/2/search`

## Implementation Notes

1. **Graceful Degradation**: Always try modern API first, fallback to legacy
2. **Response Normalization**: Convert legacy responses to modern format
3. **Error Handling**: Provide meaningful error messages and empty responses
4. **Field Mapping**: Use `customfield_10016` for story points (common default)

## Common Issues & Solutions

### 404 Errors
- **Cause**: Wrong endpoint path (especially greenhopper)
- **Solution**: Use correct paths documented above

### Permission Errors
- **Cause**: User lacks agile/board permissions
- **Solution**: Ensure user has "Browse Projects" and "View Development Tools"

### Field Not Found
- **Cause**: Story points field varies by instance
- **Solution**: Try multiple field names: `customfield_10016`, `storypoints`, etc.

### API Not Available
- **Cause**: Older Jira versions don't have agile API
- **Solution**: Implement greenhopper fallback with format conversion

## Testing
Run `test_agile_api_fix.py` to verify endpoint corrections.
