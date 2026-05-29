#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

import re
from typing import TYPE_CHECKING
from .basicunit import BasicUnit
from rich.text import Text

if TYPE_CHECKING:
    from .unit import Unit
    from .application import Application


class SubordinateUnit(BasicUnit):
    is_subordinate: bool = True

    def __init__(self, subunit_name: str, subunit_info: dict, unit: Unit) -> None:
        BasicUnit.__init__(self, subunit_name, subunit_info, unit.application.model.controller)

        self.unit = unit
        self.machine = unit.machine

    def create_application_relation(self) -> None:
        app_name = re.sub(r"\/\d+$", "", self.name)
        self.application = self.unit.application.model.get_application(app_name)
        if self.application is not None:
            self.application.add_subordinate(self)

    def get_row(
        self, color: bool, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str | Text]:
        row: list[str | Text] = []
        notesstr = ", ".join(str(n) for n in self.notes)
        namestr = "  " + self.name
        portsstr = ",".join(self.open_ports)

        if self.leader:
            namestr += "*"

        if color:
            row = [
                namestr,
                self.get_workload_status_color(),
                self.get_juju_status_color(),
                "",
                self.public_address,
                portsstr,
                self.message,
                notesstr,
            ]
        else:
            row = [
                namestr,
                self.workload_status,
                self.juju_status,
                "",
                self.public_address,
                portsstr,
                self.message,
                notesstr,
            ]

        if include_model_name:
            row.insert(0, self.unit.application.model.name)
        if include_controller_name:
            row.insert(0, self.unit.application.model.controller.name)
        return row
