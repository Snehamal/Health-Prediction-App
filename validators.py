import re
from datetime import date

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def validate_full_name(name: str):
    if not name or not name.strip():
        return False, "Full name is required."
    if len(name.strip()) < 2:
        return False, "Full name must be at least 2 characters."
    return True, ""


def validate_email(email: str):
    if not email or not EMAIL_REGEX.match(email.strip()):
        return False, "Please enter a valid email address (e.g. name@example.com)."
    return True, ""


def validate_dob(dob: date):
    if dob is None:
        return False, "Date of birth is required."
    if dob > date.today():
        return False, "Date of birth cannot be in the future."
    return True, ""


def validate_numeric_range(value, field_name: str, min_value: float, max_value: float):
    """Generic numeric validator used for glucose, haemoglobin, cholesterol."""
    try:
        num = float(value)
    except (TypeError, ValueError):
        return False, f"{field_name} must be a number."

    if num < min_value or num > max_value:
        return False, f"{field_name} should be between {min_value} and {max_value}."
    return True, ""


def validate_patient_form(full_name, dob, email, glucose, haemoglobin, cholesterol):
    """
    Runs all validations for the patient form.
    Returns (is_valid: bool, errors: list[str])
    """
    errors = []

    ok, msg = validate_full_name(full_name)
    if not ok:
        errors.append(msg)

    ok, msg = validate_dob(dob)
    if not ok:
        errors.append(msg)

    ok, msg = validate_email(email)
    if not ok:
        errors.append(msg)

    # Realistic physiological ranges used purely for sanity-checking input
    ok, msg = validate_numeric_range(glucose, "Glucose (mg/dL)", 20, 600)
    if not ok:
        errors.append(msg)

    ok, msg = validate_numeric_range(haemoglobin, "Haemoglobin (g/dL)", 2, 25)
    if not ok:
        errors.append(msg)

    ok, msg = validate_numeric_range(cholesterol, "Cholesterol (mg/dL)", 50, 600)
    if not ok:
        errors.append(msg)

    return len(errors) == 0, errors
