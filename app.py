import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("GPT-4o 간단 챗봇")
st.write("GPT-4o에게 자유롭게 질문해보세요.")

user_input = st.text_input("질문을 입력하세요:")

if user_input:
    with st.spinner("GPT-4o가 생각 중..."):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "친절한 과학 선생님처럼 대답해줘."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.5
        )
        answer = response.choices[0].message.content
        st.markdown(f"**GPT의 답변:** {answer}")
