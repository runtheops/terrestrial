class TerrestrialError(Exception):
    pass


class TerrestrialRetryError(TerrestrialError):
    pass


class TerrestrialFatalError(TerrestrialError):
    pass
