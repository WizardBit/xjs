#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

from datetime import datetime, timezone
from .networkinterface import NetworkInterface
from rich.text import Text
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .model import Model


class BasicMachine:
    column_names: list[str] = [
        "Machine",
        "Agent",
        "Status",
        "DNS",
        "Inst id",
        "Base",
        "AZ",
        "Arch",
        "Cores",
        "Memory",
        "Message",
        "Notes",
    ]

    def __init__(self, name: str, info: dict[str, Any], model: Model) -> None:
        self.notes: list[str | Text] = []
        self.network_interfaces: dict[str, NetworkInterface] = {}

        self.name: str = name
        if "juju-status" in info:
            self.juju_status: str = info["juju-status"]["current"]
            if "version" in info["juju-status"]:
                self.juju_version: str = info["juju-status"]["version"]
            else:
                self.juju_version = "NA"
        else:
            self.juju_status = info["agent-state"]
            self.juju_version = info["agent-version"]
        if "dns-name" in info:
            self.dns_name: str = info["dns-name"]
        else:
            self.dns_name = "PENDING"
        if "ip-addresses" in info:
            self.ip_addresses: list[str] | str = info["ip-addresses"]
        else:
            self.ip_addresses = "NA"
        self.instance_id: str = info["instance-id"]
        if "machine-status" in info:
            self.machine_status: str = info["machine-status"]["current"]
            if "message" in info["machine-status"]:
                self.machine_message: str = info["machine-status"]["message"]
            else:
                self.machine_message = ""
        else:
            self.machine_status = "NA"
            self.machine_message = ""

        base = info.get("base")
        if isinstance(base, dict):
            self.base: str = f"{base.get('name', '')}@{base.get('channel', '')}"
        else:
            self.base = base if base else "NA"
        self.model = model

        if "juju-status" in info:
            js_since = info["juju-status"]["since"]
            if js_since.endswith("Z"):
                js_since = js_since[:-1]
                self.juju_since: datetime = datetime.strptime(js_since, "%d %b %Y %H:%M:%S").replace(tzinfo=timezone.utc)
            else:
                self.juju_since = datetime.strptime(js_since, "%d %b %Y %H:%M:%S%z")
            model.controller.update_timestamp(self.juju_since)
        if "machine-status" in info:
            ms_since = info["machine-status"]["since"]
            if ms_since.endswith("Z"):
                ms_since = ms_since[:-1]
                self.machine_since: datetime = datetime.strptime(ms_since, "%d %b %Y %H:%M:%S").replace(tzinfo=timezone.utc)
            else:
                self.machine_since = datetime.strptime(ms_since, "%d %b %Y %H:%M:%S%z")
            model.controller.update_timestamp(self.machine_since)

        if "network-interfaces" in info:
            for interface_name, interface_info in info["network-interfaces"].items():
                self.network_interfaces[interface_name] = NetworkInterface(interface_name, interface_info, self, model)

    def get_juju_status_color(self) -> Text:
        if self.juju_status == "started":
            return Text(self.juju_status, style="green")
        elif self.juju_status in ("error", "down"):
            return Text(self.juju_status, style="red")
        elif self.juju_status == "pending":
            return Text(self.juju_status, style="orange3")
        else:
            return Text(self.juju_status, style="yellow")

    def get_machine_status_color(self) -> Text:
        if self.machine_status == "running":
            return Text(self.machine_status, style="green")
        elif self.machine_status == "pending":
            return Text(self.machine_status, style="orange3")
        elif self.machine_status == "NA":
            return Text(self.machine_status)
        else:
            return Text(self.machine_status, style="yellow")

    def get_column_names(
        self, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str]:
        fields = list(self.column_names)
        if include_model_name:
            fields.insert(0, "Model")
        if include_controller_name:
            fields.insert(0, "Controller")
        return fields
