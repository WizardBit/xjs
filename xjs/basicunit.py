#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

from datetime import datetime, timezone
from rich.text import Text
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .controller import Controller


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

    def __init__(self, name: str, info: dict[str, Any], controller: Controller) -> None:
        self.notes: list[str | Text] = []
        self.open_ports: list[str] = []
        self.subordinates: dict[str, BasicUnit] = {}
        self.message: str = ""
        self.leader: bool = False

        self.name: str = name
        self.workload_status: str = info["workload-status"]["current"]
        if "juju-status" in info:
            statuskey = "juju-status"
        elif "agent-status" in info:
            statuskey = "agent-status"
        else:
            statuskey = "none"
        self.juju_status: str = info[statuskey]["current"]
        if "version" in info[statuskey]:
            self.juju_version: str = info[statuskey]["version"]
        else:
            self.juju_version = "NA"
        if "public-address" in info:
            self.public_address: str = info["public-address"]
        else:
            self.public_address = "PENDING"
        if "message" in info[statuskey]:
            self.notes.append(info[statuskey]["message"])

        ws_since = info["workload-status"]["since"]
        if ws_since.endswith("Z"):
            ws_since = ws_since[:-1]
            self.workload_since: datetime = datetime.strptime(ws_since, "%d %b %Y %H:%M:%S").replace(tzinfo=timezone.utc)
        else:
            self.workload_since = datetime.strptime(ws_since, "%d %b %Y %H:%M:%S%z")
        controller.update_timestamp(self.workload_since)
        js_since = info[statuskey]["since"]
        if js_since.endswith("Z"):
            js_since = js_since[:-1]
            self.juju_since: datetime = datetime.strptime(js_since, "%d %b %Y %H:%M:%S").replace(tzinfo=timezone.utc)
        else:
            self.juju_since = datetime.strptime(js_since, "%d %b %Y %H:%M:%S%z")
        controller.update_timestamp(self.juju_since)

        if "message" in info["workload-status"]:
            self.message = info["workload-status"]["message"]
        if "open-ports" in info:
            self.open_ports = info["open-ports"]
        if "leader" in info:
            self.leader = info["leader"]

    def get_workload_status_color(self) -> Text:
        if self.workload_status == "active":
            return Text(self.workload_status, style="green")
        elif self.workload_status in ("error", "blocked"):
            return Text(self.workload_status, style="red")
        elif self.workload_status == "waiting":
            return Text(self.workload_status)
        elif self.workload_status == "maintenance":
            return Text(self.workload_status, style="orange3")
        else:
            return Text(self.workload_status, style="yellow")

    def get_juju_status_color(self) -> Text:
        if self.juju_status in ("idle", "executing"):
            return Text(self.juju_status, style="green")
        elif self.juju_status == "allocating":
            return Text(self.juju_status, style="orange3")
        elif self.juju_status in ("error", "lost", "failed"):
            return Text(self.juju_status, style="red")
        else:
            return Text(self.juju_status, style="yellow")

    def get_column_names(
        self, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str]:
        fields = list(self.column_names)
        if include_model_name:
            fields.insert(0, "Model")
        if include_controller_name:
            fields.insert(0, "Controller")
        return fields
