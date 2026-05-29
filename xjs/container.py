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
    iscontainer: bool = True

    def __init__(self, containername: str, containerinfo: dict[str, Any], machine: Machine, model: Model) -> None:
        BasicMachine.__init__(self, containername, containerinfo, model)
        self.machine = machine

    def get_machinemessage_color(self) -> Text:
        if self.machinemessage == "Container started":
            return Text(self.machinemessage, style="green")
        else:
            return Text(self.machinemessage, style="yellow")

    def get_row(
        self, color: bool, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str | Text]:
        row: list[str | Text] = []
        notesstr = ", ".join(str(n) for n in self.notes)

        if color:
            row = [
                self.name,
                self.get_jujustatus_color(),
                self.get_machinestatus_color(),
                self.dnsname,
                self.instanceid,
                self.base,
                "",
                "",
                "",
                "",
                self.get_machinemessage_color(),
                notesstr,
            ]
        else:
            row = [
                self.name,
                self.jujustatus,
                self.machinestatus,
                self.dnsname,
                self.instanceid,
                self.base,
                "",
                "",
                "",
                "",
                self.machinemessage,
                notesstr,
            ]

        if include_model_name:
            row.insert(0, self.machine.model.name)
        if include_controller_name:
            row.insert(0, self.machine.model.controller.name)
        return row
