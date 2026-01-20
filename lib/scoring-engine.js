/**
 * Ergonomic Scoring Engine - JavaScript Port
 * 
 * Complete RULA and REBA scoring engine ported from Python.
 * All calculations are deterministic and based on official scoring tables.
 */

// =============================================================================
// RULA TABLES (McAtamney & Corlett, 1993)
// =============================================================================

const RULA_TABLE_A = {
    1: {
        1: { 1: { 1: 1, 2: 2 }, 2: { 1: 2, 2: 2 }, 3: { 1: 2, 2: 3 }, 4: { 1: 3, 2: 3 } },
        2: { 1: { 1: 2, 2: 2 }, 2: { 1: 2, 2: 2 }, 3: { 1: 3, 2: 3 }, 4: { 1: 3, 2: 3 } },
        3: { 1: { 1: 2, 2: 3 }, 2: { 1: 3, 2: 3 }, 3: { 1: 3, 2: 3 }, 4: { 1: 4, 2: 4 } }
    },
    2: {
        1: { 1: { 1: 2, 2: 3 }, 2: { 1: 3, 2: 3 }, 3: { 1: 3, 2: 4 }, 4: { 1: 4, 2: 4 } },
        2: { 1: { 1: 3, 2: 3 }, 2: { 1: 3, 2: 3 }, 3: { 1: 3, 2: 4 }, 4: { 1: 4, 2: 4 } },
        3: { 1: { 1: 3, 2: 4 }, 2: { 1: 4, 2: 4 }, 3: { 1: 4, 2: 4 }, 4: { 1: 5, 2: 5 } }
    },
    3: {
        1: { 1: { 1: 3, 2: 3 }, 2: { 1: 4, 2: 4 }, 3: { 1: 4, 2: 4 }, 4: { 1: 5, 2: 5 } },
        2: { 1: { 1: 3, 2: 4 }, 2: { 1: 4, 2: 4 }, 3: { 1: 4, 2: 4 }, 4: { 1: 5, 2: 5 } },
        3: { 1: { 1: 4, 2: 4 }, 2: { 1: 4, 2: 4 }, 3: { 1: 4, 2: 5 }, 4: { 1: 5, 2: 5 } }
    },
    4: {
        1: { 1: { 1: 4, 2: 4 }, 2: { 1: 4, 2: 4 }, 3: { 1: 4, 2: 5 }, 4: { 1: 5, 2: 5 } },
        2: { 1: { 1: 4, 2: 4 }, 2: { 1: 4, 2: 4 }, 3: { 1: 4, 2: 5 }, 4: { 1: 5, 2: 5 } },
        3: { 1: { 1: 4, 2: 4 }, 2: { 1: 4, 2: 5 }, 3: { 1: 5, 2: 5 }, 4: { 1: 6, 2: 6 } }
    },
    5: {
        1: { 1: { 1: 5, 2: 5 }, 2: { 1: 5, 2: 5 }, 3: { 1: 5, 2: 6 }, 4: { 1: 6, 2: 7 } },
        2: { 1: { 1: 5, 2: 6 }, 2: { 1: 6, 2: 6 }, 3: { 1: 6, 2: 7 }, 4: { 1: 7, 2: 7 } },
        3: { 1: { 1: 6, 2: 6 }, 2: { 1: 6, 2: 7 }, 3: { 1: 7, 2: 7 }, 4: { 1: 7, 2: 8 } }
    },
    6: {
        1: { 1: { 1: 7, 2: 7 }, 2: { 1: 7, 2: 7 }, 3: { 1: 7, 2: 8 }, 4: { 1: 8, 2: 9 } },
        2: { 1: { 1: 8, 2: 8 }, 2: { 1: 8, 2: 8 }, 3: { 1: 8, 2: 9 }, 4: { 1: 9, 2: 9 } },
        3: { 1: { 1: 9, 2: 9 }, 2: { 1: 9, 2: 9 }, 3: { 1: 9, 2: 9 }, 4: { 1: 9, 2: 9 } }
    }
};

const RULA_TABLE_B = {
    1: { 1: { 1: 1, 2: 3 }, 2: { 1: 2, 2: 3 }, 3: { 1: 3, 2: 4 }, 4: { 1: 5, 2: 5 }, 5: { 1: 6, 2: 6 }, 6: { 1: 7, 2: 7 } },
    2: { 1: { 1: 2, 2: 3 }, 2: { 1: 2, 2: 3 }, 3: { 1: 4, 2: 5 }, 4: { 1: 5, 2: 5 }, 5: { 1: 6, 2: 7 }, 6: { 1: 7, 2: 7 } },
    3: { 1: { 1: 3, 2: 3 }, 2: { 1: 3, 2: 4 }, 3: { 1: 4, 2: 5 }, 4: { 1: 5, 2: 6 }, 5: { 1: 6, 2: 7 }, 6: { 1: 7, 2: 7 } },
    4: { 1: { 1: 5, 2: 5 }, 2: { 1: 5, 2: 6 }, 3: { 1: 6, 2: 7 }, 4: { 1: 7, 2: 7 }, 5: { 1: 7, 2: 7 }, 6: { 1: 8, 2: 8 } },
    5: { 1: { 1: 7, 2: 7 }, 2: { 1: 7, 2: 7 }, 3: { 1: 7, 2: 8 }, 4: { 1: 8, 2: 8 }, 5: { 1: 8, 2: 8 }, 6: { 1: 8, 2: 8 } },
    6: { 1: { 1: 8, 2: 8 }, 2: { 1: 8, 2: 8 }, 3: { 1: 8, 2: 8 }, 4: { 1: 8, 2: 9 }, 5: { 1: 9, 2: 9 }, 6: { 1: 9, 2: 9 } }
};

const RULA_TABLE_C = {
    1: { 1: 1, 2: 2, 3: 3, 4: 3, 5: 4, 6: 5, 7: 5 },
    2: { 1: 2, 2: 2, 3: 3, 4: 4, 5: 4, 6: 5, 7: 5 },
    3: { 1: 3, 2: 3, 3: 3, 4: 4, 5: 4, 6: 5, 7: 6 },
    4: { 1: 3, 2: 3, 3: 3, 4: 4, 5: 5, 6: 6, 7: 6 },
    5: { 1: 4, 2: 4, 3: 4, 4: 5, 5: 6, 6: 7, 7: 7 },
    6: { 1: 4, 2: 4, 3: 5, 4: 6, 5: 6, 6: 7, 7: 7 },
    7: { 1: 5, 2: 5, 3: 6, 4: 6, 5: 7, 6: 7, 7: 7 },
    8: { 1: 5, 2: 5, 3: 6, 4: 7, 5: 7, 6: 7, 7: 7 }
};

// =============================================================================
// REBA TABLES (Hignett & McAtamney, 2000)
// =============================================================================

const REBA_TABLE_A = {
    1: { 1: { 1: 1, 2: 2, 3: 3, 4: 4 }, 2: { 1: 1, 2: 2, 3: 3, 4: 4 }, 3: { 1: 3, 2: 3, 3: 5, 4: 6 } },
    2: { 1: { 1: 2, 2: 3, 3: 4, 4: 5 }, 2: { 1: 3, 2: 4, 3: 5, 4: 6 }, 3: { 1: 4, 2: 5, 3: 6, 4: 7 } },
    3: { 1: { 1: 2, 2: 4, 3: 5, 4: 6 }, 2: { 1: 4, 2: 5, 3: 6, 4: 7 }, 3: { 1: 5, 2: 6, 3: 7, 4: 8 } },
    4: { 1: { 1: 3, 2: 5, 3: 6, 4: 7 }, 2: { 1: 5, 2: 6, 3: 7, 4: 8 }, 3: { 1: 6, 2: 7, 3: 8, 4: 9 } },
    5: { 1: { 1: 4, 2: 6, 3: 7, 4: 8 }, 2: { 1: 6, 2: 7, 3: 8, 4: 9 }, 3: { 1: 7, 2: 8, 3: 9, 4: 9 } }
};

const REBA_TABLE_B = {
    1: { 1: { 1: 1, 2: 2, 3: 2 }, 2: { 1: 1, 2: 2, 3: 3 } },
    2: { 1: { 1: 1, 2: 2, 3: 3 }, 2: { 1: 2, 2: 3, 3: 4 } },
    3: { 1: { 1: 3, 2: 4, 3: 5 }, 2: { 1: 4, 2: 5, 3: 5 } },
    4: { 1: { 1: 4, 2: 5, 3: 5 }, 2: { 1: 5, 2: 6, 3: 7 } },
    5: { 1: { 1: 6, 2: 7, 3: 8 }, 2: { 1: 7, 2: 8, 3: 8 } },
    6: { 1: { 1: 7, 2: 8, 3: 8 }, 2: { 1: 8, 2: 9, 3: 9 } }
};

const REBA_TABLE_C = {
    1: { 1: 1, 2: 1, 3: 1, 4: 2, 5: 3, 6: 3, 7: 4, 8: 5, 9: 6, 10: 7, 11: 7, 12: 7 },
    2: { 1: 1, 2: 2, 3: 2, 4: 3, 5: 4, 6: 4, 7: 5, 8: 6, 9: 6, 10: 7, 11: 7, 12: 8 },
    3: { 1: 2, 2: 3, 3: 3, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7, 9: 7, 10: 8, 11: 8, 12: 8 },
    4: { 1: 3, 2: 4, 3: 4, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 8, 10: 9, 11: 9, 12: 9 },
    5: { 1: 4, 2: 4, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 8, 9: 9, 10: 9, 11: 9, 12: 9 },
    6: { 1: 6, 2: 6, 3: 6, 4: 7, 5: 8, 6: 8, 7: 9, 8: 9, 9: 10, 10: 10, 11: 10, 12: 10 },
    7: { 1: 7, 2: 7, 3: 7, 4: 8, 5: 9, 6: 9, 7: 9, 8: 10, 9: 10, 10: 11, 11: 11, 12: 11 },
    8: { 1: 8, 2: 8, 3: 8, 4: 9, 5: 10, 6: 10, 7: 10, 8: 10, 9: 10, 10: 11, 11: 11, 12: 11 },
    9: { 1: 9, 2: 9, 3: 9, 4: 10, 5: 10, 6: 10, 7: 11, 8: 11, 9: 11, 10: 12, 11: 12, 12: 12 },
    10: { 1: 10, 2: 10, 3: 10, 4: 11, 5: 11, 6: 11, 7: 11, 8: 12, 9: 12, 10: 12, 11: 12, 12: 12 },
    11: { 1: 11, 2: 11, 3: 11, 4: 11, 5: 12, 6: 12, 7: 12, 8: 12, 9: 12, 10: 12, 11: 12, 12: 12 },
    12: { 1: 12, 2: 12, 3: 12, 4: 12, 5: 12, 6: 12, 7: 12, 8: 12, 9: 12, 10: 12, 11: 12, 12: 12 }
};

// =============================================================================
// ACTION LEVELS AND RISK LEVELS
// =============================================================================

function getRulaActionLevel(score) {
    if (score <= 2) {
        return {
            level: 1,
            description: 'Acceptable posture',
            action: 'Posture is acceptable if not maintained or repeated for long periods',
            urgency: 'None required',
            color: '#22c55e'
        };
    } else if (score <= 4) {
        return {
            level: 2,
            description: 'Further investigation needed',
            action: 'Further investigation is needed and changes may be required',
            urgency: 'Review when possible',
            color: '#84cc16'
        };
    } else if (score <= 6) {
        return {
            level: 3,
            description: 'Investigation and changes required soon',
            action: 'Investigation and changes are required soon',
            urgency: 'Within 1-2 weeks',
            color: '#f97316'
        };
    } else {
        return {
            level: 4,
            description: 'Immediate investigation and changes required',
            action: 'Investigation and changes are required immediately',
            urgency: 'Immediate action',
            color: '#ef4444'
        };
    }
}

function getRebaRiskLevel(score) {
    const levels = {
        1: { level: 'Negligible', riskValue: 1, description: 'Negligible risk', action: 'None necessary', color: '#22c55e', urgency: 'No action required' },
        2: { level: 'Low', riskValue: 2, description: 'Low risk', action: 'Change may be needed', color: '#84cc16', urgency: 'Review when possible' },
        3: { level: 'Low', riskValue: 2, description: 'Low risk', action: 'Change may be needed', color: '#84cc16', urgency: 'Review when possible' },
        4: { level: 'Medium', riskValue: 3, description: 'Medium risk', action: 'Further investigation, change soon', color: '#eab308', urgency: 'Within 1-2 weeks' },
        5: { level: 'Medium', riskValue: 3, description: 'Medium risk', action: 'Further investigation, change soon', color: '#eab308', urgency: 'Within 1-2 weeks' },
        6: { level: 'Medium', riskValue: 3, description: 'Medium risk', action: 'Further investigation, change soon', color: '#eab308', urgency: 'Within 1-2 weeks' },
        7: { level: 'Medium', riskValue: 3, description: 'Medium risk', action: 'Further investigation, change soon', color: '#eab308', urgency: 'Within 1-2 weeks' },
        8: { level: 'High', riskValue: 4, description: 'High risk', action: 'Investigate and implement change', color: '#f97316', urgency: 'Soon, within 1 week' },
        9: { level: 'High', riskValue: 4, description: 'High risk', action: 'Investigate and implement change', color: '#f97316', urgency: 'Soon, within 1 week' },
        10: { level: 'High', riskValue: 4, description: 'High risk', action: 'Investigate and implement change', color: '#f97316', urgency: 'Soon, within 1 week' },
        11: { level: 'Very High', riskValue: 5, description: 'Very high risk', action: 'Implement change immediately', color: '#ef4444', urgency: 'Immediate action required' },
        12: { level: 'Very High', riskValue: 5, description: 'Very high risk', action: 'Implement change immediately', color: '#ef4444', urgency: 'Immediate action required' }
    };
    return levels[Math.min(Math.max(score, 1), 12)];
}

// =============================================================================
// RULA SCORING ENGINE
// =============================================================================

class RULAEngine {
    constructor(options = {}) {
        this.isStatic = options.isStatic ?? true;
        this.loadKg = options.loadKg ?? 0;
        this.isRepetitive = options.isRepetitive ?? false;
        this.isShockLoad = options.isShockLoad ?? false;
    }

    calculate(angles) {
        const result = {
            components: {},
            groupScores: {},
            modifiers: {},
            finalScore: 0,
            actionLevel: {}
        };

        // Score individual components
        result.components.upperArm = this.scoreUpperArm(angles);
        result.components.lowerArm = this.scoreLowerArm(angles);
        result.components.wrist = this.scoreWrist(angles);
        result.components.wristTwist = this.scoreWristTwist(angles);
        result.components.neck = this.scoreNeck(angles);
        result.components.trunk = this.scoreTrunk(angles);
        result.components.legs = this.scoreLegs(angles);

        // Table A lookup
        const ua = Math.min(Math.max(result.components.upperArm.finalScore, 1), 6);
        const la = Math.min(Math.max(result.components.lowerArm.finalScore, 1), 3);
        const w = Math.min(Math.max(result.components.wrist.finalScore, 1), 4);
        const wt = Math.min(Math.max(result.components.wristTwist.finalScore, 1), 2);
        result.groupScores.scoreARaw = RULA_TABLE_A[ua][la][w][wt];

        // Table B lookup
        const n = Math.min(Math.max(result.components.neck.finalScore, 1), 6);
        const t = Math.min(Math.max(result.components.trunk.finalScore, 1), 6);
        const l = Math.min(Math.max(result.components.legs.finalScore, 1), 2);
        result.groupScores.scoreBRaw = RULA_TABLE_B[n][t][l];

        // Muscle use and force scores
        result.modifiers.muscleUseA = (this.isStatic || this.isRepetitive) ? 1 : 0;
        result.modifiers.forceLoadA = this.getForceLoadScore();
        result.modifiers.muscleUseB = result.modifiers.muscleUseA;
        result.modifiers.forceLoadB = result.modifiers.forceLoadA;

        result.groupScores.scoreA = result.groupScores.scoreARaw + result.modifiers.muscleUseA + result.modifiers.forceLoadA;
        result.groupScores.scoreB = result.groupScores.scoreBRaw + result.modifiers.muscleUseB + result.modifiers.forceLoadB;

        // Table C lookup
        const scoreAClamped = Math.min(Math.max(result.groupScores.scoreA, 1), 8);
        const scoreBClamped = Math.min(Math.max(result.groupScores.scoreB, 1), 7);
        result.finalScore = RULA_TABLE_C[scoreAClamped][scoreBClamped];

        // Get action level
        const action = getRulaActionLevel(result.finalScore);
        result.actionLevel = {
            level: action.level,
            description: action.description,
            action: action.action,
            urgency: action.urgency,
            color: action.color
        };

        return result;
    }

    scoreUpperArm(angles) {
        const angle = angles.upperArmFlexion || 0;
        let rawScore, threshold;

        if (angle >= -20 && angle <= 20) {
            rawScore = 1; threshold = '20° extension to 20° flexion';
        } else if (angle > 20 && angle <= 45) {
            rawScore = 2; threshold = '20°-45° flexion';
        } else if (angle > 45 && angle <= 90) {
            rawScore = 3; threshold = '45°-90° flexion';
        } else if (angle > 90) {
            rawScore = 4; threshold = '>90° flexion';
        } else {
            rawScore = 3; threshold = '>45° extension';
        }

        let modifier = 0;
        const modifiers = [];
        if (angles.shoulderRaised) { modifier += 1; modifiers.push('+1 shoulder raised'); }
        if ((angles.upperArmAbduction || 0) > 45) { modifier += 1; modifiers.push('+1 arm abducted'); }
        if (angles.armSupported) { modifier -= 1; modifiers.push('-1 arm supported'); }

        return {
            rawScore,
            modifiers,
            finalScore: Math.max(1, Math.min(6, rawScore + modifier)),
            angle,
            threshold
        };
    }

    scoreLowerArm(angles) {
        const angle = angles.lowerArmFlexion || 90;
        let rawScore, threshold;

        if (angle >= 60 && angle <= 100) {
            rawScore = 1; threshold = '60°-100° flexion (optimal)';
        } else {
            rawScore = 2; threshold = '<60° or >100° flexion';
        }

        let modifier = 0;
        const modifiers = [];
        if (angles.lowerArmAcrossMidline) { modifier += 1; modifiers.push('+1 arm across midline'); }
        if ((angles.upperArmAbduction || 0) > 30) { modifier += 1; modifiers.push('+1 arm out to side'); }

        return {
            rawScore,
            modifiers,
            finalScore: Math.max(1, Math.min(3, rawScore + modifier)),
            angle,
            threshold
        };
    }

    scoreWrist(angles) {
        const angle = Math.max(angles.wristFlexion || 0, angles.wristExtension || 0);
        let rawScore, threshold;

        if (angle === 0) {
            rawScore = 1; threshold = 'Neutral position';
        } else if (angle <= 15) {
            rawScore = 2; threshold = '0°-15° flexion/extension';
        } else {
            rawScore = 3; threshold = '>15° flexion/extension';
        }

        let modifier = 0;
        const modifiers = [];
        if ((angles.wristDeviation || 0) > 15) { modifier += 1; modifiers.push('+1 wrist deviated'); }

        return {
            rawScore,
            modifiers,
            finalScore: Math.max(1, Math.min(4, rawScore + modifier)),
            angle,
            threshold
        };
    }

    scoreWristTwist(angles) {
        const isTwisted = angles.wristTwist || false;
        return {
            rawScore: isTwisted ? 2 : 1,
            modifiers: [],
            finalScore: isTwisted ? 2 : 1,
            angle: 0,
            threshold: isTwisted ? 'Near end of twisting range' : 'Mid-range of twist'
        };
    }

    scoreNeck(angles) {
        const flexion = angles.neckFlexion || 0;
        const extension = angles.neckExtension || 0;
        let rawScore, threshold;

        if (extension > 0) {
            rawScore = 4; threshold = 'Neck in extension';
        } else if (flexion >= 0 && flexion <= 10) {
            rawScore = 1; threshold = '0°-10° flexion';
        } else if (flexion > 10 && flexion <= 20) {
            rawScore = 2; threshold = '10°-20° flexion';
        } else {
            rawScore = 3; threshold = '>20° flexion';
        }

        let modifier = 0;
        const modifiers = [];
        if (Math.abs(angles.neckTwist || 0) > 10) { modifier += 1; modifiers.push('+1 neck twisted'); }
        if (Math.abs(angles.neckSideBend || 0) > 10) { modifier += 1; modifiers.push('+1 neck side-bending'); }

        return {
            rawScore,
            modifiers,
            finalScore: Math.max(1, Math.min(6, rawScore + modifier)),
            angle: flexion,
            threshold
        };
    }

    scoreTrunk(angles) {
        const angle = angles.trunkFlexion || 0;
        let rawScore, threshold;

        if (angle === 0) {
            rawScore = 1; threshold = 'Upright/well supported';
        } else if (angle > 0 && angle <= 20) {
            rawScore = 2; threshold = '0°-20° flexion';
        } else if (angle > 20 && angle <= 60) {
            rawScore = 3; threshold = '20°-60° flexion';
        } else {
            rawScore = 4; threshold = '>60° flexion';
        }

        let modifier = 0;
        const modifiers = [];
        if (Math.abs(angles.trunkTwist || 0) > 10) { modifier += 1; modifiers.push('+1 trunk twisted'); }
        if (Math.abs(angles.trunkSideBend || 0) > 10) { modifier += 1; modifiers.push('+1 trunk side-bending'); }

        return {
            rawScore,
            modifiers,
            finalScore: Math.max(1, Math.min(6, rawScore + modifier)),
            angle,
            threshold
        };
    }

    scoreLegs(angles) {
        const supported = angles.legSupported !== false;
        const weightEven = angles.legWeightEven !== false;
        return {
            rawScore: (supported && weightEven) ? 1 : 2,
            modifiers: [],
            finalScore: (supported && weightEven) ? 1 : 2,
            angle: angles.legFlexion || 90,
            threshold: (supported && weightEven) ? 'Legs supported, weight balanced' : 'Legs not supported or weight uneven'
        };
    }

    getForceLoadScore() {
        if (this.isShockLoad) return 3;
        if (this.loadKg > 10) return this.isStatic ? 3 : 2;
        if (this.loadKg >= 2) return this.isStatic ? 2 : 1;
        return 0;
    }
}

// =============================================================================
// REBA SCORING ENGINE
// =============================================================================

class REBAEngine {
    constructor(options = {}) {
        this.loadKg = options.loadKg ?? 0;
        this.coupling = options.coupling ?? 'good';
        this.isStatic = options.isStatic ?? false;
        this.isRepeated = options.isRepeated ?? false;
        this.hasRapidChange = options.hasRapidChange ?? false;
        this.isShockLoad = options.isShockLoad ?? false;
    }

    calculate(angles) {
        const result = {
            groupA: {},
            groupB: {},
            scoreC: 0,
            activityScore: 0,
            finalScore: 0,
            riskAssessment: {}
        };

        // Group A: Trunk, Neck, Legs
        result.groupA.trunk = this.scoreTrunk(angles);
        result.groupA.neck = this.scoreNeck(angles);
        result.groupA.legs = this.scoreLegs(angles);

        // Group B: Upper Arm, Lower Arm, Wrist
        result.groupB.upperArm = this.scoreUpperArm(angles);
        result.groupB.lowerArm = this.scoreLowerArm(angles);
        result.groupB.wrist = this.scoreWrist(angles);

        // Table A lookup
        const t = Math.min(Math.max(result.groupA.trunk.finalScore, 1), 5);
        const n = Math.min(Math.max(result.groupA.neck.finalScore, 1), 3);
        const l = Math.min(Math.max(result.groupA.legs.finalScore, 1), 4);
        result.groupA.scoreARaw = REBA_TABLE_A[t][n][l];
        result.groupA.loadForce = this.getLoadForceScore();
        result.groupA.scoreA = result.groupA.scoreARaw + result.groupA.loadForce;

        // Table B lookup
        const ua = Math.min(Math.max(result.groupB.upperArm.finalScore, 1), 6);
        const la = Math.min(Math.max(result.groupB.lowerArm.finalScore, 1), 2);
        const w = Math.min(Math.max(result.groupB.wrist.finalScore, 1), 3);
        result.groupB.scoreBRaw = REBA_TABLE_B[ua][la][w];
        result.groupB.coupling = this.getCouplingScore();
        result.groupB.scoreB = result.groupB.scoreBRaw + result.groupB.coupling;

        // Table C lookup
        const scoreA = Math.min(Math.max(result.groupA.scoreA, 1), 12);
        const scoreB = Math.min(Math.max(result.groupB.scoreB, 1), 12);
        result.scoreC = REBA_TABLE_C[scoreA][scoreB];

        // Activity score
        result.activityScore = this.getActivityScore();
        result.finalScore = result.scoreC + result.activityScore;

        // Risk assessment
        const risk = getRebaRiskLevel(result.finalScore);
        result.riskAssessment = {
            level: risk.level,
            riskValue: risk.riskValue,
            description: risk.description,
            action: risk.action,
            urgency: risk.urgency,
            color: risk.color
        };

        return result;
    }

    scoreTrunk(angles) {
        const angle = angles.trunkFlexion || 0;
        let rawScore, threshold;

        if (angle === 0) {
            rawScore = 1; threshold = 'Upright';
        } else if (angle > 0 && angle <= 20) {
            rawScore = 2; threshold = '0°-20° flexion';
        } else if (angle > 20 && angle <= 60) {
            rawScore = 3; threshold = '20°-60° flexion';
        } else {
            rawScore = 4; threshold = '>60° flexion';
        }

        let modifier = 0;
        const modifiers = [];
        if (Math.abs(angles.trunkTwist || 0) > 10) { modifier += 1; modifiers.push('+1 trunk twisted'); }
        if (Math.abs(angles.trunkSideBend || 0) > 10) { modifier += 1; modifiers.push('+1 trunk side-bending'); }

        return {
            rawScore,
            modifiers,
            finalScore: Math.max(1, Math.min(5, rawScore + modifier)),
            angle,
            threshold
        };
    }

    scoreNeck(angles) {
        const flexion = angles.neckFlexion || 0;
        let rawScore, threshold;

        if (flexion >= 0 && flexion <= 20) {
            rawScore = 1; threshold = '0°-20° flexion';
        } else {
            rawScore = 2; threshold = '>20° flexion';
        }

        if ((angles.neckExtension || 0) > 0) {
            rawScore = 2; threshold = 'In extension';
        }

        let modifier = 0;
        const modifiers = [];
        if (Math.abs(angles.neckTwist || 0) > 10) { modifier += 1; modifiers.push('+1 neck twisted'); }
        if (Math.abs(angles.neckSideBend || 0) > 10) { modifier += 1; modifiers.push('+1 neck side-bending'); }

        return {
            rawScore,
            modifiers,
            finalScore: Math.max(1, Math.min(3, rawScore + modifier)),
            angle: flexion,
            threshold
        };
    }

    scoreLegs(angles) {
        const weightEven = angles.legWeightEven !== false;
        let rawScore = weightEven ? 1 : 2;
        const threshold = weightEven ? 'Bilateral weight bearing' : 'Unilateral weight bearing';

        let modifier = 0;
        const modifiers = [];
        const flexion = angles.legFlexion || 0;
        if (flexion >= 30 && flexion <= 60) { modifier += 1; modifiers.push('+1 knees 30°-60° flexion'); }
        else if (flexion > 60) { modifier += 2; modifiers.push('+2 knees >60° flexion'); }

        return {
            rawScore,
            modifiers,
            finalScore: Math.max(1, Math.min(4, rawScore + modifier)),
            angle: flexion,
            threshold
        };
    }

    scoreUpperArm(angles) {
        const angle = angles.upperArmFlexion || 0;
        let rawScore, threshold;

        if (angle >= -20 && angle <= 20) {
            rawScore = 1; threshold = '20° extension to 20° flexion';
        } else if (angle > 20 && angle <= 45) {
            rawScore = 2; threshold = '20°-45° flexion';
        } else if (angle > 45 && angle <= 90) {
            rawScore = 3; threshold = '45°-90° flexion';
        } else if (angle > 90) {
            rawScore = 4; threshold = '>90° flexion';
        } else {
            rawScore = 3; threshold = '>45° extension';
        }

        let modifier = 0;
        const modifiers = [];
        if (angles.shoulderRaised) { modifier += 1; modifiers.push('+1 shoulder raised'); }
        if ((angles.upperArmAbduction || 0) > 45) { modifier += 1; modifiers.push('+1 arm abducted'); }
        if (angles.armSupported) { modifier -= 1; modifiers.push('-1 arm supported'); }

        return {
            rawScore,
            modifiers,
            finalScore: Math.max(1, Math.min(6, rawScore + modifier)),
            angle,
            threshold
        };
    }

    scoreLowerArm(angles) {
        const angle = angles.lowerArmFlexion || 90;
        let rawScore, threshold;

        if (angle >= 60 && angle <= 100) {
            rawScore = 1; threshold = '60°-100° flexion';
        } else {
            rawScore = 2; threshold = '<60° or >100° flexion';
        }

        return {
            rawScore,
            modifiers: [],
            finalScore: rawScore,
            angle,
            threshold
        };
    }

    scoreWrist(angles) {
        const angle = Math.max(angles.wristFlexion || 0, angles.wristExtension || 0);
        let rawScore, threshold;

        if (angle <= 15) {
            rawScore = 1; threshold = '0°-15° flexion/extension';
        } else {
            rawScore = 2; threshold = '>15° flexion/extension';
        }

        let modifier = 0;
        const modifiers = [];
        if ((angles.wristDeviation || 0) > 15 || angles.wristTwist) {
            modifier += 1;
            modifiers.push('+1 wrist bent/twisted');
        }

        return {
            rawScore,
            modifiers,
            finalScore: Math.max(1, Math.min(3, rawScore + modifier)),
            angle,
            threshold
        };
    }

    getLoadForceScore() {
        let base = 0;
        if (this.loadKg < 5) base = 0;
        else if (this.loadKg <= 10) base = 1;
        else base = 2;
        if (this.isShockLoad) base += 1;
        return Math.min(base, 3);
    }

    getCouplingScore() {
        const map = { good: 0, fair: 1, poor: 2, unacceptable: 3 };
        return map[this.coupling.toLowerCase()] ?? 0;
    }

    getActivityScore() {
        let score = 0;
        if (this.isStatic) score += 1;
        if (this.isRepeated) score += 1;
        if (this.hasRapidChange) score += 1;
        return Math.min(score, 3);
    }
}

// =============================================================================
// RECOMMENDATION ENGINE
// =============================================================================

function generateRecommendations(angles, rulaResult, rebaResult) {
    const recommendations = {
        overallRiskStatement: '',
        immediateActions: [],
        shortTermActions: [],
        longTermActions: [],
        workstationAdjustments: [],
        trainingNeeds: [],
        monitoringPlan: ''
    };

    // Generate overall risk statement
    const rulaScore = rulaResult.finalScore;
    const rebaScore = rebaResult.finalScore;

    if (rulaScore >= 7 || rebaScore >= 11) {
        recommendations.overallRiskStatement = `CRITICAL ERGONOMIC RISK IDENTIFIED. RULA Score: ${rulaScore}/7 (Action Level ${rulaResult.actionLevel.level}), REBA Score: ${rebaScore}/15 (${rebaResult.riskAssessment.level} Risk). Immediate intervention is required to prevent musculoskeletal injury.`;
    } else if (rulaScore >= 5 || rebaScore >= 8) {
        recommendations.overallRiskStatement = `HIGH ERGONOMIC RISK DETECTED. RULA Score: ${rulaScore}/7 (Action Level ${rulaResult.actionLevel.level}), REBA Score: ${rebaScore}/15 (${rebaResult.riskAssessment.level} Risk). Investigation and corrective action should be implemented soon.`;
    } else if (rulaScore >= 3 || rebaScore >= 4) {
        recommendations.overallRiskStatement = `MODERATE ERGONOMIC RISK PRESENT. RULA Score: ${rulaScore}/7 (Action Level ${rulaResult.actionLevel.level}), REBA Score: ${rebaScore}/15 (${rebaResult.riskAssessment.level} Risk). Further investigation is recommended.`;
    } else {
        recommendations.overallRiskStatement = `LOW ERGONOMIC RISK. RULA Score: ${rulaScore}/7 (Action Level ${rulaResult.actionLevel.level}), REBA Score: ${rebaScore}/15 (${rebaResult.riskAssessment.level} Risk). Current posture is within acceptable limits.`;
    }

    // Neck recommendations
    const neckScore = Math.max(rulaResult.components.neck.finalScore, rebaResult.groupA.neck.finalScore);
    if (neckScore >= 3) {
        const rec = {
            priority: neckScore >= 4 ? 1 : 2,
            category: neckScore >= 4 ? 'immediate' : 'shortTerm',
            bodyPart: 'neck',
            title: 'Neck Posture Correction Required',
            description: `Neck flexion of ${angles.neckFlexion?.toFixed(1) || 0}° exceeds optimal range.`,
            actions: [
                'Position computer monitor at eye level or slightly below',
                'Use a document holder positioned beside the monitor',
                'Take micro-breaks every 20 minutes to reset neck position'
            ]
        };
        if (neckScore >= 4) recommendations.immediateActions.push(rec);
        else recommendations.shortTermActions.push(rec);
    }

    // Trunk recommendations
    const trunkScore = Math.max(rulaResult.components.trunk.finalScore, rebaResult.groupA.trunk.finalScore);
    if (trunkScore >= 3) {
        const rec = {
            priority: trunkScore >= 4 ? 1 : 2,
            category: trunkScore >= 4 ? 'immediate' : 'shortTerm',
            bodyPart: 'trunk',
            title: 'Trunk Posture Improvement Needed',
            description: `Trunk flexion of ${angles.trunkFlexion?.toFixed(1) || 0}° increases spinal loading.`,
            actions: [
                'Ensure chair provides adequate lumbar support',
                'Adjust seat height so feet are flat on floor',
                'Consider a sit-stand workstation to vary posture'
            ]
        };
        if (trunkScore >= 4) recommendations.immediateActions.push(rec);
        else recommendations.shortTermActions.push(rec);
    }

    // Upper arm recommendations
    const upperArmScore = Math.max(rulaResult.components.upperArm.finalScore, rebaResult.groupB.upperArm.finalScore);
    if (upperArmScore >= 3) {
        recommendations.shortTermActions.push({
            priority: 2,
            category: 'shortTerm',
            bodyPart: 'shoulder',
            title: 'Shoulder Posture Optimization',
            description: `Upper arm elevation of ${angles.upperArmFlexion?.toFixed(1) || 0}° increases muscle fatigue.`,
            actions: [
                'Lower work surface or raise seating to reduce arm elevation',
                'Position keyboard and mouse close to body',
                'Use armrests to support forearms during typing'
            ]
        });
    }

    // Wrist recommendations
    const wristAngle = Math.max(angles.wristFlexion || 0, angles.wristExtension || 0);
    if (wristAngle > 15 || (angles.wristDeviation || 0) > 15) {
        recommendations.shortTermActions.push({
            priority: 2,
            category: 'shortTerm',
            bodyPart: 'wrist',
            title: 'Wrist Posture Correction',
            description: `Wrist deviation from neutral increases risk of carpal tunnel syndrome.`,
            actions: [
                'Keep wrists straight and neutral during typing',
                'Consider ergonomic keyboard with split design',
                'Use whole arm to move mouse, not just wrist'
            ]
        });
    }

    // Workstation recommendations
    if (rulaScore >= 3 || rebaScore >= 4) {
        recommendations.workstationAdjustments.push({
            priority: 2,
            category: 'shortTerm',
            bodyPart: 'general',
            title: 'Workstation Ergonomic Assessment',
            description: 'Multiple postural issues suggest systematic workstation review is needed.',
            actions: [
                'Conduct full workstation ergonomic assessment',
                'Review monitor, keyboard, mouse, and chair positions',
                'Consider ergonomic accessories (document holder, footrest)'
            ]
        });
    }

    // Training needs
    recommendations.trainingNeeds = [
        'Ergonomic awareness and good posture principles',
        'Proper workstation setup and adjustment',
        'Stretching and micro-break exercises'
    ];

    // Monitoring plan
    if (rulaScore >= 7 || rebaScore >= 11) {
        recommendations.monitoringPlan = 'IMMEDIATE FOLLOW-UP REQUIRED: Re-assess within 1 week after implementing changes.';
    } else if (rulaScore >= 5 || rebaScore >= 8) {
        recommendations.monitoringPlan = 'SHORT-TERM MONITORING: Re-assess within 2 weeks after implementing changes.';
    } else if (rulaScore >= 3 || rebaScore >= 4) {
        recommendations.monitoringPlan = 'PERIODIC MONITORING: Re-assess within 1 month after implementing changes.';
    } else {
        recommendations.monitoringPlan = 'MAINTENANCE MONITORING: Annual ergonomic re-assessment recommended.';
    }

    return recommendations;
}

// Export for use in serverless function and browser
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { RULAEngine, REBAEngine, generateRecommendations };
}

// Also export for browser/ES modules
if (typeof window !== 'undefined') {
    window.ScoringEngine = { RULAEngine, REBAEngine, generateRecommendations };
}
