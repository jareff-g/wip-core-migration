#!/usr/bin/env python
"""
AfterScan - Basic post-processing for scanned R8/S8 films

This utility is intended to handle the basic post-processing after film
scanning is completed.

Actions performed by this tool include:
- Stabilization
- Cropping
- Video generation

Licensed under a MIT LICENSE.

More info in README.md file
"""

__author__ = 'Juan Remirez de Esparza'
__copyright__ = "Copyright 2022-25, Juan Remirez de Esparza"
__credits__ = ["Juan Remirez de Esparza"]
__license__ = "MIT"
__module__ = "AfterScan"
__version__ = "1.40.29"
__data_version__ = "1.0"
__date__ = "2025-12-13"
__version_highlight__ = "WIP: Aftr integration in helpers, rename AppEncoder to CustomJsonEncoder."
__maintainer__ = "Juan Remirez de Esparza"
__email__ = "jremirez@hotmail.com"
__status__ = "Development"

import argparse
import sys
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import logging
import queue
import platform
import time
from datetime import datetime
import threading
import cv2
import subprocess as sp

# Due to how python works, logging code needs to be initialized here, so that AfterScan classes all use the same logger
# Global logger instance (used for the root logger)
GLOBAL_LOGGER = logging.getLogger()

def configure_logging():
    """
    Initializes the root logging system with custom handlers and format.
    
    This function sets up two handlers: one for the console (sys.stdout) 
    and one for a log file (AfterScan.log).
    """
    logs_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Logs")
    if not os.path.exists(logs_dir):
        os.mkdir(logs_dir)
    log_file_fullpath = logs_dir + "/AfterScan." + time.strftime("%Y%m%d") + ".log"

    # CRITICAL: We avoid logging.basicConfig() to allow manual control.
    
    # Define the common format
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # --- 1. Console Handler (Existing) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG) # Root level to be the only filter
    
    # --- 2. File Handler (New) ---
    # Create a handler to write logs to a file. We'll set it to capture all
    # logs at the DEBUG level initially, as file logs often need more detail.
    try:
        file_handler = logging.FileHandler(log_file_fullpath, mode='a')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG) # Root level to be the only filter
        
        # Add the File Handler
        if not any(isinstance(h, logging.FileHandler) for h in GLOBAL_LOGGER.handlers):
            print(f"Logs will be saved to {log_file_fullpath}")
            
    except Exception as e:
        # Log this error to the console (via the console_handler)
        print(f"Could not open log file '{log_file_fullpath}': {e}")
    
    # --- 3. Add Handlers to Root Logger ---
    # Add the console handler UNCONDITIONALLY as it's required for terminal output.
    GLOBAL_LOGGER.addHandler(console_handler)
    
    # Add the file handler only if creation succeeded.
    if file_handler:
        GLOBAL_LOGGER.addHandler(file_handler)
        print("Log file: %s", log_file_fullpath) # Use the newly added handler to log success
      
    # 4. Set the initial, safe level on the root logger.
    # This acts as the filter for ALL handlers attached to the root logger.
    GLOBAL_LOGGER.setLevel(logging.DEBUG) 

    print("Logging handler and format configured (initial level: INFO).")

def set_log_level_from_args(logging_level):
    if logging_level != GLOBAL_LOGGER.level:
        # Set the level on the root logger. This instantly affects all imported modules.
        # This new level determines what gets passed to the attached handlers.
        GLOBAL_LOGGER.setLevel(logging_level)
        logging.info(f"Root Log level dynamically set to: {logging_level}")
        print(f"Root Log level dynamically set to: {logging_level}")

    logging.info("AfterScann %s (%s)", __version__, __date__)
    logging.info("Log level: %s", logging_level)

# 1. CRITICAL: Call the configuration function in the global scope 
#    to configure the handler BEFORE any custom imports.
configure_logging()

from template_manager import TemplateManager
from configuration_manager import ConfigurationManager
from job_manager import JobManager
from tooltip import Tooltips
from define_rectangle import DefineRectangle
from helpers import RollingAverage, FPSTracker, CustomJsonEncoder, is_a_number, empty_queue
from application_services import AppStateStore, EventBus
from ui_manager import UIManager
from refresh_store_from_config import refresh_store_from_config

# Event bus constants
from constants import (EXIT_APP, START_CONVERT)
# Application constants
from constants import (END_TOKEN, LAST_ITEM_TOKEN, APP_VERSION, BATCH_JOB_LIST, JOB_LIST_NAME_LENGTH,
                       JOB_LIST_DESCRIPTION_LENGTH)
# Shared Store constants
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
                       FORCE_SMALL_SIZE, NUM_THREADS, BATCH_AUTOSTART, GENERATE_CSV, DISABLE_TOOLTIPS,
                       LOG_LEVEL, TEMPORAL_DENOISE_SUPPORTED, UI_MANAGER, SOURCE_DIR_FILE_LIST, TARGET_DIR_FILE_LIST)



try:
    import requests
    requests_loaded = True
except ImportError:
    requests_loaded = False


# --- 1. Core Application Logic (Testable and Reusable) ---

class AfterScanApp:
    """
    The main business logic class for post-processing scan results.
    This class is configured via its __init__ method and is kept clean
    of command-line arguments (sys.argv) for easy testing.
    """
    def __init__(self, cli_args, store: AppStateStore):
        """
        Initializes the application with validated parameters.
        """
        self.cli_args = cli_args

        """ Global variables as attribute classes."""
        # --- Shared state store ---
        self.store = store
        self.event_bus = self.store.get_state(EVENT_BUS)
        self.store.update_state(APP_VERSION, __version__)
        # --- Configuration ---
        self.config_manager = None
        # --- Add command line parameter options to shared store ---
        self.store.update_state(IGNORE_CONFIG, self.cli_args.ignore_config)
        self.store.update_state(IS_DEMO, self.cli_args.is_demo)
        self.store.update_state(USE_SIMPLE_STABILIZATION, self.cli_args.use_simple_stabilization)
        self.store.update_state(FORCE_SMALL_SIZE, self.cli_args.force_small_size)
        self.store.update_state(NUM_THREADS, self.cli_args.num_threads)
        self.store.update_state(BATCH_AUTOSTART, self.cli_args.batch_autostart)
        self.store.update_state(GENERATE_CSV, self.cli_args.generate_csv)
        self.store.update_state(DISABLE_TOOLTIPS, self.cli_args.disable_tooltips)
        self.store.update_state(LOG_LEVEL, self.cli_args.log_level)

        # --- Templates ---
        self.template_manager = None
        # --- Batch job list ---
        self.batch_job_list = None
        # --- Tooltip management ---
        self.as_tooltips = None
        # --- User interface ---
        self.win = None
        self.script_dir = ''
        self.resources_dir = ''
        self.top_win_x = 0
        self.top_win_y = 0
        # --- Graphics processing libraries ---
        self.merge_mertens = None
        self.align_mtb = None
        # --- Multithreading vars ---
        self.frame_encoding_queue = None
        self.subprocess_event_queue = None
        # --- Video generation ---
        self.ffmpeg_bin_name = None
        self.alt_ffmpeg_bin_name = None
        self.ffmpeg_installed = False
        self.ffmpeg_process = None
        # --- System support ---
        self.is_windows = False
        self.is_linux = False
        self.is_mac = False

        # Subscribe to actions originating from the UI
        self.event_bus.subscribe(EXIT_APP, self._exit_app)
        self.event_bus.subscribe(START_CONVERT, self._start_convert)

    def initialize_basics(self):
        self.win = tk.Tk()  # Create main window, store it in 'win'
        self.store.update_state(MAIN_WIN, self.win)

        # Get screen size - maxsize gives the usable screen size
        _, screen_height = self.win.maxsize()
        # Set dimensions of UI elements adapted to screen size
        if (screen_height >= 1000 and not self.cli_args.force_small_size):
            big_size = True
            font_size = 11
            preview_width = 700
            preview_height = 525
        else:
            big_size = False
            font_size = 8
            preview_width = 500
            preview_height = 375

        self.store.update_state(FONT_SIZE, font_size)    # Update shared store
        self.store.update_state(PREVIEW_WIDTH, preview_width)    # Update shared store
        self.store.update_state(PREVIEW_HEIGHT, preview_height)    # Update shared store
        self.store.update_state(BIG_SIZE, big_size)    # Update shared store

        """ delete_this
        self.display_window_title()  # setting title of the window
        """
        
        if self.config_manager.get_window_pos() != '':
            self.win.geometry(f"+{self.config_manager.get_window_pos().split('+', 1)[1]}")

        self.win.update_idletasks()

        # Set default font size
        # Change the default Font that will affect in all the widgets
        self.win.option_add("*font", "TkDefaultFont 10")

        # Init ToolTips
        self.as_tooltips = Tooltips(font_size)
        self.store.update_state(TOOLTIPS, self.as_tooltips)

        # TODO: Move to processing class
        # Init rolling Averages
        self.match_level_average = RollingAverage(50)
        self.horizontal_offset_average = RollingAverage(50)
        self.move_x_average = RollingAverage(50)
        self.move_y_average = RollingAverage(50)

        # Get Top window coordinates
        self.top_win_x = self.win.winfo_x()
        self.top_win_y = self.win.winfo_y()

        # Create merge_mertens Object for HDR
        self.merge_mertens = cv2.createMergeMertens()
        # Create Align MTB object for HDR
        self.align_mtb = cv2.createAlignMTB()

        # Check for temporalDenoise supported by OpenCV 
        temporal_denoise_supported = hasattr(cv2, 'temporalDenoising')
        if not temporal_denoise_supported:
            logging.info(f"Temporal denoise not available. OpenCV version is {cv2.__version__}")
        self.store.update_state(TEMPORAL_DENOISE_SUPPORTED, temporal_denoise_supported)

        logging.debug("AfterScan initialized")

    def get_consent(self, force = False):
        # Check reporting consent
        if requests_loaded:
            if force or  (self.config_manager.get_user_consent() == 'no' and (datetime.today()-self_config_manager.get_last_consent_date()).days >= 60):
                consent = tk.messagebox.askyesno(
                    "AfterScan User Count",
                    "Help us count AfterScan users anonymously? Reports versions to track usage. No personal data is collected, just an anonymous hash plus AfterScan versions."
                )
                last_consent_date = datetime.today()
                self.config_manager.set_last_consent_date(last_consent_date.isoformat())
                self.config_manager.set_user_consent("yes" if consent else "no")

    def multiprocessing_init(self):

        num_cores = os.cpu_count()

        if self.store.get_state(NUM_THREADS) == 0:
            if num_cores is not None:
                logging.debug(f"{num_cores} cores available")
                self.store.update_state(NUM_THREADS, int(num_cores/2))
            else:
                logging.debug("Unable to determine number of cores available")
                self.store.update_state(NUM_THREADS, 4)

        logging.debug(f"Creating {self.store.get_state(NUM_THREADS)} threads")

        self.frame_encoding_queue = queue.Queue(maxsize=20)
        self.subprocess_event_queue = queue.Queue(maxsize=20)

    def is_ffmpeg_installed(self):

        cmd_ffmpeg = [self.ffmpeg_bin_name, '-h']

        try:
            self.ffmpeg_process = sp.Popen(cmd_ffmpeg, stderr=sp.PIPE, stdout=sp.PIPE)
        except FileNotFoundError:
            self.ffmpeg_process = None
            logging.error("ffmpeg is NOT installed.")

        return self.ffmpeg_process != None

    def initialize_ffmpeg(self):
        if platform.system() == 'Windows':
            self.is_windows = True
            if self.ffmpeg_bin_name is None or self.ffmpeg_bin_name == "":
                self.ffmpeg_bin_name = 'C:\\ffmpeg\\bin\\ffmpeg.exe'
            self.alt_ffmpeg_bin_name = 'ffmpeg.exe'
            logging.debug("Detected Windows OS")
        elif platform.system() == 'Linux':
            self.is_linux = True
            if self.ffmpeg_bin_name is None or self.ffmpeg_bin_name == "":
                self.ffmpeg_bin_name = 'ffmpeg'
            self.alt_ffmpeg_bin_name = 'ffmpeg'
            logging.debug("Detected Linux OS")
        elif platform.system() == 'Darwin':
            self.is_mac = True
            if self.ffmpeg_bin_name is None or self.ffmpeg_bin_name == "":
                self.ffmpeg_bin_name = 'ffmpeg'
            self.alt_ffmpeg_bin_name = 'ffmpeg'
            logging.debug("Detected Darwin (MacOS) OS")
        else:
            if self.ffmpeg_bin_name is None or self.ffmpeg_bin_name == "":
                self.ffmpeg_bin_name = 'ffmpeg'
            self.alt_ffmpeg_bin_name = 'ffmpeg'
            logging.debug("Unknown OS detected: " + platform.system())

        if self.is_ffmpeg_installed():
            self.ffmpeg_installed = True
        else:
            self.ffmpeg_installed = False
            if platform.system() == 'Windows':  # Give windows a second try with alternate bname
                self.ffmpeg_bin_name = self.alt_ffmpeg_bin_name
                if self.is_ffmpeg_installed():
                    self.ffmpeg_installed = True
        self.store.update_state(FFMPEG_INSTALLED, self.ffmpeg_installed)
        if not self.ffmpeg_installed:
            tk.messagebox.showerror(
                "Error: ffmpeg is not installed",
                f"FFmpeg is not installed in this computer at the designated path '{ffmpeg_bin_name}'.\r\n"
                "It is not mandatory for the application to run; "
                "Frame stabilization and cropping will still work, "
                "video generation will not")

    def _exit_app(self):  # Exit Application
        # Terminate threads
        # frame_encoding_event.set()
        for i in range(0, self.store.get_state(NUM_THREADS)):
            self.frame_encoding_queue.put((END_TOKEN, 0))
            logging.debug("Inserting end token to encoding queue")

        # TODO: Check using the build-in function works fine. Before we were countign internally via active_threads var
        num_active = threading.active_count()
        while num_active > 0:
            self.win.update()
            logging.debug(f"Waiting for threads to exit, {num_active} pending")
            time.sleep(0.2)
            num_active = threading.active_count()
        logging.debug(f"All threads completed, exiting.")

        self.win.destroy()

    # TODO: Complete start_convert adapted to new code
    def _start_convert(self):
        # Load frequently used items from shared store
        source_dir_file_list = self.store.get_state(SOURCE_DIR_FILE_LIST)

        if convert_loop_running:
            convert_loop_exit_requested = True
            convert_loop_running = False
        else:
            if len(source_dir_file_list) == 0:
                tk.messagebox.showwarning(
                    "No source frames",
                    "No source frames loaded.\r\n"
                    "Please load source frames and try again.")
                return
            if not skip_frame_regeneration.get() and not delete_detected_bad_frames():
                return
            # Enforce minimum value for Gamma in case user clicks starts rigth after having manually entered a zero in GC box
            gamma_enforce_min_value()
            # Save current project status
            self.config_manager.save_configuration()
            self.batch_job_list.save_to_file(job_list_filename)
            # Empty FPS register list
            fps_tracker.reset()
            # Centralize 'frames_to_encode' update here
            if encode_all_frames.get():
                start_frame = 0
                #frames_to_encode = len(source_dir_file_list)
                frames_to_encode = get_frame_number_from_filename(source_dir_file_list[-1]) - get_frame_number_from_filename(source_dir_file_list[0]) + 1
            else:
                start_frame = int(frame_from_str.get())
                frames_to_encode = int(frame_to_str.get()) - int(frame_from_str.get()) + 1
                if start_frame + frames_to_encode > len(source_dir_file_list):
                    frames_to_encode = len(source_dir_file_list) - start_frame
            self.store.update_state(CURRENT_FRAME, start_frame)
            if frames_to_encode <= 1:
                tk.messagebox.showwarning(
                    "No frames match range",
                    "No frames to encode.\r\n"
                    "The range specified (current frame - number of frames to "
                    "encode) does not match any frame.\r\n"
                    "Please review your settings and try again.")
                return
            if not is_valid_template_size():
                tk.messagebox.showwarning(
                    "Invalid template",
                    "Template associated with this jos is bigger the search area.\r\n"
                    "Please redefine template and try again.")
                return
            if batch_job_running:
                start_batch_btn.config(text="Stop batch", bg='red', fg='white')
                # Disable all buttons in main window
                widget_status_update(DISABLED, start_batch_btn)
            else:
                Go_btn.config(text="Stop", bg='red', fg='white')
                # Disable all buttons in main window
                widget_status_update(DISABLED, Go_btn)
            FrameSync_Viewer_popup_update_widgets(DISABLED)
            self.win.update()

            self.config_manager.set_film_type(film_type.get())
            if self.config_manager.get_generate_video():
                target_video_filename = video_filename_str.get()
                name, ext = os.path.splitext(target_video_filename)
                if target_video_filename == "":   # Assign default if no filename
                    target_video_filename = (
                        "AfterScan-" +
                        datetime.now().strftime("%Y_%m_%d-%H-%M-%S") + ".mp4")
                    video_filename_str.set(target_video_filename)
                elif ext not in ['.mp4', '.MP4', '.mkv', '.MKV']:     # ext == "" does not work if filename contains dots ('Av. Manzanares')
                    target_video_filename += ".mp4"
                    video_filename_str.set(target_video_filename)
                elif os.path.isfile(os.path.join(video_target_dir_str.get(), target_video_filename)):
                    if not batch_job_running:
                        error_msg = (target_video_filename + " already exist in target "
                                    "folder. Overwrite?")
                        if not tk.messagebox.askyesno("Error!", error_msg):
                            generation_exit()
                            return

            convert_loop_running = True

            if not generate_video.get() or not skip_frame_regeneration.get():
                # Check if CSV option selected
                if self.store.get_state(GENERATE_CSV):
                    csv_filename = video_filename_str.get()
                    name, ext = os.path.splitext(csv_filename)
                    if name == "":  # Assign default if no filename
                        name = "AfterScan-"
                    csv_filename = datetime.now().strftime("%Y_%m_%d-%H-%M-%S_") + name + '.csv'
                    csv_path_name = resources_dir
                    if csv_path_name == "":
                        csv_path_name = os.getcwd()
                    csv_path_name = os.path.join(csv_path_name, csv_filename)
                    # Write header
                    with open(csv_path_name, 'w') as csv_file:
                        csv_file.write("Frame, Missing rows, Threshold, Num loops, Match level, move_x, move_y\n")
                match_level_average.clear()
                horizontal_offset_average.clear()
                move_x_average.clear()
                move_y_average.clear()
                # Disable manual stabilize popup widgets
                FrameSync_Viewer_popup_update_widgets(DISABLED)
                # Multiprocessing: Start all threads before encoding
                start_threads()
                self.win.after(1, frame_generation_loop)
            elif generate_video.get():
                # first check if resolution has been set
                if resolution_dict[self.config_manager.get_video_resolution()] == '':
                    if not batch_job_running:
                        logging.error("Error, no video resolution selected")
                        tk.messagebox.showerror("Error!", "Please specify video resolution.")
                    else:
                        logging.error(f"Cannot generate video {target_video_filename}, no video resolution selected")
                    generation_exit(success = False)
                else:
                    ffmpeg_success = False
                    ffmpeg_encoding_status = ffmpeg_state.Pending
                    self.win.after(1000, video_generation_loop)


    def run(self):
        print(self.config_manager)

        """Set CWD to folder when scrit is running."""
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        os.chdir(self.script_dir) 
        self.store.update_state(SCRIPT_DIR, self.script_dir)

        self.resources_dir = os.path.join(self.script_dir, "Resources")
        self.store.update_state(RESOURCES_DIR, self.resources_dir)

        if self.store.get_state(LOG_LEVEL) != None:
            effective_log_level = self.store.get_state(LOG_LEVEL)    # Command line value
        else:
            effective_log_level = "ERROR"   # Default to Error

        log_level = getattr(logging, effective_log_level.upper(), None)
        if not isinstance(log_level, int):
            raise ValueError('Invalid log level: %s' % log_level)
        else:
            set_log_level_from_args(log_level)

        """Create and initialize TemplateManager: Add default templates to template list."""
        self.template_manager = TemplateManager.initialize(self.script_dir)
        self.store.update_state(TEMPLATE_MANAGER, self.template_manager)
        print(f"Templates initialized")
        """Create and initialize ConfigurationManager."""
        self.config_manager = ConfigurationManager.initialize(self.script_dir)
        print(f"Configuration initialized")
        self.store.update_state(CONFIG_MANAGER, self.config_manager)
        print(f"Shared store initialized")
        if self.config_manager.load_configuration():
            self.config_manager.set_active_project(self.config_manager.get_source_dir())
        else:   # No configuration exist, assign hardcoded values to some critical attributes
            self.config_manager.set_source_dir(self.script_dir)
            #config_manager = ConfigurationManager.initialize(script_dir)
            aux_project = self.config_manager.get_project_config("no project")
            self.config_manager.save_project_config(self.script_dir, aux_project)
            self.config_manager.set_active_project(self.script_dir)
        print(f"Configuration loaded")

        self.batch_job_list = JobManager.initialize(self.script_dir)
        print(f"Job list initialized")
        self.store.update_state(BATCH_JOB_LIST, self.batch_job_list)

        self.initialize_basics()
        print(f"Basic stuff initialized")

        if self.store.get_state(DISABLE_TOOLTIPS):
            self.as_tooltips.disable()

        print(f"Tooltips disabled")

        # Check reporting consent on first run
        self.get_consent()

        # Initialize multiprocessign queues
        self.multiprocessing_init()

        # Try to detect if ffmpeg is installed
        self.initialize_ffmpeg()
        print(f"ffmpeg initialized")

        # Create main UI
        ui_manager = UIManager(None, None, self.store)
        shared_store.update_state(UI_MANAGER, ui_manager)

        self.win.config(cursor="watch")  # Set cursor to hourglass
        widget_status_update()

        load_project_config()
        refresh_store_from_config(self.store, self.config_manager)

        if not self.store.get_state(IGNORE_CONFIG):
            batch_job_list.load_from_file(None)
            refresh_job_tree()

        get_target_dir_file_list()

        adjust_last_column()

        # If Templates folder do not exist (introduced with AfterScan 1.12), copy over files from temp folder
        if copy_templates_from_temp:
            copy_jpg_files(temp_dir, resources_dir)

        self.store.update_state(UI_INIT_DONE, True)

        # Disable a few items that should be not operational without source folder
        if len(self.config_manager.get_source_dir()) == 0:
            Go_btn.config(state=DISABLED)
            cropping_btn.config(state=DISABLED)
            frame_slider.config(state=DISABLED)
        else:
            Go_btn.config(state=NORMAL)
            cropping_btn.config(state=NORMAL)
            frame_slider.config(state=NORMAL)

        init_display()

        self.win.resizable(False, False) # Lock window size once all widgets have been added (make sure all fits)

        report_usage()

        # If batch_autostart, enable suspend on completion and start batch
        if self.store.get_state(BATCH_AUTOSTART):
            suspend_on_joblist_end.set(True)
            self.win.after(2000, start_processing_job_list) # Wait 2 sec. to allow main loop to start

        self.win.config(cursor="")  # Set cursor to hourglass

        # Main Loop
        self.win.mainloop()  # running the loop that works as a trigger


# --- 2. Command Line Interface (CLI) / Entry Point Logic ---

def parse_args():
    """Handles all command-line parsing using argparse."""
    parser = argparse.ArgumentParser(
        description='A utility for automated post-processing of 8mm/S8 film scan results.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Optional arguments
    parser.add_argument(
        '-l', '--log_level',
        type=str,
        action='store',
        dest='log_level',
        default=None,
        help='Sets log level to one of [DEBUG|INFO|WARNING|ERROR].'
    )
    
    parser.add_argument(
        '-i', '--ignore_config',
        action='store_true',
        dest='ignore_config',
        default=False,
        help='Enable verbose output, showing details about execution steps.'
    )
    
    parser.add_argument(
        '-n', '--no_tooltips',
        action='store_true',
        dest='disable_tooltips',
        default=False,
        help='Disable tooltips.'
    )
    
    parser.add_argument(
        '-e', '--expert_mode_disabled',
        action='store_true',
        dest='expert_mode',
        default=False,
        help='Disable expert mode.'
    )
    
    parser.add_argument(
        '-c', '--generate_csv',
        action='store_true',
        dest='generate_csv',
        default=False,
        help='Generate CSV file with misaligned frames.'
    )
    
    parser.add_argument(
        '-s', '--start_batch',
        action='store_true',
        dest='batch_autostart',
        default=False,
        help='Initiate batch on startup (and suspend on batch completion).'
    )
    
    parser.add_argument(
        '-t', '--num_threads',
        type=int,
        action='store',
        dest='num_threads',
        default=0,  # 0 means number of threads based on number of cores (if it can be detected, otherwise 4)
        help='Number of threads to use for processing.'
    )
    
    parser.add_argument(
        '-1', '--small_screen',
        action='store_true',
        dest='force_small_size',
        default=False,
        help='Initiate on small screen mode (resolution lower than than Full HD).'
    )
    
    parser.add_argument(
        '-a', '--simple_stabilization',
        action='store_true',
        dest='use_simple_stabilization',
        default=False,
        help='Use simple stabilization algorithm, not requiring templates (but slightly less precise).'
    )
    
    parser.add_argument(
        '-b', '--dev_debug',
        action='store_true',
        dest='dev_debug_enabled',
        default=False,
        help='Enable developer debug mode.'
    )
    
    parser.add_argument(
        '-d', '--demo',
        action='store_true',
        dest='is_demo',
        default=False,
        help='Enable demo mode (to record demo video).'
    )
    
    return parser.parse_args()


# --- 3. Execution Block ---

if __name__ == "__main__":
    try:
        # Step 1: Parse the arguments from the command line
        args = parse_args()

        # Step 2: Create the single instance of the State Store (the shared object)
        shared_store = AppStateStore()

        # Step 3: Create the event bus to communicat eevents among modules
        event_bus = EventBus()
        shared_store.update_state(EVENT_BUS, event_bus)

        # Step 4: Instantiate the application with the parsed arguments
        app = AfterScanApp(args, shared_store)
        
        # Step 5: Run the application's core logic
        app.run()
        print("Finalized successfully.")
        
    except SystemExit:
        # argparse raises SystemExit on --help or error, let it pass through
        pass
    except Exception as e:
        sys.stderr.write(f"A critical error occurred: {e}\n")
        sys.exit(1)