class NotFoundException(Exception):
    """
        Exception raised when some aspect of a request could not be found
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InsufficientDataException(Exception):
    """
        Exception raised when the expected form data is missing
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
