#This script retrieves a safeguarding report and emails it to recipients specified in the code. It relies on SES from AWS to send the messages.
#Author Rob Zabel

import os
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from datetime import datetime as  dt
from datetime import timedelta 
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def lambda_handler(event, context):
    #Get Environment Variables##################################################
    # This address must be verified with Amazon SES.
    SENDER = os.environ['EMAIL_SENDER']
    # If in sandbox, this address must be verified too.
    RECIPIENT1 = os.environ['RECIPIENT1']
    RECIPIENT2 = os.environ['RECIPIENT2']
    RECIPIENT3 = os.environ['RECIPIENT3']
    RECIPIENT4 = os.environ['RECIPIENT4']
    RECIPIENT5 = os.environ['RECIPIENT5']
    RECIPIENT6 = os.environ['RECIPIENT6']
    RECIPIENT7 = os.environ['RECIPIENT7']
    # Get the AWS region 
    REGION = os.environ['REGION']
    # Create a variable for the previous days date
    YESTERDAY = dt.now().date() - timedelta(days=1)
    # Create the Subject
    SUBJECT = f"COMPANY Safeguarding Report {YESTERDAY}"

    # Get the file from S3######################################################
    s3 = boto3.client('s3')
    bucket_name = os.getenv('S3_BUCKET')
    filename = f"reports/umbrella_report {YESTERDAY}.html"
    # Lambda lets you use a temp dir to store 500mb for use with the function, add the file to it
    TMP_FILE_NAME = "/tmp/" + f"umbrella_report {YESTERDAY}.html"
    # Download the file from the event (extracted above) to the tmp location
    s3.download_file(bucket_name, filename, TMP_FILE_NAME)
    # Set the attachment to the tmp filename
    ATTACHMENT = TMP_FILE_NAME
    
    
    # Body of the email#########################################################
    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = f"""Hello<br><br>Please find the latest Safeguarding report attached for the date {YESTERDAY}.<br><br>Kind Regards
    <br>Sender name"""
    # The HTML body of the email.
    BODY_HTML = f"""\
    <html>
    <head></head>
    <body>
    <p>{BODY_TEXT}</p>
    </body>
    </html>
    """

    #Encode and create email client#############################################
    # The character encoding for the email.
    CHARSET = "utf-8"
    # Create an SES client and specify a region.
    client = boto3.client('ses',region_name=REGION)
    # Create a multipart/mixed parent container.
    msg = MIMEMultipart('mixed')
    

    # Email Headers#############################################################
    # Add subject, from and to lines.
    msg['Subject'] = SUBJECT 
    msg['From'] = SENDER 
    recipients = [f"{RECIPIENT1}, {RECIPIENT2}, {RECIPIENT3}, {RECIPIENT4}, {RECIPIENT5}, {RECIPIENT6}, {RECIPIENT7}"]
    msg['To'] =", ".join(recipients)

    # Create a multipart/alternative child container.
    msg_body = MIMEMultipart('alternative')


    # Encode the text and HTML content and set the character encoding. This step is
    # necessary if you're sending a message with characters outside the ASCII range.
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)


    # Add the text and HTML parts to the child container.
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)


    # Define the attachment part and encode it using MIMEApplication.
    att = MIMEApplication(open(ATTACHMENT, 'rb').read())


    # Add a header to tell the email client to treat this part as an attachment,
    # and to give the attachment a name.
    att.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT))


    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container.
    msg.attach(msg_body)
    

    # Add the attachment to the parent container.
    msg.attach(att)


    #Send message and catch errors #############################################
    try:
        #Provide the contents of the email.
        response = client.send_raw_email(
            Source=SENDER,
            Destinations=[
                RECIPIENT1,
                RECIPIENT2,
                RECIPIENT3,
                RECIPIENT4,
                RECIPIENT5,
                RECIPIENT6,
                RECIPIENT7
            ],
            RawMessage={
                'Data':msg.as_string(),
            },
        )   


    #Output to cloudwatch logs##################################################
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])