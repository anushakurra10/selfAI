from mailersend import MailerSendClient, EmailBuilder
from src import config


def send_email(message: str):
    try:
        # Initialize client (using API key from your config)
        mailer = MailerSendClient(api_key=config.EMAIL_API_KEY)

        # Build the email
        email = (
            EmailBuilder()
            .from_email(config.FROM_EMAIL_ID, config.FROM_EMAIL_NAME)
            .to_many([
                {
                    "email": config.TO_EMAIL_ID,
                    "name": config.TO_EMAIL_NAME,
                }
            ])
            .subject("Hello from selfAI!")
            .html(f"<p>details: {message}</p>")
            .build()
        )

        # Send email
        response = mailer.emails.send(email)
        print("Status:", response.status_code, "Request ID:", response.request_id)

    except Exception as err:
        print("Error sending email:", err)
        pass
