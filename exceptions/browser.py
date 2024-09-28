class BrowserStartException(Exception):
    def __init__(self, message="Failed to start browser", details=None):
        super().__init__(message)
        self.details = details
