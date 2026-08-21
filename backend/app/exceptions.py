class PreparationNotFoundError(LookupError):
    pass


class InvalidPreparationInputError(ValueError):
    pass


class PreparationDependencyError(RuntimeError):
    pass
