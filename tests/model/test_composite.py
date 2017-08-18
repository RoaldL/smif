from unittest.mock import Mock

import networkx
import numpy as np
import pytest
from pytest import fixture, raises
from smif.metadata import Metadata, MetadataSet
from smif.model.scenario_model import ScenarioModel
from smif.model.sector_model import SectorModel as AbstractSectorModel
from smif.model.sos_model import ModelSet, SosModel


@fixture
def get_sector_model():
    class SectorModel(AbstractSectorModel):

        def simulate(self, timestep, data=None):
            return data

        def extract_obj(self):
            pass

        def initialise(self):
            pass
    return SectorModel


@fixture
def get_water_sector_model():
    class SectorModel(AbstractSectorModel):
        """
        fluffyness -> electricity_demand
        """

        def simulate(self, timestep, input_data=None):
            results = {}
            x = input_data['fluffyness']
            results['electricity_demand'] = (
                x**3) - (6 * x**2) + (0.9 * x) + 0.15
            return results

        def extract_obj(self):
            pass

        def initialise(self):
            pass

    water_model = SectorModel('water_supply_model')
    water_model.add_input('fluffyness',
                          water_model.regions.get_entry('LSOA'),
                          water_model.intervals.get_entry('annual'),
                          'unit')
    water_model.add_output('electricity_demand',
                           water_model.regions.get_entry('LSOA'),
                           water_model.intervals.get_entry('annual'),
                           'unit')

    return water_model


@fixture
def get_energy_sector_model():
    class SectorModel(AbstractSectorModel):
        """
        electricity_demand_input -> fluffiness
        """

        def simulate(self, timestep, input_data=None):
            """Mimics the running of a sector model
            """
            results = {}
            fluff = input_data['electricity_demand_input']
            results['fluffiness'] = fluff * 0.819
            return results

        def extract_obj(self):
            pass

        def initialise(self):
            pass

    energy_model = SectorModel('energy_sector_model')
    energy_model.add_input('electricity_demand_input',
                           energy_model.regions.get_entry('LSOA'),
                           energy_model.intervals.get_entry('annual'),
                           'unit')
    energy_model.add_output('fluffiness',
                            energy_model.regions.get_entry('LSOA'),
                            energy_model.intervals.get_entry('annual'),
                            'unit')

    return energy_model


class TestModelSet:

    def test_model_set(self, get_sector_model):
        SectorModel = get_sector_model

        elec_scenario = ScenarioModel('scenario')
        elec_scenario.add_output('output',
                                 Mock(get_region_names=['oxford']),
                                 Mock(get_interval_names=['annual']),
                                 'unit')
        elec_scenario.add_data({2010: 123})

        energy_model = SectorModel('model')
        energy_model.add_input('input',
                               Mock(get_region_names=['oxford']),
                               Mock(get_interval_names=['annual']), 'unit')
        energy_model.add_dependency(elec_scenario, 'output', 'input')

        sos_model = SosModel('energy_sos_model')
        sos_model.add_model(energy_model)
        sos_model.add_model(elec_scenario)

        model_set = ModelSet([elec_scenario], sos_model)
        model_set.run(2010)


class TestBasics:

    def test_dependency_not_present(self, get_sector_model):
        SectorModel = get_sector_model
        elec_scenario = ScenarioModel('scenario')
        elec_scenario.add_output('output', Mock(), Mock(), 'unit')
        elec_scenario.add_data({2010: 123})

        energy_model = SectorModel('model')
        energy_model.add_input('input', Mock(), Mock(), 'unit')
        with raises(ValueError):
            energy_model.add_dependency(elec_scenario, 'not_present',
                                        'input')

        with raises(ValueError):
            energy_model.add_dependency(elec_scenario, 'output',
                                        'not_correct_input_name')


class TestDependencyGraph:

    def test_simple_graph(self, get_sector_model):
        SectorModel = get_sector_model
        elec_scenario = ScenarioModel('scenario')
        elec_scenario.add_output('output', Mock(), Mock(), 'unit')
        elec_scenario.add_data({2010: 123})

        energy_model = SectorModel('model')
        energy_model.add_input('input', Mock(), Mock(), 'unit')
        energy_model.add_dependency(elec_scenario, 'output', 'input')

        sos_model = SosModel('energy_sos_model')
        sos_model.add_model(energy_model)
        sos_model.add_model(elec_scenario)

        # Builds the dependency graph
        sos_model.check_dependencies()

        graph = sos_model.dependency_graph

        assert energy_model in graph
        assert elec_scenario in graph

        assert graph.edges() == [(elec_scenario, energy_model)]

    def test_get_model_sets(self, get_sector_model):
        SectorModel = get_sector_model

        elec_scenario = ScenarioModel('scenario')
        elec_scenario.add_output('output', Mock(), Mock(), 'unit')

        elec_scenario.add_data({2010: 123})

        energy_model = SectorModel('model')
        energy_model.add_input('input', Mock(), Mock(), 'unit')
        energy_model.add_dependency(elec_scenario, 'output', 'input')

        sos_model = SosModel('energy_sos_model')
        sos_model.add_model(energy_model)
        sos_model.add_model(elec_scenario)

        sos_model.check_dependencies()

        actual = sos_model._get_model_sets_in_run_order()
        expected = [{'scenario'}, {'model'}]

        for modelset, name in zip(actual, expected):
            assert modelset._model_names == name

    def test_topological_sort(self, get_sector_model):
        SectorModel = get_sector_model
        elec_scenario = ScenarioModel('scenario')
        elec_scenario.add_output('output', Mock(), Mock(), 'unit')

        elec_scenario.add_data({'output': 123})

        energy_model = SectorModel('model')
        energy_model.add_input('input', Mock(), Mock(), 'unit')
        energy_model.add_dependency(elec_scenario, 'output', 'input')

        sos_model = SosModel('energy_sos_model')
        sos_model.add_model(energy_model)
        sos_model.add_model(elec_scenario)

        sos_model.check_dependencies()

        graph = sos_model.dependency_graph
        actual = networkx.topological_sort(graph, reverse=False)
        assert actual == [elec_scenario, energy_model]


class TestSosModel:

    def test_simulate_data_not_present(self, get_sector_model):
        SectorModel = get_sector_model
        """Raise a NotImplementedError if an input is defined but no dependency links
        it to a data source
        """

        sos_model = SosModel('test')
        model = SectorModel('test_model')
        model.add_input('input', Mock(), Mock(), 'units')
        sos_model.add_model(model)
        data = {'input_not_here': 0}
        with raises(NotImplementedError):
            sos_model.simulate(2010, data)


class TestCompositeIntegration:

    def test_simplest_case(self):
        """One scenario only
        """
        elec_scenario = ScenarioModel('electricity_demand_scenario')
        elec_scenario.add_output('electricity_demand_output',
                                 Mock(), Mock(), 'unit')

        elec_scenario.add_data({2010: 123})
        sos_model = SosModel('simple')
        sos_model.add_model(elec_scenario)
        actual = sos_model.simulate(2010)
        expected = {2010: {'electricity_demand_scenario':
                           {'electricity_demand_output': 123}}}
        assert actual == expected

    def test_sector_model_null_model(self, get_energy_sector_model):
        no_inputs = get_energy_sector_model
        no_inputs._model_inputs = MetadataSet([])
        no_inputs.simulate = lambda x: x
        actual = no_inputs.simulate(2010)
        expected = 2010
        assert actual == expected

    def test_sector_model_one_input(self, get_energy_sector_model):
        elec_scenario = ScenarioModel('scenario')
        elec_scenario.add_output('output', Mock(), Mock(), 'unit')
        elec_scenario.add_data({2010: 123})

        energy_model = get_energy_sector_model
        energy_model.add_dependency(elec_scenario, 'output',
                                    'electricity_demand_input')

        sos_model = SosModel('blobby')
        sos_model.add_model(elec_scenario)
        sos_model.add_model(energy_model)

        actual = sos_model.simulate(2010)

        expected = {2010: {'energy_sector_model':
                           {'fluffiness': 100.737},
                           'scenario': {'output': 123}
                           }
                    }
        assert actual == expected


class TestNestedModels():

    def test_one_free_input(self, get_sector_model):
        SectorModel = get_sector_model
        energy_model = SectorModel('energy_sector_model')

        input_metadata = {'name': 'electricity_demand_input',
                          'spatial_resolution': Mock(),
                          'temporal_resolution': Mock(),
                          'units': 'unit'}

        expected = MetadataSet([input_metadata])

        energy_model._model_inputs = expected

        assert energy_model.free_inputs['electricity_demand_input'] == \
            expected['electricity_demand_input']

    def test_hanging_inputs(self, get_sector_model):
        """
        sos_model_high
            sos_model_lo
               -> em

        """
        SectorModel = get_sector_model
        energy_model = SectorModel('energy_sector_model')

        input_metadata = {'name': 'electricity_demand_input',
                          'spatial_resolution': Mock(),
                          'temporal_resolution': Mock(),
                          'units': 'unit'}

        energy_model._model_inputs = MetadataSet([input_metadata])

        sos_model_lo = SosModel('lower')
        sos_model_lo.add_model(energy_model)

        input_object = Metadata(input_metadata['name'],
                                input_metadata['spatial_resolution'],
                                input_metadata['temporal_resolution'],
                                input_metadata['units'])
        expected = MetadataSet([])
        expected.add_metadata_object(input_object)

        assert energy_model.free_inputs.names == ['electricity_demand_input']

        assert sos_model_lo.free_inputs.names == ['electricity_demand_input']

        sos_model_high = SosModel('higher')
        sos_model_high.add_model(sos_model_lo)

        assert sos_model_high.free_inputs['electricity_demand_input'] == \
            input_object

    @pytest.mark.xfail(reason="Nested sosmodels not yet implemented")
    def test_nested_graph(self, get_sector_model):
        """If we add a nested model, all Sectormodel and ScenarioModel objects
        are added as nodes in the graph with edges along dependencies.

        SosModel objects are not included, as they are just containers for the
        SectorModel and ScenarioModel objects, passing up inputs for deferred
        linkages to dependencies.

        Not implemented yet:
        """
        SectorModel = get_sector_model

        energy_model = SectorModel('energy_sector_model')

        input_metadata = {'name': 'electricity_demand_input',
                          'spatial_resolution': Mock(),
                          'temporal_resolution': Mock(),
                          'units': 'unit'}

        energy_model._model_inputs = MetadataSet([input_metadata])

        sos_model_lo = SosModel('lower')
        sos_model_lo.add_model(energy_model)

        sos_model_high = SosModel('higher')
        sos_model_high.add_model(sos_model_lo)

        with raises(NotImplementedError):
            sos_model_high.check_dependencies()
        graph = sos_model_high.dependency_graph
        assert graph.edges() == []

        expected = networkx.DiGraph()
        expected.add_node(sos_model_lo)
        expected.add_node(energy_model)

        assert energy_model in graph.nodes()

        scenario = ScenarioModel('electricity_demand')
        scenario.add_output('elec_demand_output', Mock(), Mock(), 'kWh')

        sos_model_high.add_dependency(scenario, 'elec_demand_output',
                                      'electricity_demand_input')

        sos_model_high.check_dependencies()
        assert graph.edges() == [(scenario, sos_model_high)]

    @pytest.mark.xfail(reason="Nested sosmodels not yet implemented")
    def test_composite_nested_sos_model(self, get_sector_model):
        """System of systems example with two nested SosModels, two Scenarios
        and one SectorModel. One dependency is defined at the SectorModel
        level, another at the lower SosModel level
        """
        SectorModel = get_sector_model

        elec_scenario = ScenarioModel('electricity_demand_scenario')
        elec_scenario.add_output('electricity_demand_output',
                                 Mock(), Mock(), 'unit')
        elec_scenario.add_data({2010: 123})

        energy_model = SectorModel('energy_sector_model')
        energy_model.add_input(
            'electricity_demand_input', Mock(), Mock(), 'unit')
        energy_model.add_input('fluffiness_input', Mock(), Mock(), 'unit')
        energy_model.add_output('cost', Mock(), Mock(), 'unit')
        energy_model.add_output('fluffyness', Mock(), Mock(), 'unit')

        def energy_function(timestep, input_data):
            """Mimics the running of a sector model
            """
            results = {}
            demand = input_data['electricity_demand_input']
            fluff = input_data['fluffiness_input']
            results['cost'] = demand * 1.2894
            results['fluffyness'] = fluff * 22
            return results

        energy_model.simulate = energy_function
        energy_model.add_dependency(elec_scenario,
                                    'electricity_demand_output',
                                    'electricity_demand_input')

        sos_model_lo = SosModel('lower')
        sos_model_lo.add_model(elec_scenario)
        sos_model_lo.add_model(energy_model)

        fluf_scenario = ScenarioModel('fluffiness_scenario')
        fluf_scenario.add_output('fluffiness', Mock(), Mock(), 'unit')
        fluf_scenario.add_data({2010: 12})

        assert sos_model_lo.free_inputs.names == ['fluffiness_input']

        sos_model_lo.add_dependency(fluf_scenario,
                                    'fluffiness',
                                    'fluffiness_input')

        assert sos_model_lo.model_inputs.names == []

        sos_model_high = SosModel('higher')
        sos_model_high.add_model(sos_model_lo)
        sos_model_high.add_model(fluf_scenario)

        actual = sos_model_high.simulate(2010)
        expected = {'fluffiness_scenario': {'fluffiness': 12},
                    'lower': {'electricity_demand_scenario':
                              {'electricity_demand_output': 123},
                              'energy_sector_model': {'cost': 158.5962,
                                                      'fluffyness': 264}
                              }
                    }

        assert actual == expected


class TestCircularDependency:

    def test_loop(self, get_energy_sector_model, get_water_sector_model):
        """Fails because no functionality to deal with loops
        """
        energy_model = get_energy_sector_model

        water_model = get_water_sector_model

        sos_model = SosModel('energy_water_model')
        water_model.add_dependency(energy_model, 'fluffiness', 'fluffyness')
        energy_model.add_dependency(water_model, 'electricity_demand',
                                    'electricity_demand_input')

        sos_model.add_model(water_model)
        sos_model.add_model(energy_model)

        assert energy_model.model_inputs.names == ['electricity_demand_input']
        assert water_model.model_inputs.names == ['fluffyness']
        assert sos_model.model_inputs.names == []

        assert energy_model.free_inputs.names == []
        assert water_model.free_inputs.names == []
        assert sos_model.free_inputs.names == []

        sos_model.check_dependencies()
        graph = sos_model.dependency_graph

        assert (water_model, energy_model) in graph.edges()
        assert (energy_model, water_model) in graph.edges()

        modelset = ModelSet([water_model, energy_model], sos_model)
        actual = modelset.guess_results(water_model, 2010)
        expected = {'electricity_demand': np.array([1.])}
        # assert actual == expected

        sos_model.max_iterations = 100
        sos_model.simulate(2010)

        expected = np.array([[0.13488114]], dtype=np.float)
        actual = sos_model.results[2010]['energy_sector_model']['fluffiness']
        np.testing.assert_allclose(actual, expected, rtol=1e-5)
        expected = np.array([[0.16469004]], dtype=np.float)
        actual = sos_model.results[2010]['water_supply_model']['electricity_demand']
        np.testing.assert_allclose(actual, expected, rtol=1e-5)