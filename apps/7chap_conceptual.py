import streamlit as st
from openai import OpenAI
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
from datetime import datetime

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

SYSTEM_PROMPTS = {
    "구심 가속도": "너는 학생이 제출한 '구심 가속도 개념'에 대한 설명을 채점하고 피드백을 주는 AI 과학 튜터야.",
    "케플러 법칙": "너는 학생이 제출한 '케플러 법칙 개념'에 대한 설명을 채점하고 피드백을 주는 AI 과학 튜터야."
}


# 초기 UI
st.title("7장 개념 학습 도우미 챗봇")

# 사용자 개념 선택
selected_concept = st.selectbox("학습할 개념을 선택하세요:", ["구심 가속도", "케플러 법칙"])



# 초기 대화 기록 세션 저장
if "messages" not in st.session_state or st.session_state.get("last_concept") != selected_concept:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPTS[selected_concept]}]
    st.session_state.last_concept = selected_concept

# 기존 대화 출력
for msg in st.session_state.messages[1:]:  # system 프롬프트는 생략
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 유저 입력 받기
user_input = st.chat_input("질문을 입력해 보세요")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="gpt-4",
            messages=st.session_state.messages
        )
        reply = response.choices[0].message.content
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})


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

    # 대화 정리 및 저장
    chat_lines = []
    for msg in st.session_state.messages[1:]:
        role = f"🙋‍♂️ {user_label}" if msg["role"] == "user" else "🤖 GPT"
        chat_lines.append(f"{role}: {msg['content']}\n")
    chat_text = "\n".join(chat_lines)

    # 저장 파일명 (학교명_이름_시간)
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"{st.session_state.user_info['school']}_{st.session_state.user_info['name']}_{timestamp}.txt"

    # 다운로드 버튼 + 이메일 전송
    clicked = st.download_button(
        label="📥 대화 내용 저장 및 개발자에게 데이터 전송",
        data=chat_text,
        file_name=filename,
        mime="text/plain"
    )

    if clicked:
        send_email("학생 대화 내용 저장본", chat_text, filename)
        st.success("✅ 대화 내용이 저장되었어요!")
