import delorean
from freezegun import freeze_time
from offers import token_validation
from .constants import PRIVATE_KEY, PUBLIC_KEY


INVALID_PUBLIC_KEY = '''
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAvlwUWlq/QH3q6bZj37Ud
uNUm54BzSVo8oERgJ8rxfJCZbNuc6kOLoPDduxgU/QQNvktIJlEt6i2YYRISNd1x
lYOg1EBM2wc6nbT0iF0EF618X+STvdH9g4UPd94G6CUXHT22gA1CPwpDtPos6Li0
BrVb2FE8RlC/cyDUQ+VOu8DijCDnnEv4lWAZUzgyLPWdRpJodMSwpfNKAHvREx8V
HqY+cd5zFisR6TuKVaMPZ68evTP++/jQ/ozN1843YSQjRmW3dkZynuGsRccUzCOA
ooXAnLUVg/2KpWbLouzYsVkHECpCgHLUJmpRvkNkv5s/02+mKyMQv6DUFA5dveSS
4wIDAQAB
-----END PUBLIC KEY-----
'''


def test_encode_and_decode():
    payload = {
        'example': 'payload',
    }

    token = token_validation.encode_token(payload, PRIVATE_KEY)
    assert payload == token_validation.decode_token(token, PUBLIC_KEY)


def test_invalid_token_header_invalid_format():
    header = 'bad header'
    result = token_validation.validate_token_header(header, PUBLIC_KEY)
    assert None is result


def test_invalid_token_header_bad_token():
    header = 'Bearer baddata'
    result = token_validation.validate_token_header(header, PUBLIC_KEY)
    assert None is result


def test_invalid_token_no_header():
    header = None
    result = token_validation.validate_token_header(header, PUBLIC_KEY)
    assert None is result


def test_invalid_token_header_not_expiry_time():
    payload = {
        'username': 'tonystark',
    }
    token = token_validation.encode_token(payload, PRIVATE_KEY)
    token = token.decode('utf8')
    header = f'Bearer {token}'
    result = token_validation.validate_token_header(header, PUBLIC_KEY)
    assert None is result


@freeze_time('2018-05-17 13:47:34')
def test_invalid_token_header_expired():
    expiry = delorean.parse('2018-05-17 13:47:33').datetime
    payload = {
        'username': 'tonystark',
        'exp': expiry,
    }
    token = token_validation.encode_token(payload, PRIVATE_KEY)
    token = token.decode('utf8')
    header = f'Bearer {token}'
    result = token_validation.validate_token_header(header, PUBLIC_KEY)
    assert None is result


@freeze_time('2018-05-17 13:47:34')
def test_invalid_token_header_no_username():
    expiry = delorean.parse('2018-05-17 13:47:34').datetime
    payload = {
        'exp': expiry,
    }
    token = token_validation.encode_token(payload, PRIVATE_KEY)
    token = token.decode('utf8')
    header = f'Bearer {token}'
    result = token_validation.validate_token_header(header, PUBLIC_KEY)
    assert None is result


def test_valid_token_header_invalid_key():
    header = token_validation.generate_token_header('tonystark', PRIVATE_KEY)
    result = token_validation.validate_token_header(header, INVALID_PUBLIC_KEY)
    assert None is result


def test_valid_token_header():
    header = token_validation.generate_token_header('tonystark', PRIVATE_KEY)
    result = token_validation.validate_token_header(header, PUBLIC_KEY)
    assert 'tonystark' == result
