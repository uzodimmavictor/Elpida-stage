# func run
# func stop

import json
import sys
from component.component import Component
from component.component_factory import factory
import package


class Context:
    listComponents: list[Component]

    def __init__(self):
        self.listComponents = []

    def readConfigFile(self, configFile: str):
        # read JSON file
        try:
            with open(configFile, "r") as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"Error: '{configFile}' file was not found.")
            return None
        except json.JSONDecodeError as exc:
            print(f"Error: '{configFile}' is not valid JSON: {exc}")
            return None

    def loadConfiguration(self, configFile: str):
        data = self.readConfigFile(configFile)
        if data is None:
            print("Data not found")
            sys.exit(1)

        # 1. Load Components
        if "Components" not in data:
            print("Missing Component Key!!")
            sys.exit(1)

        components = data["Components"]
        if not isinstance(components, list):
            raise ValueError("'Components' must be a list")

        for component_data in components:
            if not isinstance(component_data, dict):
                raise ValueError("Each component must be an object")
            if component_data.get("nom") is None:
                raise ValueError("Missing key: 'nom'")
            if component_data.get("class") is None:
                raise ValueError("Missing key: 'class'")

            isConfigurable = component_data.get("isConfigurable", False)
            component = factory(component_data["class"], component_data["nom"], isConfigurable)
            self.listComponents.append(component)

        # 2. Apply Configuration using a separate function
        self.apply_configurations(data)
        return self

    def apply_configurations(self, data: dict):
        configurations = data.get("Configuration", {})
        if not isinstance(configurations, dict):
            raise ValueError("'Configuration' must be an object")

        for component in self.listComponents:
            if not  component.isConfigurable :
                continue
            if configurations[component.nom]is None:
                raise ValueError(f"Missing configuration for component: '{component.nom}'")
            component.configure(configurations[component.nom])

    def isConfigured(self):
        for component in self.listComponents:
            if not component.isConfigured():
                print(f"[{component.nom}] is not fully configured.")
                return False
        return True

    def start(self):
        for component in self.listComponents:
            if hasattr(component, "connect"):
                component.connect()

    def stop(self):
        for component in reversed(self.listComponents):
            if hasattr(component, "disconnect"):
                component.disconnect()
