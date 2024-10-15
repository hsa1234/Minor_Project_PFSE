import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from calcs_pfse import *  # Ensure this module is correctly defined and accessible

# Main heading
st.title("2D Beam Analyzer")

# Initialize session state for load data if it doesn't exist
if "load_data" not in st.session_state:
    st.session_state["load_data"] = []

# Sidebar: Input Parameters
st.sidebar.markdown("# Input Parameters")

# Span section
st.sidebar.header('Span')
span_length = st.sidebar.number_input('Specify length of span (m)', min_value=0.0, step=0.1)

# Add Supports section
st.sidebar.header('Add Supports')
supports = st.sidebar.selectbox('Support Type', ['simply supported', 'cantilever'])

# Update support choices based on the selected beam type
if supports == 'cantilever':
    left_support = 'fixed'
    st.sidebar.write("Left Support: Fixed")
    right_support = None
else:
    left_support = st.sidebar.selectbox('Left Support', ['pin', 'roller', 'fixed'])
    right_support = st.sidebar.selectbox('Right Support', ['pin', 'roller', 'fixed'])

# Add Loads section
st.sidebar.header("Add Loads")

# Add Point Load
point_load_magnitude = st.sidebar.number_input("Point Load Magnitude (kN)", step=0.1)
point_load_location = st.sidebar.number_input(
    "Point Load Location (m)", min_value=0.0, max_value=float(span_length), step=0.1
)

if st.sidebar.button("Add Point Load"):
    st.session_state["load_data"].append({
        "type": "Point Load",
        "magnitude": point_load_magnitude,
        "location": point_load_location
    })

# Function to draw supports
def draw_support(ax, x, support_type, beam_y):
    if support_type == 'pin':
        ax.plot([x], [beam_y], marker='^', markersize=14, color='black')
    elif support_type == 'roller':
        ax.plot([x], [beam_y + 0.05], marker='^', markersize=12, color='black')
        ax.plot([x], [beam_y - 0.1], marker='o', markersize=8, color='black')
    elif support_type == 'fixed':
        ax.plot([x, x], [beam_y - 0.2, beam_y + 0.2], color='black', lw=5)

# Function to draw loads
def draw_loads(ax, load_data, beam_y, span_length):
    for load in load_data:
        ax.arrow(load['location'], beam_y + 0.45, 0, -0.3, head_width=0.5, head_length=0.1, fc='red', ec='red')
        ax.text(load['location'], beam_y + 0.45, f'{load["magnitude"]} kN', color='red', ha='center')
        ax.plot([load['location'], load['location']], [beam_y - 0.2, beam_y], 'k--', lw=1)
        ax.text(load['location'], beam_y - 0.3, f'{load["location"]:.2f} m', ha='center', fontsize=10, color='black')

# Visual verification of inputs
if span_length > 0:
    fig, ax = plt.subplots(figsize=(8, 4))
    beam_y = 0

    # Draw beam and supports
    ax.plot([0, span_length], [beam_y, beam_y], color='blue', lw=4)
    draw_support(ax, 0, left_support, beam_y)
    if supports == 'simply supported' and right_support is not None:
        draw_support(ax, span_length, right_support, beam_y)

    # Draw loads
    draw_loads(ax, st.session_state["load_data"], beam_y, span_length)

    # Add span annotation
    ax.text(span_length / 2, beam_y - 1, f'Span = {span_length:.2f} m', ha='center', fontsize=10, color='black')
    ax.set_xlim(-0.5, span_length + 0.5)
    ax.set_ylim(-1.5, 2)
    ax.axis('off')

    # Display the plot
    st.pyplot(fig)

# Button to trigger analysis
st.sidebar.markdown("# Analyze")
analyze_button = st.sidebar.button("Click to Analyze")

# Analyze the beam and display results (only reactions for now)
if analyze_button and span_length > 0:
    # Call the calculate_reactions function
    reactions, reactions_latex = calculate_reactions(supports, span_length, st.session_state["load_data"])
    st.latex(reactions_latex)

    # Display reactions
    st.subheader("Support Reactions")
    if supports == 'simply supported':
        st.markdown(f"Va = {reactions['Va']:.2f} kN", unsafe_allow_html=True)
        st.markdown(f"Vb = {reactions['Vb']:.2f} kN", unsafe_allow_html=True)
    elif supports == 'cantilever':
        st.markdown(f"Va = {reactions['Va']:.2f} kN", unsafe_allow_html=True)
        st.markdown(f"Ma = {reactions['Ma']:.2f} kN·m", unsafe_allow_html=True)

    # Shear Force Diagram
    X_sfd, V_sfd, sfd_latex = calculate_sfd(supports, span_length, st.session_state["load_data"])
    st.latex(sfd_latex)

    fig_sfd, ax_sfd = plt.subplots()
    ax_sfd.plot(X_sfd, V_sfd, label='Shear Force', color='green')
    ax_sfd.set_xlabel("Position along beam (m)")
    ax_sfd.set_ylabel("Shear Force (kN)")
    ax_sfd.grid(True)
    st.pyplot(fig_sfd)

    # Bending Moment Diagram
    X_bmd, M_bmd, bmd_latex = calculate_bmd(supports, span_length, st.session_state["load_data"], reactions)
    st.latex(bmd_latex)
    fig_bmd, ax_bmd = plt.subplots()
    ax_bmd.plot(X_bmd, M_bmd, label='Bending Moment', color='orange')
    ax_bmd.set_xlabel("Position along beam (m)")
    ax_bmd.set_ylabel("Bending Moment (kN·m)")
    ax_bmd.grid(True)
    st.pyplot(fig_bmd)
