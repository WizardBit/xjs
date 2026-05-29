#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

from .application import Application
from .model import Model


class Relation:
    column_names: list[str] = [
        "Application A",
        "Application B"
    ]

    def __init__(self, model: Model, name: str, partnername: str | dict[str, str], applicationname: str) -> None:
        if isinstance(partnername, dict):
            partnername = partnername.get("related-application", "")

        self.name: str = name
        app = model.get_application(applicationname)
        self.application: Application = app if app else Application(applicationname)
        partner = model.get_application(partnername)
        self.partner: Application = partner if partner else Application(partnername)

    def get_row(
        self, color: bool, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str]:
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
        self, include_controller_name: bool = False, include_model_name: bool = False
    ) -> list[str]:
        fields = list(self.column_names)
        if include_model_name:
            fields.insert(0, "Model")
        if include_controller_name:
            fields.insert(0, "Controller")
        return fields
