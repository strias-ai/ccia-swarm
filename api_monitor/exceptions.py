class URLConnectionError(Exception):
    """Excepción lanzada cuando hay un error en la conexión a una URL."""
    pass

class URLTimeoutError(Exception):
    """Excepción lanzada cuando la conexión a una URL se agota."""
    pass

class URLInvalidError(Exception):
    """Excepción lanzada cuando la URL es inválida."""
    pass

class URLStatusCodeError(Exception):
    """Excepción lanzada cuando el código de estado de la respuesta HTTP no es exitoso."""
    pass

class URLResponseError(Exception):
    """Excepción lanzada cuando hay un error en la respuesta de la URL."""
    pass