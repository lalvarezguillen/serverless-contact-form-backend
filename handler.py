import json
import os
from urllib.parse import parse_qs

import boto3
from marshmallow import Schema, fields, post_load, ValidationError

import config

class Contact:
    '''
    Represents a Contact event. A submission of the
    Contact form.
    '''
    def __init__(self, email: str, name: str, content: str):
        self.email = email
        self.name = name
        self.content = content
    
    def produce_ses_message(self) -> dict:
        subject = {
            'Charset': config.CHARSET,
            'Data': f'New Contact from {self.email}'
        }
        html_body = {
            'Charset': config.CHARSET,
            'Data': (
                '<p>New Contact:</p>'
                f'<p>Name: {self.name}</p>'
                f'<p>Email: {self.email}</p>'
                f'<p>Message: {self.content}</p>'
            )
        }
        text_body = {
            'Charset': config.CHARSET,
            'Data': (
                'New Contact\n'
                f'Name: {self.name}\n'
                f'Email: {self.email}\n'
                f'Message: {self.content}\n'
            )
        }
        return {
            'Body': {
                'Html': html_body,
                'Text': text_body,
            },
            'Subject': subject
        }


class ContactSchema(Schema):
    '''
    Validates the content of a Contact Form submission.
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


def send_email(contact: Contact):
    client = boto3.client('ses', region_name=config.AWS_REGION)
    resp = client.send_email(
        Destination={'ToAddresses': config.RECEIVING_ADDRESSES},
        Message=contact.produce_ses_message(),
        Source=config.SENDING_ADDRESS
    )
    print('sent email successfully')


def handle_contact(event, context):
    '''
    Handles submissions of the Contact Us form.
    '''
    body = parse_qs_single_value(event.get('body', ''))

    schema = ContactSchema()
    try:
        contact = schema.load(body)
    except ValidationError as err:
        return {
            'statusCode': 400,
            'body': json.dumps(err.messages),
        }

    send_email(contact)
    return {
        "statusCode": 200,
        "body": schema.dumps(contact)
    }
