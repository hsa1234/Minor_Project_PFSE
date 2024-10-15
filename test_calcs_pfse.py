import calcs_pfse as calcs
from math import isclose

import calcs_pfse as calcs
from math import isclose

import calcs_pfse as calcs
from math import isclose

import calcs_pfse as calcs
from math import isclose

def test_calculate_reactions():
    # Define the load data as a list of one point load
    load_data = [{'type': 'Point Load', 'magnitude': 12.5, 'location': 12.5}]

    # Call the function and store both reactions and LaTeX code separately
    result = calcs.calculate_reactions('cantilever', 25.00, load_data)

    # Extract reactions explicitly and skip the LaTeX code part
    reactions = result[0]  # This is the dictionary of reactions
    latex_code = result[1]  # We are ignoring this in the test

    # Assert that the values are close to the expected ones
    assert isclose(reactions['Va'], 12.5, rel_tol=1e-5)
    assert isclose(reactions['Ma'], 156.25, rel_tol=1e-5)




import calcs_pfse as calcs
import numpy as np
from math import isclose

def test_calculate_sfd():
    # Define the load data for a cantilever beam (point load at 12.5 m)
    load_data = [{'type': 'Point Load', 'magnitude': 12.5, 'location': 12.5}]
    span_length = 25.0

    # Call the function and get the SFD data (ignoring LaTeX)
    X, V, _ = calcs.calculate_sfd('cantilever', span_length, load_data)

    # Expected values: Shear starts with 12.5 at the fixed support, drops to 0 at the load point
    expected_shear_start = 12.5  # Reaction at fixed support
    expected_shear_end = 0.0  # Shear after the load point

    # Find the index in X closest to the load location (12.5 m)
    load_index = np.argmax(X >= 12.5)

    # Assertions
    assert isclose(V[0], expected_shear_start, rel_tol=1e-5)
    assert isclose(V[load_index], expected_shear_end, rel_tol=1e-5)



import calcs_pfse as calcs
from math import isclose
import numpy as np

def test_calculate_bmd():
    # Define the load data for a cantilever beam (point load at 12.5 m)
    load_data = [{'type': 'Point Load', 'magnitude': 12.5, 'location': 12.5}]
    span_length = 25.0

    # Call the function and get the BMD data (ignoring LaTeX)
    X, M, _ = calcs.calculate_bmd('cantilever', span_length, load_data, {'Ma': 12.5 * 12.5})

    # Convert X to a NumPy array to use comparison operations
    X = np.array(X)

    # Expected values: Max negative moment at fixed support, zero at the load location
    expected_moment_start = -12.5 * 12.5  # Max negative moment (hogging) at the fixed end
    expected_moment_at_load = 0.0  # Moment at the load location

    # Find the index in X closest to the load location (12.5 m)
    load_index = np.argmax(X >= 12.5)

    # Assertions
    assert isclose(M[0], expected_moment_start, rel_tol=1e-5)
    assert isclose(M[load_index], expected_moment_at_load, rel_tol=1e-5)




