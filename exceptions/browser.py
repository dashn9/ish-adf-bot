class PageLoadTimeoutException(Exception):
    def __init__(
        self, message="Page Failed To Fully Load Within Specified Time", details=None
    ):
        super().__init__(message)
        self.details = details
