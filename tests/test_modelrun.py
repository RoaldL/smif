from pytest import fixture
from smif.modelrun import ModelRunBuilder


@fixture(scope='function')
def get_model_run(setup_project_folder, setup_region_data):
    path = setup_project_folder
    water_supply_wrapper_path = str(
        path.join(
            'models', 'water_supply', '__init__.py'
        )
    )

    interval_data = [
        {
            'id': 1,
            'start': 'P0Y',
            'end': 'P1Y'
        }
    ]

    config_data = {
        'timesteps': [2010, 2011, 2012],
        'region_sets': {'LSOA': setup_region_data['features']},
        'interval_sets': {'annual': interval_data},
        'planning': [],
        'scenario_metadata':
            [{
                'name': 'raininess',
                'temporal_resolution': 'annual',
                'spatial_resolution': 'LSOA',
                'units': 'ml'
            }],
        'scenario_data': {
            "raininess": [
                {
                    'year': 2010,
                    'value': 3,
                    'region': 'oxford',
                    'interval': 1
                },
                {
                    'year': 2011,
                    'value': 5,
                    'region': 'oxford',
                    'interval': 1
                },
                {
                    'year': 2012,
                    'value': 1,
                    'region': 'oxford',
                    'interval': 1
                }
            ]
        },
        "sector_model_data": [
            {
                "name": "water_supply",
                "path": water_supply_wrapper_path,
                "classname": "WaterSupplySectorModel",
                "inputs": [],
                "outputs": [],
                "initial_conditions": [],
                "interventions": []
            }
        ]
        }

    builder = ModelRunBuilder()
    builder.construct(config_data)
    return builder.finish()


class TestModelRun:

    def test_run_static(self, get_model_run):
        model_run = get_model_run
        model_run.run()