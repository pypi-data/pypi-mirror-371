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
from datasets import Audio, load_dataset

from .utils import to_latin_serbian


class ASRTask:
    """
    Handles loading and preparing a dataset for Automatic Speech Recognition evaluation.
    """

    def __init__(
        self,
        dataset_name: str,
        dataset_subset: str | None = None,  # Now optional
        dataset_split: str = "test",
        audio_column: str = "audio",
        text_column: str = "text",
        hf_token: str | None = None,
    ):
        # Load dataset, with optional subset
        if dataset_subset:
            print(f"Loading dataset '{dataset_name}' with subset '{dataset_subset}' and split '{dataset_split}'")
            self.dataset = load_dataset(
                dataset_name,
                dataset_subset,
                split=dataset_split,
                trust_remote_code=True,
                token=hf_token,
            )
        else:
            print(f"Loading dataset '{dataset_name}' without subset and split '{dataset_split}'")
            self.dataset = load_dataset(
                dataset_name,
                split=dataset_split,
                trust_remote_code=True,
                token=hf_token,
            )

        # Resample audio column to 16 kHz
        self.dataset = self.dataset.cast_column(audio_column, Audio(sampling_rate=16000))

        # Standardize column names
        self.dataset = self.dataset.rename_columns({audio_column: "audio", text_column: "reference_text"})

        # Apply transliteration
        def transliterate_to_latin(text):
            text["reference_text"] = to_latin_serbian(text["reference_text"])
            return text

        self.dataset = self.dataset.map(transliterate_to_latin)

    def __iter__(self):
        return iter(self.dataset)

    def __len__(self):
        return len(self.dataset)
