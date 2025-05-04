import streamlit as st
from openai import OpenAI

# OpenAI API 키 가져오기
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("중학 과학 도우미 챗봇")
st.write("인공지능에게 자유롭게 질문해보세요.")

# 대화 기록 저장용 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "너는 중학교 과학 선생님이야. 학생의 질문이 들어오면 중학교 수준에서 친절하게 대답해줘."}
    ]

# 사용자 입력 받기
user_input = st.text_input("질문을 입력하세요:")

if user_input:
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": user_input})

    # GPT 응답 생성
    with st.spinner("GPT-4o가 생각 중..."):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state.messages,
            temperature=0.5,
        )
        gpt_reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": gpt_reply})
        
# 대화 내용을 텍스트로 정리
chat_lines = []
for msg in st.session_state.messages[1:]:
    role = "🙋‍♂️ 너" if msg["role"] == "user" else "🤖 GPT"
    chat_lines.append(f"{role}: {msg['content']}\n")
chat_text = "\n".join(chat_lines)

# 곧바로 텍스트 다운로드 버튼 표시 (한 번에 저장)
st.download_button(
    label="📥 대화 내용 TXT로 저장",
    data=chat_text,
    file_name="chat_log.txt",
    mime="text/plain"
)
