"""
****************************************************************************************************************
Class AppStateStore
Handles AfterScan centralized app store. Contains information required by several components.

Licensed under a MIT LICENSE.

More info in README.md file
****************************************************************************************************************
"""
__author__ = 'Juan Remirez de Esparza'
__copyright__ = "Copyright 2022/24, Juan Remirez de Esparza"
__credits__ = ["Juan Remirez de Esparza"]
__license__ = "MIT"
__module__ = "app_state_store"
__version__ = "1.0.0"
__date__ = "2025-12-15"
__version_highlight__ = "AppStateStore - First version"
__maintainer__ = "Juan Remirez de Esparza"
__email__ = "jremirez@hotmail.com"
__status__ = "Development"

import logging
from typing import Dict, List, Callable, Any
# Event bus constants
from constants import (EXIT_APP, START_CONVERT)
# Application constants
from constants import (END_TOKEN, LAST_ITEM_TOKEN, APP_VERSION, BATCH_JOB_LIST, JOB_LIST_NAME_LENGTH,
                       JOB_LIST_DESCRIPTION_LENGTH)
# Shared Store constants
from constants import (CONFIG_MANAGER, TEMPLATE_MANAGER, EVENT_BUS, IGNORE_CONFIG, CONFIG_FROM_FILE, FONT_SIZE,
                       MAIN_WIN, PREVIEW_WIDTH, PREVIEW_HEIGHT, TOOLTIPS, BIG_SIZE, SCRIPT_DIR, RESOURCES_DIR,
                       UI_INIT_DONE, PROJECT_NAME, SAVE_BG, SAVE_FG, CURRENT_FRAME, SOURCE_DIR, 
                       PROJECT_NAME, TARGET_DIR, VIDEO_TARGET_DIR, BATCH_JOB_RUNNING, 
                       ENCODE_ALL_FRAMES, FRAME_FROM, FRAME_TO, FRAMES_TO_ENCODE, FILM_TYPE, 
                       ROTATION_ANGLE, STABILIZATION_THRESHOLD, LOW_CONTRAST_CUSTOM_TEMPLATE, 
                       EXTENDED_STABILIZATION, CUSTOM_TEMPLATE_DEFINED, CUSTOM_TEMPLATE_NAME, 
                       CUSTOM_TEMPLATE_EXPECTED_POS, CUSTOM_TEMPLATE_FILENAME, PERFORM_CROPPING, 
                       PERFORM_DENOISE, PERFORM_SHARPNESS, PERFORM_GAMMA_CORRECTION, GAMMA_CORRECTION_VALUE, 
                       GENERATE_VIDEO, VIDEO_FILENAME, VIDEO_TITLE, SKIP_FRAME_REGENERATION, FFMPEG_PRESET, 
                       FORCE_4_3, FORCE_16_9, FRAME_FILL_TYPE, CROP_RECTANGLE, PERFORM_STABILIZATION, 
                       STABILIZATION_SHIFT_X, STABILIZATION_SHIFT_Y, PERFORM_ROTATION, VIDEO_FPS, 
                       VIDEO_RESOLUTION, CURRENT_BAD_FRAME_INDEX, USER_DEFINED_LEFT_STRIPE_WIDTH_PROPORTION, 
                       PRECISE_TEMPLATE_MATCH, FFMPEG_INSTALLED, IS_DEMO, USE_SIMPLE_STABILIZATION, 
                       FORCE_SMALL_SIZE, BATCH_AUTOSTART, GENERATE_CSV, DISABLE_TOOLTIPS, LOG_LEVEL, 
                       NUM_THREADS, TEMPORAL_DENOISE_SUPPORTED, UI_MANAGER, CONVERT_LOOP_RUNNING, 
                       CONVERT_LOOP_EXIT_REQUESTED, FIRST_ABSOLUTE_FRAME, FRAME_SCALE_REFRESH_DONE, 
                       FRAME_SCALE_REFRESH_PENDING, RECTANGLE_ACTION_ONGOING, RECTANGLE_REFRESH_REQUIRED,
                       RECTANGLE_BASE_IMAGE, RECTANGLE_ORIGINAL_IMAGE, RECTANGLE_LINE_THICKNESS,
                       CROP_AREA_DEFINED, SOURCE_DIR_FILE_LIST, TARGET_DIR_FILE_LIST, FILE_TYPE_OUT,
                       FRAME_WIDTH, FRAME_HEIGHT)


# --- 1. The Centralized State Store (Data Access) ---

class AppStateStore:
    """
    A single source of truth for all global application state.
    
    This object is designed to be passed around safely. The UI can read from it,
    and the main Application logic can write to it.
    
    NOTE: For more advanced scenarios, you would add an Observer pattern here
    to notify widgets immediately when a value changes (the combination of 
    PubSub and Store is the Redux/Flux pattern).
    """
    def __init__(self):
        # Initializing the global variables the UI needs access to
        self.state = {
            CONFIG_MANAGER: None,
            TEMPLATE_MANAGER: None,
            TOOLTIPS: None,
            EVENT_BUS: None,
            FONT_SIZE: 11,
            IGNORE_CONFIG: False,
            CONFIG_FROM_FILE: True,
            MAIN_WIN: None,
            APP_VERSION: "",
            BATCH_JOB_LIST: None,
            PREVIEW_WIDTH: 0,
            PREVIEW_HEIGHT: 0,
            BIG_SIZE: True,
            SCRIPT_DIR: "",
            RESOURCES_DIR: "",
            UI_INIT_DONE: False,
            SAVE_BG: "",
            SAVE_FG: "",
            CURRENT_FRAME: 0,
            SOURCE_DIR: "",
            PROJECT_NAME: "No project",
            TARGET_DIR: "",
            VIDEO_TARGET_DIR: "",
            BATCH_JOB_RUNNING: False,
            ENCODE_ALL_FRAMES: True,
            FRAME_FROM: 0,
            FRAME_TO: 0,
            FRAMES_TO_ENCODE: 0,
            FILM_TYPE: "S8",
            ROTATION_ANGLE: 0,
            STABILIZATION_THRESHOLD: 220,
            LOW_CONTRAST_CUSTOM_TEMPLATE: False,
            EXTENDED_STABILIZATION: False,
            CUSTOM_TEMPLATE_DEFINED: False,
            CUSTOM_TEMPLATE_NAME: "",
            CUSTOM_TEMPLATE_EXPECTED_POS: [0,0],
            CUSTOM_TEMPLATE_FILENAME: "",
            PERFORM_CROPPING: False,
            PERFORM_DENOISE: False,
            PERFORM_SHARPNESS: False,
            PERFORM_GAMMA_CORRECTION: False,
            GAMMA_CORRECTION_VALUE: 2.2,
            GENERATE_VIDEO: False,
            VIDEO_FILENAME: "",
            VIDEO_TITLE: "",
            SKIP_FRAME_REGENERATION: False,
            FFMPEG_PRESET: "veryfast",
            FORCE_4_3: False,
            FORCE_16_9: False,
            FRAME_FILL_TYPE: "none",
            CROP_RECTANGLE: [[0,0],[0,0]],
            PERFORM_STABILIZATION: False,
            STABILIZATION_SHIFT_X: 0,
            STABILIZATION_SHIFT_Y: 0,
            PERFORM_ROTATION: False,
            VIDEO_FPS: 18,
            VIDEO_RESOLUTION: "2048x1536 (QXGA)",
            CURRENT_BAD_FRAME_INDEX: 0,
            USER_DEFINED_LEFT_STRIPE_WIDTH_PROPORTION: 0.20,
            PRECISE_TEMPLATE_MATCH: False,
            FFMPEG_INSTALLED: False,
            IS_DEMO: False,
            USE_SIMPLE_STABILIZATION: False,
            FORCE_SMALL_SIZE: False,
            BATCH_AUTOSTART: False,
            GENERATE_CSV: False,
            DISABLE_TOOLTIPS: False,
            LOG_LEVEL: None, 
            NUM_THREADS: 4,
            TEMPORAL_DENOISE_SUPPORTED: False,
            UI_MANAGER: None,
            CONVERT_LOOP_RUNNING: False,
            CONVERT_LOOP_EXIT_REQUESTED: False,
            FIRST_ABSOLUTE_FRAME: 0,
            FRAME_SCALE_REFRESH_DONE: True,
            FRAME_SCALE_REFRESH_PENDING: False,
            RECTANGLE_ACTION_ONGOING: "",
            RECTANGLE_REFRESH_REQUIRED: False,
            RECTANGLE_BASE_IMAGE: None, 
            RECTANGLE_ORIGINAL_IMAGE: None,
            RECTANGLE_LINE_THICKNESS: 1,
            CROP_AREA_DEFINED: False,
            SOURCE_DIR_FILE_LIST: [],
            TARGET_DIR_FILE_LIST: [],
            FILE_TYPE_OUT: "",
            FRAME_WIDTH: 2028,
            FRAME_HEIGHT: 1520
        }

    def get_state(self, key: str):
        """Allows read access to a specific piece of state."""
        return self.state.get(key)

    def update_state(self, key: str, value):
        """Allows write access (typically restricted to main Application logic)."""
        if key in self.state:
            self.state[key] = value
            logging.info(f"Store: State '{key}' updated to '{value}'")
        else:
            logging.error(f"Store Error: Attempted to set unknown key '{key}'")

# --- 2. The Event Bus / PubSub (Action Communication) ---

class EventBus:
    """
    A simple Publish-Subscribe system for decoupled communication.
    Widgets/Components publish actions, and the App/other components subscribe
    to handle them.
    """
    def __init__(self):
        # Dictionary mapping event names (strings) to a list of handler functions
        self.handlers: Dict[str, List[Callable[..., Any]]] = {}

    def subscribe(self, event_name: str, handler: Callable[..., Any]):
        """Register a function to be called when an event occurs."""
        if event_name not in self.handlers:
            self.handlers[event_name] = []
        self.handlers[event_name].append(handler)
        print(f"Bus: Subscribed handler to '{event_name}'")

    def publish(self, event_name: str, **kwargs):
        """Trigger an event, calling all registered handlers."""
        print(f"\nBus: Publishing event '{event_name}' with data: {kwargs}")
        if event_name in self.handlers:
            for handler in self.handlers[event_name]:
                try:
                    handler(**kwargs)
                except Exception as e:
                    print(f"Bus Error: Handler for '{event_name}' failed: {e}")
        else:
            print(f"Bus: No handlers registered for '{event_name}'")

