#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any
from .basicunit import BasicUnit
from rich.text import Text

if TYPE_CHECKING:
    from .application import Application


class Unit(BasicUnit):
    issubordinate: bool = False

    def __init__(self, unitname: str, unitinfo: dict[str, Any], application: Application) -> None:
        BasicUnit.__init__(self, unitname, unitinfo, application.model.controller)

        self.application = application
        if "machine" in unitinfo:
            match = re.match(r"(\d+)\/(lx[cd]|kvm)\/(\d+)$", unitinfo["machine"])
            if match:
                self.machine = application.model.get_container(unitinfo["machine"])
            else:
                self.machine = application.model.get_machine(unitinfo["machine"])
        else:
            self.machine = None

        if "subordinates" in unitinfo:
            from .subordinateunit import SubordinateUnit

            for subunitname, subunitinfo in unitinfo["subordinates"].items():
                self.subordinates[subunitname] = SubordinateUnit(subunitname, subunitinfo, self)

    def get_row(
        self, color: bool, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str | Text]:
        row: list[str | Text] = []
        notesstr = ", ".join(str(n) for n in self.notes)
        namestr = self.name
        portsstr = ",".join(self.openports)
        if self.machine:
            machinename = self.machine.name
        else:
            machinename = "PENDING"

        if self.leader:
            namestr += "*"

        if color:
            row = [
                namestr,
                self.get_workloadstatus_color(),
                self.get_jujustatus_color(),
                machinename,
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
                machinename,
                self.publicaddress,
                portsstr,
                self.message,
                notesstr,
            ]

        if include_model_name:
            row.insert(0, self.application.model.name)
        if include_controller_name:
            row.insert(0, self.application.model.controller.name)
        return row

    def filter_dictionary(self, dictionary: dict[str, Any], key_filter: str) -> dict[str, Any]:
        return {
            key: value
            for (key, value) in dictionary.items()
            if key_filter in key
        }

    def filter_subordinates(self, subunit_filter: str) -> None:
        self.subordinates = self.filter_dictionary(self.subordinates, subunit_filter)
