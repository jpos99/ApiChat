import os

class PostgresCredentials:
	def __init__(self):
		self.user = os.getenv('DB_USER')
		self.password = os.getenv('DB_PASSWORD')
		self.host = os.getenv('DB_HOST')
		self.port = os.getenv('DB_PORT')
		self.database = os.getenv('DB_NAME')

class DjangoSecrets:
	def __init__(self):
		self.secret_key = os.getenv('DJANGO_SECRETKEY')
		self.debug = os.getenv('DJANGO_DEBUG')
		self.end_point = os.getenv('DJANGO_ENDPOINT')

class ChatSacAPI:
	def __init__(self):
		self.api_token = os.getenv('CHATSAC_TOKEN')