# Janito v3.3.0 Release Notes

## Overview
Version 3.3.0 represents a major architectural improvement focused on consolidating and streamlining the plugin system. This release delivers a cleaner, more maintainable codebase while preserving all existing functionality.

## Major Changes

### Plugin System Refactoring
- **Consolidated Architecture**: Unified plugin system from separate `plugin_system/` and `plugins/` directories into a single, coherent structure
- **Core Plugin Organization**: All core plugins now reside in `janito/plugins/core/` with logical grouping by functionality
- **Simplified Loading**: Removed deprecated plugin loading mechanisms and redundant files
- **Enhanced Discovery**: Improved plugin discovery mechanisms with better error handling

### Plugin Structure Improvements
- **Organized Core Plugins**:
  - `janito/plugins/core/filemanager/` - File management tools
  - `janito/plugins/core/codeanalyzer/` - Code analysis tools
  - `janito/plugins/core/imagedisplay/` - Image display functionality
  - `janito/plugins/core/system/` - System-level tools
  - `janito/plugins/core/web/` - Web-related tools

- **New Base Classes**: Added modern plugin base classes for better extensibility
- **Updated Manager**: Enhanced plugin manager with improved functionality and error handling

### Backward Compatibility
- All existing functionality preserved through the new core plugin system
- Old plugin system backed up to `janito/plugins_backup_20250825_070018/` for reference
- No breaking changes to public APIs

## Technical Details

### Files Added
- New plugin base classes and discovery mechanisms
- Comprehensive plugin cleanup documentation
- Enhanced CLI integration for new plugin architecture

### Files Removed
- Deprecated plugin loading mechanisms
- Redundant plugin system files
- Legacy plugin organization structures

### Files Modified
- Plugin manager and discovery systems
- CLI commands for plugin listing
- Core plugin implementations
- Tool integration layers

## Migration Notes
- **No action required** for existing users
- All existing plugins and functionality continue to work
- Plugin developers can migrate to the new structure at their convenience
- The backup directory provides reference for any custom integrations

## Development Impact
- **Cleaner codebase**: Reduced complexity and improved maintainability
- **Better organization**: Logical grouping of related functionality
- **Enhanced testing**: More focused and reliable plugin testing
- **Improved documentation**: Clearer structure for plugin development

## Version Information
- **Previous**: v3.2.0
- **Current**: v3.3.0
- **Type**: Minor version (backward-compatible architecture improvements)

## Contributors
This release represents significant refactoring work to improve the long-term maintainability and extensibility of the Janito platform.

---

For detailed migration guides and plugin development documentation, see the updated documentation in the repository.