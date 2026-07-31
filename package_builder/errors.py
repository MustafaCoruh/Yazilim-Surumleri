class PackageError(Exception):
    pass


class ValidationError(PackageError):
    pass


class PresetError(PackageError):
    pass


class XmlConfigurationError(PackageError):
    pass


class PackageWarning(UserWarning):
    pass
