from scripts.persistence_utils import occupancy_fraction, find_anchor_residue

def test_occupancy_fraction_all_within_cutoff():
    distances = [2.0, 3.5, 1.0, 3.9]
    assert occupancy_fraction(distances, cutoff=4.0) == 1.0

def test_occupancy_fraction_half_within_cutoff():
    distances = [2.0, 5.0, 2.0, 5.0]
    assert occupancy_fraction(distances, cutoff=4.0) == 0.5

def test_occupancy_fraction_empty_returns_none():
    assert occupancy_fraction([], cutoff=4.0) is None

def test_find_anchor_residue_picks_lowest_mean_distance():
    distances_per_residue = {
        0: [10.0, 10.0, 10.0],
        1: [2.0, 2.5, 2.0],   # menor média -> âncora real
        2: [8.0, 9.0, 8.0],
    }
    assert find_anchor_residue(distances_per_residue) == 1
