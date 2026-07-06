from component.component_registry import REGISTRY


def factory(key, nom, isConfigurable):
    cls = REGISTRY.get(key)
    if not cls:
        available = ", ".join(sorted(REGISTRY)) or "no registered components"
        raise ValueError(f"unknown component class: {key}. Available classes: {available}")
    return cls(nom, isConfigurable)
