from email_validator import (
    EmailNotValidError,
    validate_email
)


def _validate_email(email: str):
    message = ''
    valid = False
    try:
        validated = validate_email(email)
        email = validated.email
        valid = True

    except EmailNotValidError as error:
        message = str(error)

    return valid, message, email