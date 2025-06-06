"""
Helper functions for DBS Environment.
"""

import numpy as np


class SimulationConfig:
    """
    A temporary consolidation of shared parameters until I figure out how
    best to share them.
    """

    def __init__(
            self,
            duration=25_000,  # (ms) duration of simulation
            step_size=0.1,  # (ms)
            sample_duration=20,  # (ms)
            seed=None,
    ):
        self.seed = seed
        self.duration = duration
        self.step_size = step_size
        self.sample_duration = sample_duration


def make_synaptic_connections(num_pre, num_post, epsilon):
    """
    Returns a lookup table for synaptic connections and the number of
    connections made.

    A connection is established with a probability defined by `epsilon`.

    The synapse at `lut[pre, post]` represents a synaptic connection from a
    pre-synaptic neuron `pre` to a post-synaptic neuron `post`.
    """

    # synaptic connection lookup table
    syn_lut = np.zeros((num_pre, num_post), dtype=int)
    count = 0
    for i in range(num_pre):
        for j in range(num_post):
            if np.random.rand() <= epsilon:
                count += 1
                syn_lut[i, j] = count

    return syn_lut, count


def pulsatile_input(multi, v_stim, t_stim, x, duration, step_size):
    """
    Function to generate pulsatile input for the Ue and Ui

    multi: relative duration of the anodic and cathodic phases
    v_stim: stimulation voltage
    t_stim: pulse width
    x: duration of the neutral phase
    duration: duration of the simulation
    step: time step
    :return: Ue, Ui
    """

    num_steps = int(duration / step_size)

    Ue = np.zeros(num_steps)
    Ui = np.zeros(num_steps)

    # biphasic pulse shape symmetric = 1, asymmetric > 1
    pulse_shape = 1  # uses multi instead?

    # Ue input
    t = 0  # current time
    for i in range(num_steps):
        t += step_size

        # Anodic (negative) phase.
        if 0 <= t < t_stim:
            Ue[i] = -v_stim / multi

        # Cathodic (positive) phase.
        if t_stim <= t < 2 * t_stim + step_size:
            Ue[i] = v_stim

        # Neutral phase.
        if 2 * t_stim + step_size <= t < (2 + x) * t_stim + step_size:
            Ue[i] = 0

        # Additional anodic phase (if multi > 1).
        if (2 + x) * t_stim + step_size <= t < (2 + x + multi - 1) * t_stim:
            Ue[i] = -v_stim / multi

        # Reset time step.
        if t >= (2 + x + multi - 1) * t_stim - 0.01:
            t = 0
            Ue[i] = 0

    # Ui input
    t = 0
    for i in range(num_steps):
        t += step_size

        # cathodic phase
        if 0 <= t < t_stim:
            Ui[i] = v_stim

        # anodic phase
        if t_stim <= t < (multi + 1) * t_stim + step_size:
            Ui[i] = -v_stim / multi

        # neutral phase
        if (multi + 1) * t_stim + step_size <= t < (multi + 1 + x) * t_stim:
            Ui[i] = 0

        if t >= (multi + 1 + x) * t_stim - 0.01:
            t = 0
            Ui[i] = 0

    return Ue, Ui
