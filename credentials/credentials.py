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
		self.api_token_imaginarte = os.getenv('CHATSAC_TOKEN_IMAGINARTE')
		self.api_token_milenium = os.getenv('CHATSAC_TOKEN_MILENIUM')
		self.api_token_tecsol = os.getenv('CHATSAC_TOKEN_TECSOL')
		self.api_token_goetz = os.getenv('CHATSAC_TOKEN_GOETZ')

	def get_token(self, company):
		tokens = {
			'MLN': self.api_token_milenium,
			'IMA': self.api_token_milenium,
			'TSL': self.api_token_milenium,
			'GTZ': self.api_token_milenium,
		}
		return tokens.get(company, '')