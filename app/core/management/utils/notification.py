import boto3
import logging

from botocore.exceptions import ClientError

logger = logging.getLogger('dict_config_logger')


def list_email_verified():
    """function to return list of verified emails """
    # Create SES client
    ses = boto3.client('ses')

    response = ses.list_identities(
        IdentityType='EmailAddress',
        MaxItems=10
    )
    logger.info(response['Identities'])
    return response['Identities']


def check_if_email_verified(email):
    """Function to check if email id from user is verified """

    list_emails = list_email_verified()
    if email in list_emails:
        logger.info("Email is already Verified")
        return False
    return True


def email_verification(email):
    """Function to send email verification"""

    check = check_if_email_verified(email)

    if check:
        # Create SES client
        logger.info("Email is sent for Verification")
        ses = boto3.client('ses')

        response = ses.verify_email_identity(
            EmailAddress=email
        )

        print(response)


def send_notifications(email):
    """This function sends email of a log file """
    logger.info('Inside the send_log_email function')


    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = "example.com"

    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENT = email

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    # CONFIGURATION_SET = "ConfigSet"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    # AWS_REGION = "us-west-2"

    # The subject line for the email.
    SUBJECT = "Amazon SES Test (SDK for Python)"

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("Amazon SES Test (Python)\r\n"
                 "This email was sent with Amazon SES using the "
                 "AWS SDK for Python (Boto)."
                 )

    # The HTML body of the email.
    BODY_HTML = """<html>
        <head></head>
        <body>
          <h1>Amazon SES Test (SDK for Python)</h1>
          <p>This email was sent with
            <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
            <a href='https://aws.amazon.com/sdk-for-python/'>
              AWS SDK for Python (Boto)</a>.</p>
        </body>
        </html>
                    """

    # The character encoding for the email.
    CHARSET = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses')

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            # ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
