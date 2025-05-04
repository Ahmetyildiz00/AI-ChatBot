from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import contextlib
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Google API Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Model yapılandırması
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
)

chat_session = model.start_chat(history=[])

corporate_text = """
Senin adın Yıldız. Sana adın sorulduğunda Yıldız olarak cevap ver. Size nasıl yardımcı olabilirim? de
"""

app = FastAPI()

# CORS ayarları (React ile bağlantı için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev sunucusu portu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# İstek veri modeli
class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    combined_input = corporate_text + "\nSoru: " + request.message
    response = chat_session.send_message(combined_input)
    return {"reply": response.text}
