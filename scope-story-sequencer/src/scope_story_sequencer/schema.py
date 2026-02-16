from pydantic import Field

print("DEBUG: Loading scope-story-sequencer schema module...")

# Helper to mimic old ui_field_config since the module is missing in v0.1.3
def ui_field_config(label=None, order=None, description=None, component=None):
    extra = {}
    if label: extra["label"] = label
    if order: extra["order"] = order
    if description: extra["description"] = description
    if component: extra["component"] = component
    return extra

# Attempt to import MemFlow config to inherit from it
try:
    print("DEBUG: Attempting to import MemflowConfig...")
    from scope.core.pipelines.memflow.schema import MemflowConfig as BaseConfig
    print("DEBUG: Success importing MemflowConfig.")
except ImportError as e:
    print(f"DEBUG: Failed to import MemflowConfig: {e}")
    # Fallback: Inherit from BasePipelineConfig
    from scope.core.pipelines.base_schema import BasePipelineConfig as BaseConfig

class StorySequencerConfig(BaseConfig):
    pipeline_id: str = "scope-story-sequencer"
    pipeline_name: str = "Story Sequencer (MemFlow)"
    pipeline_description: str = "MemFlow wrapper with real-time story sequencing."
    
    # We inherit 'modes' and 'usage' from MemflowConfig automatically.
    # We DO NOT set usage=["PREPROCESSOR"] because we want to be a Main Pipeline now.

    # ------------------
    # STORY INPUTS
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
            description="Time to cross-fade between scenes (if model supports it).",
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
