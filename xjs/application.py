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
        "Rev",
        "OS",
        "Base",
        "Message",
        "Notes",
    ]

    def __init__(self, appname: str, appinfo: dict[str, Any] | None = None, model: Model = "") -> None:
        appinfo = appinfo if isinstance(appinfo, dict) else {}

        self.notes: list[str | Text] = []
        self.units: dict[str, Unit] = {}
        self.subordinates: dict[str, SubordinateUnit] = {}
        self.version: str = ""
        self.message: str = ""
        self.endpointbindings: dict[str, str] = {}
        self.charmlatestrev: int = -1
        self.exposed: str = ""

        self.name: str = appname
        self.model = model
        if "charm" in appinfo:
            self.charm: str = appinfo["charm"]

        base = appinfo.get("base")
        if isinstance(base, dict):
            self.base: str = f"{base.get('name', '')}@{base.get('channel', '')}"
        else:
            self.base = base or "NA"

        if "os" in appinfo:
            self.os: str = appinfo["os"]
        else:
            self.os = "NA"

        if "charm-origin" in appinfo:
            self.charmorigin: str = appinfo["charm-origin"]
        else:
            self.charmorigin = "NA"

        if "charm-name" in appinfo:
            self.charmname: str = appinfo["charm-name"]
        else:
            self.charmname = "NA"

        if "charm-rev" in appinfo:
            self.charmrev: int = int(appinfo["charm-rev"])
        else:
            self.charmrev = -1

        if "exposed" in appinfo:
            self.exposed = appinfo["exposed"]

        if "application-status" in appinfo:
            statuskey = "application-status"
        elif "service-status" in appinfo:
            statuskey = "service-status"
        else:
            statuskey = "none"

        if statuskey in appinfo and "current" in appinfo[statuskey]:
            self.status: str = appinfo[statuskey]["current"]
        else:
            self.status = "NA"

        if statuskey in appinfo and "since" in appinfo[statuskey]:
            since_str = appinfo[statuskey]["since"]
            if since_str.endswith("Z"):
                since_str = since_str[:-1]
                self.since: datetime = datetime.strptime(since_str, "%d %b %Y %H:%M:%S").replace(tzinfo=timezone.utc)
            else:
                self.since = datetime.strptime(since_str, "%d %b %Y %H:%M:%S%z")
            model.controller.update_timestamp(self.since)

        if statuskey in appinfo:
            if "message" in appinfo[statuskey]:
                self.message = appinfo[statuskey]["message"]
            if "version" in appinfo:
                self.version = appinfo["version"]
            if "endpoint-bindings" in appinfo:
                self.endpointbindings = appinfo["endpoint-bindings"]
            if "can-upgrade-to" in appinfo:
                match = re.match(r"\D+(\d+)$", appinfo["can-upgrade-to"])
                if match:
                    self.charmlatestrev = int(match.group(1))
                self.canupgradeto = appinfo["can-upgrade-to"]

        if self.exposed:
            self.notes.append("exposed")

        self.charmid: str = ""
        if "charm" in appinfo:
            match = re.match(r"(cs:~[^/]+)\/([^/]+/)*([^/]+)-\d+$", self.charm)
            if match:
                self.charmid = match.group(1) + "/" + self.base + "/" + match.group(3)
            else:
                match = re.match(r"cs:(.*)-\d+$", self.charm)
                if match:
                    self.charmid = "cs:" + self.base + "/" + match.group(1)
            if self.charmorigin != "charmhub":
                self.notes.append("Not from Charm Store")

        if "units" in appinfo:
            for unitname, unitinfo in appinfo["units"].items():
                unit = Unit(unitname, unitinfo, self)
                self.units[unitname] = unit

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

    def get_charmrev_color(self) -> Text:
        if self.charmlatestrev == -1:
            return Text(str(self.charmrev))
        if self.charmrev < self.charmlatestrev:
            return Text(str(self.charmrev), style="yellow")
        elif self.charmrev == self.charmlatestrev:
            return Text(str(self.charmrev), style="green")
        else:
            return Text(str(self.charmrev), style="red")

    def get_charmorigin_color(self) -> Text:
        if self.charmorigin != "charmhub":
            return Text(self.charmorigin, style="yellow")
        else:
            return Text(self.charmorigin)

    def get_row(
        self, color: bool, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str | Text]:
        row: list[str | Text] = []
        if color:
            row = [
                self.name,
                self.version,
                self.get_status_color(),
                self.get_scale_color(),
                self.charm,
                self.get_charmorigin_color(),
                self.get_charmrev_color(),
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
                self.charmorigin,
                str(self.charmrev),
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
        self, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str]:
        fields = list(self.column_names)
        if include_model_name:
            fields.insert(0, "Model")
        if include_controller_name:
            fields.insert(0, "Controller")
        return fields

    def filter_dictionary(self, dictionary: dict[str, Any], key_filter: str) -> dict[str, Any]:
        return {
            key: value
            for (key, value) in dictionary.items()
            if key_filter in key
        }

    def filter_units(self, unit_filter: str) -> None:
        self.units = self.filter_dictionary(self.units, unit_filter)
