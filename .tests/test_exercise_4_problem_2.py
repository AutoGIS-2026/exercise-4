from points_decorator import points
import os
import re
import geopandas as gpd
import pyproj


SHOPPING_CENTRES = ["Itis", "Myyrmanni", "Forum", "Iso_Omena", "Ruoholahti", "Dixi", "Jumbo"]

# YKR_ID of a grid cell, and its closest shopping centre (by public transport)
CLOSEST_SHOPPING_CENTRE = {
    5785641: "Myyrmanni",
    5876274: "Itis",
}


def normalise(name):
    """Make names comparable: "Iso_Omena", "Iso Omena", "iso-omena" → "isoomena"."""
    return re.sub(r"[^a-z]", "", str(name).lower())


def candidate_grids(namespace):
    """
    The combined grid can have any variable name (the notebook leaves this open):
    yield all large GeoDataFrames in EPSG:3067, starting with one called `grid`.
    """
    values = sorted(namespace.items(), key=lambda item: item[0] != "grid")
    for _, value in values:
        if (
            isinstance(value, gpd.GeoDataFrame)
            and value.crs == pyproj.CRS.from_epsg(3067)
            and len(value) > 1000
        ):
            yield value


def has_travel_time_columns(grid):
    columns = [normalise(column) for column in grid.columns]
    return all(
        any(normalise(shopping_centre) in column for column in columns)
        for shopping_centre in SHOPPING_CENTRES
    )


def get_row(grid, ykr_id):
    if "YKR_ID" in grid.columns:
        return grid[grid["YKR_ID"] == ykr_id].iloc[0]
    return grid.loc[ykr_id]


def shopping_centre_in(value):
    """Which shopping centre does a value name? ("Iso Omena", "pt_r_t_Iso_Omena", ...)"""
    for shopping_centre in SHOPPING_CENTRES:
        if normalise(shopping_centre) in normalise(value):
            return shopping_centre
    return None


def closest_shopping_centre_columns(grid):
    """Columns whose values are (mostly) shopping centre names."""
    for column in grid.columns:
        if column == "geometry":
            continue
        values = grid[column].dropna()
        if len(values) and values.map(shopping_centre_in).notna().mean() > 0.9:
            yield column


class TestProblem2:
    @points(1, "Problem 2: Did you import the grid data and check if the CRS is correct?")
    def test_problem_2_import_grid(self, problem2):
        section_data, namespace = problem2
        assert any(True for _ in candidate_grids(namespace))

    @points(3, "Problem 2: Did you join the public transport travel times of all seven shopping centres into the grid cells?")
    def test_problem_2_centres(self, problem2):
        section_data, namespace = problem2
        assert any(has_travel_time_columns(grid) for grid in candidate_grids(namespace))

    @points(3, "Problem 2: Some of the values for the nearest shopping centre seem to be incorrect.")
    def test_problem_2_closest_shopping_centre_value(self, problem2):
        section_data, namespace = problem2

        def correct(grid, column):
            return all(
                shopping_centre_in(get_row(grid, ykr_id)[column]) == shopping_centre
                for ykr_id, shopping_centre in CLOSEST_SHOPPING_CENTRE.items()
            )

        assert any(
            correct(grid, column)
            for grid in candidate_grids(namespace)
            for column in closest_shopping_centre_columns(grid)
        )

    @points(1.5, "Problem 2: Did you save the plot as a PNG file?")
    def test_problem_2_plot_file_exists(self, problem2):
        section_data, namespace = problem2
        png_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'dominance_areas.png')
        assert os.path.exists(png_file)

    @points(1.5, "Problem 2: Did you check that the PNG file is not empty?")
    def test_problem_2_plot_file_not_empty(self, problem2):
        section_data, namespace = problem2
        png_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'dominance_areas.png')
        assert os.path.getsize(png_file) > 0
