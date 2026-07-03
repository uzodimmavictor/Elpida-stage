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
        ## read JSON file
        try:
            with open(configFile, "r") as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print(f"Error: '{configFile}' file was not found.")
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
        for component_data in components:
            if component_data.get("nom") is None:
                raise ValueError("Missing key: 'nom'")
            if component_data.get("class") is None:
                raise ValueError("Missing key: 'class'")
            
            isConfigurable = component_data.get("isConfigurable", False)   
            component = factory(component_data["class"], component_data["nom"], isConfigurable)
            self.listComponents.append(component)

        # 2. Apply Configuration using a separate function
        self.apply_configurations(data)
        
    def apply_configurations(self, data: dict):
        if "Configuration" in data:
            for key, config_data in data["Configuration"].items():
                # Find the matching component
                for component in self.listComponents:
                    if component.nom == key and component.isConfigurable:
                        component.configure(config_data)
