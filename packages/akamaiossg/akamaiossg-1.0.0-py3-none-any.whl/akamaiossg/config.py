# sentiebl/config.py

class Config:
    """
    Holds the configuration for the SENTIEBL audit.
    This object is populated at runtime by the arguments passed to the main() function.
    """
    def __init__(self):
        # --- RUNTIME-SET PARAMETERS (placeholders) ---
        # These core parameters MUST be provided by the user when calling the main() function
        # to ensure the package is universally compatible with any environment.
        
        # Model parameterization strategy
        self.REASONING_LEVEL = None  # Options: "low", "medium", "high"
        self.METHOD_CHOICE = None  # Options: "fixed", "randomized", "gradual"

        # Analysis thresholds
        self.LONG_TEXT_THRESHOLD = None
        self.MIN_SEVERITY_TO_SAVE = None
        self.MIN_BREADTH_TO_SAVE = None

        # Execution control
        self.USE_TEST_DURATION = None  # Boolean type
        self.TEST_DURATION = None  # In seconds

        # Core parameters
        self.TEAM_NAME = None
        self.MODEL_NAME = None
        self.OLLAMA_BASE_URL = None
        self.OLLAMA_API_KEY = None
        self.OUTPUT_DIR = None
        self.ENDPOINT = None
        self.HARDWARE = None

# Instantiate the config class. It will be updated by the main() function upon execution.
config = Config()