#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from .basicmachine import BasicMachine
from .colors import Color


class Container(BasicMachine):
    iscontainer = True

    def __init__(self, containername, containerinfo, machine, model):
        """
        Create a Container object with basic information from a container
        object from a juju status output
        """
        # Setup the BasicMachine
        BasicMachine.__init__(self, containername, containerinfo, model)

        # Required Variables
        self.machine = machine

    def get_machinemessage_color(self):
        """
        Return a message string with correct colors based on the machine status
        """
        if self.machinemessage == "Container started":
            return Color.Fg.Green + self.machinemessage + Color.Reset
        else:
            return Color.Fg.Yellow + self.machinemessage + Color.Reset

    def get_row(
        self, color, include_controller_name=False, include_model_name=False
    ):
        """Return a list which can be used for a row in a table."""
        row = []
        notesstr = ", ".join(self.notes)

        if color:
            row = [
                self.name,
                self.get_jujustatus_color(),
                self.get_machinestatus_color(),
                self.dnsname,
                self.instanceid,
                self.base,
                "",
                "",
                "",
                "",
                self.get_machinemessage_color(),
                notesstr,
            ]
        else:
            row = [
                self.name,
                self.jujustatus,
                self.machinestatus,
                self.dnsname,
                self.instanceid,
                self.base,
                "",
                "",
                "",
                "",
                self.machinemessage,
                notesstr,
            ]

        if include_model_name:
            row.insert(0, self.machine.model.name)
        if include_controller_name:
            row.insert(0, self.machine.model.controller.name)
        return row
