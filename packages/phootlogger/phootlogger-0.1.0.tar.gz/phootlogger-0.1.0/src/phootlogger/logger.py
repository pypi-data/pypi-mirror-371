################################################################################
#
# Filename: logger.py
#
# Purpose:  Class create a logger and use generally across many python projects
#
################################################################################

# External imports
from typing import Tuple
import datetime
import inspect
import os
import re

################################################################################
class Logger:
    """!
    @brief      This class can be instantiated in a python project and report
                consistent logs with timestamps, function names, and classes
    """
    # --------------------------------------------------------------------------
    def __init__(self):
        # Set up default log format
        self.mb = MessageBuilder()
        self.mb.set_hide_source(False)
        self.mb.set_hide_timestamps(False)
        self.mb.set_hide_owner(True)

        # Setting up logger flags
        self._debug_mode = False

        # Setup owner file
        self.set_owner_filepath()

    # --------------------------------------------------------------------------
    def set_owner_filepath(self) -> None:
        """!
        @brief      Determines the file path of where this logger was instantiated.
                    Values is set internally to this class
        """
        # Determine the file that initialized the logger
        frame_info = inspect.stack()[1]
        filepath = frame_info.filename
        self.owner_filepath = os.path.abspath(filepath)

    # --------------------------------------------------------------------------
    def info(self, msg) -> None:
        """
        @brief      Prints out Informational message to the user

        @param      msg (string): Message to be printed out to user
        """
        # Get time stamp as soon as this is called
        ts = self._get_time_stamp()

        # Try to print the messages
        if not self._print_user_message("INFO", msg, ts):
            print("Issue with INFO log.")
            self.quit_script()

    # --------------------------------------------------------------------------
    def warning(self, msg) -> None:
        """!
        @brief      Prints out warning message to the user

        @param      msg (string): Message to be printed out to user
        """
        # Get time stamp as soon as this is called
        ts = self._get_time_stamp()

        if not self._print_user_message("WARNING", msg, ts):
            print("Issue with WARNING log.")
            self.quit_script()

    # --------------------------------------------------------------------------
    def error(self, msg) -> None:
        """
        @brief      Prints out Error message to the user

        @param      msg (string): Message to be printed out to user
        """
        # Get time stamp as soon as this is called
        ts = self._get_time_stamp()

        if not self._print_user_message("ERROR", msg, ts):
            print("Issue with ERROR log.")
            self.quit_script()

    # --------------------------------------------------------------------------
    def debug(self, msg) -> None:
        """!
        @brief      Prints out debug message to the user. This is only shown
                    when the logger is set to debug mode

        @param      msg (string): Message to be printed out to user
        """
        if self._debug_mode:
            # Get time stamp as soon as this is called
            ts = self._get_time_stamp()

            if not self._print_user_message("DEBUG", msg, ts):
                print("Issue with DEBUG log.")
                self.quit_script()

    # --------------------------------------------------------------------------
    def quit_script(self) -> None:
        """!
        @brief  Will print a message and ungracefully exit with 1
        """
        print("Exiting script.")
        exit(1)

    # --------------------------------------------------------------------------
    def set_debug_mode(self, debug_mode=True) -> None:
        """!
        @brief  When enabled, will print out debugging messages

        @param  debug_mode (bool): State to set the debug mode to. ( True = Debug, False = No debug )
        """
        self._debug_mode = debug_mode

    # --------------------------------------------------------------------------
    def hide_logs_timestamps(self, hide_timestamps=False) -> None:
        """!
        @brief  Will show or hide the timestamps printed out based on this state
        """
        self.mb.set_hide_timestamps(hide_timestamps)

    # --------------------------------------------------------------------------
    def hide_logs_source(self, hide_source=False) -> None:
        """!
        @brief  Will show or hide the source ( class / method names) printed out
                based on this state
        """
        self.mb.set_hide_source(hide_source)

    # --------------------------------------------------------------------------
    def hide_logs_owner(self, hide_owner=True) -> None:
        """!
        @brief  Will show or hide the file that owns the log instantiation,
                printed out based on this state
        """
        self.mb.set_hide_owner(hide_owner)

    # --------------------------------------------------------------------------
    def _get_caller_context(self) -> Tuple[str, str]:
        """!
        @brief      Extract the calling class and method name

        @returns    Tuple:  class_name(str):  Name of the class calling the log
                            method_name(str): Name of the method calling the log
        """
        frame = inspect.currentframe()
        logger_class = self.__class__

        # Track frames back to the caller
        while frame:
            frame = frame.f_back
            if not frame:
                break

            # Skip frames from within the logger class
            if 'self' in frame.f_locals:
                caller_self = frame.f_locals['self']
                if isinstance(caller_self, logger_class):
                    continue
                class_name = caller_self.__class__.__name__
            else:
                class_name = None

            method_name = frame.f_code.co_name
            return class_name, method_name

        # Print a warning
        if not method_name or not class_name:
            print("WARNING. Method name or Class name not found from logger.")

        return class_name, method_name

    # --------------------------------------------------------------------------
    def _print_user_message(self, message_type: str, message_to_user: str, time_stamp: str) -> bool:
        """!
        @brief      Prints out the message after everything is set

        @param      message_type (str): Type of message to be displayed.
                                        i.e. "ERROR", "INFO", "DEBUG", etc.
        @param      message_to_user (str): Message to be directly displayed to the user
        @param      time_stamp (str): Time stamp of the message

        @retval     True:   Always
        @retval     False:  Never
        """
        # Get the calling methods
        class_name, method_name = self._get_caller_context()

        # Build the string
        formatted_message = self.mb.build_log_string(time_stamp=time_stamp,
                                                     owner=self.owner_filepath,
                                                     class_name=class_name,
                                                     method_name=method_name,
                                                     message_type=message_type,
                                                     message_to_user=message_to_user)

        print(formatted_message)
        return True

    # --------------------------------------------------------------------------
    def _get_time_stamp(self) -> str:
        """!
        @brief      Gets the current time

        @returns    (str): Current time in the format: 'YYYY-mm-DD HH:MM:SS.ssssss'
        """
        current_time = str(datetime.datetime.now())
        return current_time


    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!! START OF DEPRECATION WARNING SECTION
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # --------------------------------------------------------------------------
    def _deprecation_warning(self, immediate=False):
        """!
        @brief      Notify users this method will be deprecated soon.
        """
        # Pass the soon or immediate deprecation
        time = "will soon"
        if immediate:
            time = "has been"

        # Determine the method and print out
        caller = inspect.stack()[1].function
        print(f"WARNING. The method '{caller}' {time} DEPRECATED.")

    # --------------------------------------------------------------------------
    def system(self, msg):
        self._deprecation_warning()
        self.info(msg)

    # --------------------------------------------------------------------------
    def printUserMessage(self, file_name, func_name, msg_type, msg_to_user) -> str:
        self._deprecation_warning()
        #  No longer used: file_name, func_name
        self._print_user_message(self, msg_type, msg_to_user)

    # --------------------------------------------------------------------------
    def getFileNameAndFunction(self):
        self._deprecation_warning(immediate=True)
        # self._get_file_name_and_function()

    # --------------------------------------------------------------------------
    def getMessageType(self):
        self._deprecation_warning(immediate=True)
        # self._get_message_type(self)

    # --------------------------------------------------------------------------
    def setMessageType(self, message_type) -> bool:
        self._deprecation_warning(immediate=True)
        # self._set_message_type(self, message_type)

    # --------------------------------------------------------------------------
    def setUserMessage(self, file_name, func_name, message) -> bool:
        self._deprecation_warning(immediate=True)
        # self._set_user_message(self, file_name, func_name, message)

    # --------------------------------------------------------------------------
    def getUserMessage(self) -> str:
        self._deprecation_warning(immediate=True)
        # self._get_user_message(self)

    # --------------------------------------------------------------------------
    def setFileName(self, name) -> None:
        self._deprecation_warning(immediate=True)
        # self._set_file_name(self, name)

    # --------------------------------------------------------------------------
    def getFileName(self) -> str:
        self._deprecation_warning(immediate=True)
        # self._get_file_name(self)

    # --------------------------------------------------------------------------
    def getTimeStamp(self) -> str:
        self._deprecation_warning()
        self._get_time_stamp(self)


class messages(Logger):
    def __init__(self):
        print("*****************************************************************")
        print("* WARNING:")
        print("* \tThis class has been DEPRECATED. It's name has been changed to \"Logger\".")
        print("* \tThis specific instance will soon no longer work.")
        print("*****************************************************************")
        super().__init__()

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!! END OF DEPRECATION WARNING SECTION
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

################################################################################
class MessageBuilder:
    """!
    @brief  This class is to extract the messiness of building the logs. It
            does all the formatting of the string to be printed out
    """
    # --------------------------------------------------------------------------
    def __init__(self):
        # Flags to decide what to display
        self.hide_source = False
        self.hide_timestamps = False

        # Meant to be extra info, but will look messy
        self.hide_owner = True

    # --------------------------------------------------------------------------
    def set_hide_source(self, hide_source=False):
        """!
        @brief  Will show or hide the timestamps printed out based on this state
        """
        self.hide_source = hide_source

    # --------------------------------------------------------------------------
    def set_hide_timestamps(self, hide_timestamps=False):
        """!
        @brief  Will show or hide the source ( class / method names) printed out
                based on this state
        """
        self.hide_timestamps = hide_timestamps

    # --------------------------------------------------------------------------
    def set_hide_owner(self, hide_owner=True):
        """!
        @brief  Will show or hide the file that owns the log instantiation,
                printed out based on this state
        """
        self.hide_owner = hide_owner

    # --------------------------------------------------------------------------
    def build_log_string(self,
                         time_stamp: str,
                         owner: str,
                         class_name: str,
                         method_name: str,
                         message_type: str,
                         message_to_user ) -> str:
        """!
        @brief  Builds the string to be output to the terminal

        @param  time_stamp (str): time stamp of when the log was called
        @param  owner (str): Name of the file that instantiated the logger
        @param  class_name (str): Name of the class calling the log method
        @param  method_name (str): Name of the method calling the log method
        @param  message_type (str): type of message. i.e. ERROR, INFO, DEBUG, etc.
        @param  message_to_user (str): main message to be shown to the user

        @returns Formatted string to be printed out. Example
        """
        # String will look like:
        #   time_stamp                     owner          class_name.method_name       message_type message_to_user
        #   <YYYY-MM-DD HH:MM:SS.ssssss> : <owner_file> : <class_name>:<method_name> : <TYPE> : <message>

        # Timestamp: 22 characters
        f_time_stamp = f"{time_stamp:<25}"

        # Message Type: 8 characters
        f_message_type = f"[{message_type}]"
        f_message_type = f"{f_message_type:<9}"

        # Class / Method Name: 40 characters
        f_class_name = class_name
        f_method_name = method_name
        f_source = f"{f_class_name}.{f_method_name}"
        f_source = f"{f_source:<25}"

        # Owner of the logger
        f_owner = f"{owner:<12}"

        # Format message
        f_message_to_user = re.sub(r"\n", "\n\t\t", message_to_user)

        # Build final string
        final_string = ""

        # If user wants to show time stamp
        if not self.hide_timestamps:
            final_string += f"{f_time_stamp} : "

        # If user wants to show owner of the logger
        if not self.hide_owner:
            final_string += f"{f_owner} : "

        # If user wants to show source
        if not self.hide_source:
            final_string += f"{f_source} : "

        # Bare minimum logs show error type and message
        final_string += f"{f_message_type} : {f_message_to_user}"

        return final_string
