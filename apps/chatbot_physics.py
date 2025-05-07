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

# 초기 UI
st.title("중학교 과학 학습 도우미 챗봇")
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

# 사용자 정보가 입력된 경우
if "user_info" in st.session_state:
    user_label = f"{st.session_state.user_info['school']} {st.session_state.user_info['name']}"

    # 대화 기록 초기화
    if "messages" not in st.session_state:
        st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "역할: 너는 고등학교 물리학과 관련된 개념 설명을 위한 챗봇이야.\n\n"
                "규칙:\n"
                "1. 학생의 질문에 2022 개정 교육과정의 고등학교 과학과 선택과목(물리학, 역학과 에너지, 전자기와 양자, 융합과학 탐구) 수준에서 친절하게 설명해.\n"

        server.send_message(msg)

# 초기 UI
st.title("중학교 과학 학습 도우미 챗봇")
st.write("AI 선생님에게 자유롭게 질문해보세요.")

"역할: 너는 고등학교 통합과학과 관련된 개념 설명을 위한 챗봇이야.\n\n"
                "규칙:\n"
                "1. 학생의 질문에 2022개정 교육과정의 고등학교 통합과학 수준에서 친절하게 설명해.\n"
                "2. 질문이 과학(물리, 화학, 생물, 지구과학)과 관련이 없으면 정중히 답변을 거절해.\n"
                "3. 특히 미성년자에게 부적절한 대답을 해서는 절대 안 돼."

                

    # 사용자 입력
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
