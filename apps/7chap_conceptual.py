import streamlit as st
from openai import OpenAI
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import smtplib
from datetime import datetime

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

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

GENERAL_PROMPT = """너는 학생이 제출한 '{concept_name} 개념'에 대한 설명을 채점하고 피드백을 주는 AI 과학 튜터야.
학생이 제출한 개념 설명을 다음의 <요소>를 기준으로 판단하고, <모범 답안>에 비추어 부족한 부분을 위주로 피드백 해줘.
잘한 <요소>에 대해서는 언급하지 않아도 돼. 부족한 부분에 대해 직접적인 힌트는 주지마. 너가 판단했을 때 개념 설명이 완벽해서 피드백을 해줄게 없다면 '완벽합니다. 짝짝짝'이라고 응답해줘.

<요소>
- 과학적 용어의 정확한 사용
- 과학적 용어들 사이의 관계의 명확성
- 오개념의 유무

<모범 답안>
{reference_answer}
"""
REFERENCE_ANSWERS = {
    "등속 원운동에서의 구심 가속도": """구심 가속도는 등속 원운동하는 물체에 작용하는 알짜 가속도로, 
그 크기는 속력의 제곱에 비례하고 원궤도의 반지름에 반비례한다. 
구심 가속도의 방향은 항상 원의 중심을 향한다.""",

    "케플러 법칙": """케플러 법칙은 행성의 궤도가 태양을 초점으로 하는 타원이라는 제1법칙, 
태양과 임의의 행성을 잇는 직선이 같은 시간 동안 쓸고 가는 면적은 일정하다는 제2법칙, 
행성의 공전 주기의 제곱과 공전 반경의 세제곱이 비례한다는 제3법칙을 말한다."""
}


st.title("7장 개념 학습 도우미 챗봇")

# 이름 입력
if "user_label" not in st.session_state:
    name = st.text_input("이름을 입력하세요:")
    if name:
        st.session_state.user_label = name
        st.rerun()
    st.stop()

user_label = st.session_state["user_label"]

# 개념 선택
selected_concept = st.selectbox("학습할 개념을 선택하세요:", list(REFERENCE_ANSWERS.keys()))
prompt = GENERAL_PROMPT.format(
    concept_name=selected_concept,
    reference_answer=REFERENCE_ANSWERS[selected_concept]
)

# 메시지 초기화
if "messages" not in st.session_state or st.session_state.get("last_concept") != selected_concept:
    st.session_state.messages = [
    {"role": "system", "content": prompt},
    {"role": "assistant", "content": f"{selected_concept}에 대해 어떻게 생각하나요? 자유롭게 설명해보세요!"}
]
    st.session_state.last_concept = selected_concept
    
# 대화 출력
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        speaker = f"{user_label}" if msg["role"] == "user" else "GPT"
        st.markdown(f"**{speaker}:** {msg['content']}")


# 입력 받기
user_input = st.chat_input("개념을 설명해보세요!")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(f"**{user_label}:** {user_input}")
    with st.spinner("GPT가 피드백을 작성 중입니다..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages,
                temperature=0.2,
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(f"**GPT:** {reply}")
        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")

# 저장 및 이메일 전송
chat_lines = [
    f"{user_label if msg['role'] == 'user' else 'GPT'}: {msg['content']}"
    for msg in st.session_state.messages[1:]
]
chat_text = "\n".join(chat_lines)
filename = f"{user_label}_{datetime.now().strftime('%Y%m%d')}.txt"

if st.download_button("📥 대화 저장 및 전송", chat_text, filename, mime="text/plain"):
    send_email("학생 대화 내용 저장본", chat_text, filename)
    st.success("✅ 대화가 저장되고 이메일로 전송되었어요!")
