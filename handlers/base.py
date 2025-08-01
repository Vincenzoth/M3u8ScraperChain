class Handler:
    def __init__(self):
        self.next_handler = None

    def set_next(self, handler):
        self.next_handler = handler
        return handler

    def handle(self, context):
        result = self._handle(context)
        if self.next_handler and result:
            return self.next_handler.handle(result)
        if result:
            return result
        return None

    def _handle(self, context):
        raise NotImplementedError("Implementa _handle nella sottoclasse.")
