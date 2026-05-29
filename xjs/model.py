#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

from datetime import datetime, timezone
import re
from packaging import version
from rich.text import Text
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .application import Application
    from .container import Container
    from .machine import Machine
    from .relation import Relation
    from .controller import Controller


class Model:
    latest_juju_version = version.parse("3.6.20")
    column_names: list[str] = [
        "Model",
        "Controller",
        "Cloud/Region",
        "Version",
        "SLA",
        "Timestamp",
        "Model-Status",
        "Message",
        "Notes",
    ]

    def __init__(self, modelinfo: dict[str, Any], controller: Controller, juju1env: str | None = None) -> None:
        self.notes: list[str | Text] = []
        self.applications: dict[str, Application] = {}
        self.relations: dict[str, list[Relation]] = {}
        self.machines: dict[str, Machine] = {}
        self.containers: dict[str, Container] = {}
        self.message: str = ""
        self.upgradeavailable: str = ""

        if "name" in modelinfo:
            self.name: str = modelinfo["name"]
        else:
            self.name = "NA"

        if "type" in modelinfo:
            self.type: str = modelinfo["type"]
        else:
            self.type = "NA"
        self.controller = controller

        if "controller" in modelinfo:
            self.controller.name = modelinfo["controller"]

        if "cloud" in modelinfo:
            self.cloud: str = modelinfo["cloud"]
        elif juju1env:
            self.cloud = juju1env
        else:
            self.cloud = "NA"

        if "version" in modelinfo:
            self.version: str = modelinfo["version"]
        else:
            self.version = "1.x.x"

        if "model-status" in modelinfo:
            self.modelstatus: str = modelinfo["model-status"]["current"]
        else:
            self.modelstatus = "NA"

        if "sla" in modelinfo:
            self.sla: str = modelinfo["sla"]
        else:
            self.sla = "NA"

        if "model-status" in modelinfo and "since" in modelinfo["model-status"]:
            since_str = modelinfo["model-status"]["since"]
            if since_str.endswith("Z"):
                since_str = since_str[:-1]
                self.since: datetime = datetime.strptime(since_str, "%d %b %Y %H:%M:%S").replace(tzinfo=timezone.utc)
            else:
                self.since = datetime.strptime(since_str, "%d %b %Y %H:%M:%S%z")
            controller.update_timestamp(self.since)

        if "upgrade-available" in modelinfo:
            self.upgradeavailable = modelinfo["upgrade-available"]
            self.notes.append("upgrade available: " + self.upgradeavailable)

    def add_application(self, application: Application) -> None:
        self.applications[application.name] = application

    def add_machine(self, machine: Machine) -> None:
        self.machines[machine.name] = machine

    def add_container(self, container: Container) -> None:
        self.containers[container.name] = container

    def add_relation(self, relation: Relation) -> None:
        if relation is not None:
            if relation.name not in self.relations:
                self.relations[relation.name] = []
                self.relations[relation.name].append(relation)
                return
            else:
                if not self.get_relation(relation.name, relation.application.name, relation.partner.name):
                    self.relations[relation.name].append(relation)

    def get_relation(self, name: str, app_name: str, partner_name: str) -> Relation | None:
        if name in self.relations:
            for relation in self.relations[name]:
                if (
                    (relation.application.name == app_name and relation.partner.name == partner_name)
                    or (relation.partner.name == app_name and relation.application.name == partner_name)
                ):
                    return relation
            return None
        else:
            return None

    def get_application(self, searchappname: str) -> Application | None:
        for appname, application in self.applications.items():
            if appname == searchappname:
                return application
        return None

    def get_machine(self, machinename: str) -> Machine | None:
        if machinename in self.machines:
            return self.machines[machinename]
        else:
            return None

    def get_container(self, containername: str) -> Container | None:
        if containername in self.containers:
            return self.containers[containername]
        else:
            return None

    def get_version_color(self) -> Text:
        model_version = version.parse(self.version)
        if model_version < version.parse("3.0.0") or model_version > Model.latest_juju_version:
            return Text(self.version, style="red")
        elif model_version < Model.latest_juju_version:
            return Text(self.version, style="yellow")
        else:
            return Text(self.version, style="green")

    def get_modelstatus_color(self) -> Text:
        if self.modelstatus == "available":
            return Text(self.modelstatus, style="green")
        else:
            return Text(self.modelstatus, style="red")

    def get_row(
        self, color: bool, include_controller_name: bool = True, include_model_name: bool = True
    ) -> list[str | Text]:
        if not self.controller.timestampprovided:
            if color:
                self.notes.append(Text("Guessing at timestamp", style="yellow"))
            else:
                self.notes.append("Guessing at timestamp")
        notesstr = ", ".join(str(n) for n in self.notes)
        timestampstr = self.controller.timestamp.strftime("%H:%M:%SZ")
        if color:
            return [
                self.name,
                self.controller.name,
                self.cloud,
                self.get_version_color(),
                self.sla,
                timestampstr,
                self.get_modelstatus_color(),
                self.message,
                notesstr,
            ]
        else:
            return [
                self.name,
                self.controller.name,
                self.cloud,
                self.version,
                self.sla,
                timestampstr,
                self.modelstatus,
                self.message,
                notesstr,
            ]

    def get_column_names(
        self, include_controller_name: bool = True, include_model_name: bool = True
    ) -> list[str]:
        return self.column_names

    def filter_dictionary(self, dictionary: dict[str, Any], key_filter: str) -> dict[str, Any]:
        return {
            key: value
            for (key, value) in dictionary.items()
            if key_filter in key
        }

    def filter_applications(self, app_filter: str) -> None:
        apps = self.filter_dictionary(self.applications, app_filter)
        parent_apps: dict[str, Any] = {}
        for appname, appinfo in apps.items():
            for subname, subinfo in appinfo.subordinates.items():
                parent_apps[subinfo.unit.application.name] = subinfo.unit.application
        self.applications = {**apps, **parent_apps}
        self.reset_machines()

    def filter_machines(self, machine_filter: str) -> None:
        self.machines = {
            key: value
            for (key, value) in self.machines.items()
            if key == machine_filter
        }
        self.containers = {}
        for machine in self.machines.values():
            self.containers.update(machine.containers)

    def reset_machines(self) -> None:
        machines: dict[str, Any] = {}
        containers: dict[str, Any] = {}
        for appname, appinfo in self.applications.items():
            for unitname, unitinfo in appinfo.units.items():
                if unitinfo.machine.iscontainer:
                    containers[unitinfo.machine.name] = unitinfo.machine
                    machines[unitinfo.machine.machine.name] = unitinfo.machine.machine
                else:
                    machines[unitinfo.machine.name] = unitinfo.machine
            for subunitname, subunitinfo in appinfo.subordinates.items():
                if subunitinfo.machine.iscontainer:
                    containers[subunitinfo.machine.name] = subunitinfo.machine
                    machines[subunitinfo.machine.machine.name] = subunitinfo.machine.machine
                else:
                    machines[subunitinfo.machine.name] = subunitinfo.machine
        for machinename, machine in machines.items():
            oldcontainers = machine.containers.keys() - containers.keys()
            for containername in oldcontainers:
                del machine.containers[containername]
        self.machines = machines
        self.containers = containers
