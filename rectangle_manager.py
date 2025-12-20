"""
****************************************************************************************************************
Module rectangle_manager
Collection of high level functions to handle rectangle drawing for cropping and custom template definition 
in AfterScan

Licensed under a MIT LICENSE.

More info in README.md file
****************************************************************************************************************
"""
__author__ = 'Juan Remirez de Esparza'
__copyright__ = "Copyright 2022/26, Juan Remirez de Esparza"
__credits__ = ["Juan Remirez de Esparza"]
__license__ = "MIT"
__module__ = "rectangle_manager"
__version__ = "1.0.0"
__date__ = "2025-12-20"
__version_highlight__ = "rectangle_manager - First version (grouping existing functions from legacy code)"
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
import cv2
import numpy as np
import logging


from constants import THRESHOLD_DEFAULT, CROPPING_WINDOW_TITLE, CUSTOM_TEMPLATE_WINDOW_TITLE
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
                       CROP_AREA_DEFINED)


def load_image_for_rectangle_definition(caller_instance, file):
    # load the image, clone it, and setup the mouse callback function
    ### img = Image.open(file)  # Store original image
    ongoing_action = caller_instance.store.get_state(RECTANGLE_ACTION_ONGOING)
    img = cv2.imread(file, cv2.IMREAD_UNCHANGED)
    if ongoing_action != 'cropping':   # only take left stripe if not for cropping
        img = get_image_left_stripe(img, calculated=False)
    # Rotate image if required
    if perform_rotation.get():
        img = rotate_image(img)
    # Stabilize image to make sure target image matches user visual definition
    if ongoing_action == 'cropping' and perform_stabilization.get():        
        img = stabilize_image(caller_instance.store.get_state(CURRENT_FRAME), img, img)[0]
    elif ongoing_action != 'cropping':
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Apply Otsu's thresholding if requested (for low contrast frames)
        if low_contrast_custom_template.get():
            img_bw = cv2.threshold(img_gray, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        else:
            img_bw = cv2.threshold(img_gray, float(THRESHOLD_DEFAULT), 255, cv2.THRESH_BINARY)[1]
            #img_bw = cv2.Canny(image=img_gray, threshold1=100, threshold2=20)  # Canny Edge Detection
        # Convert back to color so that we cna draw green lines on it
        img = cv2.cvtColor(img_bw, cv2.COLOR_GRAY2BGR)
    return img


def opencv_to_pil(opencv_image):
    """Converts an OpenCV image (NumPy array) to a PIL Image."""
    if len(opencv_image.shape) == 3:  # Color image
        opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(opencv_image)
    return pil_image


def interactive_rectangle_definition_cv2(caller_instance, image):
    ongoing_action = caller_instance.store.get_state(RECTANGLE_ACTION_ONGOING)
    template_manager = caller_instance.store.get_state(TEMPLATE_MANAGER)
    is_demo = caller_instance.store.get_state(IS_DEMO)
    force_small_size = caller_instance.store.get_state(FORCE_SMALL_SIZE)
    force_4_3 = caller_instance.store.get_state(FORCE_4_3)
    force_16_9 = caller_instance.store.get_state(FORCE_16_9)

    window_title = CROPPING_WINDOW_TITLE if ongoing_action == 'cropping' else CUSTOM_TEMPLATE_WINDOW_TITLE
    
    original_image = image
    caller_instance.store.set_state(RECTANGLE_ORIGINAL_IMAGE, np.copy(original_image))
    # Try to find best template
    if ongoing_action != 'cropping' and (template_manager.get_active_position() == (0, 0) or template_manager.get_active_size() == (0, 0)): # If no template defined,set default
        ix = 0
        iy = 0
        x_ = 0
        y_ = 0
        rectangle_top_left = (0,0)
        rectangle_bottom_right = (0,0)
        caller_instance.store.set_state(RECTANGLE_REFRESH_REQUIRED, True)

    # Scale area selection image as required
    work_image = np.copy(original_image)
    img_width = work_image.shape[1]
    img_height = work_image.shape[0]
    win_x = int(img_width * area_select_image_factor)
    win_y = int(img_height * area_select_image_factor)
    line_thickness = int(2/area_select_image_factor)
    caller_instance.store.set_state(RECTANGLE_LINE_THICKNESS, line_thickness)

    # work_image = np.zeros((512,512,3), np.uint8)
    caller_instance.store.set_state(RECTANGLE_BASE_IMAGE, np.copy(work_image))
    window_visible = 1
    cv2.namedWindow(window_title, cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_NORMAL)

    # Capture mouse events
    cv2.setMouseCallback(window_title, draw_rectangle, caller_instance) # Ask CV2 to pass caller instance to callback function
    cv2.imshow(window_title, work_image)
    # Cannot make window wider than required since in Windows the image is expanded tpo cover the full width
    if is_demo or force_small_size:
        cv2.resizeWindow(window_title, round(win_x/2), round(win_y/2))
    else:
        cv2.resizeWindow(window_title, win_x, win_y)
    while 1:
        window_visible = cv2.getWindowProperty(window_title, cv2.WND_PROP_VISIBLE)
        if window_visible <= 0:
            break;
        if caller_instance.store.get_state(RECTANGLE_REFRESH_REQUIRED):
            copy = work_image.copy()
            cv2.rectangle(copy, (ix, iy), (x_, y_), (0, 255, 0), line_thickness)
            cv2.imshow(window_title, copy)
            caller_instance.store.set_state(RECTANGLE_REFRESH_REQUIRED, False)
        k = cv2.waitKeyEx(1) & 0xFF
        inc_ix = 0
        inc_x = 0
        inc_iy = 0
        inc_y = 0
        # waitKey is OS dependent. So we'll check lists of possible values for each direction (arrow keys, num pad, letters)
        if not rectangle_drawing:
            if k in [81, 82, 83, 84, ord('2'), ord('4'), ord('6'), ord('8'), ord('u'), ord('d'), ord('l'), ord('r'),
                     ord('U'), ord('D'), ord('L'), ord('R'), ord('w'), ord('W'), ord('t'), ord('T'),
                     ord('s'), ord('S'), ord('n'), ord('N')]:
                ix = rectangle_top_left[0]
                iy = rectangle_top_left[1]
                x_ = rectangle_bottom_right[0]
                y_ = rectangle_bottom_right[1]
            if k == 13:  # Enter: Confirm selection
                retvalue = True
                break
            elif k in [82, ord('8'), ord('u'), ord('U')]:   # Up
                if iy > 0:
                    inc_iy = -1
                    inc_y = -1
            elif k in [84, ord('2'), ord('d'), ord('D')]:   # Down
                if y_ < img_height:
                    inc_iy = 1
                    inc_y = 1
            elif k in [81, ord('4'), ord('l'), ord('L')]:   # Left
                if ix > 0:
                    inc_ix = -1
                    inc_x = -1
            elif k in [83, ord('6'), ord('r'), ord('R')]:   # Right
                if x_ < img_width:
                    inc_ix = 1
                    inc_x = 1
            elif k in [ord('w'), ord('W')]:  # wider
                if x_ - ix < img_width:
                    if ix > 0:
                        inc_ix = -1
                    if x_ < img_width:
                        inc_x = 1
            elif k in [ord('n'), ord('N')]:  # narrower
                if x_ - ix > 4:
                    inc_ix = 1
                    inc_x = -1
            elif k in [ord('t'), ord('T')]:  # taller
                if y_ - iy < img_height:
                    if iy > 0:
                        inc_iy = -1
                    if y_ < img_height:
                        inc_y = 1
            elif k in [ord('s'), ord('S')]:  # shorter
                if y_ - iy > 4:
                    inc_iy = 1
                    inc_y = -1
            elif k == 27:  # Escape: Restore previous selection, for cropping and template
                if ongoing_action == 'cropping' and crop_area_defined:
                    rectangle_top_left = crop_top_left
                    rectangle_bottom_right = crop_bottom_right
                    retvalue = True
                if ongoing_action != 'cropping' and template_manager.get_active_position() != (0, 0) and template_manager.get_active_size() != (0, 0):
                    rectangle_top_left = template_manager.get_active_position()
                    rectangle_bottom_right = (template_manager.get_active_position()[0] + template_manager.get_active_size()[0],
                                            template_manager.get_active_position()[1] + template_manager.get_active_size()[1])
                    retvalue = True
                break
            elif k == 46 or k == 120 or k == 32:     # Space, X or Supr (inNum keypad) delete selection
                break
            if inc_x != 0 or inc_ix != 0 or inc_y != 0 or inc_iy != 0:
                ix += inc_ix
                x_ += inc_x
                iy += inc_iy
                y_ += inc_y
                w = x_ - ix
                h = y_ - iy
                if ongoing_action == 'cropping' and (force_4_3 or force_16_9) and (inc_x != 0 or inc_ix != 0):
                    y_ = iy + round(w/(1.33 if force_4_3 else 1.78))
                if ongoing_action == 'cropping' and (force_4_3 or force_16_9) and (inc_y != 0 or inc_iy != 0):
                    x_ = ix + round(h*(1.33 if force_4_3 else 1.78))
                rectangle_top_left = (ix, iy)
                rectangle_bottom_right = (x_, y_)
                caller_instance.store.set_state(RECTANGLE_REFRESH_REQUIRED, True)
    #cv2.destroyAllWindows()
    # Remove the mouse callback and destroy the window
    if window_visible:
        cv2.setMouseCallback(window_title, lambda *args: None)
        cv2.destroyWindow(window_title)
        logging.debug("Destroying popup window %s", window_title)
    else:
        logging.debug("Popup window %s closed by user", window_title)
    
    return retvalue


# (Code below to draw a rectangle to select area to crop or find hole,
# adapted from various authors in Stack Overflow)
def draw_rectangle(event, x, y, flags, param):
    caller_instance = param
    ongoing_action = caller_instance.store.get_state(RECTANGLE_ACTION_ONGOING)
    base_image = caller_instance.store.get_state(RECTANGLE_BASE_IMAGE)
    original_image = caller_instance.store.get_state(RECTANGLE_ORIGINAL_IMAGE)
    force_4_3 = caller_instance.store.get_state(FORCE_4_3)
    force_16_9 = caller_instance.store.get_state(FORCE_16_9)
    line_thickness = caller_instance.store.get_state(RECTANGLE_LINE_THICKNESS)


    if event == cv2.EVENT_LBUTTONDOWN:
        if not rectangle_drawing:
            work_image = np.copy(base_image)
            x_, y_ = -10, -10
            ix, iy = -10, -10
            rectangle_drawing = True
            ix, iy = x, y
            x_, y_ = x, y
    elif event == cv2.EVENT_MOUSEMOVE and rectangle_drawing:
        copy = work_image.copy()
        if force_4_3 and ongoing_action == 'cropping':
            w = x - ix
            h = y - iy
            if h * 1.33 > w:
                x = int(h * 1.33) + ix
            else:
                y = int(w / 1.33) + iy
        elif force_16_9 and ongoing_action == 'cropping':
            w = x - ix
            h = y - iy
            if h * 1.78 > w:
                x = int(h * 1.78) + ix
            else:
                y = int(w / 1.78) + iy
        x_, y_ = x, y
        cv2.rectangle(copy, (ix, iy), (x_, y_), (0, 255, 0), line_thickness)
        cv2.imshow(rectangle_window_title, copy)
        caller_instance.store.set_state(RECTANGLE_REFRESH_REQUIRED, True)
    elif event == cv2.EVENT_LBUTTONUP:
        rectangle_drawing = False
        copy = work_image.copy()
        if force_4_3 and ongoing_action == 'cropping':
            w = x - ix
            h = y - iy
            if h * 1.33 > w:
                x = int(h * 1.33) + ix
            else:
                y = int(w / 1.33) + iy
        elif force_16_9 and ongoing_action == 'cropping':
            w = x - ix
            h = y - iy
            if h * 1.78 > w:
                x = int(h * 1.78) + ix
            else:
                y = int(w / 1.78) + iy
        cv2.rectangle(copy, (ix, iy), (x, y), (0, 255, 0), line_thickness)
        # Update global variables with area
        # Need to account for the fact area calculated with 50% reduced image
        rectangle_top_left = (max(0, round(min(ix, x))),
                            max(0, round(min(iy, y))))
        rectangle_bottom_right = (min(original_image.shape[1], round(max(ix, x))),
                                min(original_image.shape[0], round(max(iy, y))))
        logging.debug("Original image: (%i, %i)", original_image.shape[1], original_image.shape[0])
        logging.debug("Selected area: (%i, %i), (%i, %i)",
                      rectangle_top_left[0], rectangle_top_left[1],
                      rectangle_bottom_right[0], rectangle_bottom_right[1])
        caller_instance.store.set_state(RECTANGLE_REFRESH_REQUIRED, True)


def select_rectangle_area(caller_instance):
    ongoing_action = caller_instance.store.get_state(RECTANGLE_ACTION_ONGOING)
    current_frame = caller_instance.store.get_state(CURRENT_FRAME)
    crop_area_defined = caller_instance.store.get_state(CROP_AREA_DEFINED)
    source_dir = caller_instance.store.get_state(SOURCE_DIR)

    if current_frame >= len(source_dir_file_list):
        return False

    retvalue = False
    ix, iy = -1, -1
    x_, y_ = 0, 0
    caller_instance.store.set_state(RECTANGLE_REFRESH_REQUIRED, False)
    if ongoing_action == 'cropping' and crop_area_defined:
        ix, iy = crop_top_left[0], crop_top_left[1]
        x_, y_ = crop_bottom_right[0], crop_bottom_right[1]
        rectangle_top_left = crop_top_left
        rectangle_bottom_right = crop_bottom_right
        caller_instance.store.set_state(RECTANGLE_REFRESH_REQUIRED, True)
    if ongoing_action != 'cropping' and template_manager.get_active_position() != (0, 0) and template_manager.get_active_size() != (0, 0):  # Custom template definition
        rectangle_top_left = template_manager.get_active_position()
        rectangle_bottom_right = (template_manager.get_active_position()[0] + template_manager.get_active_size()[0], template_manager.get_active_position()[1] + template_manager.get_active_size()[1])
        ix, iy = rectangle_top_left[0], rectangle_top_left[1]
        x_, y_ = rectangle_bottom_right[0], rectangle_bottom_right[1]
        caller_instance.store.set_state(RECTANGLE_REFRESH_REQUIRED, True)

    file = source_dir_file_list[current_frame]
    # If HDR mode, pick the lightest frame to select rectangle
    file3 = os.path.join(source_dir, frame_hdr_input_filename_pattern % (current_frame + 1, 2, file_type))
    if os.path.isfile(file3):  # If hdr frames exist, add them
        file = file3

    image = load_image_for_rectangle_definition(file, is_cropping)
    if enable_rectangle_popup:
        retvalue = interactive_rectangle_definition_cv2(image, is_cropping)
    else:
        image = opencv_to_pil(image)
        if not is_cropping:
            ratio = None
        elif force_4_3:
            ratio = 4/3
        elif force_16_9:
            ratio = 16/9
        else:
            ratio = None
        define_rectangle = DefineRectangle(draw_capture_canvas, image, aspect_ratio=ratio)
        define_rectangle.draw_initial_rectangle(rectangle_top_left[0], rectangle_top_left[1], rectangle_bottom_right[0], rectangle_bottom_right[1])
        rectangle_dims = define_rectangle.wait_for_enter()
        if rectangle_dims:
            x1, y1, x2, y2 = rectangle_dims

        define_rectangle.destroy()

        x1 = max(x1, 0)
        y1 = max(y1, 0)
        rectangle_top_left = (x1, y1)
        rectangle_bottom_right = (x2, y2)
        retvalue = True

    return retvalue


def select_cropping_area(caller_instance):
    caller_instance.store.set_state(RECTANGLE_ACTION_ONGOING, 'cropping')

    # Disable all buttons in main window
    widget_status_update(DISABLED,0)
    FrameSync_Viewer_popup_update_widgets(DISABLED)

    win.update()

    rectangle_window_title = crop_window_title

    if select_rectangle_area(caller_instance):
        crop_area_defined = True
        widget_status_update(NORMAL, 0)
        FrameSync_Viewer_popup_update_widgets(NORMAL)
        crop_top_left = rectangle_top_left
        crop_bottom_right = rectangle_bottom_right
        logging.debug("Crop area: (%i,%i) - (%i, %i)", crop_top_left[0],
                      crop_top_left[1], crop_bottom_right[0], crop_bottom_right[1])
    else:
        crop_area_defined = False
        widget_status_update(DISABLED, 0)
        FrameSync_Viewer_popup_update_widgets(DISABLED)
        perform_cropping.set(False)
        perform_cropping.set(False)
        generate_video_checkbox.config(state=NORMAL if ffmpeg_installed
                                       else DISABLED)
        crop_top_left = (0, 0)
        crop_bottom_right = (0, 0)

    config_manager.set_crop_rectangle((crop_top_left, crop_bottom_right))
    perform_cropping_checkbox.config(state=NORMAL if crop_area_defined
                                     else DISABLED)

    # Enable all buttons in main window
    widget_status_update(NORMAL, 0)
    FrameSync_Viewer_popup_update_widgets(NORMAL)

    if ui_init_done:
        win.after(5, scale_display_update, False)
    win.update()


def select_custom_template(caller_instance):
    caller_instane.store.set_state(RECTANGLE_ACTION_ONGOING, 'custom_template')

    # First, define custom template name and filename in case it needs to be deleted
    # Template Name = Last folder in the path, plus Frame From,  Frame to it not encoding all
    template_name = f"{os.path.split(source_dir)[-1]}"
    # Set filename
    template_filename = f"Pattern.custom.{template_name}.jpg"
    full_path_template_filename = os.path.join(resources_dir, template_filename)

    if template_manager.get_active_type() == 'custom':
        if os.path.isfile(template_manager.get_active_filename()):
            os.remove(template_manager.get_active_filename())
        if not set_film_type():
            return
    else:
        if len(source_dir_file_list) <= 0:
            tk.messagebox.showwarning(
                "No frame set loaded",
                "A set of frames is required before a custom template might be defined."
                "Please select a source folder before proceeding.")
            return
        # Disable all buttons in main window
        widget_status_update(DISABLED, 0)
        FrameSync_Viewer_popup_update_widgets(DISABLED)

        win.update()

        rectangle_window_title = custom_template_title

        if select_rectangle_area(caller_instance) and current_frame < len(source_dir_file_list):
            # Extract template from image
            file = source_dir_file_list[current_frame]
            file3 = os.path.join(source_dir, frame_hdr_input_filename_pattern % (current_frame + 1, 2, file_type))
            if os.path.isfile(file3):  # If hdr frames exist, add them
                file = file3
            full_img = cv2.imread(file, cv2.IMREAD_UNCHANGED)
            # test to stabilize custom template itself using simple algorithm (commented as it affects custom template definition)
            #move_x, move_y = calculate_frame_displacement_simple(current_frame, img)
            #img = shift_image(img, img.shape[1], img.shape[0], move_x, move_y)

            img = crop_image(full_img, rectangle_top_left, rectangle_bottom_right)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Apply Otsu's thresholding if requested (for low contrast frames)
            if low_contrast_custom_template.get():
                img_final = cv2.threshold(img_gray, 100, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            else:
                # img_bw = cv2.threshold(img_gray, float(stabilization_threshold), 255, cv2.THRESH_TRUNC | cv2.THRESH_TRIANGLE)[1]
                img_bw = cv2.threshold(img_gray, float(stabilization_threshold_default), 255, cv2.THRESH_BINARY)[1]
                # img_edges = cv2.Canny(image=img_bw, threshold1=100, threshold2=20)  # Canny Edge Detection
                img_final = img_bw

            # Write template to disk
            config_manager.set_custom_template_filename(full_path_template_filename)
            cv2.imwrite(full_path_template_filename, img_final)

            # Add template to list
            template_manager.add(template_name, full_path_template_filename, 'custom', rectangle_top_left)   # size and template automatically refreshed upon addition
            logging.debug(f"Template top left-size: {template_manager.get_active_position()} - {template_manager.get_active_size()}")
            widget_status_update(NORMAL, 0)
            FrameSync_Viewer_popup_update_widgets(NORMAL)
            custom_stabilization_btn.config(relief=SUNKEN)

            config_manager.set_custom_template_expected_pos(template_manager.get_active_position())
            config_manager.set_custom_template_name(template_manager.get_active_name())

            define_template_search_area(full_img)  # Adjust hole search area to new template

            if enable_rectangle_popup:
                # Display saved template for information
                custom_template_window_title = "Captured custom template. Press any key to continue."
                win_x = int(img_final.shape[1] * area_select_image_factor)
                win_y = int(img_final.shape[0] * area_select_image_factor)
                cv2.namedWindow(custom_template_window_title, flags=cv2.WINDOW_GUI_NORMAL)
                cv2.imshow(custom_template_window_title, img_final)

                # Cannot force window to be wider than required since in Windows image is expanded as well
                cv2.resizeWindow(custom_template_window_title, round(win_x / 2), round(win_y / 2))
                cv2.moveWindow(custom_template_window_title, win.winfo_x() + 100, win.winfo_y() + 30)
                window_visible = True
                while cv2.waitKeyEx(100) == -1:
                    window_visible = cv2.getWindowProperty(custom_template_window_title, cv2.WND_PROP_VISIBLE)
                    if window_visible <= 0:
                        break
                if window_visible > 0:
                    cv2.destroyAllWindows()
        else:
            if os.path.isfile(full_path_template_filename):  # Delete Template if it exist
                os.remove(full_path_template_filename)
                if not set_film_type():
                    return
            custom_stabilization_btn.config(relief=RAISED)
            widget_status_update(DISABLED, 0)
            FrameSync_Viewer_popup_update_widgets(DISABLED)

    config_manager.set_custom_template_defined(True if template_manager.get_active_type() == 'custom' else False)
    debug_template_refresh_template()

    # Enable all buttons in main window
    widget_status_update(NORMAL, 0)
    FrameSync_Viewer_popup_update_widgets(NORMAL)

    win.update()


