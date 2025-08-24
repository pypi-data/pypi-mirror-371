import sys

class ErrorManager:
    def __init__(self):
        self.old_hook = sys.excepthook

    def handle_error(self, exc_type, exc_value, exc_traceback):
        print("Custom Error Handler:")
        print(f"Error Type: {exc_type.__name__}")
        print(f"Error Message: {exc_value}")
        print(f"Traceback: {exc_traceback}")
    
    def install(self):
        sys.excepthook = self.handle_error
    
    def uninstall(self):
        sys.excepthook = self.old_hook