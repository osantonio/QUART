class AppError(Exception):
    """Clase base para errores de la aplicación."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ValidationError(AppError):
    """Excepción para errores de validación de datos."""
    pass
