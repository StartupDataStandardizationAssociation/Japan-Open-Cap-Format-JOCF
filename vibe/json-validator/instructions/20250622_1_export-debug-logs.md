# base instruction
Log output is important. Please output logs at DEBUG level for debugging purposes. However, set the normal log level to INFO so that large amounts of logs are not constantly output.

## Implementation Details

### Added DEBUG Level Logging
- **schema_loader.py**: Added comprehensive DEBUG logging throughout the schema loading process
  - Schema file discovery and counting
  - Individual file loading progress
  - RefResolver construction details
  - Registration of file/object schemas
  - Error details when loading fails

- **config_manager.py**: Added DEBUG logging for configuration management
  - Project root detection process
  - Config file loading status
  - Path resolution details
  - Environment variable overrides
  - Validation results

### Logging Configuration
- **Default Level**: INFO (prevents excessive output in normal operation)
- **Debug Level**: DEBUG (provides detailed information for troubleshooting)
- **Logger Namespace**: `json_validator` (avoids conflicts with other validator libraries)
- **Safe Handler Management**: Only manages handlers for `json_validator` namespace, doesn't interfere with other loggers

### Logger Hierarchy
```
json_validator
├── json_validator.config_manager
└── json_validator.schema_loader
```

### Usage
```python
from validator import setup_logging

# For debugging
setup_logging("DEBUG")

# For normal operation (default)
setup_logging("INFO")
```

### Key Design Decisions
1. **Namespace Safety**: Used `json_validator` instead of generic `validator` to avoid conflicts
2. **Handler Isolation**: Only manipulates handlers for our specific logger namespace
3. **Propagation Control**: Prevents duplicate log messages
4. **Reconfiguration Support**: Allows changing log levels during runtime

### Testing Verification
- ✅ DEBUG level shows detailed schema loading process (4 file schemas, 22 object schemas)
- ✅ INFO level shows minimal output for normal operation
- ✅ External library loggers remain unaffected
- ✅ Multiple reconfigurations work correctly