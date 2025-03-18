class DIContainer:
    _services = {}

    @classmethod
    def register(cls, name, instance):
        cls._services[name] = instance

    @classmethod
    def resolve(cls, name):
        service = cls._services.get(name)
        return service() if callable(service) else service