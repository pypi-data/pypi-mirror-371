# sentiebl/config.py

class Config:
    """
    Holds the configuration for the SENTIEBL audit.
    This object is populated at runtime by the arguments passed to the main() function.
    """
    def __init__(self):
        # --- DEFAULTS AND LESS-CHANGED PARAMETERS ---
        # These are settings that can be customized but are less environment-specific.
        
        # Model parameterization strategy
        self.REASONING_LEVEL = "low"  # Options: "low", "medium", "high"
        self.METHOD_CHOICE = "fixed"  # Options: "fixed", "randomized", "gradual"

        # --- ANALYSIS THRESHOLDS ---
        # Thresholds for analysis and saving findings.
        self.LONG_TEXT_THRESHOLD = 100
        self.MIN_SEVERITY_TO_SAVE = 0
        self.MIN_BREADTH_TO_SAVE = 0

        # --- EXECUTION CONTROL ---
        # Controls the duration of the audit.
        self.USE_TEST_DURATION = True
        self.TEST_DURATION = 5 * 60  # Default to a 5-minute test run for safety.

        # --- RUNTIME-SET PARAMETERS (placeholders) ---
        # These core parameters MUST be provided by the user when calling the main() function
        # to ensure the package is universally compatible with any environment.
        self.TEAM_NAME = None
        self.MODEL_NAME = None
        self.OLLAMA_BASE_URL = None
        self.OLLAMA_API_KEY = None
        self.OUTPUT_DIR = None
        self.ENDPOINT = None
        self.HARDWARE = None

# Instantiate the config class. It will be updated by the main() function upon execution.
config = Config()