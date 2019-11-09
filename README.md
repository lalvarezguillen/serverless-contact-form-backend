# Serverless Backend for Contact Us forms [![Build Status](https://travis-ci.org/lalvarezguillen/serverless-contact-form-backend.svg?branch=master)](https://travis-ci.org/lalvarezguillen/serverless-contact-form-backend)

This project intends to build and deploy a serveless backend to power Contact Us forms.

The goal is to receive form submissions, and email the content to a pre-configured email.

It's a work in progress.


## Local development

1. Clone this project
2. Install Python and NodeJS
3. Install NodeJS dependencies: `npm i`
4. Install Python dependencies: `pip install -r requirements.dev.txt`
5. Run tests with `pytest tests.py`

## Deployment


### Credentials & Variables
Serverless manages the deployment of this project and the infrastructure it requires. To do so, a few credentials/variables are required. Refer to [Serverless documentation](https://serverless.com/blog/serverless-secrets-api-keys/) to learn how to set those up:

* AWS Access key
* AWS Access secret
* AWS Region

Additionally, the following variables are required to run the project:

* `sending_address`: The email address where we want to be sending the emails from
* `receiving_addresses`: A list of email addresses that we want to receive the emails (IE: 'email1@domain.com,email2@domain.com')
* `identity_arn`: The domain of `sending_address` needs to be verified with AWS SES, producing an Identiy ARN. You need to provide that ARN here.

With all that set, simply run: `serverless deploy`


### AWS SES

AWS SES handles the emailing in this project, and it requires a domain to be verified before being able to use it for emailing. Refer to [AWS SES Documentation](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/verify-email-addresses.html)

Verifying your domain produces an Identity ARN that you need to provide before running this project.
