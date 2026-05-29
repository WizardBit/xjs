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
        self.networkinterfaces: dict[str, NetworkInterface] = {}

        self.name: str = name
        if "juju-status" in info:
            self.jujustatus: str = info["juju-status"]["current"]
            if "version" in info["juju-status"]:
                self.jujuversion: str = info["juju-status"]["version"]
            else:
                self.jujuversion = "NA"
        else:
            self.jujustatus = info["agent-state"]
            self.jujuversion = info["agent-version"]
        if "dns-name" in info:
            self.dnsname: str = info["dns-name"]
        else:
            self.dnsname = "PENDING"
        if "ip-addresses" in info:
            self.ipaddresses: list[str] | str = info["ip-addresses"]
        else:
            self.ipaddresses = "NA"
        self.instanceid: str = info["instance-id"]
        if "machine-status" in info:
            self.machinestatus: str = info["machine-status"]["current"]
            if "message" in info["machine-status"]:
                self.machinemessage: str = info["machine-status"]["message"]
            else:
                self.machinemessage = ""
        else:
            self.machinestatus = "NA"
            self.machinemessage = ""

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
                self.jujusince: datetime = datetime.strptime(js_since, "%d %b %Y %H:%M:%S").replace(tzinfo=timezone.utc)
            else:
                self.jujusince = datetime.strptime(js_since, "%d %b %Y %H:%M:%S%z")
            model.controller.update_timestamp(self.jujusince)
        if "machine-status" in info:
            ms_since = info["machine-status"]["since"]
            if ms_since.endswith("Z"):
                ms_since = ms_since[:-1]
                self.machinesince: datetime = datetime.strptime(ms_since, "%d %b %Y %H:%M:%S").replace(tzinfo=timezone.utc)
            else:
                self.machinesince = datetime.strptime(ms_since, "%d %b %Y %H:%M:%S%z")
            model.controller.update_timestamp(self.machinesince)

        if "network-interfaces" in info:
            for interfacename, interfaceinfo in info["network-interfaces"].items():
                self.networkinterfaces[interfacename] = NetworkInterface(interfacename, interfaceinfo, self, model)

    def get_jujustatus_color(self) -> Text:
        if self.jujustatus == "started":
            return Text(self.jujustatus, style="green")
        elif self.jujustatus in ("error", "down"):
            return Text(self.jujustatus, style="red")
        elif self.jujustatus == "pending":
            return Text(self.jujustatus, style="orange3")
        else:
            return Text(self.jujustatus, style="yellow")

    def get_machinestatus_color(self) -> Text:
        if self.machinestatus == "running":
            return Text(self.machinestatus, style="green")
        elif self.machinestatus == "pending":
            return Text(self.machinestatus, style="orange3")
        elif self.machinestatus == "NA":
            return Text(self.machinestatus)
        else:
            return Text(self.machinestatus, style="yellow")

    def get_column_names(
        self, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str]:
        fields = list(self.column_names)
        if include_model_name:
            fields.insert(0, "Model")
        if include_controller_name:
            fields.insert(0, "Controller")
        return fields
