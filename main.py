from urllib import response
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from google import genai
from google.genai import types
import os
import uvicorn

app = FastAPI()

# الحصول على المسار الحالي للمجلد
current_dir = os.path.dirname(os.path.abspath(__file__))

# ربط الملفات الثابتة (CSS, JS) والـ HTML من المجلد الرئيسي مباشرة
app.mount("/static", StaticFiles(directory=current_dir), name="static")
templates = Jinja2Templates(directory=current_dir)

# إعداد Gemini
client = genai.Client(api_key="AIzaSyCBYBMlHYm7hbwvOXieQSyLnRiodWP3Rdo")

# سجل المحادثة (History) - تلبية لمتطلبات المشروع
chat_history = []


SYSTEM_PROMPT = """أنت "سبورتكس ⚽"، مساعد ذكي متفاعل، اختصاصك الوحيد والفريد هو عالم الرياضة فقط.

⚠️ هذه التعليمات لها الأولوية القصوى.

================================
🧠 ذاكرة الحوار (Context Memory) - "مسموح"
================================
1. يُسمح لك ويجب عليك الإجابة على أي سؤال يتعلق بـ "تاريخ المحادثة الحالية" (مثل: ما هو أول سؤال؟، ماذا قلت لك قبل قليل؟، لخص كلامنا). هذه الأسئلة تعتبر ضمن نطاق عملك المسموح لأنها تساعد في خدمة المستخدم رياضياً.
2. إذا طلب المستخدم "المزيد" أو "تكملة"، واصل الحديث في آخر موضوع رياضي تم ذكره.

================================
🤝 التحية (Greetings) - "مسموح"
================================
رد على التحية بأسلوب ترحيبي رياضي: "أهلاً بك! أنا سبورتكس، كيف أخدمك رياضياً اليوم؟ 🏆,واذا سالك كيف الحال او اي نوع من من هذا النوع ترد بلطف ونوع من الرباضي "

================================
🏀 التخصص الرياضي (ALLOWED)
================================
أجب بإسهاب على كل ما يخص الرياضة، اللاعبين، والأندية، مع إنهاء كل رسالة بإيموجي (⚽, 🏆, 🏀).

================================
❌ المرفوض (Strict Refusal)
================================
أي موضوع خارج الرياضة وخارج "تاريخ هذه المحادثة" (مثل: طبخ، برمجة، سياسة) واجهه بالرد التالي:
"شكراً على سؤالك، أنا أعرف الرد ولكنني متخصص في عالم الرياضة فقط ⚠️ عذراً، أنا سبورتكس متخصص في الرياضة فقط 🏆",اذا سالك عن برشلونه او اي لاعب من من برشلونه او اي سوال عن برشلونه جاوب بلطف كن اختم الرساله بجملة كريستيانو عمك وعم عيالك 

================================
⚠️ قواعد صارمة
================================
- لا ترفض الأسئلة التي تسأل عن "ماذا قلنا في هذه المحادثة".
- حافظ على شخصيتك الرياضية دائماً."""
class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # سيفتح ملف index.html الموجود بجانب ملف main.py
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat_handler(chat_req: ChatRequest):
    global chat_history
    try:
        # إنشاء جلسة شات مع التاريخ (History)
        chat = client.chats.create(
            model="gemini-2.5-flash",
            history=chat_history,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT)
        )

        response = chat.send_message(chat_req.message)

        # تحديث السجل تلقائياً
        chat_history.append(types.UserContent(parts=[types.Part(text=chat_req.message)]))
        chat_history.append(types.ModelContent(parts=[types.Part(text=response.text)]))

        return {"response": response.text}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)