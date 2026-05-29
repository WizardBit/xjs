#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

from .basicmachine import BasicMachine
from .container import Container
from .model import Model
from rich.text import Text
from typing import Any


class Machine(BasicMachine):
    iscontainer: bool = False

    def __init__(self, machinename: str, machineinfo: dict[str, Any], model: Model) -> None:
        BasicMachine.__init__(self, machinename, machineinfo, model)

        self.containers: dict[str, Container] = {}
        self.constraints: str = ""
        self.hardware: dict[str, str] = {}
        self.hardware["arch"] = ""
        self.hardware["cores"] = ""
        self.hardware["mem"] = ""
        self.hardware["root-disk"] = ""
        self.hardware["availability-zone"] = ""

        self.model = model

        if "constraints" in machineinfo:
            self.constraints = machineinfo["constraints"]

        if "hardware" in machineinfo:
            for hardwarepair in machineinfo["hardware"].split(" "):
                key, value = hardwarepair.split("=")
                self.hardware[key] = value

        if "containers" in machineinfo:
            for containername, containerinfo in machineinfo["containers"].items():
                container = Container(containername, containerinfo, self, model)
                model.add_container(container)
                self.containers[container.name] = container

    def get_row(
        self, color: bool, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str | Text]:
        notesstr = ", ".join(str(n) for n in self.notes)
        row: list[str | Text] = []

        if color:
            row = [
                self.name,
                self.get_jujustatus_color(),
                self.get_machinestatus_color(),
                self.dnsname,
                self.instanceid,
                self.base,
                self.hardware["availability-zone"],
                self.hardware["arch"],
                self.hardware["cores"],
                self.hardware["mem"],
                self.machinemessage,
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
                self.hardware["availability-zone"],
                self.hardware["arch"],
                self.hardware["cores"],
                self.hardware["mem"],
                self.machinemessage,
                notesstr,
            ]

        if include_model_name:
            row.insert(0, self.model.name)
        if include_controller_name:
            row.insert(0, self.model.controller.name)
        return row
