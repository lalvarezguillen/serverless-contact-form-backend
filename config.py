from envparse import env


CHARSET = env.str('CHARSET', default='UTF-8')
AWS_REGION = env.str('AWS_REGION', default='us-east-1')
SENDING_ADDRESS = env.str('SENDING_ADDRESS', default='dummy@address.com')
RECEIVING_ADDRESSES = env.list('RECEIVING_ADDRESSES', default=[])