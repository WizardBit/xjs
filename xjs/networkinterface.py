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

    def __init__(
        self, interface_name: str,
        interface_info: dict[str, Any], parent: BasicMachine,
        model: Model,
    ) -> None:
        self.space: str = ""
        self.notes: list[str | Text] = []
        self.gateway: str = ""

        self.name: str = interface_name
        self.parent = parent
        self.ip_addresses: list[str] = interface_info["ip-addresses"]
        self.mac_address: str = interface_info["mac-address"]
        self.up: bool = interface_info["is-up"]
        self.model = model

        if "space" in interface_info:
            self.space = interface_info["space"]
        if "gateway" in interface_info:
            self.gateway = interface_info["gateway"]

    def get_is_up_color(self) -> Text:
        if self.up:
            return Text(str(self.up), style="green")
        else:
            return Text(str(self.up), style="red")

    def get_row(
        self, color: bool,
        include_controller_name: bool = False,
        include_model_name: bool = False,
    ) -> list[str | Text]:
        row: list[str | Text] = []
        notesstr = ", ".join(str(n) for n in self.notes)
        ipstr = ",".join(self.ip_addresses)
        if color:
            row = [
                self.parent.name,
                self.name,
                ipstr,
                self.mac_address,
                self.gateway,
                self.space,
                self.get_is_up_color(),
                notesstr,
            ]
        else:
            row = [
                self.parent.name,
                self.name,
                ipstr,
                self.mac_address,
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
        self, include_controller_name: bool = False,
        include_model_name: bool = False,
    ) -> list[str]:
        fields = list(self.column_names)
        if include_model_name:
            fields.insert(0, "Model")
        if include_controller_name:
            fields.insert(0, "Controller")
        return fields
