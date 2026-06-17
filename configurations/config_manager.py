import json
import os

from .default_config import DEFAULT_CONFIG


class ConfigManager:
    """
    Handles loading, saving, and managing application settings.

    Settings are persisted in a JSON file while DEFAULT_CONFIG
    acts as the source of truth for default values.
    """

    def __init__(self, settings_file="../configurations/settings.json"):
        """
        Initialize the configuration manager.

        Args:
            settings_file: Path to the JSON settings file.
        """
        self.settings_file = settings_file


    def load(self):
        """
        Load application configuration.

        Behavior:
        1. If the settings file does not exist, create it using
           DEFAULT_CONFIG.
        2. If the file is empty or corrupted, restore defaults.
        3. Merge user-defined settings with DEFAULT_CONFIG so that
           newly added configuration keys are automatically available.
        """

        # Create the settings file on first application startup.
        if not os.path.exists(self.settings_file):

            default_config = DEFAULT_CONFIG.copy()

            self.save(default_config)

            return default_config

        try:

            # Load persisted user settings.
            with open(self.settings_file, "r") as file:
                settings = json.load(file)

        except (json.JSONDecodeError, FileNotFoundError):

            # Treat invalid JSON as an empty configuration and
            # restore defaults below.
            settings = {}

        # Restore defaults if the configuration file is empty.
        if not settings:

            default_config = DEFAULT_CONFIG.copy()

            self.save(default_config)

            return default_config

        # Merge stored settings with defaults to ensure any
        # newly introduced configuration keys are present.
        config = DEFAULT_CONFIG.copy()
        config.update(settings)

        return config


    def save(self, config):
        """
        Persist configuration to disk.
        """

        with open(self.settings_file, "w") as file:
            json.dump(config, file, indent=4)


    def get(self, key):
        """
        Retrieve a configuration value by key.
        """

        config = self.load()

        return config.get(key)


    def set(self, key, value):
        """
        Update a configuration value and persist it.
        """

        config = self.load()

        config[key] = value

        self.save(config)


    def reset(self):
        """
        Reset all settings back to DEFAULT_CONFIG.
        """

        self.save(DEFAULT_CONFIG.copy())


    def reset_key(self, key):
        """
        Reset a single configuration key to its default value.
        """

        config = self.load()

        if key in DEFAULT_CONFIG:

            config[key] = DEFAULT_CONFIG[key]

            self.save(config)