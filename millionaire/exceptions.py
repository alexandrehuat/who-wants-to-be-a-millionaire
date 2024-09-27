class MillionaireError(Exception):
    pass


class PerformanceError(MillionaireError):
    pass


class QuestionError(MillionaireError):
    pass


class QuestionNumberError(QuestionError):
    pass


class JokerError(MillionaireError):
    pass


class DisabledJokerError(JokerError):
    pass


class JokersDisabledForQLevelError(DisabledJokerError):
    pass


class MillionaireWarning(Warning):
    pass


class QuestionWarning(MillionaireWarning):
    pass


class QuestionUnderflowWarning(QuestionWarning):
    pass
