#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only

from __future__ import annotations

import json
import sys
from .application import Application
import click
from . import __version__
from .controller import Controller
from .machine import Machine
from .model import Model
from .relation import Relation
from rich.console import Console
from rich.table import Table
from rich.text import Text
import yaml
from typing import Any, TextIO


def load_status_file(inputfile: TextIO, controllers: dict[str, Controller]) -> None:
    """Load a juju status file, inputfile is a yaml or json file"""
    rawstatus: dict[str, Any] = {}

    try:
        rawstatus = json.loads(inputfile)
    except Exception:
        try:
            rawstatus = yaml.safe_load(inputfile)
        except Exception:
            console = Console()
            console.print("[red]Error trying to load status file[/red]")
            sys.exit(1)

    if "model" not in rawstatus and "services" in rawstatus:
        controllername = "controller"
        modelkey = "environment-status"
        applicationkey = "services"
    else:
        controllername = rawstatus["model"]["controller"]
        modelkey = "model"
        applicationkey = "applications"

    if controllername in controllers:
        controller = controllers[controllername]
    else:
        if "controller" in rawstatus:
            controller = Controller(controllername, rawstatus["controller"])
        else:
            controller = Controller(controllername)
        controllers[controllername] = controller

    model = Model(rawstatus[modelkey], controller)
    if model.name in controller.models:
        console = Console()
        console.print(
            f"[red]Error model {model.name} already exists for controller {controllername}[/red]"
        )
        sys.exit(1)
    controller.add_model(model)
    for machname, machinfo in rawstatus["machines"].items():
        machine = Machine(machname, machinfo, model)
        model.add_machine(machine)
    for appname, appinfo in rawstatus[applicationkey].items():
        application = Application(appname, appinfo, model)
        model.add_application(application)
    for appname, appinfo in model.applications.items():
        for unitname, unit in appinfo.units.items():
            for subunitname, subunit in unit.subordinates.items():
                subunit.create_application_relation()

    for appname, appinfo in rawstatus[applicationkey].items():
        if "relations" in appinfo:
            for relationname, partnerapps in appinfo["relations"].items():
                for partnerapp in partnerapps:
                    relation = Relation(model, relationname, partnerapp, appname)
                    model.add_relation(relation)


def console_print_model_info(controllers: dict[str, Controller], color: bool = True) -> None:
    models: list[Model] = []
    for controllername, controller in controllers.items():
        for modelname, model in controller.models.items():
            models.append(model)
    if len(models) > 0:
        console_print_object(print_what=models, color=color)


def console_print_application_info(
    controllers: dict[str, Controller], color: bool = True, hide_scale_zero: bool = False
) -> None:
    apps: list[Application] = []
    include_controller_name = False
    include_model_name = False

    if len(controllers) > 1:
        include_controller_name = True
        include_model_name = True
    for controllername, controller in controllers.items():
        if len(controller.models) > 1:
            include_model_name = True
        for modelname, model in controller.models.items():
            for appname, app in model.applications.items():
                if not hide_scale_zero or app.get_scale() > 0:
                    apps.append(app)
    if len(apps) > 0:
        console_print_object(
            print_what=apps,
            color=color,
            include_controller_name=include_controller_name,
            include_model_name=include_model_name,
        )


def console_print_unit_info(
    controllers: dict[str, Controller], color: bool = True, hide_subordinate_units: bool = False
) -> None:
    units: list[Any] = []
    include_controller_name = False
    include_model_name = False

    if len(controllers) > 1:
        include_controller_name = True
        include_model_name = True
    for controllername, controller in controllers.items():
        if len(controller.models) > 1:
            include_model_name = True
        for modelname, model in controller.models.items():
            for appname, application in model.applications.items():
                for unitname, unit in application.units.items():
                    units.append(unit)
                    if not hide_subordinate_units:
                        for subunitname, subunit in unit.subordinates.items():
                            units.append(subunit)
    if len(units) > 0:
        console_print_object(
            print_what=units,
            color=color,
            include_controller_name=include_controller_name,
            include_model_name=include_model_name,
        )


def console_print_networkinterface_info(
    controllers: dict[str, Controller], color: bool = True, include_containers: bool = True
) -> None:
    nics: list[Any] = []
    include_controller_name = False
    include_model_name = False

    if len(controllers) > 1:
        include_controller_name = True
        include_model_name = True
    for controllername, controller in controllers.items():
        if len(controller.models) > 1:
            include_model_name = True
        for modelname, model in controller.models.items():
            for machinename, machine in model.machines.items():
                for nicname, nic in machine.networkinterfaces.items():
                    nics.append(nic)
                if include_containers:
                    for containername, container in machine.containers.items():
                        for nicname, nic in container.networkinterfaces.items():
                            nics.append(nic)
    if len(nics) > 0:
        console_print_object(
            print_what=nics,
            color=color,
            include_controller_name=include_controller_name,
            include_model_name=include_model_name,
        )


def console_print_machine_info(
    controllers: dict[str, Controller], color: bool = True, include_containers: bool = True
) -> None:
    machines: list[Any] = []
    include_controller_name = False
    include_model_name = False

    if len(controllers) > 1:
        include_controller_name = True
        include_model_name = True
    for controllername, controller in controllers.items():
        if len(controller.models) > 1:
            include_model_name = True
        for modelname, model in controller.models.items():
            for machinename, machine in model.machines.items():
                machines.append(machine)
                if include_containers:
                    for containername, container in machine.containers.items():
                        machines.append(container)
    if len(machines) > 0:
        console_print_object(
            print_what=machines,
            color=color,
            include_controller_name=include_controller_name,
            include_model_name=include_model_name,
        )


def console_print_relations(controllers: dict[str, Controller], color: bool = True) -> None:
    relations: list[Relation] = []
    include_controller_name = False
    include_model_name = False

    if len(controllers) > 1:
        include_controller_name = True
        include_model_name = True
    for controllername, controller in controllers.items():
        if len(controller.models) > 1:
            include_model_name = True
        for modelname, model in controller.models.items():
            for relationname, relation in model.relations.items():
                for singlerelation in model.relations[relationname]:
                    relations.append(singlerelation)
    if len(relations) > 0:
        console_print_object(
            print_what=relations,
            color=color,
            include_controller_name=include_controller_name,
            include_model_name=include_model_name,
        )


def console_print_object(
    print_what: list[Any],
    color: bool = True,
    include_controller_name: bool = False,
    include_model_name: bool = False,
) -> None:
    """Print a table formatted for the console and fit terminal width."""
    console = Console(no_color=not color)
    table = Table(show_header=True, header_style="bold")
    for col_name in print_what[0].get_column_names(
        include_controller_name, include_model_name
    ):
        table.add_column(col_name)

    for i, row in enumerate(print_what):
        row_data = row.get_row(color, include_controller_name, include_model_name)
        table.add_row(*row_data, style="on grey7" if color and i % 2 == 0 else "")

    console.print(table)


def filter_dictionary(dictionary: dict[str, Any], key_filter: str) -> dict[str, Any]:
    return {
        key: value for (key, value) in dictionary.items() if key_filter in key
    }


def filter_results(
    controllers: dict[str, Controller],
    ctrl_filter: str = "",
    model_filter: str = "",
    app_filter: str = "",
    unit_filter: str = "",
    subunit_filter: str = "",
    machine_filter: str = "",
) -> None:
    """Filter the status"""
    filtered_controllers: dict[str, Controller] = {}

    if ctrl_filter != "":
        filtered_controllers = filter_dictionary(controllers, ctrl_filter)
    else:
        filtered_controllers = controllers

    if model_filter != "":
        empty_controllers: list[str] = []
        for controllername, controller in filtered_controllers.items():
            controller.filter_models(model_filter)
            if len(controller.models) == 0:
                empty_controllers.append(controllername)
        for controllername in empty_controllers:
            del filtered_controllers[controllername]

    if app_filter != "":
        empty_controllers = []
        for controllername, controller in filtered_controllers.items():
            empty_models: list[str] = []
            for modelname, model in controller.models.items():
                model.filter_applications(app_filter)
                if len(model.applications) == 0:
                    empty_models.append(modelname)
            for modelname in empty_models:
                del controller.models[modelname]
            if len(controller.models) == 0:
                empty_controllers.append(controllername)
        for controllername in empty_controllers:
            del filtered_controllers[controllername]

    if unit_filter != "":
        empty_controllers = []
        for controllername, controller in filtered_controllers.items():
            empty_models = []
            for modelname, model in controller.models.items():
                empty_applications: list[str] = []
                for appname, application in model.applications.items():
                    application.filter_units(unit_filter)
                    if len(application.units) == 0:
                        empty_applications.append(appname)
                for appname in empty_applications:
                    del model.applications[appname]
                model.reset_machines()
                if len(model.applications) == 0:
                    empty_models.append(modelname)
            for modelname in empty_models:
                del controller.models[modelname]
            if len(controller.models) == 0:
                empty_controllers.append(controllername)
        for controllername in empty_controllers:
            del filtered_controllers[controllername]

    if subunit_filter != "":
        empty_controllers = []
        for controllername, controller in filtered_controllers.items():
            empty_models = []
            for modelname, model in controller.models.items():
                empty_applications = []
                for appname, application in model.applications.items():
                    empty_units: list[str] = []
                    for unitname, unit in application.units.items():
                        unit.filter_subordinates(subunit_filter)
                        if len(unit.subordinates) == 0:
                            empty_units.append(unitname)
                    for unitname in empty_units:
                        del application.units[unitname]
                    if len(application.units) == 0:
                        empty_applications.append(appname)
                for appname in empty_applications:
                    del model.applications[appname]
                model.reset_machines()
                if len(model.applications) == 0:
                    empty_models.append(modelname)
            for modelname in empty_models:
                del controller.models[modelname]
            if len(controller.models) == 0:
                empty_controllers.append(controllername)
        for controllername in empty_controllers:
            del filtered_controllers[controllername]

    if machine_filter != "":
        empty_controllers = []
        for controllername, controller in filtered_controllers.items():
            empty_models = []
            for modelname, model in controller.models.items():
                model.filter_machines(machine_filter)
                if len(model.machines) == 0:
                    empty_models.append(modelname)
            for modelname in empty_models:
                del controller.models[modelname]
            if len(controller.models) == 0:
                empty_controllers.append(controllername)
        for controllername in empty_controllers:
            del filtered_controllers[controllername]

    controllers = filtered_controllers


@click.version_option(__version__)
@click.command()
@click.option("--application", default="", help="Show only the application with the specified name", metavar="<application name>")
@click.option("--controller", default="", help="Show only the controller with the specified name", metavar="<controller name>")
@click.option("--hide-scale-zero", "-h", default=False, is_flag=True, help="Hide applications with a scale of 0")
@click.option("--hide-subordinate-units", "-s", default=False, is_flag=True, help="Hide subordinate units")
@click.option("--include-containers", "-c", default=False, is_flag=True, help="Include Container information")
@click.option("--machine", default="", help="Show only the machine with the specified name", metavar="<machine name>")
@click.option("--model", default="", help="Show only the model with the specified name", metavar="<model name>")
@click.option("--no-color", default=False, is_flag=True, help="Remove color from output")
@click.option("--show-apps", "-a", default=False, is_flag=True, help="Show application information")
@click.option("--show-machines", "-m", default=False, is_flag=True, help="Show machine information")
@click.option("--show-model", "-d", default=False, is_flag=True, help="Show model information")
@click.option("--show-net", "-n", default=False, is_flag=True, help="Show network interface information")
@click.option("--show-units", "-u", default=False, is_flag=True, help="Show unit information")
@click.option("--show-relations", "-r", default=False, is_flag=True, help="Show relation information")
@click.option("--subordinate", default="", help="Show only the subordinate unit with the specified name", metavar="<subordinate name>")
@click.option("--unit", default="", help="Show only the unit with the specified name", metavar="<unit name>")
@click.argument("statusfiles", required=True, type=click.File("r"), nargs=-1, metavar="<status files>")
def main(
    statusfiles: tuple[TextIO, ...],
    hide_scale_zero: bool,
    hide_subordinate_units: bool,
    show_apps: bool,
    show_units: bool,
    show_machines: bool,
    show_net: bool,
    show_model: bool,
    show_relations: bool,
    include_containers: bool,
    no_color: bool,
    controller: str,
    application: str,
    unit: str,
    model: str,
    machine: str,
    subordinate: str,
) -> None:
    color = not no_color
    controllers: dict[str, Controller] = {}
    for statusfile in statusfiles:
        load_status_file(statusfile, controllers)

    if (
        not show_apps
        and not show_units
        and not show_machines
        and not show_net
        and not show_model
        and not include_containers
        and not show_relations
    ):
        show_apps = True
        show_units = True
        show_machines = True
        show_net = True
        show_model = True
        show_relations = True
        include_containers = True

    if controller != "" or model != "" or application != "" or unit != "" or machine != "" or subordinate != "":
        filter_results(
            controllers,
            ctrl_filter=controller,
            model_filter=model,
            app_filter=application,
            unit_filter=unit,
            subunit_filter=subordinate,
            machine_filter=machine,
        )

    if show_model:
        console_print_model_info(controllers, color)
        print("")
    if show_apps:
        console_print_application_info(controllers, color, hide_scale_zero)
        print("")
    if show_units:
        console_print_unit_info(controllers, color, hide_subordinate_units)
        print("")
    if show_machines:
        console_print_machine_info(controllers, color, include_containers)
        print("")
    if show_net:
        console_print_networkinterface_info(controllers, color, include_containers)
        print("")
    if show_relations:
        console_print_relations(controllers, color)
        print("")


if __name__ == "__main__":
    main()
