# Apache License

# Copyright 2025 Text Intellect Team

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import torch
from transformers import pipeline


class WhisperModel:
    """
    A wrapper for the Hugging Face ASR pipeline for Whisper models.
    """

    def __init__(self, name_or_path: str, device: str = "cuda", generation_config: dict = None):
        """
        Initializes the Whisper model using the Hugging Face pipeline.

        Args:
            name_or_path (str): The model ID on the Hub or path to a local model.
            device (str): The device to run the model on ('cuda' or 'cpu').
            generation_config (dict, optional): A dictionary for generation parameters
                                                like 'language', 'task', 'temperature', etc.
                                                Defaults to None.
        """
        if device == "cuda" and not torch.cuda.is_available():
            print("Warning: CUDA not available, falling back to CPU.")
            resolved_device = "cpu"
        else:
            resolved_device = device

        # Use the provided generation_config or an empty dict if None
        generate_kwargs = generation_config if generation_config is not None else {}

        # The pipeline handles model and processor loading, device placement,
        # and long audio chunking automatically.
        print(f"Loading Whisper model from {name_or_path} on {resolved_device}...")
        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=name_or_path,
            device=resolved_device,
            chunk_length_s=30,
            stride_length_s=5,
            generate_kwargs=generate_kwargs,  # Pass the configuration here
        )

    def transcribe(self, audio_array, sampling_rate: int) -> str:
        """
        Generates a transcription for a single audio input.

        Args:
            audio_array: The raw audio waveform as a NumPy array or list of floats.
            sampling_rate (int): The sampling rate of the audio.

        Returns:
            str: The transcribed text.
        """
        # The pipeline expects a dictionary with the raw audio and sampling rate.
        # It returns a dictionary, so we extract the 'text' key.
        result = self.pipe({"raw": audio_array, "sampling_rate": sampling_rate})
        return result["text"]
