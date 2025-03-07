from fastapi import FastAPI, BackgroundTasks
from service import *
from chatsac_API import ChatSacAPIService
import uvicorn
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(BASE_DIR, 'ApiChat', '.env'))


chatapp = FastAPI()


@chatapp.post('/dispatch')
async def schedule_text_message(contacts: dict, background_tasks: BackgroundTasks) -> dict:
	chat_sac = ChatSacAPIService(contacts['sector'], contacts['company'])
	channel_status = chat_sac.get_channel_status()
	print(channel_status)
	background_tasks.add_task(
		schedule_to_send_messages,
		contacts['contacts'],
		contacts['message'],
		contacts['date'],
		contacts['sector'],
		contacts['company']
	)
	return {"channel_status": channel_status}


if __name__ == '__main__':
	uvicorn.run(chatapp, port=7000, reload=True)
