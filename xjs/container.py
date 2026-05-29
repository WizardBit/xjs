#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

from .basicmachine import BasicMachine
from rich.text import Text
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .machine import Machine
    from .model import Model


class Container(BasicMachine):
    is_container: bool = True

    def __init__(self, container_name: str, container_info: dict[str, Any], machine: Machine, model: Model) -> None:
        BasicMachine.__init__(self, container_name, container_info, model)
        self.machine = machine

    def get_machine_message_color(self) -> Text:
        if self.machine_message == "Container started":
            return Text(self.machine_message, style="green")
        else:
            return Text(self.machine_message, style="yellow")

    def get_row(
        self, color: bool, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str | Text]:
        row: list[str | Text] = []
        notesstr = ", ".join(str(n) for n in self.notes)

        if color:
            row = [
                self.name,
                self.get_juju_status_color(),
                self.get_machine_status_color(),
                self.dns_name,
                self.instance_id,
                self.base,
                "",
                "",
                "",
                "",
                self.get_machine_message_color(),
                notesstr,
            ]
        else:
            row = [
                self.name,
                self.juju_status,
                self.machine_status,
                self.dns_name,
                self.instance_id,
                self.base,
                "",
                "",
                "",
                "",
                self.machine_message,
                notesstr,
            ]

        if include_model_name:
            row.insert(0, self.machine.model.name)
        if include_controller_name:
            row.insert(0, self.machine.model.controller.name)
        return row
