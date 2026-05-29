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
    issubordinate: bool = True

    def __init__(self, subunitname: str, subunitinfo: dict, unit: Unit) -> None:
        BasicUnit.__init__(self, subunitname, subunitinfo, unit.application.model.controller)

        self.unit = unit
        self.machine = unit.machine

    def create_application_relation(self) -> None:
        appname = re.sub(r"\/\d+$", "", self.name)
        self.application = self.unit.application.model.get_application(appname)
        if self.application is not None:
            self.application.add_subordinate(self)

    def get_row(
        self, color: bool, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str | Text]:
        row: list[str | Text] = []
        notesstr = ", ".join(str(n) for n in self.notes)
        namestr = "  " + self.name
        portsstr = ",".join(self.openports)

        if self.leader:
            namestr += "*"

        if color:
            row = [
                namestr,
                self.get_workloadstatus_color(),
                self.get_jujustatus_color(),
                "",
                self.publicaddress,
                portsstr,
                self.message,
                notesstr,
            ]
        else:
            row = [
                namestr,
                self.workloadstatus,
                self.jujustatus,
                "",
                self.publicaddress,
                portsstr,
                self.message,
                notesstr,
            ]

        if include_model_name:
            row.insert(0, self.unit.application.model.name)
        if include_controller_name:
            row.insert(0, self.unit.application.model.controller.name)
        return row
