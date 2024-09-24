class Return(Exception):
    def __init__(self, value):
        super().__init__(None, None)  # Disabling stack trace and message
        self.value = value
