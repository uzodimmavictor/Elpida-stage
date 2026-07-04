REGISTRY = {
    
}

def registry(key):
    def wrapper(cls):
        REGISTRY[key] = cls
        return cls
    return wrapper