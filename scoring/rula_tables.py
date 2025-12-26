"""
RULA Scoring Tables - Official Lookup Tables for RULA Assessment

These tables are exact reproductions of the official RULA methodology
as published by McAtamney & Corlett (1993).

All scoring is deterministic and rule-based with no heuristics.
"""

# =============================================================================
# UPPER ARM SCORING (Score 1-6)
# =============================================================================

# Upper arm position score based on angle from vertical
UPPER_ARM_POSITION = {
    # (min_angle, max_angle): base_score
    (-20, 20): 1,    # 20° extension to 20° flexion
    (20, 45): 2,     # 20°-45° flexion
    (45, 90): 3,     # 45°-90° flexion
    (90, 180): 4,    # >90° flexion
    (-45, -20): 2,   # 20°-45° extension
    (-90, -45): 3,   # >45° extension
}

# Upper arm modifiers
UPPER_ARM_MODIFIERS = {
    'shoulder_raised': 1,      # +1 if shoulder is raised
    'arm_abducted': 1,        # +1 if arm is abducted
    'arm_supported': -1,      # -1 if arm is supported or person is leaning
}


# =============================================================================
# LOWER ARM SCORING (Score 1-3)
# =============================================================================

# Lower arm (elbow) position score based on elbow flexion angle
LOWER_ARM_POSITION = {
    # (min_angle, max_angle): base_score
    (60, 100): 1,    # 60°-100° flexion (optimal)
    (0, 60): 2,      # <60° or >100° flexion
    (100, 180): 2,   # >100° flexion
}

# Lower arm modifiers
LOWER_ARM_MODIFIERS = {
    'arm_across_midline': 1,   # +1 if working across midline of body
    'arm_out_to_side': 1,      # +1 if arm is working out to side of body
}


# =============================================================================
# WRIST SCORING (Score 1-4)
# =============================================================================

# Wrist position score based on wrist angle
WRIST_POSITION = {
    # (min_angle, max_angle): base_score
    (0, 0): 1,       # Neutral position
    (-15, 15): 2,    # 0°-15° flexion or extension
    (15, 180): 3,    # >15° flexion or extension
    (-180, -15): 3,  # >15° extension
}

# Wrist modifiers
WRIST_MODIFIERS = {
    'wrist_bent_from_midline': 1,  # +1 if wrist is bent away from midline (deviation)
}

# Wrist twist scoring
WRIST_TWIST = {
    'mid_range': 1,       # Wrist is mainly in mid-range of twist
    'near_end_range': 2,  # Wrist is at or near end of twisting range
}


# =============================================================================
# NECK SCORING (Score 1-6)
# =============================================================================

# Neck position score based on neck flexion angle
NECK_POSITION = {
    # (min_angle, max_angle): base_score
    (0, 10): 1,      # 0°-10° flexion
    (10, 20): 2,     # 10°-20° flexion
    (20, 90): 3,     # >20° flexion
    (-90, 0): 4,     # Extension (neck bent backward)
}

# Neck modifiers
NECK_MODIFIERS = {
    'neck_twisted': 1,     # +1 if neck is twisted
    'neck_side_bending': 1, # +1 if neck is side-bending
}


# =============================================================================
# TRUNK SCORING (Score 1-6)
# =============================================================================

# Trunk position score based on trunk flexion angle
TRUNK_POSITION = {
    # (min_angle, max_angle): base_score
    (0, 0): 1,        # Upright/sitting well supported
    (0, 20): 2,       # 0°-20° flexion
    (20, 60): 3,      # 20°-60° flexion
    (60, 180): 4,     # >60° flexion
}

# Trunk modifiers
TRUNK_MODIFIERS = {
    'trunk_twisted': 1,     # +1 if trunk is twisted
    'trunk_side_bending': 1, # +1 if trunk is side-bending
}


# =============================================================================
# LEGS SCORING (Score 1-2)
# =============================================================================

LEGS_POSITION = {
    'legs_supported_balanced': 1,    # Legs/feet well supported, weight evenly balanced
    'legs_not_supported': 2,         # Legs/feet NOT supported, weight NOT evenly balanced
}


# =============================================================================
# MUSCLE USE AND FORCE SCORES
# =============================================================================

MUSCLE_USE_SCORE = {
    'static': 1,      # +1 if posture mainly static (held >1 min)
    'repetitive': 1,  # +1 if action repeated >4 times/minute
    'dynamic': 0,     # No addition if posture is changing and not repetitive
}

FORCE_LOAD_SCORE = {
    'light': 0,       # Load < 2 kg, intermittent
    'moderate': 1,    # Load 2-10 kg, intermittent
    'moderate_static': 2,  # Load 2-10 kg, static or repeated
    'heavy': 2,       # Load > 10 kg, intermittent
    'heavy_static': 3,     # Load > 10 kg, static or repeated
    'shock': 3,       # Shock or forces with rapid buildup
}


# =============================================================================
# TABLE A - WRIST POSTURE SCORE
# Combines: Upper Arm, Lower Arm, Wrist, Wrist Twist
# =============================================================================

# Table A structure: TABLE_A[upper_arm][lower_arm][wrist][wrist_twist]
# Indices: upper_arm (1-6), lower_arm (1-3), wrist (1-4), wrist_twist (1-2)
TABLE_A = {
    1: {
        1: {
            1: {1: 1, 2: 2}, 2: {1: 2, 2: 2}, 3: {1: 2, 2: 3}, 4: {1: 3, 2: 3}
        },
        2: {
            1: {1: 2, 2: 2}, 2: {1: 2, 2: 2}, 3: {1: 3, 2: 3}, 4: {1: 3, 2: 3}
        },
        3: {
            1: {1: 2, 2: 3}, 2: {1: 3, 2: 3}, 3: {1: 3, 2: 3}, 4: {1: 4, 2: 4}
        }
    },
    2: {
        1: {
            1: {1: 2, 2: 3}, 2: {1: 3, 2: 3}, 3: {1: 3, 2: 4}, 4: {1: 4, 2: 4}
        },
        2: {
            1: {1: 3, 2: 3}, 2: {1: 3, 2: 3}, 3: {1: 3, 2: 4}, 4: {1: 4, 2: 4}
        },
        3: {
            1: {1: 3, 2: 4}, 2: {1: 4, 2: 4}, 3: {1: 4, 2: 4}, 4: {1: 5, 2: 5}
        }
    },
    3: {
        1: {
            1: {1: 3, 2: 3}, 2: {1: 4, 2: 4}, 3: {1: 4, 2: 4}, 4: {1: 5, 2: 5}
        },
        2: {
            1: {1: 3, 2: 4}, 2: {1: 4, 2: 4}, 3: {1: 4, 2: 4}, 4: {1: 5, 2: 5}
        },
        3: {
            1: {1: 4, 2: 4}, 2: {1: 4, 2: 4}, 3: {1: 4, 2: 5}, 4: {1: 5, 2: 5}
        }
    },
    4: {
        1: {
            1: {1: 4, 2: 4}, 2: {1: 4, 2: 4}, 3: {1: 4, 2: 5}, 4: {1: 5, 2: 5}
        },
        2: {
            1: {1: 4, 2: 4}, 2: {1: 4, 2: 4}, 3: {1: 4, 2: 5}, 4: {1: 5, 2: 5}
        },
        3: {
            1: {1: 4, 2: 4}, 2: {1: 4, 2: 5}, 3: {1: 5, 2: 5}, 4: {1: 6, 2: 6}
        }
    },
    5: {
        1: {
            1: {1: 5, 2: 5}, 2: {1: 5, 2: 5}, 3: {1: 5, 2: 6}, 4: {1: 6, 2: 7}
        },
        2: {
            1: {1: 5, 2: 6}, 2: {1: 6, 2: 6}, 3: {1: 6, 2: 7}, 4: {1: 7, 2: 7}
        },
        3: {
            1: {1: 6, 2: 6}, 2: {1: 6, 2: 7}, 3: {1: 7, 2: 7}, 4: {1: 7, 2: 8}
        }
    },
    6: {
        1: {
            1: {1: 7, 2: 7}, 2: {1: 7, 2: 7}, 3: {1: 7, 2: 8}, 4: {1: 8, 2: 9}
        },
        2: {
            1: {1: 8, 2: 8}, 2: {1: 8, 2: 8}, 3: {1: 8, 2: 9}, 4: {1: 9, 2: 9}
        },
        3: {
            1: {1: 9, 2: 9}, 2: {1: 9, 2: 9}, 3: {1: 9, 2: 9}, 4: {1: 9, 2: 9}
        }
    }
}


# =============================================================================
# TABLE B - NECK/TRUNK/LEGS SCORE
# Combines: Neck, Trunk, Legs
# =============================================================================

# Table B structure: TABLE_B[neck][trunk][legs]
# Indices: neck (1-6), trunk (1-6), legs (1-2)
TABLE_B = {
    1: {
        1: {1: 1, 2: 3}, 2: {1: 2, 2: 3}, 3: {1: 3, 2: 4}, 4: {1: 5, 2: 5}, 5: {1: 6, 2: 6}, 6: {1: 7, 2: 7}
    },
    2: {
        1: {1: 2, 2: 3}, 2: {1: 2, 2: 3}, 3: {1: 4, 2: 5}, 4: {1: 5, 2: 5}, 5: {1: 6, 2: 7}, 6: {1: 7, 2: 7}
    },
    3: {
        1: {1: 3, 2: 3}, 2: {1: 3, 2: 4}, 3: {1: 4, 2: 5}, 4: {1: 5, 2: 6}, 5: {1: 6, 2: 7}, 6: {1: 7, 2: 7}
    },
    4: {
        1: {1: 5, 2: 5}, 2: {1: 5, 2: 6}, 3: {1: 6, 2: 7}, 4: {1: 7, 2: 7}, 5: {1: 7, 2: 7}, 6: {1: 8, 2: 8}
    },
    5: {
        1: {1: 7, 2: 7}, 2: {1: 7, 2: 7}, 3: {1: 7, 2: 8}, 4: {1: 8, 2: 8}, 5: {1: 8, 2: 8}, 6: {1: 8, 2: 8}
    },
    6: {
        1: {1: 8, 2: 8}, 2: {1: 8, 2: 8}, 3: {1: 8, 2: 8}, 4: {1: 8, 2: 9}, 5: {1: 9, 2: 9}, 6: {1: 9, 2: 9}
    }
}


# =============================================================================
# TABLE C - FINAL RULA SCORE
# Combines: Score A (from Table A + muscle/force) and Score B (from Table B + muscle/force)
# =============================================================================

# Table C structure: TABLE_C[score_a][score_b]
# Indices: score_a (1-8), score_b (1-7)
TABLE_C = {
    1: {1: 1, 2: 2, 3: 3, 4: 3, 5: 4, 6: 5, 7: 5},
    2: {1: 2, 2: 2, 3: 3, 4: 4, 5: 4, 6: 5, 7: 5},
    3: {1: 3, 2: 3, 3: 3, 4: 4, 5: 4, 6: 5, 7: 6},
    4: {1: 3, 2: 3, 3: 3, 4: 4, 5: 5, 6: 6, 7: 6},
    5: {1: 4, 2: 4, 3: 4, 4: 5, 5: 6, 6: 7, 7: 7},
    6: {1: 4, 2: 4, 3: 5, 4: 6, 5: 6, 6: 7, 7: 7},
    7: {1: 5, 2: 5, 3: 6, 4: 6, 5: 7, 6: 7, 7: 7},
    8: {1: 5, 2: 5, 3: 6, 4: 7, 5: 7, 6: 7, 7: 7}
}


# =============================================================================
# ACTION LEVELS
# =============================================================================

ACTION_LEVELS = {
    (1, 2): {
        'level': 1,
        'description': 'Acceptable posture',
        'action': 'Posture is acceptable if not maintained or repeated for long periods',
        'urgency': 'None required',
        'color': '#22c55e'
    },
    (3, 4): {
        'level': 2,
        'description': 'Further investigation needed',
        'action': 'Further investigation is needed and changes may be required',
        'urgency': 'Review when possible',
        'color': '#84cc16'
    },
    (5, 6): {
        'level': 3,
        'description': 'Investigation and changes required soon',
        'action': 'Investigation and changes are required soon',
        'urgency': 'Within 1-2 weeks',
        'color': '#f97316'
    },
    (7, 7): {  # Score 7+
        'level': 4,
        'description': 'Immediate investigation and changes required',
        'action': 'Investigation and changes are required immediately',
        'urgency': 'Immediate action',
        'color': '#ef4444'
    }
}


def get_action_level(score: int) -> dict:
    """Get the action level details for a given RULA score."""
    if score <= 2:
        return ACTION_LEVELS[(1, 2)]
    elif score <= 4:
        return ACTION_LEVELS[(3, 4)]
    elif score <= 6:
        return ACTION_LEVELS[(5, 6)]
    else:
        return ACTION_LEVELS[(7, 7)]
