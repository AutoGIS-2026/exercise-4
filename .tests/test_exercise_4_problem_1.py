from points_decorator import points
import inspect
import os
import pandas as pd
import geopandas as gpd
import pyproj

class TestProblem1:

    @points(0.5, "Problem 1, Part 1: Did you import the grid data?")
    def test_problem_1_part_1(self, problem1):
        section_data, namespace = problem1
        section = "Part 1"
        variables = section_data[section]['variables']

        assert isinstance(variables['grid'], pd.DataFrame)

    @points(0.5, "Problem 1, Part 1: Does the `grid` dataframe contain the `YKR_ID` identifiers (as a column or as the index)?")
    def test_problem_1_part_1_index(self, problem1):
        section_data, namespace = problem1
        section = "Part 1"
        variables = section_data[section]['variables']
        grid = variables['grid']

        # using `YKR_ID` as the index makes the join easier, but is not required
        ykr_id = grid.index if grid.index.name == 'YKR_ID' else grid['YKR_ID']
        assert pd.api.types.is_integer_dtype(ykr_id)
        

    @points(1, "Problem 1, Part 2: Did you join the travel time data into the grid cells, using the correct column names?")
    def test_problem_1_part_2_columns(self, problem1):
        section_data, namespace = problem1
        section = "Part 2"
        variables = section_data[section]['variables']
    
        required_columns = ['pt_r_t_Itis', 'car_r_t_Itis', 'pt_r_t_Myyrmanni', 'car_r_t_Myyrmanni', 'geometry']

        assert all(column in variables['grid'].columns for column in required_columns)
        

    @points(1, "Problem 1, Part 2: Did you remove the no-data values (-1) from the travel time data?")
    def test_problem_1_part_2_nan(self, problem1):
        section_data, namespace = problem1
        section = "Part 2"
        variables = section_data[section]['variables']
        grid = variables['grid']
        for shopping_centre in ("Itis", "Myyrmanni"):
            for column in ("car_r_t", "pt_r_t"):
                # (`-1 in series` would check the index, not the values)
                assert not (grid[f"{column}_{shopping_centre}"] == -1).any()

    @points(2, "Problem 1, Part 3: Did you create the classification columns?")
    def test_problem_1_part_3_columns_exist(self, problem1):
        section_data, namespace = problem1
        section = "Part 3"
        variables = section_data[section]['variables']
        grid = variables['grid']

        classification_columns = ['pt_r_t_cl_Itis', 'pt_r_t_cl_Myyrmanni']
        for column in classification_columns:
            assert column in grid.columns

    @points(2, "Problem 1, Part 3: Did you reclassify the travel time values to five-minute intervals?")
    def test_problem_1_part_3_reclassification(self, problem1):
        section_data, namespace = problem1
        section = "Part 3"
        variables = section_data[section]['variables']
        grid = variables['grid']

        assert grid['pt_r_t_cl_Itis'].min() == 0.0
        assert grid['pt_r_t_cl_Itis'].max() == 12.0

        assert grid['pt_r_t_cl_Myyrmanni'].min() == 0.0
        assert grid['pt_r_t_cl_Myyrmanni'].max() == 12.0


    @points(3, "Problem 1, Part 4: Did you plot the data and add a title?")
    def test_problem_1_part_3(self, problem1):
        section_data, namespace = problem1
        section = "Part 4"
        variables = section_data[section]['variables']
        source = section_data[section]['source']
        grid = variables['grid']

        assert ".plot" in source
        assert "title" in source
        