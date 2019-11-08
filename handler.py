import json
import os
from urllib.parse import parse_qs

from marshmallow import Schema, fields, post_load


class Contact:
    '''
    Represents a Contact event. A submission of the
    Contact form.
    '''
    def __init__(self, email: str, name: str, content: str, **kwargs):
        self.email = email
        self.name = name
        self.content = content


class ContactSchema(Schema):
    '''
    Valiates the content of a Contact Form submission.
    '''
    email = fields.Email(required=True)
    name = fields.String(required=True)
    content = fields.String(required=True)

    @post_load
    def make_contact(self, data, **kwargs):
        return Contact(**data)


def parse_qs_single_value(data: str) -> dict:
    '''
    Parses a form-encoded string, extracting only one value
    per field.
    '''
    raw = parse_qs(data)
    return {key: value[0] for key, value in raw.items()}


def handle_contact(event, context):
    '''
    Handles submissions of the Contact Us form.
    '''
    body = parse_qs_single_value(event.get('body', ''))
    schema = ContactSchema()
    errors = schema.validate(body)
    if errors:
        return {
            'statusCode': 400,
            'errors': errors,
        }

    contact = schema.load(body)
    return {
        "statusCode": 200,
        "body": schema.dump(contact)
    }
