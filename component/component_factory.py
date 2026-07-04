from component.component_registry import REGISTRY

def factory(key, nom, isConfigurable):
    cls = REGISTRY.get(key)
    if not cls:
        raise ValueError(f"unknown key: {key}")
    return cls(nom, isConfigurable)
