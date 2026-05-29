#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from .application import Application


class Relation:
    """
    A Relation is a juju relation between 2 juju applications, juju status
    does not provide much information.
    """

    column_names = [
        "Application A",
        "Application B"
    ]

    def __init__(self, model, name, partnername, applicationname):
        """
        Create a Relation object from a juju status output        """

        # Handle new Juju relation format
        if isinstance(partnername, dict):
            partnername = partnername.get("related-application")

        # Default Values
        self.name = name
        self.application = model.get_application(applicationname)
        if model.get_application(partnername):
            self.partner = model.get_application(partnername)
        else:
            self.partner = Application(partnername)

    def to_dict(self):
        return {self.name: self}

    def get_row(
        self, color, include_controller_name=False, include_model_name=False
    ):
        """Return a list which can be used for a row in a table."""
        row = [
            f"{self.application.name}:{self.name}",
            f"{self.partner.name}:{self.name}",
            ]
        if include_model_name:
            row.insert(0, self.application.model.name)
        if include_controller_name:
            row.insert(0, self.application.model.controller.name)
        return row

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
