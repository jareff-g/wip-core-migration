"""
****************************************************************************************************************
Class RefreshStoreFromConfig
Refresh shared data store with the values in the provided project configuration.
In AfterScan legacy code, this was done by 'def 'decode_project_config'.
Original code was not only reading the config into global variables, it was also:
- Updating the UI. With the new code that no longer makes sense, so after the shared 
  store is up to date, a bus event would have to be fired for the UI to update itself.
- Reading the frame list on the fly. This does not belong here, to be done elsewhere

Another Class similar to this one will be needed: RefreshUiFromStore.

Licensed under a MIT LICENSE.

More info in README.md file
****************************************************************************************************************
"""
__author__ = 'Juan Remirez de Esparza'
__copyright__ = "Copyright 2022/24, Juan Remirez de Esparza"
__credits__ = ["Juan Remirez de Esparza"]
__license__ = "MIT"
__module__ = "refresh_store_from_config"
__version__ = "1.0.0"
__date__ = "2025-12-16"
__version_highlight__ = "RefreshStoreFromConfig - First version"
__maintainer__ = "Juan Remirez de Esparza"
__email__ = "jremirez@hotmail.com"
__status__ = "Development"

import os
import logging
from configuration_manager import ProjectConfigEntry
from application_services import AppStateStore
# Shared Store constants
from constants import (PROJECT_NAME, CURRENT_FRAME, SOURCE_DIR, 
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
                       PRECISE_TEMPLATE_MATCH)


'''We do not really need a class here. Converting to static function
class RefreshStoreFromConfig:
    """
    Manages the synchronization and refreshing of an internal store 
    based on external configuration settings.
    """
    def __init__(self, config_source: ProjectConfigEntry, store_target: AppStateStore):
        """
        Initializes the service with a configuration source.

        Args:
            config_source (MockConfig): An object providing configuration settings.
        """
        self.config = config_source
        self.store = store_target
        self.is_initialized = False

    def refresh_store(self):
        """
        Public method to refresh the internal store state using the configuration.
        This simulates the core functionality of updating state.
        """
        logging.debug("--- Refreshing Store State from Configuration ---")
        try:
            new_data = self._load_settings()
            
            # Update the internal store
            self.store.update(new_data)
            self.is_initialized = True
            
            logging.debug("Store successfully updated.")
            
        except Exception as e:
            # Catch any issues during config reading or parsing
            logging.debug(f"ERROR: Could not refresh store from configuration: {e}")


    def _load_settings(self):
'''
def refresh_store_from_config(store_target: AppStateStore, config_source: ProjectConfigEntry):
        settings = {}
        config = config_source

        source_dir = config.get_project_source_dir()
        if source_dir != '':
            project_name = os.path.split(source_dir)[-1].replace(',', ';')
            # If directory in configuration does not exist, set current working dir
            if not os.path.isdir(source_dir):
                source_dir = ""
                project_name = "No Project"
            else:
                # TODO: Read frame list - get_source_dir_file_list()
                pass
        settings[SOURCE_DIR] = source_dir
        settings[PROJECT_NAME] = project_name

        target_dir = config.get_target_dir()
        if target_dir != '':
            # If directory in configuration does not exist, set current working dir
            if not os.path.isdir(target_dir):
                target_dir = ""
            else:
                # TODO: Read frame list - get_target_dir_file_list()
                pass
        settings[TARGET_DIR] = target_dir

        video_target_dir = config.get_video_target_dir()
        settings[VIDEO_TARGET_DIR] = video_target_dir

        if not self.store.get_state(BATCH_JOB_RUNNING): # only if project loaded by user, otherwise it alters start encoding frame in batch mode
            current_frame = 0
            current_frame = config.get_current_frame()
            settings[CURRENT_FRAME] = current_frame

        encode_all_frames = config.get_encode_all_frames()
        settings[ENCODE_ALL_FRAMES] = encode_all_frames

        frame_from = config.get_frame_from()
        settings[FRAME_FROM] = frame_from

        frame_to = config.get_frame_to()
        settings[FRAME_TO] = frame_to

        if frame_from >= 0 and frame_to >= 0:
            frames_to_encode = frame_to - frame_from
        else:
            frames_to_encode = 0
        settings[FRAMES_TO_ENCODE] = frames_to_encode

        film_type = config.get_film_type()
        settings[FILM_TYPE] = film_type

        rotation_angle = config.get_rotation_angle()
        settings[ROTATION_ANGLE] = rotation_angle

        stabilization_threshold = config.get_stabilization_threshold()
        settings[STABILIZATION_THRESHOLD] = stabilization_threshold

        low_contrast_custom_template = config.get_low_contrast_custom_template()
        settings[LOW_CONTRAST_CUSTOM_TEMPLATE] = low_contrast_custom_template
        

        extended_stabilization = config.get_extended_stabilization()
        settings[EXTENDED_STABILIZATION] = extended_stabilization

        custom_template_defined = config.get_custom_template_defined()
        settings[CUSTOM_TEMPLATE_DEFINED] = custom_template_defined

        if custom_template_defined:
            template_name = config.get_custom_template_name()
            settings[CUSTOM_TEMPLATE_NAME] = template_name

            custom_template_expected_pos = config.get_custom_template_expected_pos()
            settings[CUSTOM_TEMPLATE_EXPECTED_POS] = custom_template_expected_pos

            full_path_template_filename = config.get_custom_template_filename()
            settings[CUSTOM_TEMPLATE_FILENAME] = full_path_template_filename

            if not os.path.exists(full_path_template_filename):
                logging.debug(f"Custom template in project {template_name} does not exist ({full_path_template_filename})")
                """"
                tk.messagebox.showwarning(
                    "Template in project invalid",
                    f"The custom template saved for project {template_name} is invalid."
                    "Please redefine custom template for this project.")
                """
                settings[CUSTOM_TEMPLATE_FILENAME] = ''
                settings[CUSTOM_TEMPLATE_DEFINED] = False
            else:
                logging.debug(f"Adding custom template {template_name} from configuration to template list (filename {full_path_template_filename})")

        perform_cropping = config.get_perform_cropping()
        settings[PERFORM_CROPPING] = perform_cropping

        perform_denoise = config.get_perform_denoise()
        settings[PERFORM_DENOISE] = perform_denoise

        perform_sharpness = config.get_perform_sharpness()
        settings[PERFORM_SHARPNESS] = perform_sharpness

        perform_gamma_correction = config.get_perform_gamma_correction()
        settings[PERFORM_GAMMA_CORRECTION] = perform_gamma_correction

        gamma_correction_value = config.get_gamma_correction_value()
        settings[GAMMA_CORRECTION_VALUE] = gamma_correction_value

        crop_rectangle = config.get_crop_rectangle()
        settings[CROP_RECTANGLE] = crop_rectangle   # Top-left = crop_rectangle[0], bottom-right = crop_rectangle[1]

        force_4_3 = config.get_force_4_3()
        settings[FORCE_4_3] = force_4_3

        force_16_9 = False if force_4_3 else config.get_force_16_9()
        settings[FORCE_16_9] = force_16_9

        frame_fill_type = config.get_frame_fill_type()
        settings[FRAME_FILL_TYPE] = frame_fill_type

        generate_video = config.get_generate_video()
        settings[GENERATE_VIDEO] = generate_video

        video_filename = config.get_video_filename()
        settings[VIDEO_FILENAME] = video_filename

        video_title = config.get_video_title()
        settings[VIDEO_TITLE] = video_title

        # Snake case from the start
        skip_frame_regeneration = config.get_skip_frame_regeneration()
        settings[SKIP_FRAME_REGENERATION] = skip_frame_regeneration

        ffmpeg_preset = config.get_ffmpeg_preset()
        settings[FFMPEG_PRESET] = ffmpeg_preset

        perform_stabilization = config.get_perform_stabilization()
        settings[PERFORM_STABILIZATION] = perform_stabilization

        stabilization_shift_y = config.get_stabilization_shift_y()
        settings[STABILIZATION_SHIFT_Y] = stabilization_shift_y

        stabilization_shift_x = config.get_stabilization_shift_x()
        settings[STABILIZATION_SHIFT_X] = stabilization_shift_x

        perform_rotation = config.get_perform_rotation()
        settings[PERFORM_ROTATION] = perform_rotation

        video_fps = config.get_video_fps()
        settings[VIDEO_FPS] = video_fps

        video_resolution = config.get_video_resolution()
        settings[VIDEO_RESOLUTION] = video_resolution

        current_bad_frame_index = config.get_current_bad_frame_index()
        settings[CURRENT_BAD_FRAME_INDEX] = current_bad_frame_index

        user_defined_left_stripe_width_proportion = config.get_user_defined_left_stripe_width_proportion()
        settings[USER_DEFINED_LEFT_STRIPE_WIDTH_PROPORTION] = user_defined_left_stripe_width_proportion
        # Don't really need to retrieve the config date, this is intended only to be written. But anyhow...

        precise_template_match = config.get_precise_template_match()
        settings[PRECISE_TEMPLATE_MATCH] = precise_template_match

        """ This code was there in the old decode_project_config. It might need to be put elsewhere.
        if len(source_dir_file_list) > 0:
            adjust_dimensions_based_on_frame()

        widget_status_update(NORMAL)
        FrameSync_Viewer_popup_update_widgets(NORMAL)

        load_bad_frame_list()

        win.update()
        """
        # The structure is built incrementally and returned
        ### Exchange next two lines if moving back to class
        ### return settings
        store_target.update(settings)


