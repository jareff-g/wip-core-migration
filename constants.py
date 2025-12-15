"""
****************************************************************************************************************
constants module
Centralized storage for all application-wide constants.

Using a dedicated module for constants prevents circular dependencies and
ensures that these immutable values are easily discoverable.

Licensed under a MIT LICENSE.

More info in README.md file
****************************************************************************************************************
"""
__author__ = 'Juan Remirez de Esparza'
__copyright__ = "Copyright 2022/24, Juan Remirez de Esparza"
__credits__ = ["Juan Remirez de Esparza"]
__license__ = "MIT"
__module__ = "ui_manager"
__version__ = "1.0.0"
__date__ = "2025-12-15"
__version_highlight__ = "UIManager - First version (stub for now)"
__maintainer__ = "Juan Remirez de Esparza"
__email__ = "jremirez@hotmail.com"
__status__ = "Development"


# --- Project State Constants ---
DEFAULT_PROJECT_ID = "P-000-NEW_SESSION"
MAX_FILE_SIZE_MB = 1024

# --- Mode Constants (Used for AppStateStore keys and logic) ---
MODE_INSPECTION = "Inspection"
MODE_ANALYSIS = "Analysis"
MODE_REPORTING = "Reporting"

# --- Event Bus Constants (Used for subscription/publishing keys) ---
EXIT_APP = "EXIT_APP"

# --- UI Defaults ---
DEFAULT_WINDOW_TITLE = "AfterScan v2.1"
DEFAULT_THEME_COLOR = "#0A2463"

# --- Queue tokens ---
END_TOKEN = "TERMINATE_PROCESS"
LAST_ITEM_TOKEN = "LAST_ITEM"

# --- Data Shared store ids ---
CONFIG_MANAGER = "config_manager"
EVENT_BUS = "event_bus"
FONT_SIZE = "font_size"
IGNORE_CONFIG = "ignore_config"
MAIN_WIN = "win"
APP_VERSION = "app_version"
