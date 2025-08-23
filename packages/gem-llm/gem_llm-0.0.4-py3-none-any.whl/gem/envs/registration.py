# Copyright 2025 AxonRL Team. All Rights Reserved.
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

"""Environment registration."""

import importlib
from dataclasses import dataclass, field
from functools import partial
from typing import Any, Callable, Dict, Optional, Sequence, Union

from gem.core import Env, EnvWrapper
from gem.vector.async_vector_env import AsyncVectorEnv
from gem.vector.sync_vector_env import SyncVectorEnv
from gem.vector.vector_env import VectorEnv


@dataclass
class EnvSpec:
    """A specification for creating environments."""

    id: str
    entry_point: Union[Callable, str]
    kwargs: Dict[str, Any] = field(default_factory=dict)


ENV_REGISTRY: Dict[str, EnvSpec] = {}


def register(env_id: str, entry_point: Union[Callable, str], **kwargs: Any):
    """Register an environment with a given ID."""
    if env_id in ENV_REGISTRY:
        raise ValueError(f"Environment {env_id} already registered.")
    ENV_REGISTRY[env_id] = EnvSpec(id=env_id, entry_point=entry_point, kwargs=kwargs)


def print_envs():
    if not ENV_REGISTRY:
        print("No environments registered.")
    else:
        print("Detailed Registered Environments:")
        for env_id, env_spec in ENV_REGISTRY.items():
            print(f"  - {env_id}:")
            print(f"      Entry Point: {env_spec.entry_point}")
            print(f"      Kwargs: {env_spec.kwargs}")


def make(env_id: str, **kwargs) -> Env:
    if env_id not in ENV_REGISTRY:
        raise ValueError(f"Environment {env_id} not found in registry.")

    env_spec = ENV_REGISTRY[env_id]

    if isinstance(env_spec.entry_point, str):
        module_path, class_name = env_spec.entry_point.split(":")
        try:
            module = importlib.import_module(module_path)
            env_class: Callable = getattr(module, class_name)
        except (ModuleNotFoundError, AttributeError) as e:
            raise ImportError(
                f"Could not import {module_path}.{class_name}. Error: {e}"
            )
    else:
        env_class: Callable = env_spec.entry_point

    env = env_class(**{**env_spec.kwargs, **kwargs})

    env.env_id = env_id
    env.entry_point = env_spec.entry_point

    return env


def make_vec(
    env_ids: Union[str, Sequence[str]],
    wrappers: Optional[Sequence[EnvWrapper]] = None,
    vec_kwargs: Optional[Sequence[dict]] = None,
    async_mode: bool = False,
    seed: int = 0,
    **kwargs,
) -> VectorEnv:
    def create_single_env(env_id, idx: int) -> Env:
        # set vec specific kwargs
        if vec_kwargs is not None:
            _kwargs = vec_kwargs[idx]
        else:
            _kwargs = {}
        # set different seed for each environment in vec
        if "seed" not in _kwargs:
            _kwargs["seed"] = seed + idx
        # update with additional kwargs
        _kwargs.update(**kwargs)
        # create the environment
        single_env = make(env_id, **_kwargs)
        # apply wrappers if provided
        if wrappers is None:
            return single_env
        for wrapper in wrappers:
            single_env = wrapper(single_env)
        return single_env

    if isinstance(env_ids, str):
        env_ids = [env_ids]

    num_envs = len(env_ids)

    if async_mode:
        print(f"AsyncVectorEnv with {num_envs} environments.")
        env = AsyncVectorEnv(
            env_ids=env_ids,
            env_fns=[
                partial(create_single_env, env_ids[i], i) for i in range(num_envs)
            ],
        )
    else:
        print(f"SyncVectorEnv with {num_envs} environments.")
        env = SyncVectorEnv(
            env_ids=env_ids,
            env_fns=[
                partial(create_single_env, env_ids[i], i) for i in range(num_envs)
            ],
        )
    return env
