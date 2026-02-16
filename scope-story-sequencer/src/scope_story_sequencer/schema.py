from pydantic import Field
from scope.core.pipelines.base_schema import BasePipelineConfig

print("DEBUG: Defining StorySequencerConfig class...")

class StorySequencerConfig(BasePipelineConfig):
    pipeline_id: str = "scope-story-sequencer"
    pipeline_name: str = "Story Sequencer"
    pipeline_description: str = "A real-time prompt sequencer controlling MemFlow."
    
    modes: dict = {"video": {"default": True}}

    # ------------------
    # STORY INPUTS
    # ------------------
    
    current_prompt: str = Field(
        default="A calm landscape",
        json_schema_extra={
            "label": "Current Scene",
            "order": 10,
            "description": "The active scene description.",
            "component": "textarea",
            "props": {"rows": 2}
        }
    )
    
    next_prompt: str = Field(
        default="A stormy ocean",
        json_schema_extra={
            "label": "Next Scene",
            "order": 20,
            "description": "Queue the next scene description here.",
            "component": "textarea",
            "props": {"rows": 2}
        }
    )
    
    transition_duration: float = Field(
        default=2.0,
        ge=0.1,
        le=10.0,
        json_schema_extra={
            "label": "Transition Duration (s)",
            "order": 30,
            "description": "Time to cross-fade between scenes."
        }
    )
    
    trigger_transition: bool = Field(
        default=False,
        json_schema_extra={
            "label": "Trigger Transition",
            "order": 40,
            "description": "Start the blend to the next scene.",
            "component": "pulse"
        }
    )
    
    # ------------------
    # MEMFLOW PARAMS
    # ------------------
    
    model_id: str = Field(
        default="memflow", 
        json_schema_extra={"label": "Model ID", "order": 100}
    )
    
    guidance_scale: float = Field(
        default=1.5,
        ge=1.0,
        le=20.0,
        json_schema_extra={"label": "Guidance Scale", "order": 110}
    )
    
    num_inference_steps: int = Field(
        default=4,
        ge=1,
        le=50,
        json_schema_extra={"label": "Steps", "order": 120}
    )
