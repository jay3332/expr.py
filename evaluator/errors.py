class EvaluatorError(Exception):
    ...


class CastingError(ValueError, EvaluatorError):
    ...


class BadOperation(EvaluatorError):
    ...
