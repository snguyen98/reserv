import logging

class ConsoleFilter(logging.Filter):
    """
    Defines a logging filter for the development server logs
    """
    def filter(self, record):
        filter_strs = [
             "Press CTRL+C to quit",
             "This is a development server."
        ]
        return not any(filter_str in record.getMessage() 
                       for filter_str in filter_strs)
    

class WebRequestFilter(logging.Filter):
    """
    Defines a logging filter for all web requests made by werkzeug
    """
    def filter(self, record):
        filter_strs = [
             "HTTP/1.1"
        ]
        return not any(filter_str in record.getMessage() 
                       for filter_str in filter_strs)