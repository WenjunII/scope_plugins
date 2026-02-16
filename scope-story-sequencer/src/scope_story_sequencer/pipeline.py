import time
import torch
import importlib
from scope.core.plugins.hookspecs import hookimpl
from .schema import StorySequencerConfig

# Fallback base if needed
try:
    from scope.core.pipelines.interface import Pipeline as BasePipeline
except ImportError:
    class BasePipeline:
        def __init__(self, device=None, **kwargs): pass
        def __call__(self, video, **kwargs): return {"video": video[0] if video else None}
        @classmethod
        def get_config_class(cls): return None

class StorySequencerPipeline(BasePipeline):
    @classmethod
    def get_config_class(cls):
        return StorySequencerConfig

    def __init__(self, device=None, **kwargs):
        self.memflow = None
        
        # Try importing MemFlow pipeline DYNAMICALLY
        try:
            # We guess the path based on file structure: scope.core.pipelines.memflow.pipeline
            module = importlib.import_module("scope.core.pipelines.memflow.pipeline")
            MemflowPipeline = getattr(module, "MemflowPipeline", None)
            if MemflowPipeline:
                print("DEBUG: Successfully loaded MemflowPipeline class. Initializing...")
                self.memflow = MemflowPipeline(device, **kwargs)
            else:
                print("DEBUG: Found module but no MemflowPipeline class.")
        except Exception as e:
            print(f"DEBUG: Failed to load MemFlow pipeline: {e}")

        # If fallback, init base
        if not self.memflow:
            super().__init__(device, **kwargs)
            
        # State Tracking
        self.active_prompt = ""
        self.queued_prompt = ""
        self.transition_start_time = 0.0
        self.transition_active = False
        self.duration = 2.0

    def __call__(self, video: list[torch.Tensor], **kwargs) -> dict:
        # 1. READ PARAMS
        current_text_ui = kwargs.get("current_prompt", "")
        next_text_ui = kwargs.get("next_prompt", "")
        trigger = kwargs.get("trigger_transition", False)
        
        # 2. STORY LOGIC
        if not self.active_prompt and current_text_ui:
            self.active_prompt = current_text_ui

        if trigger and not self.transition_active:
            print(f"Triggering transition: '{current_text_ui}' -> '{next_text_ui}'")
            self.transition_active = True
            self.active_prompt = next_text_ui
            # In a real transition, we'd reset this flag after duration
            self.transition_active = False 

        # 3. DELEGATE TO MEMFLOW
        if self.memflow:
            # Inject our active prompt
            if self.active_prompt:
                kwargs["prompt"] = self.active_prompt
                
            # Pass to inner pipeline
            return self.memflow(video, **kwargs)
        else:
            # Fallback pass-through
            return {"video": video[0] if video else None}
