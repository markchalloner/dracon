
class DraconConfigError(Exception):
    """Raised when the config trying to load is not valid"""
    pass


class DraconOutputError(Exception):
    """Raised when writing output fails"""
    pass
