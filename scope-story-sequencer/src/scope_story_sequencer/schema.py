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
        title="Current Scene",
        description="The active scene description.",
        # Pydantic v1 specific extra fields for UI
        component="textarea",
        props={"rows": 2},
        order=10
    )
    
    next_prompt: str = Field(
        default="A stormy ocean",
        title="Next Scene",
        description="Queue the next scene description here.",
        component="textarea",
        props={"rows": 2},
        order=20
    )
    
    transition_duration: float = Field(
        default=2.0,
        ge=0.1,
        le=10.0,
        title="Transition Duration (s)",
        description="Time to cross-fade between scenes.",
        order=30
    )
    
    trigger_transition: bool = Field(
        default=False,
        title="Trigger Transition",
        description="Start the blend to the next scene.",
        component="pulse",
        order=40
    )
    
    # ------------------
    # MEMFLOW PARAMS
    # ------------------
    
    model_id: str = Field(
        default="memflow", 
        title="Model ID",
        order=100
    )
    
    guidance_scale: float = Field(
        default=1.5,
        ge=1.0,
        le=20.0,
        title="Guidance Scale",
        order=110
    )
    
    num_inference_steps: int = Field(
        default=4,
        ge=1,
        le=50,
        title="Steps",
        order=120
    )
