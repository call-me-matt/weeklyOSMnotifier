import pprint
import smtplib
import traceback
from email.mime.text import MIMEText


def post(self):
    # dunno why the loop at this call and the list-handling inside - just leaving it as a param for paranoids
    for recipient in self.mail_to:

        TO = recipient if type(recipient) is list else [recipient]
        if not TO:
            return

        # Prepare actual message
        msg = MIMEText(self.mail_body, "plain", "UTF-8")
        msg["From"] = self.mail_from
        msg["To"] = ", ".join(TO)
        msg["Subject"] = self.mail_subject
        # pprint.pprint((self.mail_USER, self.mail_PW,self.mail_from, TO, msg.as_string()))

        try:
            server = smtplib.SMTP(self.mail_smtp_host, self.mail_smtp_port)
            server.ehlo()
            server.starttls()
            server.login(self.mail_USER, self.mail_PW)
            server.sendmail(self.mail_from, TO, msg.as_string())
            server.close()
            self.logger.info("successfully sent the mail to " + ", ".join(TO))
        except:
            self.logger.error("failed to send mail")
            traceback.print_exc()
            pprint.pprint((self.mail_USER, self.mail_PW, self.mail_from))

    return
