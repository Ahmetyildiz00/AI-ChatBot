from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import pandas as pd

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.agents import AgentExecutor

load_dotenv()

df = pd.read_excel("product_list.xlsx", dtype=str)
df.dropna(how="all", inplace=True)
df.columns = df.columns.str.strip().str.lower()

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3,
    top_p=0.95,
    top_k=40,
    max_output_tokens=1024
)

agent = create_pandas_dataframe_agent(
    llm,
    df,
    verbose=False,
    allow_dangerous_code=True,
    handle_parsing_errors=True,
    number_of_head_rows=len(df),
)

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent.agent,
    tools=agent.tools,
    verbose=True,
    handle_parsing_errors=True,
    return_intermediate_steps=False
)
def get_available_categories(df: pd.DataFrame) -> str:
    categories = df["kategori"].unique()
    return f"Şu an için stoklarımızda {', '.join(categories)} bulunmaktadır. 😊"

corporate_prompt = """
Sen Lunera markasının dijital asistanısın. Görevin, müşterilerden gelen sorulara dostane, kibar ve yardımsever bir şekilde yanıt vermektir. Emoji kullanabilirsin. Aşağıdaki kurallara uymalısın:
Her zaman Türkçe yanıt ver. Sadece konuşma ortasında "Merhaba" deme.
Veri çerçevesi zaten Python ortamında tanımlı olduğu için yeniden oluşturma veya kopyalama yapma. Sadece df kullan.

• Şirket bilgisi istenirse: Lunera 2020 yılında kurulmuş, erkek giyim üzerine çalışan modern bir giyim markasıdır.
• Kurucusu: Ahmet Yıldız’dır. Bu bilgiyi sadece müşteri "kurucunuz kim?" diye sorarsa ver.
• Çalışma saatleri müşteri sorarsa:
  - Hafta içi 08:00 - 18:00
  - Cumartesi 09:00 - 17:00
  - Pazar ve resmi tatillerde kapalı
• Kargo firmaları sorulursa: MNG Kargo, Yurt İçi Kargo ve Aras Kargo.
• Kargo ücreti sorulursa: 500 TL ve üzeri alışverişlerde ücretsiz. Altında 75 TL'dir.
• İade süreci: Ürün iade süresi 14 gün içinde başlatılmalıdır. İade süreci başlatıldıktan sonra 3 iş günü içinde kargo firması ürünü alır. Ürün bize ulaştıktan sonra 5 iş günü içinde iade işlemi tamamlanır.
• İade süreci başlatma: İade süreci başlatmak için müşteri hizmetleri ile iletişime geçilmelidir.
• Ürün değişimi: Ürün değişimi yapılmamaktadır. İade süreci başlatılmalı ve yeni ürün siparişi verilmelidir.

Aşağıdaki konularda hiçbir şekilde yardımcı olma:
- Günlük hayat (hava durumu, matematik soruları, genel sohbet)
- Giyim dışındaki ürünler veya farklı alanlar
Böyle bir durumda nazikçe şu şekilde cevap ver:
"Üzgünüm, bu konuda yardımcı olamıyorum. Ürünlerimizle ilgili başka bir sorunuz varsa memnuniyetle yardımcı olurum"
"""

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

def get_available_categories(df: pd.DataFrame) -> str:
    categories = df["kategori"].unique()
    return f"Şu an için stoklarımızda {', '.join(categories)} bulunmaktadır. 😊"

last_product_context = {}  # Ürün bilgisini saklamak için global sözlük

@app.post("/chat")
async def chat(request: ChatRequest):
    user_message = request.message.strip().lower()

    # Kullanıcı önce ürün sorduysa (kategori-renk-beden içeren)
    kategori_keywords = ["tişört", "gömlek", "pantolon"]
    kategori = next((k for k in kategori_keywords if k in user_message), None)
    renkler = df["renk"].str.lower().unique().tolist()
    renk = next((r for r in renkler if r in user_message), None)
    bedenler = df["beden"].astype(str).str.lower().unique().tolist()
    beden = next((b for b in bedenler if b in user_message), None)

    if kategori and renk and beden:
        last_product_context["kategori"] = kategori
        last_product_context["renk"] = renk
        last_product_context["beden"] = beden

    if "fiyat" in user_message and not any(k in user_message for k in kategori_keywords):
        ctx = last_product_context
        if all(k in ctx for k in ("kategori", "renk", "beden")):
            row = df[
                (df["kategori"] == ctx["kategori"]) &
                (df["renk"] == ctx["renk"]) &
                (df["beden"].astype(str).str.lower() == ctx["beden"])
            ]
            if not row.empty:
                fiyat = row.iloc[0]["fiyat"]
                return {"reply": f"{ctx['renk'].capitalize()} renk {ctx['beden']} beden {ctx['kategori']} fiyatı: {fiyat}"}

    if "hangi ürünler" in user_message or "neler var" in user_message or "kategori" in user_message:
        return {"reply": get_available_categories(df)}

    full_prompt = f"""{corporate_prompt}
Kullanıcı sorusu: {request.message}
"""
    try:
        result = agent_executor.invoke({"input": full_prompt})
        return {"reply": result["output"] if isinstance(result, dict) and "output" in result else str(result)}
    except Exception as e:
        return {"reply": f"Üzgünüm, bir hata oluştu. Lütfen tekrar dener misiniz?\n\n[Hata: {str(e)}]"}
