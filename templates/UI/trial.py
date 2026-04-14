from django.core.exceptions import ValidationError
import re

def password_validation(password):

    if len(password) < 8:
        raise ValidationError("Password must be at least 8 characters long.")

    elif not password[0].isupper():
        raise ValidationError("First character must be an Alphabet in Capital letter.")

    elif not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValidationError("Password must contain at least one special character.")

    elif not re.search(r'[0123456789]', password):
        raise ValidationError("Password must contain at least one Number.")

    print('Password Correct')

password=input('Enter the Password : ')
password_validation(password)