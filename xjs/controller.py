#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .model import Model


class Controller:
    zerodate: datetime = datetime.fromtimestamp(0, tz=timezone.utc)

    def __init__(self, controllername: str, controllerinfo: dict[str, Any] | None = None) -> None:
        if controllerinfo is None:
            controllerinfo = {}

        self.notes: list[str] = []
        self.models: dict[str, Model] = {}
        self.name: str = controllername

        self.timestampprovided: bool = False
        self.timestamp: datetime = Controller.zerodate

        if "timestamp" in controllerinfo:
            self.timestampprovided = True
            ts: str = controllerinfo["timestamp"]
            if ts[:8].count(":") == 2 and ts[:2].isdigit():
                ts = "01 Jan 1970 " + ts
            if ts.endswith("Z"):
                ts = ts[:-1]
                self.timestamp = datetime.strptime(ts, "%d %b %Y %H:%M:%S").replace(tzinfo=timezone.utc)
            elif re.match(r".*[+-]\d\d:\d\d$", ts):
                self.timestamp = datetime.strptime(ts, "%d %b %Y %H:%M:%S%z")
            else:
                self.timestamp = datetime.strptime(ts, "%d %b %Y %H:%M:%S")

    def update_timestamp(self, date: datetime) -> None:
        if self.timestampprovided:
            str_time = self.timestamp.strftime("%H:%M:%S%z")
            str_date = date.strftime("%d %b %Y")
            temp_date = datetime.strptime(str_date + " " + str_time, "%d %b %Y %H:%M:%S%z")
            if temp_date > self.timestamp:
                self.timestamp = temp_date
        else:
            if date > self.timestamp:
                self.timestamp = date

    def add_model(self, model: Model) -> None:
        self.models[model.name] = model

    def filter_dictionary(self, dictionary: dict[str, Any], key_filter: str) -> dict[str, Any]:
        return {
            key: value
            for (key, value) in dictionary.items()
            if key_filter in key
        }

    def filter_models(self, model_filter: str) -> None:
        self.models = self.filter_dictionary(self.models, model_filter)
