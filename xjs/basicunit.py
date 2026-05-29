#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

import re
from .colors import Color
import pendulum

class BasicUnit:
    """
    A BasicMachine Object is inherited by Units and Subordinates so common
    attributes and functions remain here
    """

    column_names = [
        "Unit",
        "Workload",
        "Agent",
        "Machine",
        "Public address",
        "Ports",
        "Message",
        "Notes",
    ]

    def __init__(self, name, info, controller):
        """
        Create a BasicUnit object with basic information from a unit or
        subordinate object from a juju status output
        """
        # Default Values
        self.notes = []
        self.openports = []
        self.subordinates = {}
        self.message = ""
        self.leader = False

        # Required Variables
        self.name = name
        self.workloadstatus = info["workload-status"]["current"]
        if "juju-status" in info:
            statuskey = "juju-status"
        elif "agent-status" in info:
            statuskey = "agent-status"
        else:
            statuskey = "none"
        self.jujustatus = info[statuskey]["current"]
        if "version" in info[statuskey]:
            self.jujuversion = info[statuskey]["version"]
        if "public-address" in info:
            self.publicaddress = info["public-address"]
        else:
            self.publicaddress = "PENDING"
        if "message" in info[statuskey]:
            self.notes.append(info[statuskey]["message"])

        # Required Dates
        if re.match(r".*Z$", info["workload-status"]["since"]):
            info["workload-status"]["since"] = re.sub(r"Z$", "", info["workload-status"]["since"])
            self.workloadsince = pendulum.from_format(
                info["workload-status"]["since"],
                "DD MMM YYYY HH:mm:ss",
                tz="UTC",
            )
        else:
            self.workloadsince = pendulum.from_format(
                info["workload-status"]["since"], "DD MMM YYYY HH:mm:ssZ"
            )
        controller.update_timestamp(self.workloadsince)
        if re.match(r".*Z$", info[statuskey]["since"]):
            info[statuskey]["since"] = re.sub(r"Z$", "", info[statuskey]["since"])
            self.jujusince = pendulum.from_format(
                info[statuskey]["since"], "DD MMM YYYY HH:mm:ss", tz="UTC"
            )
        else:
            self.jujusince = pendulum.from_format(
                info[statuskey]["since"], "DD MMM YYYY HH:mm:ssZ"
            )
        controller.update_timestamp(self.jujusince)

        # Optional Variables
        if "message" in info["workload-status"]:
            self.message = info["workload-status"]["message"]
        if "open-ports" in info:
            self.openports = info["open-ports"]
        if "leader" in info:
            self.leader = info["leader"]

    def to_dict(self):
        return {self.name: self}

    def get_workloadstatus_color(self):
        """
        Return a status string with correct colors based on workload status
        """
        if self.workloadstatus == "active":
            return Color.Fg.Green + self.workloadstatus + Color.Reset
        elif self.workloadstatus in ("error", "blocked"):
            return Color.Fg.Red + self.workloadstatus + Color.Reset
        elif self.workloadstatus == "waiting":
            return self.workloadstatus
        elif self.workloadstatus == "maintenance":
            return Color.Fg.Orange + self.workloadstatus + Color.Reset
        else:
            return Color.Fg.Yellow + self.workloadstatus + Color.Reset

    def get_jujustatus_color(self):
        """Return a status string with correct colors based on juju status"""
        if self.jujustatus in ("idle", "executing"):
            return Color.Fg.Green + self.jujustatus + Color.Reset
        elif self.jujustatus == "allocating":
            return Color.Fg.Orange + self.jujustatus + Color.Reset
        elif self.jujustatus in ("error", "lost", "failed"):
            return Color.Fg.Red + self.jujustatus + Color.Reset
        else:
            return Color.Fg.Yellow + self.jujustatus + Color.Reset

    def get_column_names(
        self, include_controller_name=False, include_model_name=False
    ):
        """Append the controller name and/or model name as necessary"""
        fields = list(self.column_names)
        if include_model_name:
            fields.insert(0, "Model")
        if include_controller_name:
            fields.insert(0, "Controller")
        return fields
