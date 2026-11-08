import importlib.util
import pathlib

import numpy as np

spec = importlib.util.spec_from_file_location(
    'obstacle_distance', pathlib.Path(__file__).parents[1] / 'scripts' / 'obstacle_distance.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_nearest_in_centre_wins_and_edges_are_ignored():
    depth = np.full((100, 100), 5.0, dtype=np.float32)
    depth[50, 50] = 1.2
    depth[0, 0] = 0.3  # outside the centre window
    assert module.nearest_distance(depth) == np.float32(1.2)


def test_invalid_pixels_are_skipped():
    depth = np.full((100, 100), np.inf, dtype=np.float32)
    depth[45, 45] = np.nan
    depth[55, 55] = 2.0
    assert module.nearest_distance(depth) == 2.0


def test_nothing_in_range_gives_none():
    assert module.nearest_distance(np.full((100, 100), np.inf, dtype=np.float32)) is None
