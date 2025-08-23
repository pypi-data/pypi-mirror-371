import pytest
from episode.optimize_properties import create_dictionary
from episode.semantic_representation import Composition
import numpy as np
from episode.optimize_properties import from_parameters_to_raw_properties

def test_create_dictionary_bounded_composition_x0_not_specified():
    # Mock the Composition object
    composition = Composition(("++b","+-b"))
    # Call the function
    dictionary, n_all_parameters = create_dictionary(composition, x0_included=True)

    assert dictionary['horizontal_values'][1] - dictionary['horizontal_values'][0] == 2
    assert dictionary['vertical_values'][1] - dictionary['vertical_values'][0] == 2
    assert dictionary['infinite_properties'] is None
    assert dictionary['t_last_finite_transition_point'] is None
    assert dictionary['first_derivative_at_start'][1] - dictionary['first_derivative_at_start'][0] == 1
    assert dictionary['first_derivative_at_end'][1] - dictionary['first_derivative_at_end'][0] == 1
    assert dictionary['second_derivative_at_end'] is None
    assert dictionary['x0'] is None

    assert n_all_parameters == 6

def test_from_parameters_to_raw_properties():
    parameters = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0])
    dictionary = {
        'horizontal_values': (0, 2),
        'vertical_values': (2, 4),
        'infinite_properties': (4, 5),
        'first_derivative_at_start': (5, 6),
        'first_derivative_at_end': (6, 7),
        'second_derivative_at_end': None,
        'x0': None,
        't_last_finite_transition_point': None
    }

    result = from_parameters_to_raw_properties(parameters, dictionary)

    assert np.array_equal(result['horizontal_values'], np.array([1.0, 2.0]))
    assert np.array_equal(result['vertical_values'], np.array([3.0, 4.0]))
    assert np.array_equal(result['infinite_properties'], np.array([5.0]))
    assert result['first_derivative_at_start'] == 6.0
    assert result['first_derivative_at_end'] == 7.0
    assert result['second_derivative_at_end'] is None
    assert result['x0'] is None
    assert result['t_last_finite_transition_point'] is None

