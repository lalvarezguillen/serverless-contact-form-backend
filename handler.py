import json
import os
from urllib.parse import parse_qs
from typing import Optional

import requests
import boto3
from marshmallow import Schema, fields, post_load, ValidationError

import config


class Contact:
    """
    Represents a Contact event. A submission of the
    Contact form.
    """

    def __init__(
        self,
        email: str,
        name: str,
        content: str,
        subject: str,
        phone: Optional[str] = None,
        company_name: Optional[str] = None,
        *args,
        **kwargs,
    ):
        self.email = email
        self.name = name
        self.content = content
        self.subject = subject
        self.phone = phone
        self.company_name = company_name

    def _produce_html_body(self) -> dict:
        body = (
            "<p>New Contact:</p>"
            f"<p>Name: {self.name}</p>"
            f"<p>Email: {self.email}</p>"
            f"<p>Subject: {self.subject}</p>"
            f"<p>Message: {self.content}</p>"
        )

        if self.phone:
            body += f"<p>Phone: {self.phone}</p>"

        if self.company_name:
            body += f"<p>Company Name: {self.company_name}</p>"

        return body

    def _produce_plaintext_body(self) -> dict:
        body = (
            "New Contact:\n"
            f"Name: {self.name}\n"
            f"Email: {self.email}\n"
            f"Subject: {self.subject}\n"
            f"Message: {self.content}\n"
        )

        if self.phone:
            body += f"Phone: {self.phone}\n"

        if self.company_name:
            body += f"Company Name: {self.company_name}\n"

        return body

    def produce_ses_message(self) -> dict:
        subject = {
            "Charset": config.CHARSET,
            "Data": f"New Contact from {self.email}",
        }
        html_body = self._produce_html_body()
        text_body = self._produce_plaintext_body()
        return {
            "Body": {
                "Html": {"Charset": config.CHARSET, "Data": html_body},
                "Text": {"Charset": config.CHARSET, "Data": text_body},
            },
            "Subject": subject,
        }

    def produce_mailgun_message(self) -> dict:
        return {
            "from": config.SENDING_ADDRESS,
            "to": config.RECEIVING_ADDRESSES,
            "subject": f"New Contact from {self.email}",
            "text": self._produce_html_body(),
        }


class ContactSchema(Schema):
    """
    Validates the content of a Contact Form submission.
    """

    email = fields.Email(required=True)
    name = fields.String(required=True)
    subject = fields.String(required=True)
    content = fields.String(required=True)
    phone = fields.String()
    company_name = fields.String()

    @post_load
    def make_contact(self, data, **kwargs):
        return Contact(**data)


def parse_qs_single_value(data: str) -> dict:
    """
    Parses a form-encoded string, extracting only one value
    per field.
    """
    raw = parse_qs(data)
    return {key: value[0] for key, value in raw.items()}


def send_email(contact: Contact):
    client = boto3.client("ses", region_name=config.AWS_REGION)
    resp = client.send_email(
        Destination={"ToAddresses": config.RECEIVING_ADDRESSES},
        Message=contact.produce_ses_message(),
        Source=config.SENDING_ADDRESS,
    )
    print("sent email successfully")


def send_mailgun_email(contact: Contact):
    resp = requests.post(
        config.MAILGUN_URL,
        auth={"api", config.MAILGUN_API_KEY},
        data=contact.produce_mailgun_message(),
    )
    print(f'Mailgun Resp: {resp.status_code} {resp.text}')


def handle_contact(event, context):
    """
    Handles submissions of the Contact Us form.
    """
    body = parse_qs_single_value(event.get("body", ""))

    schema = ContactSchema()
    try:
        contact = schema.load(body)
    except ValidationError as err:
        return {
            "statusCode": 400,
            "body": json.dumps(err.messages),
        }

    send_mailgun_email(contact)
    return {"statusCode": 200, "body": schema.dumps(contact)}
