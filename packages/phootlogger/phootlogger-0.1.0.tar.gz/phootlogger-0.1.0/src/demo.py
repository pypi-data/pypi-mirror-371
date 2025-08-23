from phootlogger import logger


################################################################################
class Test:
    # --------------------------------------------------------------------------
    def __init__(self):
        self.logger = logger.Logger()

    # --------------------------------------------------------------------------
    def nominal_demo(self):
        """!
        @brief      This test will show what each output is
        """
        self.logger.error("Error message here.")
        self.logger.warning("Warning message here.")
        self.logger.info("Info message here.")

        self.logger.set_debug_mode(False)
        self.logger.debug("This debug message will not show up.")

        self.logger.set_debug_mode(True)
        self.logger.debug("Debug message here.")

    # --------------------------------------------------------------------------
    def hiding_fields_demo(self):
        """!
        @brief
        """
        self.logger.set_debug_mode(True)

        print("\n------------------------------------------")
        print("No fields hidden.")
        print("------------------------------------------")
        self.logger.error("Error message here.")
        self.logger.warning("Warning message here.")
        self.logger.info("Info message here.")
        self.logger.debug("Debug message here.")

        print("\n------------------------------------------")
        print("Timestamps hidden.")
        print("------------------------------------------")
        # Hide section
        self.logger.hide_logs_timestamps(True)
        # Print logs
        self.logger.error("Error message here.")
        self.logger.warning("Warning message here.")
        self.logger.info("Info message here.")
        self.logger.debug("Debug message here.")
        # Show section
        self.logger.hide_logs_timestamps(False)

        print("\n------------------------------------------")
        print("Source ( class/method name ) Hidden.")
        print("------------------------------------------")
        # Hide section
        self.logger.hide_logs_source(True)
        # Print logs
        self.logger.error("Error message here.")
        self.logger.warning("Warning message here.")
        self.logger.info("Info message here.")
        self.logger.debug("Debug message here.")
        # Show section
        self.logger.hide_logs_timestamps(False)

        print("\n------------------------------------------")
        print("Source and Timestamps Hidden.")
        print("------------------------------------------")
        # Hide sections
        self.logger.hide_logs_timestamps(True)
        self.logger.hide_logs_source(True)
        # Print logs
        self.logger.error("Error message here.")
        self.logger.warning("Warning message here.")
        self.logger.info("Info message here.")
        self.logger.debug("Debug message here.")
        # Show sections
        self.logger.hide_logs_timestamps(False)
        self.logger.hide_logs_source(False)

        print("\n------------------------------------------")
        print("Owner Shown.")
        print("------------------------------------------")
        # Show section
        self.logger.hide_logs_owner(False)
        # Print logs
        self.logger.error("Error message here.")
        self.logger.warning("Warning message here.")
        self.logger.info("Info message here.")
        self.logger.debug("Debug message here.")
        # Hide section
        self.logger.hide_logs_owner(True)


    # --------------------------------------------------------------------------
    def deprecation_demo(self):
        """!
        @brief      This test will what deprecation warnings look like
        """
        # Initializing a deprecated class
        msg = logger.messages()

        # Nominal methods still work
        msg.error("error message here.")

        # Deprecated method still works but will see a warning
        msg.system("normal message here.")

    # --------------------------------------------------------------------------
    def quit_script_demo(self):
        """!
        @brief      This Demo will show what quitting the script looks like
        """
        self.logger.quit_script()
        print("This message will not show up.")

# --------------------------------------------------------------------------
def main():
    test = Test()

    print("\n==========================================")
    print("Start of Nominal Demo")
    print("==========================================\n")
    test.nominal_demo()

    print("\n==========================================")
    print("Start of Showing/Hiding Fields Demo")
    print("==========================================\n")
    test.hiding_fields_demo()

    print("\n==========================================")
    print("Start of Deprecation Demo")
    print("==========================================\n")
    test.deprecation_demo()

    print("\n==========================================")
    print("Start of Quit Script Demo")
    print("==========================================\n")
    test.quit_script_demo()

# --------------------------------------------------------------------------
if __name__ == "__main__":
    main()
