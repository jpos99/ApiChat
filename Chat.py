from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from starlette.responses import JSONResponse

import service
from chatsac_API import ChatSacAPIService
import uvicorn

chatapp = FastAPI()
chatsac = ChatSacAPIService()


@chatapp.get('/')
async def home():
	channel_status = chatsac.get_channel_status()
	return channel_status["status"]


@chatapp.post('/dispatch')
async def schedule_text_message(contacts: dict, background_tasks: BackgroundTasks) -> dict:
	background_tasks.add_task(service.schedule_to_send_messages, contacts['contacts'], contacts['message'], contacts['date'])
	return {"status": "Recebido"}


if __name__ == '__main__':
	uvicorn.run(chatapp, port=7000)
