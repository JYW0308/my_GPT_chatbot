import streamlit as st
from openai import OpenAI
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
from datetime import datetime
import io

# OpenAI 클라이언트 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 이메일 전송 함수
def send_email(subject, body, filename):
    sender = st.secrets["EMAIL_SENDER"]
    receiver = st.secrets["EMAIL_RECEIVER"]
    password = st.secrets["EMAIL_APP_PASSWORD"]

    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    msg.attach(MIMEText("첨부된 대화 내용을 확인하세요.", "plain"))

    part = MIMEApplication(body.encode("utf-8"), Name=filename)
    part['Content-Disposition'] = f'attachment; filename="{filename}"'
    msg.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(msg)

# 초기 설정
st.title("중학 과학 도우미 챗봇")
st.write("AI 선생님에게 자유롭게 질문해보세요.")

# 사용자 정보 입력
if "user_info" not in st.session_state:
    with st.form("user_info_form"):
        school = st.text_input("학교명")
        name = st.text_input("이름")
        submitted = st.form_submit_button("시작하기")
        if submitted and school and name:
            st.session_state.user_info = {"school": school, "name": name}
            st.rerun()
        elif submitted:
            st.warning("학교명과 이름을 모두 입력해주세요.")

if "user_info" in st.session_state:
    user_label = f"{st.session_state.user_info['school']} {st.session_state.user_info['name']}"

    # 대화 기록 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "너는 중학교 과학 선생님이야. 학생의 질문이 들어오면 중학교 수준에서 친절하게 대답해줘."}
        ]

    # 사용자 입력 받기
    user_input = st.chat_input(f"{user_label}님, 질문을 입력하세요")

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
            st.markdown(f"**🙋‍♂️ {user_label}:** {msg['content']}")
        else:
            st.markdown(f"**🤖 GPT:** {msg['content']}")

    # 대화 내용 저장
    chat_lines = []
    for msg in st.session_state.messages[1:]:
        role = f"🙋‍♂️ {user_label}" if msg["role"] == "user" else "🤖 GPT"
        chat_lines.append(f"{role}: {msg['content']}\n")
    chat_text = "\n".join(chat_lines)

    # 저장 시 파일 이름 설정 (학교명_이름.txt)
    filename = f"{st.session_state.user_info['school']}_{st.session_state.user_info['name']}.txt"

    # 저장 버튼
    st.download_button(
        label="📥 대화 내용 저장",
        data=chat_text,
        file_name=filename,
        mime="text/plain"
    )

    # 동시에 이메일 전송
    send_email("학생 대화 내용 저장본", chat_text, filename)
    st.success("✅ 대화 내용이 저장되었어요!")
