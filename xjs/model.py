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

    def __init__(self, model_info: dict[str, Any], controller: Controller, juju1env: str | None = None) -> None:
        self.notes: list[str | Text] = []
        self.applications: dict[str, Application] = {}
        self.relations: dict[str, list[Relation]] = {}
        self.machines: dict[str, Machine] = {}
        self.containers: dict[str, Container] = {}
        self.message: str = ""
        self.upgrade_available: str = ""

        if "name" in model_info:
            self.name: str = model_info["name"]
        else:
            self.name = "NA"

        if "type" in model_info:
            self.type: str = model_info["type"]
        else:
            self.type = "NA"
        self.controller = controller

        if "controller" in model_info:
            self.controller.name = model_info["controller"]

        if "cloud" in model_info:
            self.cloud: str = model_info["cloud"]
        elif juju1env:
            self.cloud = juju1env
        else:
            self.cloud = "NA"

        if "version" in model_info:
            self.version: str = model_info["version"]
        else:
            self.version = "1.x.x"

        if "model-status" in model_info:
            self.model_status: str = model_info["model-status"]["current"]
        else:
            self.model_status = "NA"

        if "sla" in model_info:
            self.sla: str = model_info["sla"]
        else:
            self.sla = "NA"

        if "model-status" in model_info and "since" in model_info["model-status"]:
            since_str = model_info["model-status"]["since"]
            if since_str.endswith("Z"):
                since_str = since_str[:-1]
                self.since: datetime = datetime.strptime(since_str, "%d %b %Y %H:%M:%S").replace(tzinfo=timezone.utc)
            else:
                self.since = datetime.strptime(since_str, "%d %b %Y %H:%M:%S%z")
            controller.update_timestamp(self.since)

        if "upgrade-available" in model_info:
            self.upgrade_available = model_info["upgrade-available"]
            self.notes.append("upgrade available: " + self.upgrade_available)

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

    def get_application(self, search_app_name: str) -> Application | None:
        for app_name, application in self.applications.items():
            if app_name == search_app_name:
                return application
        return None

    def get_machine(self, machine_name: str) -> Machine | None:
        if machine_name in self.machines:
            return self.machines[machine_name]
        else:
            return None

    def get_container(self, container_name: str) -> Container | None:
        if container_name in self.containers:
            return self.containers[container_name]
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

    def get_model_status_color(self) -> Text:
        if self.model_status == "available":
            return Text(self.model_status, style="green")
        else:
            return Text(self.model_status, style="red")

    def get_row(
        self, color: bool, include_controller_name: bool = True, include_model_name: bool = True
    ) -> list[str | Text]:
        if not self.controller.timestamp_provided:
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
                self.get_model_status_color(),
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
                self.model_status,
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
        for app_name, app_info in apps.items():
            for subname, subinfo in app_info.subordinates.items():
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
        for app_name, app_info in self.applications.items():
            for unit_name, unit_info in app_info.units.items():
                if unit_info.machine.is_container:
                    containers[unit_info.machine.name] = unit_info.machine
                    machines[unit_info.machine.machine.name] = unit_info.machine.machine
                else:
                    machines[unit_info.machine.name] = unit_info.machine
            for subunit_name, subunit_info in app_info.subordinates.items():
                if subunit_info.machine.is_container:
                    containers[subunit_info.machine.name] = subunit_info.machine
                    machines[subunit_info.machine.machine.name] = subunit_info.machine.machine
                else:
                    machines[subunit_info.machine.name] = subunit_info.machine
        for machine_name, machine in machines.items():
            oldcontainers = machine.containers.keys() - containers.keys()
            for container_name in oldcontainers:
                del machine.containers[container_name]
        self.machines = machines
        self.containers = containers
