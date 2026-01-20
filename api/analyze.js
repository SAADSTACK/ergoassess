/**
 * Serverless API - Ergonomic Posture Analysis
 * Vercel Serverless Function using Gemini Vision API
 */

// Import scoring engine
const { RULAEngine, REBAEngine, generateRecommendations } = require('../lib/scoring-engine.js');

// Gemini API configuration
const GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent';

// Detailed prompt for posture analysis
const POSTURE_ANALYSIS_PROMPT = `You are an expert ergonomic posture analyst. Analyze this image and extract body joint angles for RULA/REBA ergonomic assessment.

CRITICAL: You must return ONLY a valid JSON object with NO additional text, markdown, or code blocks. Do not include \`\`\`json or any other formatting.

Analyze the person's posture in the image and estimate the following angles in degrees:

{
  "poseDetected": true or false,
  "angles": {
    "neckFlexion": number (0-60, forward bend of neck),
    "neckExtension": number (0-30, backward bend of neck),
    "neckTwist": number (0-45, rotation of neck),
    "neckSideBend": number (0-45, lateral bend of neck),
    "trunkFlexion": number (0-90, forward bend of trunk/torso),
    "trunkExtension": number (0-30, backward lean),
    "trunkTwist": number (0-45, rotation of trunk),
    "trunkSideBend": number (0-45, lateral bend of trunk),
    "upperArmFlexion": number (-20 to 180, shoulder/arm elevation forward),
    "upperArmAbduction": number (0-90, arm raised to side),
    "shoulderRaised": boolean (true if shoulder is raised/shrugged),
    "armSupported": boolean (true if arm is resting on support),
    "lowerArmFlexion": number (0-180, elbow bend angle),
    "lowerArmAcrossMidline": boolean (true if forearm crosses body midline),
    "wristFlexion": number (0-90, wrist bent down),
    "wristExtension": number (0-70, wrist bent up),
    "wristDeviation": number (0-45, wrist bent sideways),
    "wristTwist": boolean (true if forearm is pronated/supinated at extreme),
    "legFlexion": number (0-150, knee bend angle),
    "legSupported": boolean (true if feet are supported on floor),
    "legWeightEven": boolean (true if weight is evenly distributed)
  },
  "description": "Brief description of the observed posture",
  "concerns": ["List of main ergonomic concerns observed"]
}

Guidelines:
- If you cannot see a body part clearly, estimate based on visible context
- Use 0 for neutral/straight positions
- neckFlexion: looking down increases this value
- trunkFlexion: bending forward increases this value  
- upperArmFlexion: arm raised forward increases this (negative = behind body)
- lowerArmFlexion: 90° is right angle at elbow, 180° is straight arm
- If no person is visible or pose cannot be detected, set poseDetected to false

Return ONLY the JSON object, nothing else.`;

module.exports = async function handler(req, res) {
    // Enable CORS
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }

    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    try {
        const { image, isStatic, loadKg, coupling, isRepetitive, subjectId } = req.body;

        if (!image) {
            return res.status(400).json({ error: 'No image data provided' });
        }

        // Get API key from environment
        const apiKey = process.env.GEMINI_API_KEY;
        if (!apiKey) {
            return res.status(500).json({ error: 'API key not configured' });
        }

        // Extract base64 image data
        let imageData = image;
        let mimeType = 'image/jpeg';

        if (image.startsWith('data:')) {
            const matches = image.match(/^data:([^;]+);base64,(.+)$/);
            if (matches) {
                mimeType = matches[1];
                imageData = matches[2];
            }
        }

        // Call Gemini Vision API
        const geminiResponse = await fetch(`${GEMINI_API_URL}?key=${apiKey}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                contents: [{
                    parts: [
                        { text: POSTURE_ANALYSIS_PROMPT },
                        {
                            inline_data: {
                                mime_type: mimeType,
                                data: imageData
                            }
                        }
                    ]
                }],
                generationConfig: {
                    temperature: 0.1,
                    topP: 0.8,
                    maxOutputTokens: 2048
                }
            })
        });

        if (!geminiResponse.ok) {
            const errorText = await geminiResponse.text();
            console.error('Gemini API error:', errorText);
            return res.status(500).json({
                error: 'Failed to analyze image',
                details: errorText
            });
        }

        const geminiData = await geminiResponse.json();

        // Extract text response
        let responseText = '';
        if (geminiData.candidates && geminiData.candidates[0]?.content?.parts) {
            responseText = geminiData.candidates[0].content.parts
                .map(p => p.text || '')
                .join('');
        }

        // Parse JSON from response
        let analysisResult;
        try {
            // Clean up response - remove markdown code blocks if present
            responseText = responseText
                .replace(/```json\s*/gi, '')
                .replace(/```\s*/g, '')
                .trim();

            analysisResult = JSON.parse(responseText);
        } catch (parseError) {
            console.error('Failed to parse Gemini response:', responseText);
            return res.status(500).json({
                error: 'Failed to parse posture analysis',
                rawResponse: responseText.substring(0, 500)
            });
        }

        if (!analysisResult.poseDetected) {
            return res.status(400).json({
                error: 'Could not detect pose in image',
                suggestion: 'Please ensure the person is clearly visible with good lighting.'
            });
        }

        const angles = analysisResult.angles;

        // Calculate RULA score
        const rulaEngine = new RULAEngine({
            isStatic: isStatic !== false,
            loadKg: loadKg || 0,
            isRepetitive: isRepetitive || false
        });
        const rulaResult = rulaEngine.calculate(angles);

        // Calculate REBA score
        const rebaEngine = new REBAEngine({
            loadKg: loadKg || 0,
            coupling: coupling || 'good',
            isStatic: isStatic !== false,
            isRepeated: isRepetitive || false
        });
        const rebaResult = rebaEngine.calculate(angles);

        // Generate recommendations
        const recommendations = generateRecommendations(angles, rulaResult, rebaResult);

        // Generate assessment ID
        const assessmentId = `EA-${Date.now()}-${Math.random().toString(36).substr(2, 6)}`;

        // Build response
        const response = {
            success: true,
            assessmentId,
            timestamp: new Date().toISOString(),
            subjectId: subjectId || 'Anonymous',

            posture: {
                description: analysisResult.description,
                concerns: analysisResult.concerns
            },

            angles,

            rula: {
                score: rulaResult.finalScore,
                actionLevel: rulaResult.actionLevel.level,
                actionDescription: rulaResult.actionLevel.description,
                actionRecommendation: rulaResult.actionLevel.action,
                actionUrgency: rulaResult.actionLevel.urgency,
                color: rulaResult.actionLevel.color,
                details: rulaResult
            },

            reba: {
                score: rebaResult.finalScore,
                riskLevel: rebaResult.riskAssessment.level,
                riskDescription: rebaResult.riskAssessment.description,
                riskAction: rebaResult.riskAssessment.action,
                riskUrgency: rebaResult.riskAssessment.urgency,
                color: rebaResult.riskAssessment.color,
                details: rebaResult
            },

            recommendations
        };

        return res.status(200).json(response);

    } catch (error) {
        console.error('Analysis error:', error);
        return res.status(500).json({
            error: 'Internal server error',
            message: error.message
        });
    }
};
