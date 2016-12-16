# -*- coding: utf-8 -*-
"""Read and parse the config files for the system-of-systems model
"""
import logging
import os
from . parse_config import ConfigParser

LOGGER = logging.getLogger(__name__)

class SosModelReader(object):
    """Encapsulates the parsing of the system-of-systems configuration

    Arguments
    =========
    config_file_path : str
        A path to the master config file

    """
    def __init__(self, config_file_path):
        LOGGER.info("Getting config file from %s", config_file_path)

        self.config_file_path = config_file_path
        self.config_file_dir = os.path.dirname(config_file_path)

        self.config = None
        self.timesteps = None
        self.sector_model_data = None

    def load(self):
        """Load and check all config
        """
        self.config = self._load_sos_config()
        self.timesteps = self._load_timesteps()
        self.sector_model_data = self._load_sector_model_data()

    @property
    def data(self):
        """Expose all model configuration data
        """
        return {
            "timesteps": self.timesteps,
            "sector_model_config": self.sector_model_data,
            "planning": None
        }

    def _load_sos_config(self):
        """Parse model master config

        - configures run mode
        - points to timesteps file
        - points to shared data files
        - points to sector models and sector model data files
        """
        msg = "Looking for configuration data in {}".format(self.config_file_path)
        LOGGER.info(msg)

        config_parser = ConfigParser(self.config_file_path)
        config_parser.validate_as_modelrun_config()

        return config_parser.data

    def _load_timesteps(self):
        """Parse model timesteps
        """
        file_path = self._get_path_from_config(self.config['timesteps'])
        os.path.exists(file_path)

        config_parser = ConfigParser(file_path)
        config_parser.validate_as_timesteps()

        return config_parser.data

    def _load_sector_model_data(self):
        """Parse list of sector models to run

        Model details include:
        - model name
        - model config directory
        - SectorModel class name to call
        """
        return self.config['sector_models']

    def _load_planning(self):
        """Loads the set of build instructions for planning
        """
        planning_relative_path = self.config['planning']
        planning = []
        for filepath in planning_relative_path:
            parser = ConfigParser(filepath)
            parser.validate_as_pre_specified_planning()
            planning.extend(parser.data)

        return planning

    def _get_path_from_config(self, path):
        """Return an absolute path, given a path provided from a config file
        - if provided path is relative, join it to the config file directory
        """
        if os.path.isabs(path):
            return path
        else:
            return os.path.join(self.config_file_dir, path)