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


"""
Whisper-Evaluator: A simple, modular framework to evaluate Whisper models in notebooks.
"""

__version__ = "0.0.33"

splash_screen = r"""
   _   _ ___   _    __      ___    _                    ___          _
  /_\ (_)   \ /_\   \ \    / / |_ (_)____ __  ___ _ _  | __|_ ____ _| |
 / _ \| | |) / _ \   \ \/\/ /| ' \| (_-< '_ \/ -_) '_| | _|\ V / _` | |
/_/ \_\_|___/_/ \_\   \_/\_/ |_||_|_/__/ .__/\___|_|   |___|\_/\__,_|_| v0.0.33
                                       |_|
"""

# Print the splash screen when the package is imported
print(splash_screen)

# Expose the main Evaluator class to the top-level of the package
from .evaluator import *  # noqa F403
