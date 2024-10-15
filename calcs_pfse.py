import numpy as np

def calculate_reactions(supports, span_length, load_data):
    reactions = {"Va": 0, "Vb": 0, "Ma": 0}
    latex_code = ""  # Initialize LaTeX code string

    if span_length == 0:
        return reactions, "Span length cannot be zero."

    if supports == 'simply supported':
        total_moment_about_left = 0
        total_moment_about_right = 0
        total_load = 0

        # Accumulate loads and moments
        for load in load_data:
            if load["type"] == "Point Load":
                total_load += load["magnitude"]
                total_moment_about_left += load["magnitude"] * (span_length - load["location"])
                total_moment_about_right += load["magnitude"] * load["location"]

        # Calculate reactions
        if total_load != 0:
            reactions["Vb"] = total_moment_about_right / span_length
            reactions["Va"] = total_moment_about_left / span_length

        # Generate LaTeX code for the calculations
        latex_code = (
            r"\textbf{Simply Supported Beam:}\\"
            rf"\text{{Total point loads }}: \sum P = {total_load:.2f} \, \text{{kN}}\\"
            r"\text{Moment about left support: }\\"
            rf"V_b = \frac{{\sum M_a}}{{L}} = \frac{{{total_moment_about_right:.2f}}}{{{span_length}}} = {reactions['Vb']:.2f} \, \text{{kN}}\\"
            rf"V_a = \frac{{\sum M_b}}{{L}} = \frac{{{total_moment_about_left:.2f}}}{{{span_length}}} = {reactions['Va']:.2f} \, \text{{kN}}"
        )

    elif supports == 'cantilever':
        total_vertical_load = 0
        total_moment_about_fixed = 0

        for load in load_data:
            if load["type"] == "Point Load":
                total_vertical_load += load["magnitude"]
                total_moment_about_fixed += load["magnitude"] * load["location"]

        if total_vertical_load != 0:
            reactions["Va"] = total_vertical_load
            reactions["Ma"] = total_moment_about_fixed

        latex_code = (
            r"\textbf{Cantilever Beam:}\\"
            rf"V_a = \sum P = {reactions['Va']:.2f} \, \text{{kN}}\\"
            rf"M_a = \sum (P \cdot a) = {reactions['Ma']:.2f} \, \text{{kN}}\cdot\text{{m}}"
        )


    return reactions, latex_code


def calculate_sfd(supports, span_length, load_data):
    """
    Calculates the Shear Force at different points along the beam with multiple point loads.

    Parameters:
    - supports: Type of supports ('simply supported' or 'cantilever')
    - span_length: Length of the beam (in meters)
    - load_data: List of loads (each load is a dictionary with keys 'type', 'magnitude', and 'location')

    Returns:
    - X: Positions along the length of the beam
    - V: Shear force values at those positions
    - sfd_latex: LaTeX string for display in the app
    """
    
    # Unpack the tuple returned by calculate_reactions() correctly
    reactions, _ = calculate_reactions(supports, span_length, load_data)

    Va = reactions.get('Va', 0)
    Vb = reactions.get('Vb', 0)

    # Number of points to calculate the shear force at
    num_points = 100
    X = np.linspace(0, span_length, num_points)
    V = np.zeros_like(X)

    if supports == 'simply supported':
        # Loop through each point on the beam
        for i, x in enumerate(X):
            V[i] = Va  # Start with the reaction at the left support

            # Apply load effects on the shear force
            for load in load_data:
                if load['type'] == 'Point Load':
                    point_load_magnitude = load['magnitude']
                    point_load_location = load['location']

                    if x >= point_load_location:
                        V[i] -= point_load_magnitude  # Subtract the load after its location

    elif supports == 'cantilever':
        # Loop through each point on the beam
        for i, x in enumerate(X):
            V[i] = Va  # Start with the reaction at the fixed support

            # Apply load effects on the shear force
            for load in load_data:
                if load['type'] == 'Point Load':
                    point_load_magnitude = load['magnitude']
                    point_load_location = load['location']

                    if x >= point_load_location:
                        V[i] -= point_load_magnitude  # Subtract the load after its location

    # Generate LaTeX code for critical points
    sfd_latex = r"Shear Force Diagram Calculations:\\"
    critical_indices = [0] + [i for i, x in enumerate(X) if any(load['location'] == x for load in load_data)] + [len(X) - 1]

    for idx in critical_indices:
        sfd_latex += f"V(x = {X[idx]:.2f}) = {V[idx]:.2f}\\, \\text{{kN}}\\\\ "

    return X, V, sfd_latex






def calculate_bmd(supports, span_length, load_data, reactions):
    """
    Calculate the bending moment at critical points along the beam.

    Parameters:
    - supports: Type of beam ('simply supported' or 'cantilever')
    - span_length: Length of the beam (in meters)
    - load_data: List of load dictionaries containing load type, magnitude, and location
    - reactions: Dictionary of reactions at supports ('Va', 'Vb', 'Ma' for cantilever)

    Returns:
    - X_critical: Positions at critical points along the beam
    - M_critical: Bending moments at those critical points (negative for hogging)
    - bmd_latex: LaTeX string for display in the app
    """
    # Initialize bending moment values and critical points
    X = []  # Positions along the beam
    M = []  # Bending moments at critical points

    if supports == 'cantilever':
        for load in load_data:
            if load['type'] == 'Point Load':
                P = load['magnitude']
                a = load['location']

                # 1. Add the fixed support with maximum hogging moment (negative)
                X.append(0)  # Fixed end position
                M.append(-(P * a))  # Negative moment at the fixed support

                # 2. Add the load location where the moment becomes zero
                X.append(a)  # Load position
                M.append(0)  # Moment at load location

        # 3. Ensure the free end of the beam is accounted for
        if a < span_length:
            X.append(span_length)  # Free end position
            M.append(0)  # Moment remains zero beyond the load

    elif supports == 'simply supported':
        Va = reactions.get('Va', 0)
        Vb = reactions.get('Vb', 0)

        # Loop through each load and add its contribution
        for load in load_data:
            if load['type'] == 'Point Load':
                P = load['magnitude']
                a = load['location']

                # Calculate the moment at the given location
                moment_at_a = Va * a - P * (a - a)  # Moment due to reactions and applied load
                X.append(a)
                M.append(moment_at_a)

        # Moment at the start and end of the beam is zero
        X.insert(0, 0)  # Start of the beam
        M.insert(0, 0)  # Moment at the start is zero
        X.append(span_length)  # End of the beam
        M.append(0)  # Moment at the end is zero

    # Generate LaTeX code for critical points
    bmd_latex = r"Bending Moment Diagram Calculations:\\"
    bmd_latex += "".join(
        [f"M(x = {x:.2f}) = {m:.2f}\\, \\text{{kN}} \\cdot \\text{{m}}\\\\ " for x, m in zip(X, M)]
    )

    return X, M, bmd_latex









