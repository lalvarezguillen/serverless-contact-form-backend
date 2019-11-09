from unittest.mock import patch

import pytest
from marshmallow import ValidationError

from handler import parse_qs_single_value, ContactSchema, Contact, handle_contact

@pytest.mark.parametrize(
    'inp, expected_out',
    (
        ('', {}),
        ('thisis=sparta;thatis=notsparta', {'thisis': 'sparta', 'thatis': 'notsparta'}),
        ('thisis=sparta;thisis=alsosparta', {'thisis': 'sparta'})
    )
)
def test_parse_qs_single_value(inp, expected_out):
    assert parse_qs_single_value(inp) == expected_out



class TestContactSchema:
    @pytest.mark.parametrize(
        'inp',
        (
            {'email': 'thisis@sparta.com', 'name': 'spartan', 'content': 'this is sparta'},
        )
    )
    def test_success(self, inp):
        contact = ContactSchema().load(inp)
        assert contact.email == inp['email']
        assert contact.name == inp['name']
        assert contact.content == inp['content']

    @pytest.mark.parametrize(
        'inp',
        (
            {'email': 'invalid@email', 'name': 'spartan', 'content': 'this is sparta'},
            {'name': 'spartan', 'content': 'this is sparta'},
            {'email': 'thisis@sparta.com', 'content': 'this is sparta'},
            {'email': 'thisis@sparta.com', 'name': 'spartan'},
        )
    )
    def test_error(self, inp):
        with pytest.raises(ValidationError):
            ContactSchema().load(inp)



class TestHandleContact:
    @pytest.mark.parametrize(
        'inp',
        (
            {'body': 'email=thisis@sparta.com;name=spartan;content=thisissparta'},
        )
    )
    def test_success(self, inp):
        with patch('handler.send_email') as send_email_mock:
            resp = handle_contact(inp, {})
            assert send_email_mock.call_count == 1
        assert resp['statusCode'] == 200

    @pytest.mark.parametrize(
        'inp',
        (
            {'body': 'name=spartan;content=thisissparta'},
        )
    )
    def test_error(self, inp):
        with patch('handler.send_email') as send_email_mock:
            resp = handle_contact(inp, {})
            assert not send_email_mock.called
        assert resp['statusCode'] == 400