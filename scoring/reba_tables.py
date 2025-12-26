"""
REBA Scoring Tables - Official Lookup Tables for REBA Assessment

These tables are exact reproductions of the official REBA methodology
as published by Hignett & McAtamney (2000).

All scoring is deterministic and rule-based with no heuristics.
"""

# =============================================================================
# TRUNK SCORING (Score 1-5)
# =============================================================================

TRUNK_POSITION = {
    # (min_angle, max_angle): base_score
    (0, 0): 1,        # Upright
    (0, 20): 2,       # 0°-20° flexion or extension
    (20, 60): 3,      # 20°-60° flexion, >20° extension
    (60, 180): 4,     # >60° flexion
}

TRUNK_MODIFIERS = {
    'trunk_twisted': 1,     # +1 if trunk is twisted
    'trunk_side_bending': 1, # +1 if trunk is side-bending
}


# =============================================================================
# NECK SCORING (Score 1-3)
# =============================================================================

NECK_POSITION = {
    # (min_angle, max_angle): base_score
    (0, 20): 1,       # 0°-20° flexion
    (20, 180): 2,     # >20° flexion or in extension
}

NECK_MODIFIERS = {
    'neck_twisted': 1,      # +1 if neck is twisted
    'neck_side_bending': 1, # +1 if neck is side-bending
}


# =============================================================================
# LEGS SCORING (Score 1-4)
# =============================================================================

LEGS_POSITION = {
    'bilateral_weight_bearing': 1,    # Walking or sitting, bilateral weight-bearing
    'unilateral_weight_bearing': 2,   # Unilateral weight bearing, feather weight bearing, or unstable posture
}

LEGS_MODIFIERS = {
    'knee_flexion_30_60': 1,  # +1 if knees bent 30°-60°
    'knee_flexion_over_60': 2, # +2 if knees bent >60° (except seated)
}


# =============================================================================
# UPPER ARM SCORING (Score 1-6)
# =============================================================================

UPPER_ARM_POSITION = {
    # (min_angle, max_angle): base_score
    (-20, 20): 1,     # 20° extension to 20° flexion
    (20, 45): 2,      # 20°-45° flexion, >20° extension
    (45, 90): 3,      # 45°-90° flexion
    (90, 180): 4,     # >90° flexion
}

UPPER_ARM_MODIFIERS = {
    'shoulder_raised': 1,     # +1 if shoulder is raised
    'arm_abducted': 1,        # +1 if arm is abducted
    'arm_supported': -1,      # -1 if leaning or arm supported
}


# =============================================================================
# LOWER ARM SCORING (Score 1-2)
# =============================================================================

LOWER_ARM_POSITION = {
    # (min_angle, max_angle): base_score
    (60, 100): 1,     # 60°-100° flexion
    (0, 60): 2,       # <60° or >100° flexion
    (100, 180): 2,
}


# =============================================================================
# WRIST SCORING (Score 1-3)
# =============================================================================

WRIST_POSITION = {
    # (min_angle, max_angle): base_score
    (0, 15): 1,       # 0°-15° flexion or extension
    (15, 180): 2,     # >15° flexion or extension
}

WRIST_MODIFIERS = {
    'wrist_bent_or_twisted': 1,  # +1 if wrist is bent from midline or twisted
}


# =============================================================================
# LOAD/FORCE SCORE
# =============================================================================

LOAD_FORCE_SCORE = {
    'light': 0,           # Load < 5 kg
    'moderate': 1,        # Load 5-10 kg
    'heavy': 2,           # Load > 10 kg
    'shock_or_rapid': 1,  # +1 additional if shock or rapid build up of force
}


# =============================================================================
# COUPLING SCORE
# =============================================================================

COUPLING_SCORE = {
    'good': 0,         # Well fitted handle and mid-range power grip
    'fair': 1,         # Hand hold acceptable but not ideal, or coupling is acceptable
    'poor': 2,         # Hand hold not acceptable although possible
    'unacceptable': 3, # No handles, coupling is awkward, unsafe, or not possible, body part used for coupling
}


# =============================================================================
# ACTIVITY SCORE
# =============================================================================

ACTIVITY_SCORE = {
    'static': 1,           # +1 if one or more body parts are static (>1 min)
    'repeated_small': 1,   # +1 if repeated small range actions (>4x/min)
    'rapid_large': 1,      # +1 if action causes rapid large range changes in postures
}


# =============================================================================
# TABLE A - TRUNK/NECK/LEGS
# Combines posture scores to get Score A
# =============================================================================

# Table A structure: TABLE_A[trunk][neck][legs]
# Indices: trunk (1-5), neck (1-3), legs (1-4)
TABLE_A = {
    1: {
        1: {1: 1, 2: 2, 3: 3, 4: 4},
        2: {1: 1, 2: 2, 3: 3, 4: 4},
        3: {1: 3, 2: 3, 3: 5, 4: 6}
    },
    2: {
        1: {1: 2, 2: 3, 3: 4, 4: 5},
        2: {1: 3, 2: 4, 3: 5, 4: 6},
        3: {1: 4, 2: 5, 3: 6, 4: 7}
    },
    3: {
        1: {1: 2, 2: 4, 3: 5, 4: 6},
        2: {1: 4, 2: 5, 3: 6, 4: 7},
        3: {1: 5, 2: 6, 3: 7, 4: 8}
    },
    4: {
        1: {1: 3, 2: 5, 3: 6, 4: 7},
        2: {1: 5, 2: 6, 3: 7, 4: 8},
        3: {1: 6, 2: 7, 3: 8, 4: 9}
    },
    5: {
        1: {1: 4, 2: 6, 3: 7, 4: 8},
        2: {1: 6, 2: 7, 3: 8, 4: 9},
        3: {1: 7, 2: 8, 3: 9, 4: 9}
    }
}


# =============================================================================
# TABLE B - UPPER ARM/LOWER ARM/WRIST
# Combines posture scores to get Score B
# =============================================================================

# Table B structure: TABLE_B[upper_arm][lower_arm][wrist]
# Indices: upper_arm (1-6), lower_arm (1-2), wrist (1-3)
TABLE_B = {
    1: {
        1: {1: 1, 2: 2, 3: 2},
        2: {1: 1, 2: 2, 3: 3}
    },
    2: {
        1: {1: 1, 2: 2, 3: 3},
        2: {1: 2, 2: 3, 3: 4}
    },
    3: {
        1: {1: 3, 2: 4, 3: 5},
        2: {1: 4, 2: 5, 3: 5}
    },
    4: {
        1: {1: 4, 2: 5, 3: 5},
        2: {1: 5, 2: 6, 3: 7}
    },
    5: {
        1: {1: 6, 2: 7, 3: 8},
        2: {1: 7, 2: 8, 3: 8}
    },
    6: {
        1: {1: 7, 2: 8, 3: 8},
        2: {1: 8, 2: 9, 3: 9}
    }
}


# =============================================================================
# TABLE C - FINAL REBA SCORE
# Combines Score A and Score B to get final REBA score
# =============================================================================

# Table C structure: TABLE_C[score_a][score_b]
# Indices: score_a (1-12), score_b (1-12)
TABLE_C = {
    1: {1: 1, 2: 1, 3: 1, 4: 2, 5: 3, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 7, 12: 7},
    2: {1: 1, 2: 2, 3: 2, 4: 3, 5: 4, 6: 4, 7: 5, 8: 6, 9: 6, 10: 7, 11: 7, 12: 8},
    3: {1: 2, 2: 3, 3: 3, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 7, 10: 8, 11: 8, 12: 8},
    4: {1: 3, 2: 4, 3: 4, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 8, 10: 9, 11: 9, 12: 9},
    5: {1: 4, 2: 4, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 8, 9: 9, 10: 9, 11: 9, 12: 9},
    6: {1: 6, 2: 6, 3: 6, 4: 7, 5: 8, 6: 8, 7: 9, 8: 9, 9: 10, 10: 10, 11: 10, 12: 10},
    7: {1: 7, 2: 7, 3: 7, 4: 8, 5: 9, 6: 9, 7: 9, 8: 10, 9: 10, 10: 11, 11: 11, 12: 11},
    8: {1: 8, 2: 8, 3: 8, 4: 9, 5: 10, 6: 10, 7: 10, 8: 10, 9: 10, 10: 11, 11: 11, 12: 11},
    9: {1: 9, 2: 9, 3: 9, 4: 10, 5: 10, 6: 10, 7: 11, 8: 11, 9: 11, 10: 12, 11: 12, 12: 12},
    10: {1: 10, 2: 10, 3: 10, 4: 11, 5: 11, 6: 11, 7: 11, 8: 12, 9: 12, 10: 12, 11: 12, 12: 12},
    11: {1: 11, 2: 11, 3: 11, 4: 11, 5: 12, 6: 12, 7: 12, 8: 12, 9: 12, 10: 12, 11: 12, 12: 12},
    12: {1: 12, 2: 12, 3: 12, 4: 12, 5: 12, 6: 12, 7: 12, 8: 12, 9: 12, 10: 12, 11: 12, 12: 12}
}


# =============================================================================
# RISK LEVELS
# =============================================================================

RISK_LEVELS = {
    1: {
        'level': 'Negligible',
        'risk_value': 1,
        'description': 'Negligible risk',
        'action': 'None necessary',
        'color': '#22c55e',
        'urgency': 'No action required'
    },
    2: {
        'level': 'Low',
        'risk_value': 2,
        'description': 'Low risk',
        'action': 'Change may be needed',
        'color': '#84cc16',
        'urgency': 'Review when possible'
    },
    3: {
        'level': 'Low',
        'risk_value': 2,
        'description': 'Low risk',
        'action': 'Change may be needed',
        'color': '#84cc16',
        'urgency': 'Review when possible'
    },
    4: {
        'level': 'Medium',
        'risk_value': 3,
        'description': 'Medium risk',
        'action': 'Further investigation, change soon',
        'color': '#eab308',
        'urgency': 'Within 1-2 weeks'
    },
    5: {
        'level': 'Medium',
        'risk_value': 3,
        'description': 'Medium risk',
        'action': 'Further investigation, change soon',
        'color': '#eab308',
        'urgency': 'Within 1-2 weeks'
    },
    6: {
        'level': 'Medium',
        'risk_value': 3,
        'description': 'Medium risk',
        'action': 'Further investigation, change soon',
        'color': '#eab308',
        'urgency': 'Within 1-2 weeks'
    },
    7: {
        'level': 'Medium',
        'risk_value': 3,
        'description': 'Medium risk',
        'action': 'Further investigation, change soon',
        'color': '#eab308',
        'urgency': 'Within 1-2 weeks'
    },
    8: {
        'level': 'High',
        'risk_value': 4,
        'description': 'High risk',
        'action': 'Investigate and implement change',
        'color': '#f97316',
        'urgency': 'Soon, within 1 week'
    },
    9: {
        'level': 'High',
        'risk_value': 4,
        'description': 'High risk',
        'action': 'Investigate and implement change',
        'color': '#f97316',
        'urgency': 'Soon, within 1 week'
    },
    10: {
        'level': 'High',
        'risk_value': 4,
        'description': 'High risk',
        'action': 'Investigate and implement change',
        'color': '#f97316',
        'urgency': 'Soon, within 1 week'
    },
    11: {
        'level': 'Very High',
        'risk_value': 5,
        'description': 'Very high risk',
        'action': 'Implement change immediately',
        'color': '#ef4444',
        'urgency': 'Immediate action required'
    },
    12: {
        'level': 'Very High',
        'risk_value': 5,
        'description': 'Very high risk',
        'action': 'Implement change immediately',
        'color': '#ef4444',
        'urgency': 'Immediate action required'
    },
    13: {
        'level': 'Very High',
        'risk_value': 5,
        'description': 'Very high risk',
        'action': 'Implement change immediately',
        'color': '#ef4444',
        'urgency': 'Immediate action required'
    },
    14: {
        'level': 'Very High',
        'risk_value': 5,
        'description': 'Very high risk',
        'action': 'Implement change immediately',
        'color': '#ef4444',
        'urgency': 'Immediate action required'
    },
    15: {
        'level': 'Very High',
        'risk_value': 5,
        'description': 'Very high risk',
        'action': 'Implement change immediately',
        'color': '#ef4444',
        'urgency': 'Immediate action required'
    }
}


def get_risk_level(score: int) -> dict:
    """Get the risk level details for a given REBA score."""
    # Clamp to valid range
    score = max(1, min(15, score))
    return RISK_LEVELS[score]
