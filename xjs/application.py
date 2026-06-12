#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

from datetime import datetime, timezone
import re
from .unit import Unit
from rich.text import Text
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .model import Model
    from .subordinateunit import SubordinateUnit


class Application:
    column_names: list[str] = [
        "App",
        "Version",
        "Status",
        "Scale",
        "Charm",
        "Store",
        "Channel",
        "Rev",
        "OS",
        "Base",
        "Message",
        "Notes",
    ]

    def __init__(
        self, app_name: str, app_info: dict[str, Any] | None = None,
        model: Model = "",
    ) -> None:
        app_info = app_info if isinstance(app_info, dict) else {}

        self.notes: list[str | Text] = []
        self.units: dict[str, Unit] = {}
        self.subordinates: dict[str, SubordinateUnit] = {}
        self.version: str = ""
        self.message: str = ""
        self.endpoint_bindings: dict[str, str] = {}
        self.charm_latest_rev: int = -1
        self.exposed: str = ""

        self.name: str = app_name
        self.model = model
        if "charm" in app_info:
            self.charm: str = app_info["charm"]

        base = app_info.get("base")
        if isinstance(base, dict):
            self.base: str = (
                f"{base.get('name', '')}@{base.get('channel', '')}"
            )
        else:
            self.base = base or "NA"

        if "os" in app_info:
            self.os: str = app_info["os"]
        else:
            self.os = "NA"

        if "charm-origin" in app_info:
            self.charm_origin: str = app_info["charm-origin"]
        else:
            self.charm_origin = "NA"

        if "charm-name" in app_info:
            self.charm_name: str = app_info["charm-name"]
        else:
            self.charm_name = "NA"

        if "charm-rev" in app_info:
            self.charm_rev: int = int(app_info["charm-rev"])
        else:
            self.charm_rev = -1

        if "charm-channel" in app_info:
            self.channel: str = app_info["charm-channel"]
        else:
            self.channel = "NA"

        if "exposed" in app_info:
            self.exposed = app_info["exposed"]

        if "application-status" in app_info:
            statuskey = "application-status"
        elif "service-status" in app_info:
            statuskey = "service-status"
        else:
            statuskey = "none"

        if statuskey in app_info and "current" in app_info[statuskey]:
            self.status: str = app_info[statuskey]["current"]
        else:
            self.status = "NA"

        if statuskey in app_info and "since" in app_info[statuskey]:
            since_str = app_info[statuskey]["since"]
            if since_str.endswith("Z"):
                since_str = since_str[:-1]
                self.since: datetime = (
                    datetime.strptime(since_str, "%d %b %Y %H:%M:%S")
                    .replace(tzinfo=timezone.utc)
                )
            else:
                self.since = datetime.strptime(
                    since_str, "%d %b %Y %H:%M:%S%z",
                )
            model.controller.update_timestamp(self.since)

        if statuskey in app_info:
            if "message" in app_info[statuskey]:
                self.message = app_info[statuskey]["message"]
            if "version" in app_info:
                self.version = app_info["version"]
            if "endpoint-bindings" in app_info:
                self.endpoint_bindings = app_info["endpoint-bindings"]
            if "can-upgrade-to" in app_info:
                match = re.match(r"\D+(\d+)$", app_info["can-upgrade-to"])
                if match:
                    self.charm_latest_rev = int(match.group(1))
                self.can_upgrade_to = app_info["can-upgrade-to"]

        if self.exposed:
            self.notes.append("exposed")

        self.charm_id: str = ""
        if "charm" in app_info:
            match = re.match(r"(cs:~[^/]+)\/([^/]+/)*([^/]+)-\d+$", self.charm)
            if match:
                self.charm_id = (
                    match.group(1) + "/" + self.base + "/" + match.group(3)
                )
            else:
                match = re.match(r"cs:(.*)-\d+$", self.charm)
                if match:
                    self.charm_id = "cs:" + self.base + "/" + match.group(1)
            if self.charm_origin != "charmhub":
                self.notes.append("Not from Charm Store")

        if "units" in app_info:
            for unit_name, unit_info in app_info["units"].items():
                unit = Unit(unit_name, unit_info, self)
                self.units[unit_name] = unit

    def add_subordinate(self, subunit: SubordinateUnit) -> None:
        self.subordinates[subunit.name] = subunit

    def get_scale(self) -> int:
        return len(self.units) + len(self.subordinates)

    def get_status_color(self) -> Text:
        if self.status == "active":
            return Text(self.status, style="green")
        elif self.status in ("error", "blocked"):
            return Text(self.status, style="red")
        elif self.status == "waiting":
            return Text(self.status)
        elif self.status == "maintenance":
            return Text(self.status, style="orange3")
        else:
            return Text(self.status, style="yellow")

    def get_scale_color(self) -> Text:
        scale = self.get_scale()
        if scale == 0:
            return Text(str(scale), style="red")
        else:
            return Text(str(scale))

    def get_charm_rev_color(self) -> Text:
        if self.charm_latest_rev == -1:
            return Text(str(self.charm_rev))
        if self.charm_rev < self.charm_latest_rev:
            return Text(str(self.charm_rev), style="yellow")
        elif self.charm_rev == self.charm_latest_rev:
            return Text(str(self.charm_rev), style="green")
        else:
            return Text(str(self.charm_rev), style="red")

    def get_charm_origin_color(self) -> Text:
        if self.charm_origin != "charmhub":
            return Text(self.charm_origin, style="yellow")
        else:
            return Text(self.charm_origin)

    def get_row(
        self, color: bool,
        include_controller_name: bool = False,
        include_model_name: bool = False,
    ) -> list[str | Text]:
        row: list[str | Text] = []
        if color:
            row = [
                self.name,
                self.version,
                self.get_status_color(),
                self.get_scale_color(),
                self.charm,
                self.get_charm_origin_color(),
                self.channel,
                self.get_charm_rev_color(),
                self.os,
                self.base,
                self.message,
                ", ".join(str(n) for n in self.notes),
            ]
        else:
            row = [
                self.name,
                self.version,
                self.status,
                str(self.get_scale()),
                self.charm,
                self.charm_origin,
                self.channel,
                str(self.charm_rev),
                self.os,
                self.base,
                self.message,
                ", ".join(str(n) for n in self.notes),
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

    def filter_dictionary(
        self, dictionary: dict[str, Any], key_filter: str,
    ) -> dict[str, Any]:
        return {
            key: value
            for (key, value) in dictionary.items()
            if key_filter in key
        }

    def filter_units(self, unit_filter: str) -> None:
        self.units = self.filter_dictionary(self.units, unit_filter)

    def filter_units_by_workload_status(self, statuses: set[str]) -> None:
        filtered_units = {}
        for unit_name, unit in self.units.items():
            if unit.workload_status in statuses:
                filtered_units[unit_name] = unit
                unit.subordinates = {
                    n: s for n, s in unit.subordinates.items()
                    if s.workload_status in statuses
                }
            else:
                filtered_subs = {
                    n: s for n, s in unit.subordinates.items()
                    if s.workload_status in statuses
                }
                if filtered_subs:
                    unit.subordinates = filtered_subs
                    filtered_units[unit_name] = unit
        self.units = filtered_units
        self.subordinates = {
            n: s for n, s in self.subordinates.items()
            if s.workload_status in statuses
        }

    def filter_units_by_agent_status(self, statuses: set[str]) -> None:
        filtered_units = {}
        for unit_name, unit in self.units.items():
            if unit.juju_status in statuses:
                filtered_units[unit_name] = unit
                unit.subordinates = {
                    n: s for n, s in unit.subordinates.items()
                    if s.juju_status in statuses
                }
            else:
                filtered_subs = {
                    n: s for n, s in unit.subordinates.items()
                    if s.juju_status in statuses
                }
                if filtered_subs:
                    unit.subordinates = filtered_subs
                    filtered_units[unit_name] = unit
        self.units = filtered_units
        self.subordinates = {
            n: s for n, s in self.subordinates.items()
            if s.juju_status in statuses
        }

    def filter_units_unwanted(self) -> None:
        filtered_units = {}
        for unit_name, unit in self.units.items():
            is_unwanted = (
                unit.workload_status != "active"
                or unit.juju_status != "idle"
            )
            if is_unwanted:
                unit.subordinates = {
                    n: s for n, s in unit.subordinates.items()
                    if s.workload_status != "active"
                    or s.juju_status != "idle"
                }
                filtered_units[unit_name] = unit
            else:
                filtered_subs = {
                    n: s for n, s in unit.subordinates.items()
                    if s.workload_status != "active"
                    or s.juju_status != "idle"
                }
                if filtered_subs:
                    unit.subordinates = filtered_subs
                    filtered_units[unit_name] = unit
        self.units = filtered_units
        self.subordinates = {
            n: s for n, s in self.subordinates.items()
            if s.workload_status != "active"
            or s.juju_status != "idle"
        }
