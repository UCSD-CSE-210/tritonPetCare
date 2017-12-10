import smtplib

class EmailHandler(object):
	@staticmethod
	def send_authentication(email, userId, code):
		recipient = email + "@ucsd.edu"
		url = "http://127.0.0.1:5000/authenticate?userId=" + userId + "&code=" + code
		message = "To activate your account for TritonPetCare, click here: " + url
		EmailHandler.send_email(recipient, message)

	@staticmethod
	def send_interest(postOwnerId, postOwnerEmail, userId, userEmail):
		recipient = postOwnerEmail + "@ucsd.edu"
		url = "http://127.0.0.1:5000/profile?userId=" + userId + "&login=" + postOwnerId
		message = ("Someone just got interested in your post.\n"
				"You can look into his/her profile at: " + url + " \n"
				"And to contact the potential CareGiver, his/her email is: " + userEmail + "@ucsd.edu"
		)
		EmailHandler.send_email(recipient, message)

	@staticmethod
	def send_email(recipient, body):
		gmail_user = "tritonpetcare@gmail.com"
		gmail_pwd = "cse210project"
		FROM = "tritonpetcare@gmail.com"
		TO = recipient if type(recipient) is list else [recipient]
		SUBJECT = "Notification from TritonPetCare"
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