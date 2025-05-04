import streamlit as st
from openai import OpenAI
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
import datetime
import io

# OpenAI API 클라이언트 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 학교와 이름 입력받기
st.title("중학 과학 도우미 챗봇")
school = st.text_input("학교명을 입력하세요:")
name = st.text_input("이름을 입력하세요:")

if school and name:
    # 대화 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "너는 중학교 과학 선생님이야. 학생의 질문이 들어오면 중학교 수준에서 친절하게 대답해줘."}
        ]

    # 사용자 입력
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
            st.markdown(f"**🙋‍♂️ {school} {name}:** {msg['content']}")
        else:
            st.markdown(f"**🤖 GPT:** {msg['content']}")

    # 대화 텍스트 생성
    chat_lines = []
    for msg in st.session_state.messages[1:]:
        role = f"🙋‍♂️ {school} {name}" if msg["role"] == "user" else "🤖 GPT"
        chat_lines.append(f"{role}: {msg['content']}\n")
    chat_text = "\n".join(chat_lines)

    # 현재 시각 기반 파일명
    now = datetime.datetime.now()
    filename = now.strftime("%Y%m%d%H%M") + ".txt"

    # 텍스트 파일 준비
    file_buffer = io.BytesIO(chat_text.encode("utf-8"))

    # 이메일 전송 함수
    def send_email_with_attachment(subject, body_text, filename, file_buffer):
        sender = st.secrets["EMAIL_SENDER"]
        receiver = st.secrets["EMAIL_RECEIVER"]
        password = st.secrets["EMAIL_APP_PASSWORD"]

        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = receiver

        # 본문 추가
        msg.attach(MIMEText(body_text, "plain"))

        # 첨부파일 추가
        part = MIMEApplication(file_buffer.getvalue(), Name=filename)
        part["Content-Disposition"] = f'attachment; filename="{filename}"'
        msg.attach(part)

        # 메일 전송
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.send_message(msg)

    # 저장 및 전송 동시 수행
    if st.download_button(
        label="📥 대화 내용 저장",
        data=chat_text,
        file_name=filename,
        mime="text/plain"
    ):
        send_email_with_attachment("학생 대화 저장본", f"{school} {name} 학생의 대화 내용입니다.", filename, file_buffer)
        st.success("✅ 대화 내용이 텍스트로 저장되었어요!")

else:
    st.info("📌 먼저 학교명과 이름을 입력해 주세요.")
