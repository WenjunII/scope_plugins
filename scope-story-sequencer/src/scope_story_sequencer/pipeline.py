import json
import time
import torch
from scope.core.pipelines.interface import Pipeline
from scope.core.pipelines.requirements import Requirements
from scope.core.plugins.hookspecs import hookimpl
from .schema import StorySequencerConfig

class StorySequencerPipeline(Pipeline):
    def get_config_class(self):
        return StorySequencerConfig

    def __init__(self, device=None, **kwargs):
        super().__init__(device, **kwargs)
        
        # State Tracking
        self.active_prompt = ""
        self.queued_prompt = ""
        self.blend_weight = 0.0  # 0.0 = active, 1.0 = queued
        self.transition_start_time = 0.0
        self.transition_active = False
        self.duration = 2.0
        
        # Recording History
        self.recorded_sequence = []
        self.recording_start_time = 0.0
        self.is_recording = False

    def prepare(self):
        # We need video input (or at least metadata stream)
        # But this preprocessor mostly manipulates metadata (prompts)
        return Requirements(input_size=512)

    def __call__(self, video: list[torch.Tensor], **kwargs) -> dict:
        # 1. READ PARAMS from kwargs (Standard Scope Pattern)
        # ----------------------------------------------------
        current_text_ui = kwargs.get("current_prompt", "")
        next_text_ui = kwargs.get("next_prompt", "")
        duration = kwargs.get("transition_duration", 2.0)
        trigger = kwargs.get("trigger_transition", False)
        record = kwargs.get("is_recording", False)
        export = kwargs.get("export_json", False)
        filename = kwargs.get("json_filename", "story_sequence.json")
        
        # 2. HANDLE RECORDING STATE
        # -------------------------
        if record and not self.is_recording:
            # Just started recording
            self.is_recording = True
            self.recording_start_time = time.time()
            self.recorded_sequence = []
            print(f"Started recording story sequence to memory...")
        elif not record and self.is_recording:
            # Just stopped recording
            self.is_recording = False
            print(f"Stopped recording. Total events: {len(self.recorded_sequence)}")

        # 3. HANDLE TRANSITION LOGIC
        # --------------------------
        now = time.time()
        
        # If trigger pulse received (or UI changed significantly)
        if trigger and not self.transition_active:
            print(f"Triggering transition: '{current_text_ui}' -> '{next_text_ui}' ({duration}s)")
            self.transition_active = True
            self.transition_start_time = now
            self.active_prompt = current_text_ui
            self.queued_prompt = next_text_ui
            self.duration = duration
            
            # Record this event if recording is on
            if self.is_recording:
                event = {
                    "time": now - self.recording_start_time,
                    "prompt_from": self.active_prompt,
                    "prompt_to": self.queued_prompt,
                    "duration": self.duration
                }
                self.recorded_sequence.append(event)

        # Calculate blend weight
        if self.transition_active:
            elapsed = now - self.transition_start_time
            if elapsed >= self.duration:
                # Transition complete
                self.blend_weight = 1.0
                self.transition_active = False
                # Promote queued prompt to active for the next cycle
                # (Ideally, we'd update the UI field back, but plugins can't write to UI yet)
                # So we just hold the state here
                self.active_prompt = self.queued_prompt 
                self.queued_prompt = "" # Clear queue internally
            else:
                # Linear interpolation
                self.blend_weight = elapsed / self.duration
        else:
            # Steady state
            self.blend_weight = 0.0
            # If no transition active, just pass through the UI text
            self.active_prompt = current_text_ui

        # 4. EXPORT LOGIC
        # ---------------
        if export and self.recorded_sequence:
            try:
                with open(filename, 'w') as f:
                    json.dump(self.recorded_sequence, f, indent=2)
                print(f"Exported {len(self.recorded_sequence)} events to {filename}")
            except Exception as e:
                print(f"Failed to export JSON: {e}")

        # 5. INJECT METADATA & PASS THROUGH VIDEO
        # ---------------------------------------
        # We attach prompt/weight data to the output dict
        # The main pipeline (StreamDiffusion) must be configured to read these keys!
        
        output_metadata = {
            "prompt": self.active_prompt,
            "negative_prompt": kwargs.get("negative_prompt", ""), # Pass through existing
            # If we are blending, we might want to send BOTH prompts to a mixing pipeline
            "prompt_2": self.queued_prompt if self.transition_active else "",
            "blend_weight": self.blend_weight
        }
        
        # Merge our metadata into the kwargs for downstream consumers
        # (Note: Scope pipelines return a dict of {key: tensor}, metadata is usually implicit or side-channel)
        # For now, we return the video as-is, but the Side-Effect is the state management above.
        
        # To actually CONTROL the main pipeline, we rely on Scope's "Global Parameter" sharing
        # or we assume this plugin IS the pipeline wrapping the model.
        # But since we defined it as a PREPROCESSOR, it just modifies the stream.
        
        # The proper way to inject prompts into a downstream pipeline in Scope 
        # is usually via the "prompt" argument in the return dict IF the pipeline supports it.
        # However, Scope preprocessors typically return {"video": tensor}.
        # Parameters like "prompt" are usually global.
        
        # WORKAROUND: We print the status for now to verify logic.
        # In a real setup, we would need the Main Pipeline to read "prompt_blend" from a shared state.
        
        # Return video unchanged (Pass-Through)
        # Input video is list[Tensor], we return dict{"video": Tensor}
        if video and len(video) > 0:
            # Flatten batch dim if needed, or just take first frame
            # video[0] is typically (1, C, H, W) or (C, H, W)
            return {"video": video[0]}
            
        # Fallback for no video input
        return {}
