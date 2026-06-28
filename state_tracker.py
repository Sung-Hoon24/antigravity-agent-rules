import json

# State Machine Definition File
FUNNEL_SCHEMA = {
    "title": "The Hard Problem - Funnel Flow Map",
    "total_duration": 300,  # 5 minutes (in seconds)
    "scenes": [
        {
            "timecode_start": "0:00",
            "timecode_end": "2:30",
            "state": "S1 - Authority Build-up",
            "goal": "Establish premise and define the problem.",
            "assets": ["DeepIndigo_BG.mp4", "Neuro_Broll.mp4"],
            "logic_check": "Verify logical consistency between physical science and subjective experience.",
        },
        {
            "timecode_start": "2:30",
            "timecode_end": "3:05",
            "state": "T1 - Conceptual Failure Gateway",
            "goal": "Trigger initial logical discomfort.",
            "component": "ERROR_4001",  # Designer Component Name
            "props": {
                "trigger_source": "LogicGap",
                "duration": 2.5,
                "intensity": "High",
            },
            "action": "Forced visual/audio interruption (Glitch VFX).",
        },
        {
            "timecode_start": "3:05",
            "timecode_end": "4:15",
            "state": "S2 - Information Deficiency Amplification",
            "goal": "Personalize the knowledge gap and increase anxiety.",
            "assets": ["QuestionMark_Broll.mp4"],
            "logic_check": "Maintain ambiguity; avoid providing a simple answer.",
        },
        {
            "timecode_start": "4:15",
            "timecode_end": "END",
            "state": "T2 - Funnel Transition Point (Paywall)",
            "goal": "Mandate the need for external, structured knowledge.",
            "component": "ERROR_4001 + CTA Overlay",
            "props": {
                "trigger_source": "ExternalResourceNeeded",
                "duration": 3.0,
                "intensity": "Medium-Low",
            },
            "action": "Hard stop on narrative; force user attention to the CTA button.",
        },
    ],
}


def save_schema(data):
    """Saves the schema definition as a JSON file for easy developer reference."""
    filepath = "funnel_state_machine_v1.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"\n✅ Schema successfully saved to {filepath}")


if __name__ == "__main__":
    save_schema(FUNNEL_SCHEMA)
