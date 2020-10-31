# define Python user-defined exceptions
class Error(Exception):
    # Base class for other exceptions
    pass


# Custom Error class for GenericSqliteConnector

class GenericSqliteConnectorError(Error):
    pass


class DuplicationMouseError(GenericSqliteConnectorError):
    """
    Raised when the duplication mouse occured during insertion
    """
    def __init__(self, duplicated_mouse_input):
        self.duplicated_mouse_input = duplicated_mouse_input
        self.message = '['
        for m in self.duplicated_mouse_input:
            self.message += str(m) + ','
        self.message = self.message[:-1] + ']'
        super().__init__(self.message)


class MouseNotFoundError(GenericSqliteConnectorError):
    """
    Raised when the non-existed mouse occured during updates and deletion
    """
    def __init__(self, duplicated_mouse_input):
        self.duplicated_mouse_input = duplicated_mouse_input
        self.message = '['
        for m in self.duplicated_mouse_input:
            self.message += str(m) + ','
        self.message = self.message[:-1] + ']'
        super().__init__(self.message)


# Custom Error class for MouseControllerError
class MouseControllerError(Error):
    pass


class WrongTypeError(MouseControllerError):
    pass


