import json
import time
import torch
from scope.core.plugins.hookspecs import hookimpl
from .schema import StorySequencerConfig

print("DEBUG: Loading scope-story-sequencer pipeline module...")

# Attempt to import MemFlow pipeline to inherit from it
try:
    print("DEBUG: Attempting to import MemflowPipeline...")
    from scope.core.pipelines.memflow.pipeline import MemflowPipeline as BasePipeline
    print("DEBUG: Success importing MemflowPipeline.")
except ImportError as e:
    print(f"DEBUG: Failed to import MemflowPipeline: {e}")
    # Fallback: Inherit from base Pipeline (Pass-through mode)
    # If Interface is also missing, try base Pipeline from wherever it is
    try:
        from scope.core.pipelines.interface import Pipeline as BasePipeline
    except ImportError:
        # Absolute last resort for v0.1.3 if structure is totally different
        class BasePipeline:
            def __init__(self, device=None, **kwargs): pass
            def __call__(self, video, **kwargs): return {"video": video[0] if video else None}
            def get_config_class(self): return None

class StorySequencerPipeline(BasePipeline):
    def get_config_class(self):
        return StorySequencerConfig

    def __init__(self, device=None, **kwargs):
        super().__init__(device, **kwargs)
        
        # State Tracking
        self.active_prompt = ""
        self.queued_prompt = ""
        self.transition_start_time = 0.0
        self.transition_active = False
        self.duration = 2.0
        
        # Recording History
        self.recorded_sequence = []
        self.recording_start_time = 0.0
        self.is_recording = False

    def __call__(self, video: list[torch.Tensor], **kwargs) -> dict:
        # 1. READ PARAMS from kwargs
        current_text_ui = kwargs.get("current_prompt", "")
        next_text_ui = kwargs.get("next_prompt", "")
        duration = kwargs.get("transition_duration", 2.0)
        trigger = kwargs.get("trigger_transition", False)
        record = kwargs.get("is_recording", False)
        export = kwargs.get("export_json", False)
        filename = kwargs.get("json_filename", "story_sequence.json")
        
        # 2. HANDLE RECORDING STATE
        if record and not self.is_recording:
            self.is_recording = True
            self.recording_start_time = time.time()
            self.recorded_sequence = []
            print(f"Started recording story sequence...")
        elif not record and self.is_recording:
            self.is_recording = False
            print(f"Stopped recording. Total events: {len(self.recorded_sequence)}")

        # 3. HANDLE TRANSITION LOGIC
        now = time.time()
        
        # Initialize active prompt on first run
        if not self.active_prompt and current_text_ui:
            self.active_prompt = current_text_ui

        if trigger and not self.transition_active:
            print(f"Triggering transition: '{current_text_ui}' -> '{next_text_ui}'")
            self.transition_active = True
            self.transition_start_time = now
            self.active_prompt = next_text_ui # Immediate switch for MemFlow (it handles coherence)
            self.duration = duration
            
            if self.is_recording:
                event = {
                    "time": now - self.recording_start_time,
                    "prompt": self.active_prompt,
                    "duration": self.duration
                }
                self.recorded_sequence.append(event)
                
        # Reset trigger flag internally if needed, but usually UI handles it.
        if self.transition_active:
            elapsed = now - self.transition_start_time
            if elapsed >= self.duration:
                self.transition_active = False

        # 4. EXPORT LOGIC
        if export and self.recorded_sequence:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.recorded_sequence, f, indent=2)
                print(f"Exported {len(self.recorded_sequence)} events to {filename}")
            except Exception as e:
                print(f"Failed to export JSON: {e}")

        # 5. INJECT PROMPT & DELEGATE TO MEMFLOW
        # --------------------------------------
        # We override the 'prompt' in kwargs with our managed active prompt
        if self.active_prompt:
            kwargs["prompt"] = self.active_prompt
            
        # Pass everything to the real MemFlow pipeline
        return super().__call__(video, **kwargs)
