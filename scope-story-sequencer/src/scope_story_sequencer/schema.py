from pydantic import Field
from scope.core.pipelines.base_schema import BasePipelineConfig
from scope.core.ui_schema import ui_field_config

class StorySequencerConfig(BasePipelineConfig):
    pipeline_id: str = "scope-story-sequencer"
    pipeline_name: str = "Story Sequencer"
    pipeline_description: str = "A real-time prompt sequencer and transition controller."
    
    # Defaults to VIDEO mode (preprocessor)
    modes: dict = {"video": {"default": True}}
    
    # Mark as a preprocessor so it appears in the preprocessor list, NOT the main pipeline list
    # usage: list = ["PREPROCESSOR"]
    
    # ------------------
    # INPUTS & STATE
    # ------------------
    
    current_prompt: str = Field(
        default="A calm landscape",
        json_schema_extra=ui_field_config(
            label="Current Scene",
            order=10,
            description="The active scene description.",
        )
    )
    
    next_prompt: str = Field(
        default="A stormy ocean",
        json_schema_extra=ui_field_config(
            label="Next Scene",
            order=20,
            description="Queue the next scene description here.",
        )
    )
    
    transition_duration: float = Field(
        default=2.0,
        ge=0.1,
        le=10.0,
        json_schema_extra=ui_field_config(
            label="Transition Duration (s)",
            order=30,
            description="Time to cross-fade between scenes.",
        )
    )
    
    # ------------------
    # ACTIONS
    # ------------------
    
    trigger_transition: bool = Field(
        default=False,
        json_schema_extra=ui_field_config(
            label="Trigger Transition",
            order=40,
            description="Start the blend to the next scene.",
            component="pulse"
        )
    )
    
    is_recording: bool = Field(
        default=False,
        json_schema_extra=ui_field_config(
            label="Record Sequence",
            order=50,
            description="If ON, saves timing/prompts to internal memory.",
        )
    )
    
    export_json: bool = Field(
        default=False,
        json_schema_extra=ui_field_config(
            label="Export JSON",
            order=60,
            description="Save the recorded sequence to a file.",
            component="pulse"
        )
    )
    
    json_filename: str = Field(
        default="story_sequence.json",
        json_schema_extra=ui_field_config(
            label="JSON Filename",
            order=70,
            description="Filename for the exported sequence.",
        )
    )
