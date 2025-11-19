from .validators import ValidateExistingEmail, ValidateNewPassword, ValidateOptionalVerificationCode

# Restore request schemas
class RestoreRequest(ValidateExistingEmail, ValidateNewPassword, ValidateOptionalVerificationCode):
    """Request schema for restoring a user"""