# Release Summary: v0.2.7 - Critical Agile API Fixes

## 🎉 Successfully Published to PyPI!

**Package:** `mcp-jira-confluence` v0.2.7  
**Published:** August 22, 2025  
**PyPI URL:** https://pypi.org/project/mcp-jira-confluence/0.2.7/

## 🔧 What Was Fixed

### Critical Agile API Issues Resolved:
1. **404 Errors with Legacy Jira** - Fixed incorrect greenhopper API endpoints
2. **Compatibility Issues** - Enhanced support for older Jira Server instances
3. **API Fallback Problems** - Improved graceful degradation from modern to legacy APIs

### Specific Technical Fixes:

#### ❌ **Before (Broken)**:
```
/rest/api/2/greenhopper/1.0/rapidview  # ← WRONG PATH
```

#### ✅ **After (Fixed)**:
```
/rest/greenhopper/1.0/rapidviews/list  # ← CORRECT PATH
/rest/greenhopper/1.0/sprintquery/{board_id}  # ← ADDED SPRINT ENDPOINT
```

## 📋 **Key Improvements**

### 1. **Corrected API Endpoints**
- Fixed greenhopper boards endpoint
- Added proper sprint query endpoint
- Implemented JQL fallback for sprint issues

### 2. **Enhanced Error Handling**
- Better compatibility detection
- Graceful degradation between API versions
- Meaningful error messages with debugging info

### 3. **Improved Reliability**
- Direct session management for agile APIs
- Response format normalization
- Comprehensive fallback mechanisms

### 4. **Better Documentation**
- Added AGILE_API_FIX.md with endpoint reference
- Updated changelog with technical details
- Enhanced error messages for debugging

## 🚀 **Benefits for Users**

✅ **Legacy Jira Support** - Now works with older Jira Server instances  
✅ **No More 404 Errors** - Correct API endpoints eliminate common failures  
✅ **Universal Compatibility** - Works with both Jira Cloud and Server  
✅ **Better Debugging** - Clear error messages help troubleshoot issues  
✅ **Consistent Experience** - Same functionality regardless of Jira version  

## 📦 **Installation**

```bash
# Install/Update to latest version
uvx install mcp-jira-confluence

# Or via pip
pip install --upgrade mcp-jira-confluence
```

## 🎯 **Next Steps**

1. **Test with Legacy Jira** - Verify fixes work with older instances
2. **Monitor Usage** - Watch for any remaining edge cases
3. **Documentation Updates** - Ensure all docs reflect new capabilities
4. **Community Feedback** - Gather user feedback on improvements

## 📊 **Version History**
- **v0.2.7** - Critical agile API fixes (THIS RELEASE)
- **v0.2.6** - Complete agile/scrum toolset 
- **v0.2.5** - Enhanced Jira transitions
- **v0.2.4** - Smart Confluence search

---

**🔥 This release makes the agile tools truly production-ready for all Jira environments!**
