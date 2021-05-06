import logging
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import boto3
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


def send_notifications(email, sender):
    """This function sends email of a log file """
    logger.info('Inside the send_log_email function')
    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    SENDER = sender

    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    RECIPIENT = email

    # The subject line for the email.
    SUBJECT = "New Message From OpenLXP Portal"

    # The full path to the file that will be attached to the email.
    ATTACHMENT = '/opt/app/openlxp-xia-edx/core/management/logs/debug.log'

    # The email body for recipients with non-HTML email clients.
    # BODY_TEXT = "Hello,\r\nPlease check the attached file for Openlxp " \
    #             "Notifications. "

    # The HTML body of the email.
    BODY_HTML = """\
       <html>
       <head></head>
       <body>
       <h1>Hello!</h1>
       <p>Please check the attached file for OpenLXP Notifications</p>
       </body>
       </html>
       """

    # The character encoding for the email.
    CHARSET = "utf-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses')

    # Create a multipart/mixed parent container.
    msg = MIMEMultipart('mixed')
    # Add subject, from and to lines.
    msg['Subject'] = SUBJECT
    msg['From'] = SENDER
    msg['To'] = ', '.join(RECIPIENT)

    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart('alternative')

    # Encode the text and HTML content and set the character encoding.
    # This step is necessary if you're sending a message with characters
    # outside the ASCII range.
    # textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)

    # Add the text and HTML parts to the child container.
    # msg_body.attach(textpart)
    msg_body.attach(htmlpart)

    # Define the attachment part and encode it using MIMEApplication.
    att = MIMEApplication(open(ATTACHMENT, 'rb').read())

    # Add a header to tell the email client to treat this part as an
    # attachment, and to give the attachment a name.
    att.add_header('Content-Disposition', 'attachment',
                   filename="Please check attachment here")

    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container.
    msg.attach(msg_body)

    # Add the attachment to the parent container.
    msg.attach(att)
    # print(msg)
    try:
        # Provide the contents of the email.
        response = client.send_raw_email(
            Source=SENDER,
            Destinations=RECIPIENT
            ,
            RawMessage={
                'Data': msg.as_string(),
            }
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])


def delete_verified_email(email_to_delete):
    """Function to delete email verification"""

    # Create SES client
    ses = boto3.client('ses')

    response = ses.delete_identity(
        Identity=email_to_delete
    )
    logger.info('email got deleted')
    logger.info(response)
