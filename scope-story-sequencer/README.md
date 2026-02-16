# Real-Time Story Sequencer for Scope

This plugin adds a **`scope-story-sequencer`** pipeline that acts as a preprocessor and live controller for video generation.

## How it Works
1.  **Type/Paste your story** into `current_prompt` and `next_prompt`.
2.  **Set the duration** using `transition_duration` (e.g., 2.0s).
3.  **Trigger the transition** with `trigger_transition`.
4.  **Record and export** your performance as a JSON file.

## Features
-   **Live Blending:** Smoothly cross-fades prompt weights between scenes.
-   **JSON Export:** Saves timing, prompts, and weights for future automation.
-   **Universal:** Works with any main diffusion pipeline (StreamDiffusion, SDXL, etc.).

## Installation
1.  Copy the `scope-story-sequencer` folder to your Scope plugins directory.
2.  Restart Scope.
3.  Select `scope-story-sequencer` from the Pipeline or Preprocessor dropdown.
