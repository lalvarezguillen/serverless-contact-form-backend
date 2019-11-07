import json
import os
from urllib.parse import parse_qs

from email_validator import validate_email, EmailNotValidError


DEV_NAME = os.environ.get('dev_name', 'default dev name')


class FormData:
    def __init__(self, email: str, name: str, content: str, **kwargs):
        self.email = email
        self.name = name
        self.content = content


class ValidationError(Exception):
    '''
    To be raised when the form data is not valid
    '''

def is_email(text: str) -> bool:
    return '@' in text and '.' in text


def parse_form_data(form_data: str) -> FormData:
    parsed = parse_qs(form_data)
    fields = ['email', 'name', 'content']
    for field in fields:
        if not parsed.get(field):
            raise ValidationError(f'{field} is required')
    
    try:
        validate_email(parsed['email'][0], check_deliverability=False)
    except EmailNotValidError:
        raise ValidationError(f'Invalid email')
    
    return FormData(
        parsed['email'][0],
        parsed['name'][0],
        parsed['content'][0]
    )


def hello(event, context):
    body = event.get('body', {})

    try:
        form_data = parse_form_data(body)
    except ValidationError as err:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(err)})
        }

    return {
        "statusCode": 200,
        "body": json.dumps(form_data.__dict__)
    }
