import smtplib

class EmailHandler(object):
	@staticmethod
	def send_authentication(email, userId, code):
		recipient = email + "@ucsd.edu"
		url = "http://127.0.0.1:5000/authenticate?userId=" + userId + "&code=" + code
		EmailHandler.send_email(recipient, "Authentication for TritonPetCare", url)

	@staticmethod
	def send_email(recipient, subject, body):
		gmail_user = "tritonpetcare@gmail.com"
		gmail_pwd = "cse210project"
		FROM = "tritonpetcare@gmail.com"
		TO = recipient if type(recipient) is list else [recipient]
		SUBJECT = subject
		TEXT = body

		# Prepare actual message
		message = """From: %s\nTo: %s\nSubject: %s\n\n%s
		""" % (FROM, ", ".join(TO), SUBJECT, TEXT)
		try:
			server = smtplib.SMTP("smtp.gmail.com", 587)
			server.ehlo()
			server.starttls()
			server.login(gmail_user, gmail_pwd)
			server.sendmail(FROM, TO, message)
			server.close()
		except:
			pass