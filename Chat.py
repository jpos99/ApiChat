from fastapi import FastAPI, BackgroundTasks
from service import *
import uvicorn

chatapp = FastAPI()


@chatapp.post('/dispatch')
async def schedule_text_message(contacts: dict, background_tasks: BackgroundTasks) -> dict:
	background_tasks.add_task(schedule_to_send_messages, contacts['contacts'], contacts['message'], contacts['date'])
	return {"status": "Recebido"}


if __name__ == '__main__':
	uvicorn.run(chatapp, port=7000, reload=True)
