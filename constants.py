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
TBD_DEFAULT_PROJECT_ID = "P-000-NEW_SESSION"
TBD_MAX_FILE_SIZE_MB = 1024

# --- Mode Constants (Used for AppStateStore keys and logic) ---
TBD_MODE_INSPECTION = "Inspection"
TBD_MODE_ANALYSIS = "Analysis"
TBD_MODE_REPORTING = "Reporting"

# --- Event Bus Constants (Used for subscription/publishing keys) ---
EXIT_APP = "exit_app"
START_CONVERT = "start_convert"

# --- UI Defaults, limits & other values ---
JOB_LIST_NAME_LENGTH = 100
JOB_LIST_DESCRIPTION_LENGTH = 100

# --- Queue tokens ---
END_TOKEN = "TERMINATE_PROCESS"
LAST_ITEM_TOKEN = "LAST_ITEM"

# --- Data Shared store ids ---
CONFIG_MANAGER = "config_manager"
TOOLTIPS = "tooltips"
EVENT_BUS = "event_bus"
FONT_SIZE = "font_size"
IGNORE_CONFIG = "ignore_config"
CONFIG_FROM_FILE = "config_from_file"
MAIN_WIN = "win"
APP_VERSION = "app_version"
BATCH_JOB_LIST = "batch_job_list"
PREVIEW_WIDTH = "preview_width"
PREVIEW_HEIGTH = "preview_height"
BIG_SIZE = "big_size"
SCRIPT_DIR = "script_dir"
UI_INIT_DONE = "ui_init_done"
PROJECT_NAME = "project_name"
SAVE_BG = "save_bg"
SAVE_FG = "save_fg"
CURRENT_FRAME = "current_frame"
SOURCE_DIR = "source_dir"
PROJECT_NAME = "project_name"
TARGET_DIR = "target_dir"
VIDEO_TARGET_DIR = "video_target_dir"
BATCH_JOB_RUNNING = "batch_job_running"
CURRENT_FRAME = "current_frame"
ENCODE_ALL_FRAMES = "encode_all_frames"
FRAME_FROM = "frame_from"
FRAME_TO = "frame_to"
FRAMES_TO_ENCODE = "frames_to_encode"
FILM_TYPE = "film_type"
ROTATION_ANGLE = "rotation_angle"
STABILIZATION_THRESHOLD = "stabilization_threshold"
LOW_CONTRAST_CUSTOM_TEMPLATE = "low_contrast_custom_template"
EXTENDED_STABILIZATION = "extended_stabilization"
CUSTOM_TEMPLATE_DEFINED = "custom_template_defined"
CUSTOM_TEMPLATE_NAME = "custom_template_name"
CUSTOM_TEMPLATE_EXPECTED_POS = "custom_template_expected_pos"
CUSTOM_TEMPLATE_FILENAME = "custom_template_filename"
PERFORM_CROPPING = "perform_cropping"
PERFORM_DENOISE = "perform_denoise"
PERFORM_SHARPNESS = "perform_sharpness"
PERFORM_GAMMA_CORRECTION = "perform_gamma_correction"
GAMMA_CORRECTION_VALUE = "gamma_correction_value"
GENERATE_VIDEO = "generate_video"
VIDEO_FILENAME = "video_filename"
VIDEO_TITLE = "video_title"
SKIP_FRAME_REGENERATION = "skip_frame_regeneration"
FFMPEG_PRESET = "ffmpeg_preset"
FORCE_4_3 = "force_4_3"
FORCE_16_9 = "force_16_9"
FRAME_FILL_TYPE = "frame_fill_type"
CROP_RECTANGLE = "crop_rectangle"
PERFORM_STABILIZATION = "perform_stabilization"
STABILIZATION_SHIFT_X = "stabilization_shift_x"
STABILIZATION_SHIFT_Y = "stabilization_shift_y"
PERFORM_ROTATION = "perform_rotation"
VIDEO_FPS = "video_fps"
VIDEO_RESOLUTION = "video_resolution"
CURRENT_BAD_FRAME_INDEX = "current_bad_frame_index"
USER_DEFINED_LEFT_STRIPE_WIDTH_PROPORTION = "user_defined_left_stripe_width_proportion"
PRECISE_TEMPLATE_MATCH = "precise_template_match"

