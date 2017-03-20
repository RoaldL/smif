from copy import copy

from pytest import approx, raises
from smif import SpaceTimeValue
from smif.convert import SpaceTimeConvertor
from smif.convert.area import RegionRegister, RegionSet
from smif.convert.interval import TimeIntervalRegister
from test_area import regions_half_squares as fixture_regions
from test_interval import months, seasons


class TestSpaceTimeConvertor:

    def test_instantiation(self):
        SpaceTimeConvertor([], None, None, None, None, None, None)

    def test_conversion_not_required(self):
        convertor = SpaceTimeConvertor([], 'a', 'a', 'x', 'x', None, None)
        assert convertor._convert_intervals_required() is False
        assert convertor._convert_regions_required() is False

    def test_conversion_is_required(self):
        convertor = SpaceTimeConvertor([], 'a', 'b', 'x', 'y', None, None)
        assert convertor._convert_intervals_required() is True
        assert convertor._convert_regions_required() is True

    def test_multiple_units_raises_notimplemented(self):
        data = [SpaceTimeValue('a', '1_0', 31, 'days'),
                SpaceTimeValue('a', '1_2', 31, 'minutes'),
                SpaceTimeValue('b', '1_1', 28, 'seconds')]
        with raises(NotImplementedError):
            SpaceTimeConvertor(data, 'a', 'a', 'x', 'x', None, None)

    def test_data_by_regions(self):
        data = [SpaceTimeValue('a', '1_0', 31, 'days'),
                SpaceTimeValue('a', '1_2', 31, 'days'),
                SpaceTimeValue('b', '1_1', 28, 'days')]
        convertor = SpaceTimeConvertor(data, 'a', 'a', 'x', 'x', None, None)

        expected = {'a': [SpaceTimeValue('a', '1_0', 31, 'days'),
                          SpaceTimeValue('a', '1_2', 31, 'days')],
                    'b': [SpaceTimeValue('b', '1_1', 28, 'days')]}

        assert convertor.data_by_region == expected

    def test_one_region_pass_through_time(self, months, seasons, fixture_regions):
        """Only one region, 12 months, neither space nor time conversion is required

        """

        data = [SpaceTimeValue('a', '1_0', 31, 'days'),
                SpaceTimeValue('a', '1_1', 28, 'days'),
                SpaceTimeValue('a', '1_2', 31, 'days'),
                SpaceTimeValue('a', '1_3', 30, 'days'),
                SpaceTimeValue('a', '1_4', 31, 'days'),
                SpaceTimeValue('a', '1_5', 30, 'days'),
                SpaceTimeValue('a', '1_6', 31, 'days'),
                SpaceTimeValue('a', '1_7', 31, 'days'),
                SpaceTimeValue('a', '1_8', 30, 'days'),
                SpaceTimeValue('a', '1_9', 31, 'days'),
                SpaceTimeValue('a', '1_10', 30, 'days'),
                SpaceTimeValue('a', '1_11', 31, 'days')]

        intervals = TimeIntervalRegister()
        intervals.add_interval_set(months, 'months')
        intervals.add_interval_set(seasons, 'months')

        regions = RegionRegister()
        regions.register(fixture_regions)

        convertor = SpaceTimeConvertor(data,
                                       'half_squares',
                                       'half_squares',
                                       'months',
                                       'months',
                                       regions,
                                       intervals)

        assert convertor.data_regions == set(['a'])
        assert convertor.data_by_region == {'a': data}

        actual = convertor.convert()

        expected = [SpaceTimeValue('a', '1_0', 31, 'days'),
                    SpaceTimeValue('a', '1_1', 28, 'days'),
                    SpaceTimeValue('a', '1_2', 31, 'days'),
                    SpaceTimeValue('a', '1_3', 30, 'days'),
                    SpaceTimeValue('a', '1_4', 31, 'days'),
                    SpaceTimeValue('a', '1_5', 30, 'days'),
                    SpaceTimeValue('a', '1_6', 31, 'days'),
                    SpaceTimeValue('a', '1_7', 31, 'days'),
                    SpaceTimeValue('a', '1_8', 30, 'days'),
                    SpaceTimeValue('a', '1_9', 31, 'days'),
                    SpaceTimeValue('a', '1_10', 30, 'days'),
                    SpaceTimeValue('a', '1_11', 31, 'days')]

        assert actual == expected

    def test_one_region_time_aggregation(self, months, seasons, fixture_regions):

        data = [SpaceTimeValue('a', '1_0', 31, 'days'),
                SpaceTimeValue('a', '1_1', 28, 'days'),
                SpaceTimeValue('a', '1_2', 31, 'days'),
                SpaceTimeValue('a', '1_3', 30, 'days'),
                SpaceTimeValue('a', '1_4', 31, 'days'),
                SpaceTimeValue('a', '1_5', 30, 'days'),
                SpaceTimeValue('a', '1_6', 31, 'days'),
                SpaceTimeValue('a', '1_7', 31, 'days'),
                SpaceTimeValue('a', '1_8', 30, 'days'),
                SpaceTimeValue('a', '1_9', 31, 'days'),
                SpaceTimeValue('a', '1_10', 30, 'days'),
                SpaceTimeValue('a', '1_11', 31, 'days')]

        intervals = TimeIntervalRegister()
        intervals.add_interval_set(months, 'months')
        intervals.add_interval_set(seasons, 'seasons')

        regions = RegionRegister()
        regions.register(fixture_regions)

        convertor = SpaceTimeConvertor(data,
                                       'half_squares',
                                       'half_squares',
                                       'months',
                                       'seasons',
                                       regions,
                                       intervals)
        assert convertor.data_regions == set(['a'])
        assert convertor.data_by_region == {'a': data}

        actual = convertor.convert()

        expected = [SpaceTimeValue('a', 'winter', 31. + 31 + 28, 'days'),
                    SpaceTimeValue('a', 'spring', 31. + 30 + 31, 'days'),
                    SpaceTimeValue('a', 'summer', 30. + 31 + 31, 'days'),
                    SpaceTimeValue('a', 'autumn', 30. + 31 + 30, 'days')]

        for act, exp in zip(actual, expected):
            assert act.region == exp.region
            assert act.interval == exp.interval
            assert act.value == approx(exp.value)
            assert act.units == exp.units

    def test_two_region_time_aggregation(self, months, seasons, fixture_regions):

        region_a = [SpaceTimeValue('a', '1_0', 31, 'days'),
                    SpaceTimeValue('a', '1_1', 28, 'days'),
                    SpaceTimeValue('a', '1_2', 31, 'days'),
                    SpaceTimeValue('a', '1_3', 30, 'days'),
                    SpaceTimeValue('a', '1_4', 31, 'days'),
                    SpaceTimeValue('a', '1_5', 30, 'days'),
                    SpaceTimeValue('a', '1_6', 31, 'days'),
                    SpaceTimeValue('a', '1_7', 31, 'days'),
                    SpaceTimeValue('a', '1_8', 30, 'days'),
                    SpaceTimeValue('a', '1_9', 31, 'days'),
                    SpaceTimeValue('a', '1_10', 30, 'days'),
                    SpaceTimeValue('a', '1_11', 31, 'days')]
        region_b = [SpaceTimeValue('b', '1_0', 31+1, 'days'),
                    SpaceTimeValue('b', '1_1', 28+1, 'days'),
                    SpaceTimeValue('b', '1_2', 31+1, 'days'),
                    SpaceTimeValue('b', '1_3', 30+1, 'days'),
                    SpaceTimeValue('b', '1_4', 31+1, 'days'),
                    SpaceTimeValue('b', '1_5', 30+1, 'days'),
                    SpaceTimeValue('b', '1_6', 31+1, 'days'),
                    SpaceTimeValue('b', '1_7', 31+1, 'days'),
                    SpaceTimeValue('b', '1_8', 30+1, 'days'),
                    SpaceTimeValue('b', '1_9', 31+1, 'days'),
                    SpaceTimeValue('b', '1_10', 30+1, 'days'),
                    SpaceTimeValue('b', '1_11', 31+1, 'days')]
        data = copy(region_a)
        data.extend(region_b)
        assert len(data) == 24

        intervals = TimeIntervalRegister()
        intervals.add_interval_set(months, 'months')
        intervals.add_interval_set(seasons, 'seasons')

        regions = RegionRegister()
        regions.register(fixture_regions)

        convertor = SpaceTimeConvertor(data,
                                       'half_squares',
                                       'half_squares',
                                       'months',
                                       'seasons',
                                       regions,
                                       intervals)
        assert convertor.data_regions == set(['a', 'b'])
        assert convertor.data_by_region['a'] == region_a
        assert convertor.data_by_region['b'] == region_b

        actual = convertor.convert()

        expected = [SpaceTimeValue('a', 'winter', 31. + 31 + 28, 'days'),
                    SpaceTimeValue('a', 'spring', 31. + 30 + 31, 'days'),
                    SpaceTimeValue('a', 'summer', 30. + 31 + 31, 'days'),
                    SpaceTimeValue('a', 'autumn', 30. + 31 + 30, 'days'),
                    SpaceTimeValue('b', 'winter', 31. + 31 + 28 + 3, 'days'),
                    SpaceTimeValue('b', 'spring', 31. + 30 + 31 + 3, 'days'),
                    SpaceTimeValue('b', 'summer', 30. + 31 + 31 + 3, 'days'),
                    SpaceTimeValue('b', 'autumn', 30. + 31 + 30 + 3, 'days')]

        for act, exp in zip(actual, expected):
            assert act.region == exp.region
            assert act.interval == exp.interval
            assert act.value == approx(exp.value)
            assert act.units == exp.units
