"""Test SectorModel and SectorModelBuilder
"""
from copy import copy
from unittest.mock import Mock

import numpy as np
from pytest import raises
from smif.metadata import Metadata, MetadataSet
from smif.model.scenario_model import ScenarioModel
from smif.model.sector_model import SectorModel, SectorModelBuilder
from smif.parameters import ParameterList


class EmptySectorModel(SectorModel):

    def initialise(self, initial_conditions):
        pass

    def simulate(self, timestep, data=None):
        return {}

    def extract_obj(self, results):
        return 0


class TestCompositeSectorModel():

    def test_add_input(self):

        model = EmptySectorModel('test_model')
        model.add_input('input_name', [], [], 'units')

        inputs = model.model_inputs

        assert inputs.names == ['input_name']
        assert inputs.units == ['units']

        assert inputs['input_name'] == Metadata('input_name', [], [], 'units')

    def test_add_output(self):

        model = EmptySectorModel('test_model')
        model.add_output('output_name', Mock(), Mock(), 'units')

        outputs = model.model_outputs

        assert outputs.names == ['output_name']
        assert outputs.units == ['units']

    def test_run_sector_model(self):

        model = EmptySectorModel('test_model')
        model.add_input('input_name', [], [], 'units')
        data = {'input_name': [0]}
        actual = model.simulate(2010, data)
        assert actual == {}

    def test_scenario_dependencies(self):

        scenario_model = ScenarioModel('test_scenario')
        scenario_model.add_output('scenario_output', Mock(), Mock(), 'units')
        data = np.array([[[120.23]]])
        timesteps = [2010]
        scenario_model.add_data(data, timesteps)

        model = EmptySectorModel('test_model')
        model.add_input('input_name', Mock(), Mock(), 'units')
        model.add_dependency(scenario_model, 'scenario_output', 'input_name')

        assert 'input_name' in model.deps
        assert model.get_scenario_data('input_name') == data


class TestSectorModelBuilder():

    def test_add_inputs(self, setup_project_folder):

        model_path = str(setup_project_folder.join('models', 'water_supply',
                                                   '__init__.py'))

        builder = SectorModelBuilder('test')
        builder.load_model(model_path, 'WaterSupplySectorModel')

        inputs = [{'name': 'an_input',
                   'spatial_resolution': 'LSOA',
                   'temporal_resolution': 'annual',
                   'units': 'tonnes'}]

        builder.add_inputs(inputs)

        assert 'an_input' in builder._sector_model.model_inputs.names

    def test_sector_model_builder(self, setup_project_folder):
        model_path = str(setup_project_folder.join('models', 'water_supply',
                                                   '__init__.py'))

        register = Mock()
        register.get_entry = Mock(return_value='a_resolution_set')

        registers = {'regions': register,
                     'intervals': register}

        builder = SectorModelBuilder('water_supply', registers)
        builder.load_model(model_path, 'WaterSupplySectorModel')

        assets = [
            {
                'name': 'water_asset_a',
                'type': 'water_pump',
                'attributes': {
                    'capital_cost': 1000,
                    'economic_lifetime': 25,
                    'operational_lifetime': 25
                }
            }
        ]
        builder.add_interventions(assets)

        # builder.add_inputs(inputs)
        # builder.add_outputs(outputs)

        model = builder.finish()
        assert isinstance(model, SectorModel)

        assert model.name == 'water_supply'
        assert model.intervention_names == ['water_asset_a']
        assert model.interventions == assets

    def test_path_not_found(self):
        builder = SectorModelBuilder('water_supply', Mock())
        with raises(FileNotFoundError) as ex:
            builder.load_model('/fictional/path/to/model.py', 'WaterSupplySectorModel')
        msg = "Cannot find '/fictional/path/to/model.py' for the 'water_supply' model"
        assert msg in str(ex.value)


class TestInputs:

    def test_add_no_inputs(self, setup_project_folder):
        model_path = str(setup_project_folder.join('models', 'water_supply', '__init__.py'))
        registers = {'regions': Mock(),
                     'intervals': Mock()}

        builder = SectorModelBuilder('water_supply_test', registers)
        builder.load_model(model_path, 'WaterSupplySectorModel')
        builder.add_inputs(None)
        sector_model = builder.finish()
        assert isinstance(sector_model.model_inputs, MetadataSet)
        actual_inputs = sector_model.model_inputs.names
        assert actual_inputs == []


class TestSectorModel(object):

    def test_interventions_names(self):
        assets = [
            {'name': 'water_asset_a'},
            {'name': 'water_asset_b'},
            {'name': 'water_asset_c'}
        ]
        model = EmptySectorModel('test_model')
        model.interventions = assets

        intervention_names = model.intervention_names

        assert len(intervention_names) == 3
        assert 'water_asset_a' in intervention_names
        assert 'water_asset_b' in intervention_names
        assert 'water_asset_c' in intervention_names

    def test_interventions(self):
        interventions = [
            {
                'name': 'water_asset_a',
                'capital_cost': 1000,
                'economic_lifetime': 25,
                'operational_lifetime': 25
            },
            {
                'name': 'water_asset_b',
                'capital_cost': 1500,
            },
            {
                'name': 'water_asset_c',
                'capital_cost': 3000,
            }
        ]
        model = EmptySectorModel('test_model')
        model.interventions = interventions
        actual = model.interventions

        assert actual == interventions

        assert sorted(model.intervention_names) == [
            'water_asset_a',
            'water_asset_b',
            'water_asset_c'
        ]


class TestParameters():

    def test_add_parameter(self):
        """Adding a parameter adds a reference to the parameter list entry to
        the model that contains it.
        """

        model = copy(EmptySectorModel('test_model'))
        model.simulate = lambda x, y: {'savings': y['smart_meter_savings']}

        param_config = {'name': 'smart_meter_savings',
                        'description': 'The savings from smart meters',
                        'absolute_range': (0, 100),
                        'suggested_range': (3, 10),
                        'default_value': 3,
                        'units': '%'}
        model.add_parameter(param_config)

        assert isinstance(model.parameters, ParameterList)

        param_config['parent'] = model

        assert model.parameters['smart_meter_savings'] == param_config

        actual = model.simulate(2010, {'smart_meter_savings': 3})
        expected = {'savings': 3}
        assert actual == expected
