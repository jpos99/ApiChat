import time
from datetime import datetime, timedelta, date
from random import randint
from chatsac_API import ChatSacAPIService
from DBOperations import DBOperation


def remove_non_numeric_chars(string):
	return ''.join(char for char in string if char.isdigit())


def remove_nine_digit(number):
	if len(number) == 11:
		number = number[:2] + number[3:]
	return number


def is_ready_to_recieve_msg(chat):
	days_to_not_send_message = 2
	date_days_before = date.today() - timedelta(days=days_to_not_send_message)
	if 'messages' in chat.keys():
		for message in chat['messages']:
			if message['isPrivate'] == False and message['isSystemMessage'] == False:
				date_last_message = datetime.strptime(
					message['dhMessage'].split('T')[0],
					'%Y-%m-%d'
				).date()
				if date_last_message >= date_days_before:
					return False
	return True


def personalize_message(base_message: str, contact_name: str) -> str:
	return base_message.replace('#NOME', contact_name.split(' ')[0])


def schedule_to_send_messages(contact_data, message, datetime_to_start, sector, company):
	chatsac_api = ChatSacAPIService(sector, company)
	scheduled_datetime = datetime.strptime(f'{datetime_to_start[0]}T{datetime_to_start[1]}', '%Y-%m-%dT%H:%M')
	data_base = DBOperation()
	not_send_contact = []
	for phone_number, contact_data in contact_data.items():
		if len(phone_number) > 9 and contact_data['formando_id'] not in not_send_contact:
			contact_wa = chatsac_api.get_contact_by_number(phone_number)
			if 'status' in contact_wa.keys():
				if chatsac_api.number_exists_wa(phone_number)['status'] == 'VALID_WA_NUMBER':
					contact = chatsac_api.create_new_contact(contact_data, phone_number)
					if 'status' in contact.keys() and contact['status'] in ['200', '201', '202', '203', '204', '205']:
						contact_wa = chatsac_api.get_contact_by_number(phone_number)
					else:
						print(f'Contato {phone_number} não pode ser inserido na plataforma ChatSac.')
						continue
				else:
					continue
			contact_details = chatsac_api.get_contact_details_by_id(contact_wa['id'])
			time.sleep(1)
			if 'curChatId' not in contact_details.keys():
				wa_chat = chatsac_api.create_chat(phone_number, contact_wa['id'])
			else:
				wa_chat = chatsac_api.get_chat_information_by_id(contact_details['curChatId'])

			contact_ready_to_receive_msg = is_ready_to_recieve_msg(wa_chat)
			if not contact_ready_to_receive_msg:
				menssagem = 'Menssagem não enviada pois está em contato'
				not_send_contact.append(contact_data['formando_id'])
				conversa_id = data_base.update_chat_db(wa_chat, contact_details['curChatId'], contact_data['formando_id'], phone_number)
				data_base.update_message_db(wa_chat, conversa_id)
				data_base.update_formando(contact_data['formando_id'], menssagem, phone_number)
				continue
			personalized_message = personalize_message(message, contact_data['nome'])
			utc_to_send_message = datetime.strftime(scheduled_datetime + timedelta(hours=3), '%Y-%m-%dT%H:%M:%SZ')
			agendamento_envio_msg = {
				"description": "Menssagem inicial",
				"dhScheduled": utc_to_send_message,
				"messageType": 0,
				"content": personalized_message,
				"recipient": phone_number,
			}
			print(agendamento_envio_msg)
			chatsac_api.schedule_text_message(agendamento_envio_msg)
			scheduled_datetime = scheduled_datetime + timedelta(seconds=randint(1, 10))
			contact_details = chatsac_api.get_contact_details_by_id(contact_wa['id'])
			time.sleep(0.5)
			print(contact_details)
			conversa_id = data_base.update_chat_db(
				wa_chat,
				contact_details['curChatId'],
				contact_data['formando_id'],
				phone_number
			)
			data_base.update_message_db(wa_chat, conversa_id)
			data_base.update_formando(
				contact_data['formando_id'],
				agendamento_envio_msg['content'],
				agendamento_envio_msg['recipient']
			)
		else:
			continue
