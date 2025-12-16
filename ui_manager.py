"""
****************************************************************************************************************
Class UIManager
Handles AfterScan user interface

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


import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import tkinter.messagebox
from tkinter import DISABLED, NORMAL, LEFT, RIGHT, TOP, BOTTOM, N, W, E, NW, NS, EW, RAISED, SUNKEN, END, VERTICAL, HORIZONTAL
from tkinter import Toplevel, Label, Button, Frame, LabelFrame, Canvas, Text, Scrollbar, Scale, Entry, Radiobutton, Listbox
from tkinter import Tk, IntVar, StringVar, OptionMenu

from PIL import ImageTk, Image, ImageDraw, ImageFont
from queue import Queue
import logging
import webbrowser
import os
from dataclasses import asdict


from helpers import (RollingAverage, FPSTracker, CustomJsonEncoder, is_a_number, 
                     empty_queue, generate_dict_hash, normalize_job_name, on_paste_all_entries)
from configuration_manager import ConfigurationManager
from application_services import AppStateStore, EventBus
# Event bus constants
from constants import (EXIT_APP, START_CONVERT)
# Application constants
from constants import (END_TOKEN, LAST_ITEM_TOKEN, APP_VERSION, BATCH_JOB_LIST, JOB_LIST_NAME_LENGTH,
                       JOB_LIST_DESCRIPTION_LENGTH)
# Shared Store constants
from constants import (CONFIG_MANAGER, EVENT_BUS, IGNORE_CONFIG, CONFIG_FROM_FILE, FONT_SIZE,
                       MAIN_WIN, PREVIEW_WIDTH, PREVIEW_HEIGTH, TOOLTIPS, BIG_SIZE, SCRIPT_DIR, 
                       UI_INIT_DONE, PROJECT_NAME, SAVE_BG, SAVE_FG, CURRENT_FRAME)



class UIManager:
    """
    Manages the user interface and serves as the bridge between user actions
    and the communication queues.
    """
    def __init__(self, input_queue: Queue, output_queue: Queue, store: AppStateStore):
        # The UI is dependent on both queues
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.store = store
        self.bus = store.get_state(EVENT_BUS)
        self.win = self.store.get_state(MAIN_WIN)
        self.font_size = self.store.get_state(FONT_SIZE)
        self.config_manager = self.store.get_state(CONFIG_MANAGER)
        self.batch_job_list = self.store.get_state(BATCH_JOB_LIST)
        self.user_consent = self.config_manager.get_user_consent()
        self.tooltips = self.store.get_state(TOOLTIPS)
        self.big_size = self.store.get_state(BIG_SIZE)
        self.script_dir = self.store.get_state(SCRIPT_DIR)
        self.ignore_config = self.store.get_state(IGNORE_CONFIG)


        # Placeholder for UI components initialization
        print("UIManager initialized and linked to communication queues.")

    def start_ui_loop(self):
        """Starts the main event loop for the UI."""
        print("UI Loop started (Placeholder: monitoring output queue for results).")
        # In the final implementation, this would be an event loop
        # that monitors self.output_queue for results to display.

    def simulate_user_input(self, data):
        """Simulates a user action that submits a new task."""
        print(f"UI received user input: '{data}'. Submitting to input queue.")
        self.input_queue.put(data)

    def check_for_results(self):
        """Periodically checks the output queue for results to update the display."""
        try:
            result = self.output_queue.get(block=False)
            print(f"UI received result: {result}")
            self.output_queue.task_done()
            return result
        except Exception: # queue.Empty
            return None

    # --- Utility functions ---
    # new function to refresh the user interface from the values in the shared store
    def refresh_ui_from_store(self):
        self.frames_source_dir.delete(0, 'end')
        self.frames_source_dir.insert('end', self.store.get_state(SOURCE_DIR))
        self.frames_source_dir.after(100, self.frames_source_dir.xview_moveto, 1)
        self.frames_target_dir.delete(0, 'end')
        self.frames_target_dir.insert('end', self.store.get_state(TARGET_DIR))
        self.frames_target_dir.after(100, self.frames_target_dir.xview_moveto, 1)

        self.video_target_dir_str.set(self.store.get_state(VIDEO_TARGET_DIR))
        if self.video_target_dir_str.get() != '':
            # If directory in configuration does not exist, set current output working dir
            if not os.path.isdir(self.video_target_dir_str.get()):
                self.video_target_dir_str.set(self.store.get_state(TARGET_DIR))  # use frames target dir as fallback option
            self.video_target_dir_entry.after(100, self.video_target_dir_entry.xview_moveto, 1)
        self.encode_all_frames.set(self.store.get_state(ENCODE_ALL_FRAMES))
        self.frame_from_str.set(str(self.store.get_state(FRAME_FROM)))
        self.frame_to_str.set(str(self.store.get_state(FRAME_TO)))
        self.film_type.set(self.store.get_state(FILM_TYPE))
        self.rotation_angle_str.set(self.store.get_state(ROTATION_ANGLE))
        self.stabilization_threshold_str.set(self.store.get_state(STABILIZATION_THRESHOLD))
        self.low_contrast_custom_template.set(self.store.get_state(LOW_CONTRAST_CUSTOM_TEMPLATE))
        self.extended_stabilization.set(self.store.get_state(EXTENDED_STABILIZATION))
        if (self.store.get_state(CUSTOM_TEMPLATE_DEFINED)):
            template_manager.add(self.store.get_state(CUSTOM_TEMPLATE_NAME), 
                                      self.store.get_state(CUSTOM_TEMPLATE_FILENAME), 
                                      "custom", 
                                      self.store.get_state(CUSTOM_TEMPLATE_EXPECTED_POS))
            debug_template_refresh_template()
            pass
        else:
            set_film_type()
        self.perform_cropping.set(self.store.get_state(PERFORM_CROPPING))
        self.perform_denoise.set(self.store.get_state(PERFORM_DENOISE))
        self.perform_sharpness.set(self.store.get_state(PERFORM_SHARPNESS))
        self.perform_gamma_correction.set(self.store.get_state(PERFORM_GAMMA_CORRECTION))
        self.gamma_correction_str.set(self.store.get_state(GAMMA_CORRECTION_VALUE))
        self.force_4_3_crop.set(self.store.get_state(FORCE_4_3))
        self.force_16_9_crop.set(self.store.get_state(FORCE_16_9))
        self.frame_fill_type.set(self.store.get_state(FRAME_FILL_TYPE))
        self.generate_video.set(self.store.get_state(GENERATE_VIDEO))
        self.video_filename_str.set(self.store.get_state(VIDEO_FILENAME))
        self.video_title_str.set(self.store.get_state(VIDEO_TITLE))
        self.video_fps = eval(self.store.get_state(VIDEO_FPS))
        self.skip_frame_regeneration.set(self.store.get_state(SKIP_FRAME_REGENERATION))
        self.ffmpeg_preset.set(self.store.get_state(FFMPEG_PRESET))
        self.perform_stabilization.set(self.store.get_state(PERFORM_STABILIZATION))
        self.stabilization_shift_y_value.set(self.store.get_state(STABILIZATION_SHIFT_Y))
        self.stabilization_shift_x_value.set(self.store.get_state(STABILIZATION_SHIFT_X))
        self.perform_rotation.set(self.store.get_state(PERFORM_ROTATION))
        self.video_fps_dropdown_selected.set(self.store.get_state(VIDEO_FPS))
        self.set_fps(self.store.get_state(VIDEO_FPS))
        self.resolution_dropdown_selected.set(self.store.get_state(VIDEO_RESOLUTION))




    # Refresh config class from UI
    def update_config_from_ui(self):
        self.config_manager.set_project_source_dir(source_dir)
        self.config_manager.set_target_dir(target_dir)
        self.config_manager.set_current_frame(self.store.get_state(CURRENT_FRAME))
        self.config_manager.set_skip_frame_regeneration(skip_frame_regeneration.get())
        self.config_manager.set_ffmpeg_preset(ffmpeg_preset.get())
        self.config_manager.set_perform_cropping(perform_cropping.get())
        self.config_manager.set_perform_denoise(perform_denoise.get())
        self.config_manager.set_perform_sharpness(perform_sharpness.get())
        self.config_manager.set_perform_gamma_correction(perform_gamma_correction.get())
        self.config_manager.set_gamma_correction_value(float(gamma_correction_str.get()))
        self.config_manager.set_frame_fill_type(frame_fill_type.get())
        self.config_manager.set_extended_stabilization(extended_stabilization.get())
        self.config_manager.set_low_contrast_custom_template(low_contrast_custom_template.get())
        self.config_manager.set_video_title(video_title_str.get())
        self.config_manager.set_video_filename(video_filename_str.get())
        self.config_manager.set_frame_from(int(frame_from_str.get()))
        self.config_manager.set_frame_to(int(frame_to_str.get()))

        self.config_manager.set_current_bad_frame_index(current_bad_frame_index)
        if stabilize_area_defined:
            self.config_manager.set_perform_stabilization(perform_stabilization.get())
            self.config_manager.set_stabilization_shift_y(stabilization_shift_y_value.get())
            self.config_manager.set_stabilization_shift_x(stabilization_shift_x_value.get())

        self.config_manager.set_perform_rotation(perform_rotation.get())
        self.config_manager.set_video_resolution(self.config_manager.get_video_resolution())
        self.config_manager.set_video_fps(self.config_manager.get_video_fps())
        self.config_manager.set_generate_video(generate_video.get())
        self.config_manager.set_video_target_dir(video_target_dir_str.get())
        self.config_manager.set_frame_fill_type(frame_fill_type.get())
        
        if len(bad_frame_list) > 0:
            save_bad_frame_list()   # Bad frames need to be saved even in batch mode

        # Do not save if current project comes from batch job
        if not self.store.get_state(CONFIG_FROM_FILE) or self.ignore_config:
            return

        self.config_manager.save_configuration()


    # Validation function for different widgets
    def validate_entry_length(self, P, widget_name):
        max_lengths = {
            "video_filename": 100,  # First Entry widget (Tkinter auto-names widgets)
            "video_title": 200,   # Second Entry widget
        }

        max_length = max_lengths.get(widget_name.split(".")[-1], 10)  # Default to 10 if not found
        if len(P) > max_length:
            tk.messagebox.showerror("Error!",
                                f"Maximum length for this field is {max_length}")
            return 
        return len(P) <= max_length

    # --- Treeview functions ---

    def refresh_job_tree(self):
        global job_list_treeview, job_list_hash
        for item_id in job_list_treeview.get_children():
            job_list_treeview.delete(item_id)
        keys = list(self.batch_job_list.get_all_jobs().items())
        # for job_name, job_entry in batch_job_list.get_all_jobs().items():
        for job_name, job_entry in keys:
            if len(job_name) > JOB_LIST_NAME_LENGTH:  # In case name is longer than JOB_LIST_NAME_LENGTH (25)
                new_entry_name = normalize_job_name(job_name)
                logging.error(f"Detected name too long in job list, replacing '{job_name}' by '{new_entry_name}'")
                job_entry.job_name = new_entry_name
                self.batch_job_list.add_job(job_entry)
                self.batch_job_list.delete_job(job_name)
                job_name = new_entry_name
            # Add to listbox
            job_list_treeview.insert('', 'end', text=job_name, values=(self.batch_job_list.get_job(job_name).get_description(),),
                                        tags=("done","joblist_font",) if self.batch_job_list.is_job_done(job_name) else ("pending","joblist_font",))
            self.batch_job_list.mark_job_attempted(job_name, self.batch_job_list.is_job_done(job_name))
        for job_name, job_entry in self.batch_job_list.get_all_jobs().items():
            item_id = self.search_job_name_in_job_treeview(job_name)
            if item_id is not None:
                job_list_treeview.item(item_id, tags=("done","joblist_font",) if self.batch_job_list.is_job_done(job_name) else ("pending","joblist_font",))

        job_list_hash = generate_dict_hash(self.batch_job_list.get_all_jobs())


    def search_job_name_in_job_treeview(self, job_name):
        """
        Find the index of the first element in a tuple that starts with search_str.
        Returns -1 if no match is found.
        """
        for item_id in job_list_treeview.get_children():  # Iterate over all items
            name = job_list_treeview.item(item_id, "text")  # Retrieve Name (column #0)
            if name == job_name:  # Check first column
                return item_id
        return -1

    # --- Other miscellaneous functions

    def display_window_title(self):
        job_name = self.batch_job_list.get_job_list_name()
        title = f"{__module__} {__version__}"
        if job_name != '':
            title += f" - {job_name}"
        self.win.title(title)  # setting title of the window

    # --- File handling functions ---

    def set_source_folder(self):
        source_dir = self.config_manager.get_source_dir()
        target_dir = self.config_manager.get_target_dir()

        # Write project data before switching project
        if source_dir is not None and source_dir != '':   
            self.update_config_from_ui()

        aux_dir = filedialog.askdirectory(
            initialdir=source_dir,
            title="Select folder with captured images to process")

        if not aux_dir or aux_dir == "" or aux_dir == ():
            return
        elif target_dir == aux_dir:
            tk.messagebox.showerror(
                "Error!",
                "Source folder cannot be the same as target folder.")
            return
        else:
            self.win.config(cursor="watch")  # Set cursor to hourglass
            self.store.update_state(UI_INIT_DONE, False)
            source_dir = aux_dir
            self.frames_source_dir.delete(0, 'end')
            self.frames_source_dir.insert('end', source_dir)
            self.frames_source_dir.after(100, self.frames_source_dir.xview_moveto, 1)
            # Create a project id (folder name) for the stats logging below
            # Replace any commas by semi colon to avoid problems when generating csv by AfterScanAnalysis
            project_name = os.path.split(source_dir)[-1].replace(',', ';')
            self.store.update_state(PROJECT_NAME, project_name)
            self.config_manager.set_source_dir(source_dir)

        # Create new project and add to list if it does not exist
        if not self.config_manager.project_exists(source_dir):
            new_project = self.config_manager.get_project_config(source_dir)    # Returns new project if it does not exist
            self.config_manager.save_project_config(source_dir, new_project)
            self.config_manager.set_active_project(source_dir)
            
        self.load_project_config()  # Needs source_dir defined

        decode_project_config(self)  # Needs first_absolute_frame defined

        # If not defined in project, create target folder inside source folder
        if target_dir == '':
            target_dir = os.path.join(source_dir, 'out')
            if not os.path.isdir(target_dir):
                os.mkdir(target_dir)
            get_target_dir_file_list()
            self.frames_target_dir.delete(0, 'end')
            self.frames_target_dir.insert('end', target_dir)
            self.frames_target_dir.after(100, self.frames_target_dir.xview_moveto, 1)
            self.config_manager.set_target_dir(target_dir)

        # Enable Start and Crop buttons, plus slider, once we have files to handle
        cropping_btn.config(state=NORMAL)
        self.frame_slider.config(state=NORMAL)
        Go_btn.config(state=NORMAL)
        self.frame_slider.set(self.store.get_state(CURRENT_FRAME))
        

        init_display()
        widget_status_update(NORMAL)
        FrameSync_Viewer_popup_update_widgets(NORMAL)
        self.store.update_state(UI_INIT_DONE, True)
        self.win.config(cursor="")  # Reset cursor to standard arrow

    def load_project_config(self):
        if self.ignore_config:
            return

        self.config_manager.set_active_project(self.config_manager.get_source_dir())
        project_instance = self.config_manager.get_project_config(self.config_manager.get_source_dir())

        for field_name, value in asdict(project_instance).items():
            logging.debug(f"Field: {field_name}, Value: {value}, Type: {type(value).__name__}")

        # Allow to determine source of current project, to avoid
        # saving it in case of batch processing
        self.store.update_state(CONFIG_FROM_FILE, True)
        widget_status_update(NORMAL)
        FrameSync_Viewer_popup_update_widgets(NORMAL)

    # --------------------------------------------
    # --- User Interface widget action methods ---
    # --------------------------------------------

    def save_named_job_list(self):
        global job_list, job_list_hash, job_list_filename
        start_dir = os.path.split(job_list_filename)[0]  
        aux_file = filedialog.asksaveasfilename(
            initialdir=start_dir,
            defaultextension=".json",
            initialfile=job_list_filename,
            filetypes=[("Joblist JSON files", "*.joblist.json"), ("JSON files", "*.json")],
            title="Select file to save job list")
        if len(aux_file) > 0:
            job_list_hash = generate_dict_hash(self.batch_job_list.get_all_jobs())
            # Remove only the exact suffix if present
            if not aux_file.endswith(".joblist.json"):
                # Remove .json or .joblist if they exist separately
                aux_file = aux_file.removesuffix(".json").removesuffix(".joblist")
                # Append the correct suffix
                aux_file = f"{aux_file}.joblist.json"
            self.batch_job_list.save_to_file(aux_file)
            job_list_filename = aux_file
            self.config_manager.set_job_list_filename(job_list_filename)
            self.display_window_title()


    def load_named_job_list(self):
        global job_list, job_list_filename, job_list_hash

        aux_hash = generate_dict_hash(self.batch_job_list.get_all_jobs())
        if job_list_hash != aux_hash:   # Current job list modified since loaded
            if tk.messagebox.askyesno(
                "Save job list?",
                "Current lob list contains unsaved changes.\r\n"
                "Do you want to save them before loading the new job list?\r\n"):
                self.save_named_job_list()
        start_dir = os.path.split(job_list_filename)[0]  
        aux_file = filedialog.askopenfilename(
            initialdir=start_dir,
            defaultextension=".json",
            filetypes=[("Joblist JSON files", "*.joblist.json"), ("JSON files", "*.json")],
            title="Select file to retrieve job list")
        if len(aux_file) > 0:
            self.batch_job_list.load_from_file(aux_file)
            self.refresh_job_tree()
            job_list_filename = aux_file
            self.config_manager.set_job_list_filename(job_list_filename)
            job_list_hash = generate_dict_hash(self.batch_job_list.get_all_jobs())
            self.display_window_title()

    def exit_app(self):
        # Save configuration if required
        if not self.ignore_config:
            self.update_config_from_ui()
            self.config_manager.set_version(self.store.get_state(APP_VERSION))
            try:
                if self.win is not None and self.win.winfo_exists():
                    self.config_manager.set_window_pos(self.win.geometry())
            except Exception as e:
                logging.error(f"Error while trying to save main window geometry: {e}")
            self.config_manager.save_configuration()
        self.config_manager.rename_legacy_configuration_files()
        self.batch_job_list.rename_legacy_configuration_files()
        self.batch_job_list.save_to_file(job_list_filename)
        # Publish exit event (to be handled by main app)
        self.bus.publish(EXIT_APP)

    def start_convert(self):
        # Publish exit event (to be handled by main app)
        self.bus.publish(START_CONVERT)

    def perform_cropping_selection(self):
        self.generate_video_checkbox.config(state=NORMAL if self.ffmpeg_installed
                                    else DISABLED)
        self.config_manager.set_perform_cropping(self.perform_cropping.get())
        if self.ui_init_done:
            self.win.after(5, scale_display_update)

    def generate_video_selection(self):
        self.config_manager.set_generate_video(self.generate_video.get())
        widget_status_update(NORMAL)
        FrameSync_Viewer_popup_update_widgets(NORMAL)

    # --------------------------------------
    # --- User Interface building blocks ---
    # --------------------------------------

    def _init_ui_menu(self):
        # Menu bar
        self.menu_bar = tk.Menu(self.win)
        self.win.config(menu=self.menu_bar)
        
        # Register max length validation function
        self.vcmd = (self.win.register(self.validate_entry_length), "%P", "%W")  # Pass widget name (%W)

        # File menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu, font=("Arial", self.font_size))
        self.file_menu.add_command(label="Save job list", command=self.save_named_job_list, font=("Arial", self.font_size))
        self.file_menu.add_command(label="Load job list", command=self.load_named_job_list, font=("Arial", self.font_size))
        self.file_menu.add_separator()  # Optional divider
        self.file_menu.add_command(label="Exit", command=self.exit_app, font=("Arial", self.font_size))

        # Help Menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu, font=("Arial", self.font_size))
        self.help_menu.add_command(label="User Guide", font=("Arial", self.font_size), 
                            command=lambda: webbrowser.open("https://github.com/jareff-g/AfterScan/wiki/AfterScan-user-interface-description"))
        self.help_menu.add_command(label="Discord Server", font=("Arial", self.font_size), 
                            command=lambda: webbrowser.open("https://discord.gg/r2UGkH7qg2"))
        self.help_menu.add_command(label="AfterScan Wiki", font=("Arial", self.font_size), 
                            command=lambda: webbrowser.open("https://github.com/jareff-g/AfterScan/wiki"))
        if self.user_consent == "no":
            self.help_menu.add_command(label="Report AfterScan usage", font=("Arial", self.font_size), 
                                command=lambda: get_consent(True))
        self.help_menu.add_command(label="About AfterScan", font=("Arial", self.font_size), 
                            command=lambda: webbrowser.open("https://github.com/jareff-g/AfterScan/wiki/AfterScan:-8mm,-Super-8-film-post-scan-utility"))

    def _init_canvas_section(self):
        # Create a frame to add a border to the preview
        self.left_area_frame = Frame(self.win)
        #left_area_frame.grid(row=0, column=0, padx=5, pady=5, sticky=N)
        self.left_area_frame.pack(side=LEFT, padx=5, pady=5, anchor=N)
        # Create a LabelFrame to act as a border
        self.border_frame = tk.LabelFrame(self.left_area_frame, bd=2, relief=tk.GROOVE)
        self.border_frame.pack(expand=True, fill="both", padx=5, pady=5)
        # Retrieve canvas dimensions
        preview_width = self.store.get_state(PREVIEW_WIDTH)
        preview_height = self.store.get_state(PREVIEW_HEIGTH)
        # Create the canvas
        self.draw_capture_canvas = Canvas(self.border_frame, bg='dark grey', width=preview_width, height=preview_height)
        self.draw_capture_canvas.pack(side=TOP, anchor=N)
        # Initialize canvas image (to avoid multiple use of create_image)
        #Create an empty photoimage
        self.draw_capture_canvas.image = ImageTk.PhotoImage(Image.new("RGBA", (1, 1), (0, 0, 0, 0)), master=self.draw_capture_canvas) #create a transparent 1x1 image.
        self.draw_capture_canvas.image_id = self.draw_capture_canvas.create_image(0, 0, anchor=tk.NW, image=self.draw_capture_canvas.image)

        # New scale under canvas 
        self.frame_selected = IntVar()
        self.frame_slider = Scale(self.border_frame, orient=HORIZONTAL, from_=0, to=0, showvalue=False,
                            variable=self.frame_selected, highlightthickness=1,
                            length=preview_width, takefocus=1, font=("Arial", self.font_size))
        self.frame_slider.bind("<ButtonRelease-1>", process_scale_value)
        self.frame_slider.bind("<KeyRelease>", process_scale_value)
        self.frame_slider.pack(side=BOTTOM, pady=4)
        self.frame_slider.set(self.store.get_state(CURRENT_FRAME))
        self.tootips.add(self.frame_slider, "Browse around frames to be processed")

    def _init_top_right_section(self):
        # Frame for standard widgets to the right of the preview
        self.right_area_frame = Frame(self.win)
        #right_area_frame.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky=N)
        self.right_area_frame.pack(side=LEFT, padx=5, pady=5, anchor=N)

        # Frame for top section of standard widgets ******************************
        self.regular_top_section_frame = Frame(self.right_area_frame)
        self.regular_top_section_frame.pack(side=TOP, padx=2, pady=2)

        # Create frame to display current frame and slider
        self.frame_frame = LabelFrame(self.regular_top_section_frame, text='Current frame',
                                width=35, height=10, font=("Arial", self.font_size-2))
        self.frame_frame.grid(row=1, column=0, sticky='nsew')

        self.selected_frame_number = Label(self.frame_frame, width=12, text='Number:', font=("Arial", self.font_size))
        self.selected_frame_number.pack(side=TOP, pady=2)
        self.tootips.add(self.selected_frame_number, "Frame number, as stated in the filename")

        self.selected_frame_index = Label(self.frame_frame, width=12, text='Index:', font=("Arial", self.font_size))
        self.selected_frame_index.pack(side=TOP, pady=2)
        self.tootips.add(self.selected_frame_index, "Sequential frame index, from 1 to n")

        self.selected_frame_time = Label(self.frame_frame, width=12, text='Time:', font=("Arial", self.font_size))
        self.selected_frame_time.pack(side=TOP, pady=2)
        self.tootips.add(self.selected_frame_time, "Time in the source film where this frame is located")

        # Application status label
        self.app_status_label = Label(self.regular_top_section_frame, width=46 if self.big_size else 46, borderwidth=2,
                                relief="groove", text='Status: Idle',
                                highlightthickness=1, font=("Arial", self.font_size))
        self.app_status_label.grid(row=2, column=0, columnspan=3, pady=5, sticky=EW)

        # Application Exit button
        self.Exit_btn = Button(self.regular_top_section_frame, text="Exit", width=10,
                        height=5, command=self.exit_app, activebackground='red',
                        activeforeground='white', wraplength=80, font=("Arial", self.font_size))
        self.Exit_btn.grid(row=0, column=1, rowspan=2, padx=10, sticky='nsew')

        self.tootips.add(self.Exit_btn, "Exit AfterScan")

        # Application start button
        self.Go_btn = Button(self.regular_top_section_frame, text="Start", width=12, height=5,
                        command=self.start_convert, activebackground='green',
                        activeforeground='white', wraplength=80, font=("Arial", self.font_size))
        self.Go_btn.grid(row=0, column=2, rowspan=2, sticky='nsew')

        self.tootips.add(self.Go_btn, "Start post-processing using current settings")

        # Add AfterScan Logo
        self.win.update_idletasks()
        available_width = self.frame_frame.winfo_width()
        logo_file = os.path.join(self.script_dir, "AfterScan_logo.jpeg")
        try:
            logo_image = Image.open(logo_file)  # Replace with your logo file name
        except FileNotFoundError as e:
            logo_image = None
            logging.warning(f"Could not find AfterScan logo file: {e}")
        if logo_image != None:
            # Resize the image (e.g., to 50% of its original size)
            ratio = available_width / logo_image.width
            new_width = int(logo_image.width * ratio)
            new_height = int(logo_image.height * ratio)
            resized_logo = logo_image.resize((new_width, new_height), Image.LANCZOS) #use LANCZOS for high quality resizing.
            # Convert to PhotoImage
            logo_image = ImageTk.PhotoImage(resized_logo, master=self.draw_capture_canvas)
            if logo_image:
                self.logo_label = tk.Label(self.regular_top_section_frame, image=logo_image)

                # Delete reference to previous image, if any
                aux_image = None
                if hasattr(self.logo_label, 'image'):
                    aux_image = self.logo_label.image
                self.logo_label.image = logo_image  # Keep a reference!
                if aux_image:
                    del aux_image
                self.logo_label.grid(row=0, column=0, sticky='nsew')

    def _init_folder_selection_section(self):
        # Create frame to select source and target folders *******************************
        self.folder_frame = LabelFrame(self.right_area_frame, text='Folder selection', width=30,
                                height=8, font=("Arial", self.font_size-2))
        self.folder_frame.pack(padx=2, pady=2, ipadx=5, expand=True, fill="both")

        self.source_folder_frame = Frame(self.folder_frame)
        self.source_folder_frame.pack(side=TOP)
        self.frames_source_dir = Entry(self.source_folder_frame, width=34 if self.big_size else 34,
                                        borderwidth=1, font=("Arial", self.font_size))
        self.frames_source_dir.pack(side=LEFT)
        self.frames_source_dir.delete(0, 'end')
        self.frames_source_dir.insert('end', self.config_manager.get_source_dir())
        self.frames_source_dir.after(100, self.frames_source_dir.xview_moveto, 1)
        self.frames_source_dir.bind('<<Paste>>', lambda event, entry=self.frames_source_dir: on_paste_all_entries(event, entry))

        self.tootips.add(self.frames_source_dir, "Directory where the source frames are located")

        self.source_folder_btn = Button(self.source_folder_frame, text='Source', width=6,
                                height=1, command=set_source_folder,
                                activebackground='green',
                                activeforeground='white', wraplength=80, font=("Arial", self.font_size))
        self.source_folder_btn.pack(side=LEFT)

        self.self.tootips.add(self.source_folder_btn, "Selects the directory where the source frames are located")

        self.target_folder_frame = Frame(self.folder_frame)
        self.target_folder_frame.pack(side=TOP)
        self.frames_target_dir = Entry(self.target_folder_frame, width=34 if self.big_size else 34,
                                        borderwidth=1, font=("Arial", self.font_size))
        self.frames_target_dir.pack(side=LEFT)
        self.frames_target_dir.bind('<<Paste>>', lambda event, entry=self.frames_target_dir: on_paste_all_entries(event, entry))
        
        self.tootips.add(self.frames_target_dir, "Directory where generated frames will be stored")

        self.target_folder_btn = Button(self.target_folder_frame, text='Target', width=6,
                                height=1, command=set_frames_target_folder,
                                activebackground='green',
                                activeforeground='white', wraplength=80, font=("Arial", self.font_size))
        self.target_folder_btn.pack(side=LEFT)

        self.tootips.add(self.target_folder_btn, "Selects the directory where the generated frames will be stored")

        self.store.update_state(SAVE_BG, self.source_folder_btn['bg'])
        self.store.update_state(SAVE_FG, self.source_folder_btn['fg'])

        self.folder_bottom_frame = Frame(self.folder_frame)
        self.folder_bottom_frame.pack(side=BOTTOM, ipady=2)

    def _init_post_processing_section(self):
        # Define post-processing area *********************************************
        self.postprocessing_frame = LabelFrame(self.right_area_frame,
                                        text='Frame post-processing',
                                        width=40, height=8, font=("Arial", self.font_size-2))
        self.postprocessing_frame.pack(padx=2, pady=2, ipadx=5, expand=True, fill="both")
        postprocessing_row = 0
        self.postprocessing_frame.grid_columnconfigure(0, weight=1)
        self.postprocessing_frame.grid_columnconfigure(1, weight=1)
        self.postprocessing_frame.grid_columnconfigure(2, weight=1)

        # Radio buttons to select R8/S8. Required to select adequate pattern, and match position
        self.film_type = StringVar()
        self.film_type_S8_rb = Radiobutton(self.postprocessing_frame, text="Super 8", variable=self.film_type, command=set_film_type,
                                    width=11 if self.big_size else 11, value='S8', font=("Arial", self.font_size))
        self.film_type_S8_rb.grid(row=postprocessing_row, column=0, sticky=W)
        self.tootips.add(self.film_type_S8_rb, "Handle as Super 8 film")
        self.film_type_R8_rb = Radiobutton(self.postprocessing_frame, text="Regular 8", variable=self.film_type, command=set_film_type,
                                    width=11 if self.big_size else 11, value='R8', font=("Arial", self.font_size))
        self.film_type_R8_rb.grid(row=postprocessing_row, column=1, sticky=W)
        self.tootips.add(self.film_type_R8_rb, "Handle as 8mm (Regular 8) film")
        self.film_type.set('S8')
        postprocessing_row += 1

        # Check box to select encoding of all frames
        encode_all_frames = tk.BooleanVar(value=False)
        encode_all_frames_checkbox = tk.Checkbutton(
            postprocessing_frame, text='Encode all frames',
            variable=encode_all_frames, onvalue=True, offvalue=False,
            command=encode_all_frames_selection, width=14, font=("Arial", self.font_size))
        encode_all_frames_checkbox.grid(row=postprocessing_row, column=0,
                                            columnspan=3, sticky=W)
        self.tootips.add(encode_all_frames_checkbox, "If selected, all frames in source folder will be encoded")
        postprocessing_row += 1

        # Entry to enter start/end frames
        frames_to_encode_label = tk.Label(postprocessing_frame,
                                        text='Frame range:',
                                        width=12, font=("Arial", self.font_size))
        frames_to_encode_label.grid(row=postprocessing_row, column=0, columnspan=2, sticky=W)
        frame_from_str = tk.StringVar(value=0)
        frame_from_entry = Entry(postprocessing_frame, textvariable=frame_from_str, width=5, borderwidth=1, font=("Arial", self.font_size))
        frame_from_entry.grid(row=postprocessing_row, column=1, sticky=W)
        frame_from_entry.config(state=NORMAL)
        frame_from_entry.bind("<Double - Button - 1>", update_frame_from)
        frame_from_entry.bind("<Button - 2>", update_frame_from)
        frame_from_entry.bind('<<Paste>>', lambda event, entry=frame_from_entry: on_paste_all_entries(event, entry))
        frame_from_entry.bind("<FocusOut>", update_frame_from)
        self.tootips.add(frame_from_entry, "First frame to be processed, if not encoding the entire set")
        frame_to_str = tk.StringVar(value=0)
        frames_separator_label = tk.Label(postprocessing_frame, text='to', width=2, font=("Arial", self.font_size))
        frames_separator_label.grid(row=postprocessing_row, column=1)
        frame_to_entry = Entry(postprocessing_frame, textvariable=frame_to_str, width=5, borderwidth=1, font=("Arial", self.font_size))
        frame_to_entry.grid(row=postprocessing_row, column=1, sticky=E)
        frame_to_entry.config(state=NORMAL)
        frame_to_entry.bind("<Double - Button - 1>", update_frame_to)
        frame_to_entry.bind("<Button - 2>", update_frame_to)
        frame_to_entry.bind('<<Paste>>', lambda event, entry=frame_to_entry: on_paste_all_entries(event, entry))
        frame_to_entry.bind("<FocusOut>", update_frame_to)
        self.tootips.add(frame_to_entry, "Last frame to be processed, if not encoding the entire set")

        postprocessing_row += 1

        # Check box to do rotate image
        perform_rotation = tk.BooleanVar(value=False)
        perform_rotation_checkbox = tk.Checkbutton(
            postprocessing_frame, text='Rotate image:',
            variable=perform_rotation, onvalue=True, offvalue=False, width=11,
            command=perform_rotation_selection, font=("Arial", self.font_size))
        perform_rotation_checkbox.grid(row=postprocessing_row, column=0,
                                            columnspan=1, sticky=W)
        perform_rotation_checkbox.config(state=NORMAL)
        self.tootips.add(perform_rotation_checkbox, "Rotate generated frames")

        # Spinbox to select rotation angle
        rotation_angle_str = tk.StringVar(value=str(0))
        #rotation_angle_selection_aux = postprocessing_frame.register(rotation_angle_selection)
        rotation_angle_spinbox = tk.Spinbox(
            postprocessing_frame,
            command=rotation_angle_selection, width=5,
            textvariable=rotation_angle_str, from_=-5, to=5,
            format="%.1f", increment=0.1, font=("Arial", self.font_size))
        rotation_angle_spinbox.grid(row=postprocessing_row, column=1, sticky=W)
        rotation_angle_spinbox.bind("<FocusOut>", rotation_angle_spinbox_focus_out)
        self.tootips.add(rotation_angle_spinbox, "Angle to use when rotating frames")
        #rotation_angle_selection('down')
        rotation_angle_label = tk.Label(postprocessing_frame,
                                        text='°',
                                        width=1, font=("Arial", self.font_size))
        rotation_angle_label.grid(row=postprocessing_row, column=1)
        rotation_angle_label.config(state=NORMAL)
        postprocessing_row += 1

        ### Stabilization controls
        # Custom film perforation template
        custom_stabilization_btn = Button(postprocessing_frame,
                                        text='Define custom template',
                                        width=18, height=1,
                                        command=select_custom_template,
                                        activebackground='green',
                                        activeforeground='white', font=("Arial", self.font_size))
        custom_stabilization_btn.config(relief=SUNKEN if template_manager.get_active_type() == 'Custom' else RAISED)
        custom_stabilization_btn.grid(row=postprocessing_row, column=0, columnspan=2, padx=5, pady=5, sticky=W)
        self.tootips.add(custom_stabilization_btn,
                    "Define a custom template for this project (vs the automatic template defined by AfterScan)")

        low_contrast_custom_template = tk.BooleanVar(value=False)
        low_contrast_custom_template_checkbox = tk.Checkbutton(
            postprocessing_frame, text='Low contrast helper',
            variable=low_contrast_custom_template, onvalue=True, offvalue=False, width=16,
            command=low_contrast_custom_template_selection, font=("Arial", self.font_size))
        low_contrast_custom_template_checkbox.grid(row=postprocessing_row, column=1,
                                            columnspan=2, sticky=E)
        self.tootips.add(low_contrast_custom_template_checkbox, "Activate when defining a custom template using a low contrast frame")

        postprocessing_row += 1

        # Check box to do stabilization or not
        perform_stabilization = tk.BooleanVar(value=False)
        perform_stabilization_checkbox = tk.Checkbutton(
            postprocessing_frame, text='Stabilize',
            variable=perform_stabilization, onvalue=True, offvalue=False, width=7,
            command=perform_stabilization_selection, font=("Arial", self.font_size))
        perform_stabilization_checkbox.grid(row=postprocessing_row, column=0,
                                            columnspan=1, sticky=W)
        self.tootips.add(perform_stabilization_checkbox, "Stabilize generated frames. Sprocket hole is used as common reference, it needs to be clearly visible")
        # Label to display the match level of current frame to template
        stabilization_threshold_match_label = Label(postprocessing_frame, width=4, borderwidth=1, relief='sunken', font=("Arial", self.font_size))
        stabilization_threshold_match_label.grid(row=postprocessing_row, column=0, sticky=E)
        self.tootips.add(stabilization_threshold_match_label, "Dynamically displays the match quality of the sprocket hole template. Green is good, orange acceptable, red is bad")

        # Extended search checkbox (replace radio buttons for fast/precise stabilization)
        extended_stabilization = tk.BooleanVar(value=False)
        extended_stabilization_checkbox = tk.Checkbutton(
            postprocessing_frame, text='Extend',
            variable=extended_stabilization, onvalue=True, offvalue=False, width=6,
            command=extended_stabilization_selection, font=("Arial", self.font_size))
        #extended_stabilization_checkbox.grid(row=postprocessing_row, column=1, columnspan=1, sticky=W)
        extended_stabilization_checkbox.forget()
        self.tootips.add(extended_stabilization_checkbox, "Extend the area where AfterScan looks for sprocket holes. In some cases this might help")

        # Stabilization shift: Since film might not be centered around hole(s) this gives the option to move it up/down
        # Spinbox for gamma correction
        stabilization_shift_label = tk.Label(postprocessing_frame, text='Offset X/Y:',
                                            width=14, font=("Arial", self.font_size))
        stabilization_shift_label.grid(row=postprocessing_row, column=1, columnspan=1, sticky=E)

        stabilization_shift_x_value = tk.IntVar(value=0)
        stabilization_shift_x_spinbox = tk.Spinbox(postprocessing_frame, width=3, command=select_stabilization_shift_x,
            textvariable=stabilization_shift_x_value, from_=-150, to=150, increment=-5, font=("Arial", self.font_size))
        stabilization_shift_x_spinbox.grid(row=postprocessing_row, column=2, sticky=W)
        self.tootips.add(stabilization_shift_x_spinbox, "Allows to shift the frame left or right after stabilization "
                                    "(to compensate for films where the frame is not centered around the hole/holes)")
        stabilization_shift_x_spinbox.bind("<FocusOut>", select_stabilization_shift_x)

        stabilization_shift_y_value = tk.IntVar(value=0)
        stabilization_shift_y_spinbox = tk.Spinbox(postprocessing_frame, width=3, command=select_stabilization_shift_y,
            textvariable=stabilization_shift_y_value, from_=-150, to=150, increment=-5, font=("Arial", self.font_size))
        stabilization_shift_y_spinbox.grid(row=postprocessing_row, column=2, sticky=E)
        self.tootips.add(stabilization_shift_y_spinbox, "Allows to shift the frame up or down after stabilization "
                                    "(to compensate for films where the frame is not centered around the hole/holes)")
        stabilization_shift_y_spinbox.bind("<FocusOut>", select_stabilization_shift_y)

        postprocessing_row += 1

        ### Cropping controls
        # Check box to do cropping or not
        cropping_btn = Button(postprocessing_frame, text='Define crop area',
                            width=12, height=1, command=select_cropping_area,
                            activebackground='green', activeforeground='white',
                            wraplength=120, font=("Arial", self.font_size))
        cropping_btn.grid(row=postprocessing_row, column=0, sticky=E)
        self.tootips.add(cropping_btn, "Open popup window to define the cropping rectangle")

        perform_cropping = tk.BooleanVar(value=False)
        perform_cropping_checkbox = tk.Checkbutton(
            postprocessing_frame, text='Crop', variable=perform_cropping,
            onvalue=True, offvalue=False, command=perform_cropping_selection,
            width=4, font=("Arial", self.font_size))
        perform_cropping_checkbox.grid(row=postprocessing_row, column=1, sticky=W)
        self.tootips.add(perform_cropping_checkbox, "Crop generated frames to the user-defined limits ('Define crop area' button)")

        force_4_3_crop = tk.BooleanVar(value=False)
        force_4_3_crop_checkbox = tk.Checkbutton(
            postprocessing_frame, text='4:3', variable=force_4_3_crop,
            onvalue=True, offvalue=False, command=force_4_3_selection,
            width=4, font=("Arial", self.font_size))
        force_4_3_crop_checkbox.grid(row=postprocessing_row, column=1, sticky=E)
        self.tootips.add(force_4_3_crop_checkbox, "Enforce 4:3 aspect ratio when defining the cropping rectangle")

        force_16_9_crop = tk.BooleanVar(value=False)
        force_16_9_crop_checkbox = tk.Checkbutton(
            postprocessing_frame, text='16:9', variable=force_16_9_crop,
            onvalue=True, offvalue=False, command=force_16_9_selection,
            width=4, font=("Arial", self.font_size))
        force_16_9_crop_checkbox.grid(row=postprocessing_row, column=2, sticky=W)
        self.tootips.add(force_16_9_crop_checkbox, "Enforce 16:9 aspect ratio when defining the cropping rectangle")

        postprocessing_row += 1

        # Check box to perform denoise
        perform_denoise = tk.BooleanVar(value=False)
        perform_denoise_checkbox = tk.Checkbutton(
            postprocessing_frame, text='Denoise', variable=perform_denoise,
            onvalue=True, offvalue=False, command=perform_denoise_selection,
            font=("Arial", self.font_size))
        perform_denoise_checkbox.grid(row=postprocessing_row, column=0, sticky=W)
        self.tootips.add(perform_denoise_checkbox, "Apply denoise algorithm (using OpenCV's 'fastNlMeansDenoisingColored') to the generated frames")

        # Check box to perform sharpness
        perform_sharpness = tk.BooleanVar(value=False)
        perform_sharpness_checkbox = tk.Checkbutton(
            postprocessing_frame, text='Sharpen', variable=perform_sharpness,
            onvalue=True, offvalue=False, command=perform_sharpness_selection,
            font=("Arial", self.font_size))
        perform_sharpness_checkbox.grid(row=postprocessing_row, column=1, sticky=W)
        self.tootips.add(perform_sharpness_checkbox, "Apply sharpen algorithm (using OpenCV's 'filter2D') to the generated frames")

        # Check box to do gamma correction
        perform_gamma_correction = tk.BooleanVar(value=False)
        perform_gamma_correction_checkbox = tk.Checkbutton(
            postprocessing_frame, text='GC:', variable=perform_gamma_correction, command=perform_gamma_correction_selection,
            onvalue=True, offvalue=False, font=("Arial", self.font_size))
        perform_gamma_correction_checkbox.grid(row=postprocessing_row, column=2, sticky=W)
        perform_gamma_correction_checkbox.config(state=NORMAL)
        self.tootips.add(perform_gamma_correction_checkbox, "Apply gamma correction to the generated frames")

        # Spinbox for gamma correction
        gamma_correction_str = tk.StringVar(value="2.2")
        gamma_correction_spinbox = tk.Spinbox(postprocessing_frame, width=3, command=select_gamma_correction_value,
            textvariable=gamma_correction_str, from_=0.1, to=4, format="%.1f", increment=0.1, font=("Arial", self.font_size))
        gamma_correction_spinbox.grid(row=postprocessing_row, column=2, sticky=E)
        self.tootips.add(gamma_correction_spinbox, "Gamma correction value (default is 2.2, has to be greater than zero)")
        # Bind focus-out event to enforce the minimum value
        gamma_correction_spinbox.bind("<FocusOut>", gamma_enforce_min_value)

        postprocessing_row += 1

        # This checkbox enables 'fake' frame completion when, due to stabilization process, part of the frame is lost at the
        # top or at the bottom. It is named 'fake' because to fill in the missing part, a fragment of the previous or next
        # frame is used. Not perfect, but better than leaving the missing part blank, as it would happen without this.
        # Also, for this to work the cropping rectangle should encompass the full frame, top to bottom.
        # And yes, in theory we could pick the missing fragment of the same frame by picking the picture of the
        # next/previous frame, BUT it is not given that it will be there, as the next/previous frame might have been
        # captured without the required part.
        frame_fill_type = StringVar()
        perform_fill_none_rb = Radiobutton(postprocessing_frame, text='No frame fill',
                                        variable=frame_fill_type, value='none', font=("Arial", self.font_size))
        perform_fill_none_rb.grid(row=postprocessing_row, column=0, sticky=W)
        self.tootips.add(perform_fill_none_rb, "Badly aligned frames will be left with the missing part of the image black after stabilization")
        perform_fill_fake_rb = Radiobutton(postprocessing_frame, text='Fake fill',
                                        variable=frame_fill_type, value='fake', font=("Arial", self.font_size))
        perform_fill_fake_rb.grid(row=postprocessing_row, column=1, sticky=W)
        self.tootips.add(perform_fill_fake_rb, "Badly aligned frames will have the missing part of the image completed with a fragment of the next/previous frame after stabilization")
        perform_fill_dumb_rb = Radiobutton(postprocessing_frame, text='Dumb fill',
                                        variable=frame_fill_type, value='dumb', font=("Arial", self.font_size))
        perform_fill_dumb_rb.grid(row=postprocessing_row, column=2, sticky=W)
        self.tootips.add(perform_fill_dumb_rb, "Badly aligned frames will have the missing part of the image filled with the adjacent pixel row after stabilization")
        frame_fill_type.set('fake')

        postprocessing_row += 1

        # Define video generating area ************************************
        video_frame = LabelFrame(right_area_frame,
                                text='Video generation',
                                width=30, height=8, font=("Arial", self.font_size-2))
        video_frame.pack(padx=2, pady=2, ipadx=5, expand=True, fill="both")
        video_row = 0
        video_frame.grid_columnconfigure(0, weight=1)
        video_frame.grid_columnconfigure(1, weight=1)
        video_frame.grid_columnconfigure(2, weight=1)

        # Check box to generate video or not
        generate_video = tk.BooleanVar(value=False)
        generate_video_checkbox = tk.Checkbutton(video_frame,
                                                text='Video',
                                                variable=generate_video,
                                                onvalue=True, offvalue=False,
                                                command=generate_video_selection,
                                                width=5, font=("Arial", self.font_size))
        generate_video_checkbox.grid(row=video_row, column=0, sticky=W, padx=5)
        generate_video_checkbox.config(state=NORMAL if ffmpeg_installed
                                    else DISABLED)
        self.tootips.add(generate_video_checkbox, "Generate an MP4 video, once all frames have been processed")

        # Check box to skip frame regeneration
        skip_frame_regeneration = tk.BooleanVar(value=False)
        skip_frame_regeneration_cb = tk.Checkbutton(
            video_frame, text='Skip Frame regeneration',
            variable=skip_frame_regeneration, onvalue=True, offvalue=False,
            width=20, font=("Arial", self.font_size))
        skip_frame_regeneration_cb.grid(row=video_row, column=1,
                                        columnspan=2, sticky=W, padx=5)
        skip_frame_regeneration_cb.config(state=NORMAL if ffmpeg_installed
                                        else DISABLED)
        self.tootips.add(skip_frame_regeneration_cb, "If frames have ben already generated in a previous run, and you want to only generate the vieo, check this one")

        video_row += 1

        # Video target folder
        video_target_dir_str = StringVar()
        video_target_dir_entry = Entry(video_frame, textvariable=video_target_dir_str, width=30, borderwidth=1, font=("Arial", self.font_size))
        video_target_dir_entry.grid(row=video_row, column=0, columnspan=2, sticky=W, padx=5)
        video_target_dir_entry.bind('<<Paste>>', lambda event, entry=video_target_dir_entry: on_paste_all_entries(event, entry))
        self.tootips.add(video_target_dir_entry, "Directory where the generated video will be stored")

        video_target_folder_btn = Button(video_frame, text='Target', width=6,
                                height=1, command=set_video_target_folder,
                                activebackground='green',
                                activeforeground='white', wraplength=80, font=("Arial", self.font_size))
        video_target_folder_btn.grid(row=video_row, column=2, columnspan=2, sticky=W, padx=5)
        self.tootips.add(video_target_folder_btn, "Selects directory where the generated video will be stored")
        video_row += 1

        # Video filename
        video_filename_str = StringVar()
        video_filename_label = Label(video_frame, text='Video filename:', font=("Arial", self.font_size))
        video_filename_label.grid(row=video_row, column=0, sticky=W, padx=5)
        video_filename_name = Entry(video_frame, textvariable=video_filename_str, name="video_filename", 
                                    validate="key", validatecommand=vcmd,
                                    width=26 if big_size else 26, borderwidth=1, font=("Arial", self.font_size))
        video_filename_name.grid(row=video_row, column=1, columnspan=2, sticky=W, padx=5)
        video_filename_name.bind('<<Paste>>', lambda event, entry=video_filename_name: on_paste_all_entries(event, entry))
        self.tootips.add(video_filename_name, "Filename of video to be created")

        video_row += 1

        # Video title (add title at the start of the video)
        video_title_str = StringVar()
        video_title_label = Label(video_frame, text='Video title:', font=("Arial", self.font_size))
        video_title_label.grid(row=video_row, column=0, sticky=W, padx=5)
        video_title_name = Entry(video_frame, textvariable=video_title_str, name="video_title", 
                                validate="key", validatecommand=vcmd,
                                width=26 if big_size else 26, borderwidth=1, font=("Arial", self.font_size))
        video_title_name.grid(row=video_row, column=1, columnspan=2, sticky=W, padx=5)
        video_title_name.bind('<<Paste>>', lambda event, entry=video_title_name: on_paste_all_entries(event, entry))
        self.tootips.add(video_title_name, "Video title. If entered, a simple title sequence will be generated at the start of the video, using a sequence randomly selected from the same video, running at half speed")

        video_row += 1

        # Drop down to select FPS
        # Dropdown menu options
        fps_list = [
            "8",
            "9",
            "16",
            "16.67",
            "18",
            "24",
            "25",
            "29.97",
            "30",
            "48",
            "50"
        ]

        # datatype of menu text
        video_fps_dropdown_selected = StringVar()

        # initial menu text
        video_fps_dropdown_selected.set("18")

        # Create FPS Dropdown menu
        video_fps_frame = Frame(video_frame)
        video_fps_frame.grid(row=video_row, column=0, sticky=W)
        video_fps_label = Label(video_fps_frame, text='FPS:', font=("Arial", self.font_size))
        video_fps_label.pack(side=LEFT, anchor=W, padx=5)
        video_fps_label.config(state=DISABLED)
        video_fps_dropdown = OptionMenu(video_fps_frame,
                                        video_fps_dropdown_selected, *fps_list,
                                        command=set_fps)
        video_fps_dropdown.config(takefocus=1, font=("Arial", self.font_size))
        video_fps_dropdown.pack(side=LEFT, anchor=E, padx=5)
        video_fps_dropdown.config(state=DISABLED)
        self.tootips.add(video_fps_dropdown, "Number of frames per second (FPS) of the video to be generated. Usually Super8 goes at 18 FPS, and Regular 8 at 16 FPS, although some cameras allowed to use other speeds (faster for smoother movement, slower for extended play time)")

        # Create FFmpeg preset options
        ffmpeg_preset_frame = Frame(video_frame)
        ffmpeg_preset_frame.grid(row=video_row, column=1, columnspan=2, sticky=W, padx=5)
        ffmpeg_preset = StringVar()
        ffmpeg_preset_rb1 = Radiobutton(ffmpeg_preset_frame,
                                        text="Best quality (slow)",
                                        variable=ffmpeg_preset, value='veryslow', font=("Arial", self.font_size))
        ffmpeg_preset_rb1.pack(side=TOP, anchor=W, padx=5)
        ffmpeg_preset_rb1.config(state=DISABLED)
        self.tootips.add(ffmpeg_preset_rb1, "Best quality, but very slow encoding. Maps to the same ffmpeg option")

        ffmpeg_preset_rb2 = Radiobutton(ffmpeg_preset_frame, text="Medium",
                                        variable=ffmpeg_preset, value='medium', font=("Arial", self.font_size))
        ffmpeg_preset_rb2.pack(side=TOP, anchor=W, padx=5)
        ffmpeg_preset_rb2.config(state=DISABLED)
        self.tootips.add(ffmpeg_preset_rb2, "Compromise between quality and encoding speed. Maps to the same ffmpeg option")
        ffmpeg_preset_rb3 = Radiobutton(ffmpeg_preset_frame,
                                        text="Fast (low quality)",
                                        variable=ffmpeg_preset, value='veryfast', font=("Arial", self.font_size))
        ffmpeg_preset_rb3.pack(side=TOP, anchor=W, padx=5)
        ffmpeg_preset_rb3.config(state=DISABLED)
        self.tootips.add(ffmpeg_preset_rb3, "Faster encoding speed, lower quality (but not so much IMHO). Maps to the same ffmpeg option")
        ffmpeg_preset.set('medium')
        video_row += 1

        # Drop down to select resolution
        # datatype of menu text
        resolution_dropdown_selected = StringVar()

        # initial menu text
        resolution_dropdown_selected.set("1920x1440 (1080P)")

        # Create resolution Dropdown menu
        resolution_frame = Frame(video_frame)
        resolution_frame.grid(row=video_row, column=0, columnspan= 2, sticky=W)
        resolution_label = Label(resolution_frame, text='Resolution:', font=("Arial", self.font_size))
        resolution_label.pack(side=LEFT, anchor=W, padx=5)
        resolution_label.config(state=DISABLED)
        resolution_dropdown = OptionMenu(resolution_frame,
                                        resolution_dropdown_selected, *resolution_dict.keys(),
                                        command=set_resolution)
        resolution_dropdown.config(takefocus=1, font=("Arial", self.font_size))
        resolution_dropdown.pack(side=LEFT, anchor=E, padx=5)
        resolution_dropdown.config(state=DISABLED)
        self.tootips.add(resolution_dropdown, "Resolution to be used when generating the video")

        # Create button to play the video
        video_play_btn = Button(video_frame, text='▶', width=8,
                                height=1, command=play_video,
                                activebackground='green',
                                activeforeground='white', wraplength=80, font=("Arial", self.font_size))
        video_play_btn.grid(row=video_row, column=2, sticky=E, padx=5)
        self.tootips.add(video_play_btn, "Play the generated video")

        video_row += 1

        # Extra (expert) area ***************************************************
        if expert_mode:
            extra_frame = LabelFrame(right_area_frame,
                                    text='Expert options',
                                    width=50, height=8, font=("Arial", self.font_size-2))
            extra_frame.pack(padx=5, pady=5, ipadx=5, ipady=5, expand=True, fill="both")
            extra_frame.grid_columnconfigure(0, weight=1)
            extra_frame.grid_columnconfigure(1, weight=1)
            extra_row = 0

            # Check box to display misaligned frame monitor/editor
            display_template_popup_btn = Button(extra_frame,
                                                text='FrameSync Editor',
                                                command=FrameSync_Viewer_popup,
                                                width=15, font=("Arial", self.font_size))
            display_template_popup_btn.config(relief=SUNKEN if frame_sync_viewer_opened else RAISED)
            display_template_popup_btn.grid(row=extra_row, column=0, padx=5, sticky="nsew")
            ### extra_frame.grid_columnconfigure(0, weight=1)
            self.tootips.add(display_template_popup_btn, "Display popup window with dynamic debug information.Useful for developers only")

            # Settings button, at the bottom of top left area
            options_btn = Button(extra_frame, text="Settings", command=cmd_settings_popup, width=15,
                                relief=RAISED, font=("Arial", self.font_size), name='options_btn')
            options_btn.widget_type = "general"
            options_btn.grid(row=extra_row, column=1, padx=5, sticky="nsew")
            self.tootips.add(options_btn, "Set AfterScan options.")
            extra_row += 1

            # Spinbox to select stabilization threshold - Ignored, to be removed in the future
            stabilization_threshold_label = tk.Label(extra_frame,
                                                    text='Threshold:',
                                                    width=11, font=("Arial", self.font_size))
            #stabilization_threshold_label.grid(row=extra_row, column=1, columnspan=1, sticky=E)
            stabilization_threshold_label.grid_forget()
            stabilization_threshold_str = tk.StringVar(value=str(stabilization_threshold))
            stabilization_threshold_selection_aux = extra_frame.register(
                stabilization_threshold_selection)
            stabilization_threshold_spinbox = tk.Spinbox(
                extra_frame,
                command=(stabilization_threshold_selection_aux, '%d'), width=6,
                textvariable=stabilization_threshold_str, from_=0, to=255, font=("Arial", self.font_size))
            #stabilization_threshold_spinbox.grid(row=extra_row, column=2, sticky=W)
            stabilization_threshold_spinbox.grid_forget()
            stabilization_threshold_spinbox.bind("<FocusOut>", stabilization_threshold_spinbox_focus_out)
            self.tootips.add(stabilization_threshold_spinbox, "Threshold value to isolate the sprocket hole from the rest of the image while definint the custom template")

            extra_row += 1

        # Define job list area ***************************************************
        # Replace listbox with treeview
        # Define style for labelframe
        style = ttk.Style()
        style.configure("TLabelframe.Label", font=("Arial", self.font_size-2))
        # Create a frame to hold Treeview and scrollbars
        job_list_frame = ttk.LabelFrame(left_area_frame,
                                text='Job List',
                                width=50, height=8)
        job_list_frame.pack(side=TOP, padx=2, pady=2, anchor=W)

        # Create Treeview with a single column
        job_list_treeview = ttk.Treeview(job_list_frame, columns=("description"))

        # Define style for headings
        style.configure("Treeview.Heading", font=("Arial", self.font_size, "bold")) #Change header font.

        # Define the single column
        name_width = 130 if force_small_size else 200
        description_width = 250 if force_small_size else 340
        job_list_treeview.heading("#0", text="Name")
        job_list_treeview.heading("description", text="Description")
        job_list_treeview.column("#0", anchor="w", width=name_width, minwidth=name_width, stretch=tk.NO)
        job_list_treeview.column("description", anchor="w", width=description_width, minwidth=1400, stretch=tk.NO)

        # job listbox scrollbars
        job_list_listbox_scrollbar_y = ttk.Scrollbar(job_list_frame, orient="vertical", command=job_list_treeview.yview)
        job_list_treeview.configure(yscrollcommand=job_list_listbox_scrollbar_y.set)
        job_list_listbox_scrollbar_y.grid(row=0, column=1, sticky=NS)
        job_list_listbox_scrollbar_x = ttk.Scrollbar(job_list_frame, orient="horizontal", command=job_list_treeview.xview)
        job_list_treeview.configure(xscrollcommand=job_list_listbox_scrollbar_x.set)
        job_list_listbox_scrollbar_x.grid(row=1, column=0, columnspan=1, sticky=EW)

        # Layout
        job_list_treeview.grid(column=0, row=0, padx=5, pady=2, ipadx=5)

        # Define tags for different row colors
        job_list_treeview.tag_configure("pending", foreground="black")
        job_list_treeview.tag_configure("ongoing", foreground="blue")
        job_list_treeview.tag_configure("done", foreground="green")
        job_list_treeview.tag_configure("joblist_font", font=("Arial", self.font_size))

        # Bind the keys to be used alog
        job_list_treeview.bind("<Delete>", job_list_delete_current)
        job_list_treeview.bind("<Return>", job_list_load_current)
        job_list_treeview.bind("<KP_Enter>", job_list_load_current)
        job_list_treeview.bind("<Double - Button - 1>", job_list_load_current)
        job_list_treeview.bind("r", job_list_rerun_current)
        job_list_treeview.bind('<<ListboxSelect>>', job_list_process_selection)
        job_list_treeview.bind("u", job_list_move_up)
        job_list_treeview.bind("d", job_list_move_down)
        job_list_listbox_disabled = False   # to prevent processing clicks on listbox, as disabling it will prevent checkign status of each job
        
        # Define job list button area
        job_list_btn_frame = Frame(job_list_frame,
                                width=50, height=8)
        job_list_btn_frame.grid(row=0, column=2, padx=2, pady=2, sticky=W)

        # Add job button
        add_job_btn = Button(job_list_btn_frame, text="Add job", width=12, height=1,
                        command=job_list_add_current, activebackground='green',
                        activeforeground='white', wraplength=100, font=("Arial", self.font_size))
        add_job_btn.pack(side=TOP, padx=2, pady=2)
        self.tootips.add(add_job_btn, "Add to job list a new job using the current settings defined on the right area of the AfterScan window")

        # Delete job button
        delete_job_btn = Button(job_list_btn_frame, text="Delete job", width=12, height=1,
                        command=job_list_delete_selected, activebackground='green',
                        activeforeground='white', wraplength=100, font=("Arial", self.font_size))
        delete_job_btn.pack(side=TOP, padx=2, pady=2)
        self.tootips.add(delete_job_btn, "Delete currently selected job from list")

        # Rerun job button
        rerun_job_btn = Button(job_list_btn_frame, text="Rerun job", width=12, height=1,
                        command=job_list_rerun_selected, activebackground='green',
                        activeforeground='white', wraplength=100, font=("Arial", self.font_size))
        rerun_job_btn.pack(side=TOP, padx=2, pady=2)
        self.tootips.add(rerun_job_btn, "Toggle 'run' state of currently selected job in list")

        # Start processing job button
        start_batch_btn = Button(job_list_btn_frame, text="Start batch", width=12, height=1,
                        command=start_processing_job_list, activebackground='green',
                        activeforeground='white', wraplength=100, font=("Arial", self.font_size))
        start_batch_btn.pack(side=TOP, padx=2, pady=2)
        self.tootips.add(start_batch_btn, "Start processing jobs in list")

        # Suspend on end checkbox
        # suspend_on_joblist_end = tk.BooleanVar(value=False)
        # suspend_on_joblist_end_cb = tk.Checkbutton(
        #     job_list_btn_frame, text='Suspend on end',
        #     variable=suspend_on_joblist_end, onvalue=True, offvalue=False,
        #     width=13)
        # suspend_on_joblist_end_cb.pack(side=TOP, padx=2, pady=2)

        suspend_on_completion_label = Label(job_list_btn_frame, text='Suspend on:', font=("Arial", self.font_size))
        suspend_on_completion_label.pack(side=TOP, anchor=W, padx=2, pady=2)
        suspend_on_completion = StringVar()
        suspend_on_batch_completion_rb = Radiobutton(job_list_btn_frame, text="Job completion",
                                    variable=suspend_on_completion, value='job_completion', font=("Arial", self.font_size))
        suspend_on_batch_completion_rb.pack(side=TOP, anchor=W, padx=2, pady=2)
        self.tootips.add(suspend_on_batch_completion_rb, "Suspend computer when all jobs in list have been processed")
        suspend_on_job_completion_rb = Radiobutton(job_list_btn_frame, text="Batch completion",
                                    variable=suspend_on_completion, value='batch_completion', font=("Arial", self.font_size))
        suspend_on_job_completion_rb.pack(side=TOP, anchor=W, padx=2, pady=2)
        self.tootips.add(suspend_on_batch_completion_rb, "Suspend computer when current job being processed is complete")
        no_suspend_rb = Radiobutton(job_list_btn_frame, text="No suspend",
                                    variable=suspend_on_completion, value='no_suspend', font=("Arial", self.font_size))
        no_suspend_rb.pack(side=TOP, anchor=W, padx=2, pady=2)
        self.tootips.add(suspend_on_batch_completion_rb, "Do not suspend when done")

        suspend_on_completion.set("no_suspend")

        postprocessing_bottom_frame = Frame(video_frame, width=30)
        postprocessing_bottom_frame.grid(row=video_row, column=0)


