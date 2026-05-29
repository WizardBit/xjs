#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

from .basicmachine import BasicMachine
from .container import Container
from .model import Model
from rich.text import Text
from typing import Any


class Machine(BasicMachine):
    is_container: bool = False

    def __init__(self, machine_name: str, machine_info: dict[str, Any], model: Model) -> None:
        BasicMachine.__init__(self, machine_name, machine_info, model)

        self.containers: dict[str, Container] = {}
        self.constraints: str = ""
        self.hardware: dict[str, str] = {}
        self.hardware["arch"] = ""
        self.hardware["cores"] = ""
        self.hardware["mem"] = ""
        self.hardware["root-disk"] = ""
        self.hardware["availability-zone"] = ""

        self.model = model

        if "constraints" in machine_info:
            self.constraints = machine_info["constraints"]

        if "hardware" in machine_info:
            for hardwarepair in machine_info["hardware"].split(" "):
                key, value = hardwarepair.split("=")
                self.hardware[key] = value

        if "containers" in machine_info:
            for container_name, container_info in machine_info["containers"].items():
                container = Container(container_name, container_info, self, model)
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
                self.get_juju_status_color(),
                self.get_machine_status_color(),
                self.dns_name,
                self.instance_id,
                self.base,
                self.hardware["availability-zone"],
                self.hardware["arch"],
                self.hardware["cores"],
                self.hardware["mem"],
                self.machine_message,
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
                self.hardware["availability-zone"],
                self.hardware["arch"],
                self.hardware["cores"],
                self.hardware["mem"],
                self.machine_message,
                notesstr,
            ]

        if include_model_name:
            row.insert(0, self.model.name)
        if include_controller_name:
            row.insert(0, self.model.controller.name)
        return row
