class DependencyError(Exception):
    pass

class CycleError(DependencyError):
    pass

class AppError(Exception):
    pass

class CallbackError(AppError):
    pass

class TerminateError(AppError):
    pass

class ModuleError(AppError):
    pass

class ModuleInitError(ModuleError):
    pass

class ModuleTerminateError(ModuleError):
    pass