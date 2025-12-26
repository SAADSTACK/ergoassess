"""
Standards Database - ISO/HSE Ergonomic Standards Reference

Contains reference standards and guidelines for ergonomic assessment
and workplace recommendations aligned with international standards.
"""

# =============================================================================
# ISO STANDARDS REFERENCE
# =============================================================================

ISO_STANDARDS = {
    'ISO 11226': {
        'title': 'Ergonomics — Evaluation of static working postures',
        'scope': 'Static posture assessment for work positions maintained for extended periods',
        'key_principles': [
            'Neutral postures minimize musculoskeletal stress',
            'Static postures should be limited in duration',
            'Joint angles should remain within acceptable ranges',
            'Support structures reduce postural load'
        ],
        'posture_guidelines': {
            'neck': {
                'acceptable': '0° to 25° flexion',
                'conditionally_acceptable': '25° to 85° flexion, or in extension if supported',
                'not_acceptable': '>85° flexion, unsupported extension'
            },
            'trunk': {
                'acceptable': '0° to 20° flexion with support',
                'conditionally_acceptable': '20° to 60° flexion',
                'not_acceptable': '>60° flexion without support'
            },
            'upper_arm': {
                'acceptable': '0° to 20° flexion, no abduction',
                'conditionally_acceptable': '20° to 60° flexion or slight abduction',
                'not_acceptable': '>60° flexion or significant abduction'
            }
        }
    },
    'ISO 11228-1': {
        'title': 'Ergonomics — Manual handling — Part 1: Lifting and carrying',
        'scope': 'Assessment of risks from lifting and carrying tasks',
        'key_principles': [
            'Reduce load weight where possible',
            'Improve grip and coupling',
            'Minimize reach distance',
            'Avoid twisting during lifts'
        ],
        'load_limits': {
            'reference_mass': '25 kg (professional workers)',
            'optimal_conditions': 'Up to 25 kg with ideal posture and coupling',
            'reduced_conditions': 'Reduce by multipliers based on posture, frequency, coupling'
        }
    },
    'ISO 11228-3': {
        'title': 'Ergonomics — Manual handling — Part 3: Handling of low loads at high frequency',
        'scope': 'Repetitive tasks with low force but high frequency',
        'key_principles': [
            'Limit repetition rates',
            'Provide adequate rest breaks',
            'Minimize force requirements',
            'Avoid awkward postures during repetitive tasks'
        ]
    },
    'EN 1005-4': {
        'title': 'Safety of machinery — Human physical performance — Part 4: Machine handling postures',
        'scope': 'Evaluation of working postures and movements in machinery operation',
        'key_principles': [
            'Design for neutral postures',
            'Avoid sustained static postures',
            'Minimize extreme joint positions',
            'Consider anthropometric variability'
        ]
    }
}


# =============================================================================
# HSE GUIDANCE REFERENCE
# =============================================================================

HSE_GUIDANCE = {
    'upper_limb_disorders': {
        'title': 'Upper limb disorders in the workplace',
        'reference': 'HSG60',
        'key_recommendations': [
            'Design tasks to avoid repetitive movements',
            'Provide adequate breaks and job rotation',
            'Ensure workstation is adjustable',
            'Train workers on correct postures'
        ]
    },
    'display_screen_equipment': {
        'title': 'Working with display screen equipment',
        'reference': 'L26',
        'key_recommendations': [
            'Eyes should be level with top of monitor',
            'Arms should be horizontal when typing',
            'Feet should be flat on floor or footrest',
            'Regular breaks from screen work'
        ]
    },
    'manual_handling': {
        'title': 'Manual handling at work',
        'reference': 'L23',
        'key_recommendations': [
            'Avoid manual handling where possible',
            'Assess remaining handling operations',
            'Reduce risk of injury to lowest practical level',
            'Review assessments periodically'
        ]
    }
}


# =============================================================================
# ERGONOMIC PRINCIPLES
# =============================================================================

ERGONOMIC_PRINCIPLES = {
    'neutral_posture': {
        'definition': 'A comfortable working posture where joints are naturally aligned',
        'characteristics': [
            'Spine maintains natural S-curve',
            'Shoulders relaxed, not elevated',
            'Elbows close to body at ~90°',
            'Wrists straight, not bent or twisted',
            'Thighs parallel to floor',
            'Feet flat on floor or supported'
        ]
    },
    'work_zone': {
        'primary': 'Area within forearm reach (30-40 cm) - frequent tasks',
        'secondary': 'Area within arm reach (40-60 cm) - occasional tasks',
        'tertiary': 'Beyond arm reach - infrequent tasks only'
    },
    'task_design': {
        'principles': [
            'Minimize reach distance',
            'Allow postural variation',
            'Provide adequate rest periods',
            'Match task demands to worker capabilities',
            'Enable job rotation'
        ]
    }
}


# =============================================================================
# BODY-PART SPECIFIC GUIDANCE
# =============================================================================

BODY_PART_GUIDANCE = {
    'neck': {
        'risks': [
            'Forward head posture leading to neck strain',
            'Prolonged neck flexion causing muscle fatigue',
            'Twisted neck from poor monitor placement'
        ],
        'recommendations': [
            'Position monitor at eye level',
            'Use document holders beside monitor',
            'Take micro-breaks every 20-30 minutes',
            'Perform neck stretches regularly'
        ]
    },
    'trunk': {
        'risks': [
            'Forward trunk flexion increasing disc pressure',
            'Twisting combined with bending',
            'Sustained static postures'
        ],
        'recommendations': [
            'Provide lumbar support in seating',
            'Ensure work surface is at appropriate height',
            'Avoid prolonged forward reaching',
            'Use sit-stand workstations where appropriate'
        ]
    },
    'shoulders': {
        'risks': [
            'Elevated shoulders from high work surface',
            'Abducted arms from wide workstation layout',
            'Static muscle loading'
        ],
        'recommendations': [
            'Lower work surface or raise seating',
            'Bring tasks closer to body midline',
            'Provide arm rests for supported work',
            'Allow regular shoulder relaxation breaks'
        ]
    },
    'elbows': {
        'risks': [
            'Extreme flexion or extension',
            'Sustained static positions',
            'Contact stress from hard surfaces'
        ],
        'recommendations': [
            'Maintain 80-120° elbow angle',
            'Use padded armrests',
            'Vary tasks to change elbow position',
            'Avoid leaning on elbows'
        ]
    },
    'wrists': {
        'risks': [
            'Flexion or extension beyond neutral',
            'Ulnar/radial deviation',
            'Repetitive motions',
            'Contact stress from desk edge'
        ],
        'recommendations': [
            'Keep wrists straight during keyboard use',
            'Use split or ergonomic keyboards',
            'Position mouse close to keyboard',
            'Use padded wrist rests during pauses only'
        ]
    },
    'legs': {
        'risks': [
            'Prolonged sitting reducing circulation',
            'Feet dangling without support',
            'Uneven weight distribution'
        ],
        'recommendations': [
            'Use footrest if feet do not reach floor',
            'Ensure adequate thigh clearance',
            'Alternate between sitting and standing',
            'Take walking breaks regularly'
        ]
    }
}


# =============================================================================
# WORKSTATION TYPES
# =============================================================================

WORKSTATION_GUIDANCE = {
    'computer_workstation': {
        'monitor': [
            'Position at arm\'s length distance',
            'Top of screen at or slightly below eye level',
            'Tilt screen 10-20° back',
            'Reduce glare with proper positioning or filters'
        ],
        'keyboard': [
            'Position directly in front of user',
            'Height allowing relaxed shoulders',
            'Slight negative tilt if possible',
            'Wrists straight during typing'
        ],
        'mouse': [
            'Position beside keyboard at same height',
            'Use whole arm for large movements',
            'Consider vertical or trackball alternatives',
            'Alternate hands if possible'
        ],
        'chair': [
            'Adjustable seat height and depth',
            'Lumbar support at lower back curve',
            'Armrests at elbow height when relaxed',
            'Five-point base for stability'
        ]
    },
    'industrial_workstation': {
        'work_surface': [
            'Height based on task requirements',
            'Precision work: higher surface (5-10 cm above elbow)',
            'Light work: at elbow height',
            'Heavy work: below elbow height'
        ],
        'standing': [
            'Anti-fatigue matting',
            'Footrail or footrest',
            'Ability to shift weight',
            'Sit-stand capability where possible'
        ],
        'material_handling': [
            'Position frequently used items in primary work zone',
            'Use mechanical aids for heavy items',
            'Provide bin tilters and lift tables',
            'Minimize floor-to-overhead motions'
        ]
    }
}


def get_standard_reference(standard_code: str) -> dict:
    """Get reference information for a specific standard."""
    if standard_code in ISO_STANDARDS:
        return ISO_STANDARDS[standard_code]
    return None


def get_body_part_guidance(body_part: str) -> dict:
    """Get ergonomic guidance for a specific body part."""
    return BODY_PART_GUIDANCE.get(body_part.lower(), {})


def get_workstation_guidance(workstation_type: str) -> dict:
    """Get guidance for a specific workstation type."""
    return WORKSTATION_GUIDANCE.get(workstation_type.lower(), {})
