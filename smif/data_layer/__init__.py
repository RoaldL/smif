# -*- coding: utf-8 -*-
"""Data access modules for loading system-of-systems model configuration
"""
from abc import ABCMeta, abstractmethod
from logging import getLogger

class API(meta=ABCMeta):

    def __init__(self, connection):

        self.logger = getLogger(__name__)
        self.connection = connection


    def read_sos_model_runs(self):
        """The list of sos model runs

        Returns
        -------
        list
        """
        raise NotImplementedError

    def read_sos_model_run_configuration(self, sos_model_run_name):
        """Read the sos model run configuration

        Arguments
        ---------
        sos_model_run_name : str
            The unique name of the sos model run

        Returns
        -------
        dict
            Contains the number of iterations in the model run results
        """
        raise NotImplementedError

    def read_sos_model_run_results(self, sos_model_run_name):
        """Returns all the sos model run results

        Returns
        -------
        dict
        """
        raise NotImplementedError

    def read_sos_model_run_results_iteration(sos_model_run_name, iter_name):
        """Returns a named iteration from the sos model run results

        Arguments
        ---------
        sos_model_run_name : str
        iter_name : int

        Returns
        -------
        """
        raise NotImplementedError

    def read_sos_models():
        """The list of sos models

        Returns
        -------
        list
        """
        raise NotImplementedError

    def read_sos_model_configuration(name):
        """The sos model configuration

        Arguments
        ---------
        name : str
            Unique name of the sos model

        Returns
        -------
        """
        raise NotImplementedError

    def read_sector_models():
        """The list of sector models

        Returns
        -------
        list
        """
        raise NotImplementedError

    def read_sector_model_configuration(name):
        """The sector model configuration

        Arguments
        ---------
        name : str
            The unique name of the sector model

        Returns
        -------
        """
        raise NotImplementedError

    def read_region_sets():
        """The region set definitions

        Returns
        -------
        list
        """
        raise NotImplementedError

    def read_region_set_data(name):
        """Get region set data

        Returns
        -------
        numpy.ndarray
        """
        raise NotImplementedError

    def read_interval_sets():
        """The list of interval sets

        Returns
        -------
        list
        """
        raise NotImplementedError

    def read_interval_set_data(name):
        """Get interval set data

        Arguments
        ---------
        name : str

        Returns
        -------
        numpy.ndarray
        """
        raise NotImplementedError

    def read_units():
        """Get the user-defined unit definitions for Pint

        Returns
        -------
        dict
        """
        raise NotImplementedError

    def read_scenario_sets():
        """Reads in the scenario sets

        Returns
        -------
        list

        Examples
        --------
        >>>api = smif.data_layer.YamlApi('./')
        >>>api.read_scenario_sets()
        [{'name': 'population', 
          'description': 'The annual change in UK population'}]

        """
        raise NotImplementedError

    def read_scenarios(scenario_set_name):
        """

        Arguments
        ---------
        scenario_set_name : str
            The unique name of the scenario set

        Returns
        -------
        list

        Examples
        --------
        >>>api = smif.data_layer.YamlApi('./')
        >>>api.read_scenarios('population')
        ['High Population (ONS)', 'Low Population (ONS)']
        """
        raise NotImplementedError

    def read_scenario_metadata(scenario_name):
        """

        Arguments
        ---------
        scenario_name : str

        Returns
        -------
        dict
        """
        raise NotImplementedError

    def read_scenario_data(scenario_name):
        """

        Arguments
        ---------
        scenario_name : str

        Returns
        -------
        numpy.ndarray
        """
        raise NotImplementedError

    def read_narrative_sets():
        """

        Returns
        -------
        """
        raise NotImplementedError

    def read_narratives(narrative_set_name):
        """

        Arguments
        ---------
        narrative_set_name : str

        Returns
        -------
        list
        """
        raise NotImplementedError

    def read_narrative_metadata(narrative_name): metadata:
        """

        Arguments
        ---------
        narrative_name : str

        Returns
        -------
        """
        raise NotImplementedError

    def read_narrative_data(narrative_name): data:
        """

        Arguments
        ---------
        narrative_name : str

        Returns
        -------
        """
        raise NotImplementedError

    def write_project(data):
        """

        Arguments
        ---------
        data : dict

        Returns
        -------
        """
        raise NotImplementedError

    def write_scenario_sets(data):
        """Write the scenario sets

        Arguments
        ---------
        data : list

        Examples
        --------
        >>> data = ['population', 'economic growth', 'climate']
        >>> api.write_scenario_sets(data)
        """
        raise NotImplementedError

    def write_scenario_metadata(metadata):
        """Write the scenario metadata

        Arguments
        ---------
        data : dict

        Examples
        --------
        >>> metadata = {'name': 'Low Population (ONS)',
                        'description': 'The Low Forecast for UK population',
                        'scenario_set': 'population',
                        'parameter': 'population_count',
                        'spatial_resolution': 'lad',
                        'temporal_resolution': 'annual',
                        'units': 'people'}
        >>> api.write_scenario_metadata(metadata)
        """
        raise NotImplementedError

    def write_scenario_data(scenario_name, parameter, data):
        """Write the scenario data

        Arguments
        ---------
        scenario_name : str
            The name of the scenario
        parameter : str
            The output parameter to write the data to
        data : numpy.ndarray
            The array of values
        """
        raise NotImplementedError

    def write_narrative_sets(data):
        """

        Arguments
        ---------
        data : dict
        """
        raise NotImplementedError

    def write_narrative_metadata(metadata):
        """

       Arguments
        ---------
        data : dict

        """
        raise NotImplementedError

    def write_narrative_data(narrative_name, data):
        """

        Arguments
        ---------
        data : dict
        """
        raise NotImplementedError

    def write_region_set(data):
        """

        Arguments
        ---------
        data : dict
        """
        raise NotImplementedError

    def write_interval_set(data):
        """

         Arguments
        ---------
        data : dict
        """
        raise NotImplementedError

    def write_units(data):
        """

        Arguments
        ---------
        data : dict
        """
        raise NotImplementedError

    def write_sector_model(data):
        """

        Arguments
        ---------
        data : dict
        """
        raise NotImplementedError

    def write_sos_model(data):
        """

        Arguments
        ---------
        data : dict
        """
        raise NotImplementedError

    def write_sos_model_run(data):
        """

        Arguments
        ---------
        data : dict
        """
        raise NotImplementedError

    def write_sos_model_run_results(sos_model_run_name, iteration_name, data):
        """

        Arguments
        ---------
        data : dict
        """
        raise NotImplementedError