class SubLedgerError(Exception):
    """Base class for all domain-level errors. Each subclass carries the
    HTTP status code its route-level exception handler should return."""

    status_code = 400

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(SubLedgerError):
    status_code = 404


class DuplicateEmailError(SubLedgerError):
    status_code = 400


class InactivePlanError(SubLedgerError):
    status_code = 400


class InactiveSubscriptionError(SubLedgerError):
    status_code = 400


class DuplicateActiveSubscriptionError(SubLedgerError):
    status_code = 400


class InvalidPaymentAmountError(SubLedgerError):
    status_code = 400
