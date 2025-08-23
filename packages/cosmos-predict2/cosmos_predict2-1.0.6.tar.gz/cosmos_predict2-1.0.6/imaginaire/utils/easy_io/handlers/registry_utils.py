# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from imaginaire.utils.easy_io.handlers.base import BaseFileHandler
from imaginaire.utils.easy_io.handlers.byte_handler import ByteHandler
from imaginaire.utils.easy_io.handlers.csv_handler import CsvHandler
from imaginaire.utils.easy_io.handlers.gzip_handler import GzipHandler
from imaginaire.utils.easy_io.handlers.imageio_video_handler import ImageioVideoHandler
from imaginaire.utils.easy_io.handlers.json_handler import JsonHandler
from imaginaire.utils.easy_io.handlers.jsonl_handler import JsonlHandler
from imaginaire.utils.easy_io.handlers.np_handler import NumpyHandler
from imaginaire.utils.easy_io.handlers.pandas_handler import PandasHandler
from imaginaire.utils.easy_io.handlers.pickle_handler import PickleHandler
from imaginaire.utils.easy_io.handlers.pil_handler import PILHandler
from imaginaire.utils.easy_io.handlers.tarfile_handler import TarHandler
from imaginaire.utils.easy_io.handlers.torch_handler import TorchHandler
from imaginaire.utils.easy_io.handlers.torchjit_handler import TorchJitHandler
from imaginaire.utils.easy_io.handlers.txt_handler import TxtHandler
from imaginaire.utils.easy_io.handlers.yaml_handler import YamlHandler

file_handlers = {
    "json": JsonHandler(),
    "yaml": YamlHandler(),
    "yml": YamlHandler(),
    "pickle": PickleHandler(),
    "pkl": PickleHandler(),
    "tar": TarHandler(),
    "jit": TorchJitHandler(),
    "npy": NumpyHandler(),
    "txt": TxtHandler(),
    "csv": CsvHandler(),
    "pandas": PandasHandler(),
    "gz": GzipHandler(),
    "jsonl": JsonlHandler(),
    "byte": ByteHandler(),
}

for torch_type in ["pt", "pth", "ckpt"]:
    file_handlers[torch_type] = TorchHandler()
for img_type in ["jpg", "jpeg", "png", "bmp", "gif"]:
    file_handlers[img_type] = PILHandler()
    file_handlers[img_type].format = img_type
for video_type in ["mp4", "avi", "mov", "webm", "flv", "wmv"]:
    file_handlers[video_type] = ImageioVideoHandler()


def _register_handler(handler, file_formats):
    """Register a handler for some file extensions.

    Args:
        handler (:obj:`BaseFileHandler`): Handler to be registered.
        file_formats (str or list[str]): File formats to be handled by this
            handler.
    """
    if not isinstance(handler, BaseFileHandler):
        raise TypeError(f"handler must be a child of BaseFileHandler, not {type(handler)}")
    if isinstance(file_formats, str):
        file_formats = [file_formats]
    if not all([isinstance(item, str) for item in file_formats]):
        raise TypeError("file_formats must be a str or a list of str")
    for ext in file_formats:
        file_handlers[ext] = handler


def register_handler(file_formats, **kwargs):
    def wrap(cls):
        _register_handler(cls(**kwargs), file_formats)
        return cls

    return wrap
