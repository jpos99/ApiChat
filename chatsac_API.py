import json
import requests
import os
from dotenv import load_dotenv
from credentials.credentials import ChatSacAPI


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(BASE_DIR, 'ApiChat', '.env'))
api_credentials = ChatSacAPI()


class ChatSacAPIService:

	def __init__(self, sector, company):
		self.base_url_request = 'https://api.chatsac.com/core/v2/api/'
		self.api_token = api_credentials.get_token(company)

		def get_sector_id():
			url = f'{self.base_url_request}sectors'
			headers = {
				'access-token': self.api_token,
				'Accept': 'application/json'
			}
			response = json.loads(requests.get(url=url, headers=headers).text)
			if isinstance(response, list):
				for item in response:
					if 'name' in item.keys():
						if item['name'] == sector:
							return item['id']
			else:
				print(f"Error occurred when getting sector id: {response['status']}, {response['msg']}")
				return 'unknown'

		self.sector_id = get_sector_id()

	def get_contact_by_number(self, number):
		if number[0:2] == '55':
			url = f'{self.base_url_request}contacts/number/{number}'
		else:
			url = f'{self.base_url_request}contacts/number/55{number}'
		headers = {
			'access-token': self.api_token,
			'Content-Type': 'application/json'
		}
		response = requests.get(url=url, headers=headers).text
		response = json.loads(response)
		return response

	def create_new_contact(self, contact, number):
		url = f'{self.base_url_request}contacts/'
		if number[0:2] != '55':
			number = f'55{number}'.strip()
		contact_data = {
			'nickName': f'{contact["curso"]} {contact["external_id"]} {contact["nome"]}'.strip(),
			'number': f'{number}',
			'email': contact['email'].strip(),
			'observation': 'Contato inserido pelo fluxo de disparo.'
		}
		contact_str = json.dumps(contact_data, ensure_ascii=False).encode('utf-8')
		headers = {
			'access-token': self.api_token,
			'Accept': 'application/json',
			'Content-Type': 'application/json; charset=utf-8'
		}
		response = requests.post(url=url, data=contact_str, headers=headers).text
		response = json.loads(response)
		return response

	def get_contact_details_by_id(self, contact_id):
		url = f'{self.base_url_request}contacts/{contact_id}'
		headers = {
			'access-token': self.api_token,
			'Content-Type': 'application/json'
		}
		response = requests.get(url=url, headers=headers).text
		response = json.loads(response)
		return response

	def number_exists_wa(self, number):
		url = f'{self.base_url_request}wa-number-check/{number}'
		headers = {
			'access-token': self.api_token,
			'Accept': 'application/json'
		}
		response = requests.post(url=url, headers=headers, ).text
		response = json.loads(response)
		return response

	def get_channel_status(self):
		url = f'{self.base_url_request}channel/status'
		headers = {
			'access-token': self.api_token,
			'Accept': 'application/json'
		}
		response = requests.get(url=url, headers=headers).text
		response = json.loads(response)
		return response

	def get_message_by_id(self, id_message):
		url = f'{self.base_url_request}chats/{id_message}'
		headers = {
			'access-token': self.api_token,
			'Accept': 'application/json'
		}
		response = requests.get(url=url, headers=headers).text
		response = json.loads(response)
		return response

	def get_chat_information_by_id(self, id_chat):
		url = f'{self.base_url_request}chats/{id_chat}'
		headers = {
			'access-token': self.api_token,
			'Accept': 'application/json'
		}
		response = requests.get(url=url, headers=headers).text
		response = json.loads(response)
		return response

	def create_chat(self, number, contact_id):
		url = f'{self.base_url_request}chats/create-new'
		body = (
			str(
					{
						'number': number,
						'contactId': contact_id,
						'sectorId': self.sector_id
					}
			)
		).replace('\n', '').replace("'", '"')
		headers = {
			'access-token': self.api_token,
			'Accept': 'application/json',
			'Content-Type': "application/json"
		}
		response = requests.post(url=url, data=body, headers=headers).text
		response = json.loads(response)
		return response

	def set_params(self):
		pass

	def send_text_message(self, number, contact_id, message):
		url = f'{self.base_url_request}chats/send-text'
		body = {
			"number": number,
			"contactId": contact_id,
			"message": message,
			"isWhisper": False,
			"forceSend": True,
			"verifyContact": False
		}
		headers = {
			'access-token': self.api_token,
			'Accept': 'application/json',
			'Content-Type': 'application/json; charset=utf-8'
		}
		response = requests.post(url=url, json=body, headers=headers).text
		response = json.loads(response)
		print('ENVIO DE MSG =', response)
		return response

	def schedule_text_message(self, body):
		url = f'{self.base_url_request}chats/messages/scheduler'
		headers = {
			'access-token': self.api_token,
			'Accept': 'application/json',
			'Content-Type': 'application/json; charset=utf-8'
		}
		response = requests.post(url=url, json=body, headers=headers).text
		response = json.loads(response)
		print('ENVIO DE MSG =', response)
		return response
