from __future__ import annotations

import dataclasses
from typing import Literal

from dynamicprompts.commands.base import Command


@dataclasses.dataclass(frozen=True)
class Predicate:
    op: Literal["eq", "neq", "defined", "truthy"]
    args: tuple[Command | str, ...]


@dataclasses.dataclass(frozen=True)
class IfCommand(Command):
    predicate: Predicate
    then_command: Command
    else_command: Command | None = None
    sampling_method = None
