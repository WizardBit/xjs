#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

from rich.text import Text
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .basicmachine import BasicMachine
    from .model import Model


class NetworkInterface:
    column_names: list[str] = [
        "Machine",
        "Interface",
        "IP",
        "MAC",
        "Gateway",
        "Space",
        "Up",
        "Notes",
    ]

    def __init__(self, interfacename: str, interfaceinfo: dict[str, Any], parent: BasicMachine, model: Model) -> None:
        self.space: str = ""
        self.notes: list[str | Text] = []
        self.gateway: str = ""

        self.name: str = interfacename
        self.parent = parent
        self.ipaddresses: list[str] = interfaceinfo["ip-addresses"]
        self.macaddress: str = interfaceinfo["mac-address"]
        self.up: bool = interfaceinfo["is-up"]
        self.model = model

        if "space" in interfaceinfo:
            self.space = interfaceinfo["space"]
        if "gateway" in interfaceinfo:
            self.gateway = interfaceinfo["gateway"]

    def get_isup_color(self) -> Text:
        if self.up:
            return Text(str(self.up), style="green")
        else:
            return Text(str(self.up), style="red")

    def get_row(
        self, color: bool, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str | Text]:
        row: list[str | Text] = []
        notesstr = ", ".join(str(n) for n in self.notes)
        ipstr = ",".join(self.ipaddresses)
        if color:
            row = [
                self.parent.name,
                self.name,
                ipstr,
                self.macaddress,
                self.gateway,
                self.space,
                self.get_isup_color(),
                notesstr,
            ]
        else:
            row = [
                self.parent.name,
                self.name,
                ipstr,
                self.macaddress,
                self.gateway,
                self.space,
                str(self.up),
                notesstr,
            ]

        if include_model_name:
            row.insert(0, self.model.name)
        if include_controller_name:
            row.insert(0, self.model.controller.name)
        return row

    def get_column_names(
        self, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str]:
        fields = list(self.column_names)
        if include_model_name:
            fields.insert(0, "Model")
        if include_controller_name:
            fields.insert(0, "Controller")
        return fields
