class TimezoneFetchException(Exception):
    def __init__(self, message="Failed to fetch timezone", details=None):
        super().__init__(message)
        self.details = details
