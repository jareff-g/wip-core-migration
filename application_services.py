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
from constants import (EXIT_APP, END_TOKEN, LAST_ITEM_TOKEN, CONFIG_MANAGER, EVENT_BUS, IGNORE_CONFIG, FONT_SIZE, MAIN_WIN)

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
            EVENT_BUS: None,
            FONT_SIZE: 11,
            MAIN_WIN: None,
            CONFIG_MANAGER: None,
            IGNORE_CONFIG: False,
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

