import streamlit as st
from openai import OpenAI
from email.mime.text import MIMEText
import smtplib


client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def send_email(subject, body):
    sender = st.secrets["EMAIL_SENDER"]
    receiver = st.secrets["EMAIL_RECEIVER"]
    password = st.secrets["EMAIL_APP_PASSWORD"]

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)
        
st.title("중학 과학 도우미 챗봇")
st.write("인공지능에게 자유롭게 질문해보세요.")

# 대화 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "너는 중학교 과학 선생님이야. 학생의 질문이 들어오면 중학교 수준에서 친절하게 대답해줘."}
    ]
# 사용자 입력 받기 (st.chat_input은 자동으로 초기화됨)
user_input = st.chat_input("질문을 입력하세요")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("GPT-4o가 생각 중..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages,
                temperature=0.5,
            )
            gpt_reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": gpt_reply})
        except Exception as e:
            st.error(f"⚠️ 오류 발생: {e}")

# 대화 출력
for msg in st.session_state.messages[1:]:
    if msg["role"] == "user":
        st.markdown(f"**🙋‍♂️ 너:** {msg['content']}")
    else:
        st.markdown(f"**🤖 GPT:** {msg['content']}")

# 대화 텍스트 파일 다운로드
chat_lines = []
for msg in st.session_state.messages[1:]:
    role = "🙋‍♂️ 너" if msg["role"] == "user" else "🤖 GPT"
    chat_lines.append(f"{role}: {msg['content']}\n")
chat_text = "\n".join(chat_lines)

st.download_button(
    label="📥 대화 내용 TXT로 저장",
    data=chat_text,
    file_name="chat_log.txt",
    mime="text/plain"
)
if st.button("📥 대화 내용 이메일로 전송"):
    send_email("학생 대화 내용 저장본", chat_text)
    st.success("✅ 대화 내용이 이메일로 전송되었어요!")
