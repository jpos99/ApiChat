import requests
from credentials import credentials
import json


class DBOperation:
	db_credentials = credentials.DjangoSecrets()
	DJANGO_ENDPOINT = db_credentials.end_point

	def update_chat_db(self, wa_chat, chat_id, formando_id, phone_number):
		data = {
			"formando": formando_id,
			"telefone_formando": phone_number,
			"external_chat_id": chat_id,
			"status": wa_chat.get('status', 0),
			"type": wa_chat.get('type', 0),
			"description": wa_chat.get('description', 'Mensagem inicial'),
			"secondary_description": wa_chat.get('secondaryDescription', 'Mensagem inicial'),
			"count_unread_messages": wa_chat.get('countUnreadMessages'),
			"last_seen": wa_chat.get('lastSeen', '2020-01-01T00:00:00.000'),
			"contact_id": wa_chat.get('contact', {}).get('id', ''),
			"contact_name": wa_chat.get('contact', {}).get('name', ''),
			"contact_secondaryName": wa_chat.get('contact', {}).get('secondaryName', 'Não Especificado'),
			"contact_number": wa_chat.get('contact', {}).get('number', ''),
			"contact_is_me": wa_chat.get('contact', {}).get('isMe', 'False'),
			"contact_tags": wa_chat.get('contact', {}).get('tags', ''),
			"last_message_id": wa_chat.get('lastMessage', {}).get('id', ''),
			"last_message_text": wa_chat.get('lastMessage', {}).get('text', ''),
			"last_message_utc_dh_message": wa_chat.get('lastMessage', {}).get('utcDhMessage', ''),
			"last_message_utc_dh_message_unix_time": wa_chat.get('lastMessage', {}).get('utcDhMessageUnixTime', ''),
			"last_message_is_private": wa_chat.get('lastMessage', {}).get('isPrivate', 'False'),
		}

		response = requests.get(f"{self.DJANGO_ENDPOINT}conversa/{chat_id}/")
		if response.status_code == 404:
			print('Conversa json data=', data)
			response = requests.post(f"{self.DJANGO_ENDPOINT}conversa/create/", json=data)
		else:
			response = requests.put(f"{self.DJANGO_ENDPOINT}conversa/update/{chat_id}/", json=data)

		if response.status_code not in [200, 201]:
			print(f"Error occurred when saving conversa: {response.status_code}, {response.text}")
			return None
		return response.json()['id']

	def update_message_db(self, wa_chat, conversa_id):
		message_ids = []
		for message in wa_chat.get('messages', []):
			data = {
				"conversa": conversa_id,
				"external_message_id": message.get('IdMessage'),
				"data_hora_envio": message.get('dhMessage', ''),
				"sender_name": message.get('senderName', ''),
				"text": message.get('text', ''),
				"is_sent_by_me": message.get('isSentByMe', ''),
				"is_deleted": message.get('isDeleted', ''),
				"is_forwarded": message.get('isForwarded', ''),
				"is_reply": message.get('isReply', ''),
				"is_mms": message.get('isMMS', ''),
				"is_private": message.get('isPrivate', ''),
				"is_system_message": message.get('isSystemMessage', ''),
				"origen": message.get('origen', ''),
				"status_message": message.get('statusMessage', ''),
			}

			response = requests.get(f"{self.DJANGO_ENDPOINT}menssagem/{message.get('IdMessage')}/")
			if response.status_code == 404:
				response = requests.post(f"{self.DJANGO_ENDPOINT}menssagem/create/", json=data)
			else:
				response = requests.put(f"{self.DJANGO_ENDPOINT}menssagem/update/{message.get('IdMessage')}/", json=data)

			if response.status_code not in [200, 201]:
				print(f"Error occurred when saving message: {response.text}")
				continue
			
			message_ids.append(response.json()['id'])
		
		return message_ids

	def update_formando(self, formando_id, personalized_message, phone_number):
		data = {
			"formando_historico": formando_id,
			"usuario_historico": 2,
			"descricao_historico": f'Mensagem {personalized_message} enviada ao formando {formando_id} no contato numero: {phone_number}'
		}
		response = requests.post(f"{self.DJANGO_ENDPOINT}historico/create/", json=data)
		if response.status_code != 201:
			print(f"Error occurred when saving historico: {response.text}")