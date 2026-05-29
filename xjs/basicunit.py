#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

from datetime import datetime, timezone
from rich.text import Text
from typing import Any


class BasicUnit:
    column_names: list[str] = [
        "Unit",
        "Workload",
        "Agent",
        "Machine",
        "Public address",
        "Ports",
        "Message",
        "Notes",
    ]

    def __init__(self, name: str, info: dict[str, Any], controller: Any) -> None:
        self.notes: list[str | Text] = []
        self.openports: list[str] = []
        self.subordinates: dict[str, Any] = {}
        self.message: str = ""
        self.leader: bool = False

        self.name: str = name
        self.workloadstatus: str = info["workload-status"]["current"]
        if "juju-status" in info:
            statuskey = "juju-status"
        elif "agent-status" in info:
            statuskey = "agent-status"
        else:
            statuskey = "none"
        self.jujustatus: str = info[statuskey]["current"]
        if "version" in info[statuskey]:
            self.jujuversion: str = info[statuskey]["version"]
        if "public-address" in info:
            self.publicaddress: str = info["public-address"]
        else:
            self.publicaddress = "PENDING"
        if "message" in info[statuskey]:
            self.notes.append(info[statuskey]["message"])

        ws_since = info["workload-status"]["since"]
        if ws_since.endswith("Z"):
            ws_since = ws_since[:-1]
            self.workloadsince: datetime = datetime.strptime(ws_since, "%d %b %Y %H:%M:%S").replace(tzinfo=timezone.utc)
        else:
            self.workloadsince = datetime.strptime(ws_since, "%d %b %Y %H:%M:%S%z")
        controller.update_timestamp(self.workloadsince)
        js_since = info[statuskey]["since"]
        if js_since.endswith("Z"):
            js_since = js_since[:-1]
            self.jujusince: datetime = datetime.strptime(js_since, "%d %b %Y %H:%M:%S").replace(tzinfo=timezone.utc)
        else:
            self.jujusince = datetime.strptime(js_since, "%d %b %Y %H:%M:%S%z")
        controller.update_timestamp(self.jujusince)

        if "message" in info["workload-status"]:
            self.message = info["workload-status"]["message"]
        if "open-ports" in info:
            self.openports = info["open-ports"]
        if "leader" in info:
            self.leader = info["leader"]

    def to_dict(self) -> dict[str, BasicUnit]:
        return {self.name: self}

    def get_workloadstatus_color(self) -> Text:
        if self.workloadstatus == "active":
            return Text(self.workloadstatus, style="green")
        elif self.workloadstatus in ("error", "blocked"):
            return Text(self.workloadstatus, style="red")
        elif self.workloadstatus == "waiting":
            return Text(self.workloadstatus)
        elif self.workloadstatus == "maintenance":
            return Text(self.workloadstatus, style="orange3")
        else:
            return Text(self.workloadstatus, style="yellow")

    def get_jujustatus_color(self) -> Text:
        if self.jujustatus in ("idle", "executing"):
            return Text(self.jujustatus, style="green")
        elif self.jujustatus == "allocating":
            return Text(self.jujustatus, style="orange3")
        elif self.jujustatus in ("error", "lost", "failed"):
            return Text(self.jujustatus, style="red")
        else:
            return Text(self.jujustatus, style="yellow")

    def get_column_names(
        self, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str]:
        fields = list(self.column_names)
        if include_model_name:
            fields.insert(0, "Model")
        if include_controller_name:
            fields.insert(0, "Controller")
        return fields
