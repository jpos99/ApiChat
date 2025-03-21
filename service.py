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
			try:
				contact_wa = chatsac_api.get_contact_by_number(phone_number)
				if contact_wa.get('status', None) is not None:
					if chatsac_api.number_exists_wa(phone_number)['status'] == 'VALID_WA_NUMBER':
						contact = chatsac_api.create_new_contact(contact_data, phone_number)
						if contact.get('status', None) in ['200', '201', '202', '203', '204', '205']:
							contact_wa = chatsac_api.get_contact_by_number(phone_number)
						else:
							print(f'Contato {phone_number} não pode ser inserido na plataforma ChatSac.')
							data_base.update_formando(
								contact_data['formando_id'],
								f'Erro ao inserir contato na plataforma: {contact.get("status")}',
								phone_number
							)
							continue
					else:
						data_base.update_formando(
							contact_data['formando_id'],
							'Número não é um WhatsApp válido',
							phone_number
						)
						continue

				if not contact_wa or not contact_wa.get('id'):
					error_msg = f"Dados do contato inválidos para o número {phone_number}"
					print(error_msg)
					data_base.update_formando(contact_data['formando_id'], error_msg, phone_number)
					continue

				try:
					contact_details = chatsac_api.get_contact_details_by_id(contact_wa.get('id'))
					if not contact_details:
						error_msg = f"Não foi possível obter detalhes do contato {phone_number}"
						print(error_msg)
						data_base.update_formando(contact_data['formando_id'], error_msg, phone_number)
						continue
				except Exception as e:
					error_msg = f"Erro ao obter detalhes do contato {phone_number}: {str(e)}"
					print(error_msg)
					data_base.update_formando(contact_data['formando_id'], error_msg, phone_number)
					continue

				time.sleep(0.5)
				if contact_details.get('curChatId', None) is None:
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
					personalized_message,
					phone_number
				)
			except Exception as e:
				error_msg = f"Erro inesperado ao processar contato {phone_number}: {str(e)}"
				print(error_msg)
				data_base.update_formando(contact_data['formando_id'], error_msg, phone_number)
				continue
		else:
			continue


def send_messages_to_contact(contact, messages, sector, company):
	print('CHAMOU SERVIÇE')
	chatsac_api = ChatSacAPIService(sector, company)
	data_base = DBOperation()
	phone_number = remove_non_numeric_chars(contact['number'])
	
	if phone_number != '':
		try:
			contact_details = chatsac_api.get_contact_by_number(phone_number)
			if not contact_details or 'curChatId' not in contact_details:
				print(f"Erro: Detalhes do contato inválidos para {phone_number}")
				return
				
			wa_chat = chatsac_api.get_chat_information_by_id(contact_details['curChatId'])
			if not wa_chat or 'contact' not in wa_chat:
				print(f"Erro: Chat inválido para {phone_number}")
				return

			for message in messages:
				response = chatsac_api.send_text_message(
					phone_number, 
					wa_chat['contact'], 
					message
				)
				
				print(f"Resposta do envio: {response}")
				
				if response.get('status') == '200':
					conversa_id = data_base.update_chat_db(
						wa_chat,
						contact_details['curChatId'],
						contact['formando_id'],
						phone_number
					)
					
					if conversa_id:
						data_base.update_message_db(wa_chat, conversa_id)
						data_base.update_formando(
							contact['formando_id'],
							message,
							phone_number
						)
					else:
						print(f"Erro: Não foi possível obter ID da conversa para {phone_number}")
				else:
					print('Resposta da api com erro:', response.get('status'), response.get('error'))
				
		except Exception as e:
			print(f"Erro ao processar mensagem para {phone_number}: {str(e)}")
	else:
		print('Numero não encontrado no contato', contact)