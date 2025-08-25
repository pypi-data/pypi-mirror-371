## Installation and Usage

1. **Install Python**  
    Make sure you have Python installed. Download it from [python.org](https://www.python.org/downloads/).

2. **Install pyerrorhelper**  
    ```bash
    pip install pyerrorhelper
    ```

3. **How to use the library**  
    ```
    from pyerrorhelper import ErrorManager

    if __name__ == "__main__":
        error_manager = ErrorManager()
        error_manager.install()
    
    def cause_error():
        return 1 / 0  # This will raise a ZeroDivisionError
    
    cause_error()
    
    error_manager.uninstall()
    ```
