# Copyright (c) 2025 Kodo Robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from pathlib import Path
from typing import Tuple

from ros2em.utils.env_utils import BASE_DIR, env_path

DOCKER_IMAGE = "tiryoh/ros2-desktop-vnc"

def compose_file(name: str) -> Path:
    return env_path(name) / "docker-compose.yml"

def write_compose_file(path: Path, content: str):
    with open(path, "w") as f:
        f.write(content)

def generate_compose_content(name: str, distro: str, port_mappings: list[str]) -> str:
    ports_yaml = "\n".join([f"      - \"{mapping}\"" for mapping in port_mappings])
    return f"""
services:
  ros2:
    image: tiryoh/ros2-desktop-vnc:{distro}
    container_name: {name}
    volumes:
      - {BASE_DIR}:/home/ubuntu/ros2_ws/src
    ports:
{ports_yaml}
    shm_size: 512m
    restart: unless-stopped
    command: bash -c "tail -f /dev/null"
""".strip()