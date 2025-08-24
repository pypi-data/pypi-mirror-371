""" This module handles application settings using a configuration file.
It provides methods to load, save, and access settings with defaults."""
import configparser
from pathlib import Path

CL_CONFIG_PATH = Path.home() / ".config" / "colossus_ltsm" / "colossus_ltsm.cfg"
CL_DEFAULTS = {
    "scale": "8",
    "cols": "16"
}


class Settings:
    """ Singleton class to manage application settings."""

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.load()

    def load(self):
        """ Load settings from the config file,
        or use defaults if not present."""
        try:
            if CL_CONFIG_PATH.exists():
                self.config.read(CL_CONFIG_PATH)
            if "Display" not in self.config:
                self.config["Display"] = CL_DEFAULTS
            else:
                # Fill in any missing keys
                for key, val in CL_DEFAULTS.items():
                    self.config["Display"].setdefault(key, val)
            # If no file exists, create it with defaults
            if not CL_CONFIG_PATH.exists():
                self.save()
        except Exception as e:
            # fallback
            print(f"[Settings] Error loading config: {e}, using defaults")
            self.config["Display"] = CL_DEFAULTS.copy()

    def save(self):
        """ Save the current settings to the config file."""
        try:
            CL_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with CL_CONFIG_PATH.open("w") as f:
                self.config.write(f)
        except Exception as e:
            print(f"[Settings] Error saving config: {e}")

    def getint(self, section, option, fallback):
        """ Get an integer setting with a fallback value."""
        try:
            return self.config.getint(section, option, fallback=fallback)
        except Exception:
            return fallback


# create settings instance singleton.
settings = Settings()

if __name__ == "__main__":
    print("This is a module, not a standalone script.")
else:
    print("Settings module loaded.")
