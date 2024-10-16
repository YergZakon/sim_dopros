import streamlit as st
import anthropic

# Инициализация клиента Anthropic с использованием секрета Streamlit
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# Остальной код остается без изменений
questions = [
    "Где вы были вечером 1 января 2024 года?",
    "Вы знакомы с Сейдахметовым Е.С.?",
    "Расскажите о вашем распорядке дня 1 января 2024 года.",
    "Вы когда-нибудь были в районе улицы Сатпаева в Жезказгане?",
    "Какие марки автомобилей вам нравятся?",
    "Вы можете описать, где вы обычно паркуете свой автомобиль?",
    "Как вы обычно проводите новогодние праздники?",
    "У вас есть друзья или знакомые, владеющие автомобилем Lexus?",
    "Вы когда-нибудь сталкивались с кражами или ограблениями?",
    "Как вы относитесь к дорогим автомобилям?",
    "Была ли у вас когда-нибудь машина марки Lexus?",
    "Вы можете описать ваше финансовое положение на начало 2024 года?",
    "Как вы объясните наличие отпечатков ваших пальцев на ручке двери Lexus?",
    "Вы можете описать содержимое вашего портмоне?",
    "Какие у вас планы на будущее?"
]

def generate_response(question, conversation_history):
    system_prompt = """Вы - Хуснутдинов Данияр Тагирович, подозреваемый в краже из автомобиля Lexus RX300 1 января 2024 года в Жезказгане. Вы виновны, но пытаетесь это скрыть. Ваши ответы должны быть уклончивыми, неполными или даже ложными, но не слишком очевидно. Вы нервничаете во время допроса, что может проявляться в вашей речи. Старайтесь не отвечать прямо на вопросы, особенно касающиеся Lexus или кражи. Ваша цель - избежать признания вины."""

    messages = conversation_history + [
        {"role": "user", "content": f"Вопрос следователя: {question}"}
    ]

    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=200,
        system=system_prompt,
        messages=messages
    )
    return response.content[0].text

def evaluate_response(question, response):
    suspicious_keywords = ['lexus', 'кража', 'угон', 'деньги', 'портмоне', 'отпечатки', 'улица сатпаева']
    evasive_phrases = ['не помню', 'не уверен', 'может быть', 'возможно', 'не совсем понимаю']
    
    lower_response = response.lower()
    suspicion_score = sum(keyword in lower_response for keyword in suspicious_keywords)
    evasiveness_score = sum(phrase in lower_response for phrase in evasive_phrases)
    
    total_score = suspicion_score + evasiveness_score
    rating = min(max(total_score, 1), 5)  # Ограничиваем оценку от 1 до 5
    
    explanation = f"Ответ содержит {suspicion_score} подозрительных ключевых слов и {evasiveness_score} уклончивых фраз."
    if rating <= 2:
        explanation += " Ответ кажется относительно прямым и не вызывает больших подозрений."
    elif rating <= 4:
        explanation += " Ответ вызывает некоторые подозрения и кажется уклончивым."
    else:
        explanation += " Ответ крайне подозрителен и уклончив."
    
    return rating, explanation

def main():
    st.set_page_config(page_title="Симулятор допроса", page_icon="🕵️")
    st.title("Симулятор допроса подозреваемого")

    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []
    if 'asked_questions' not in st.session_state:
        st.session_state.asked_questions = []
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'responses' not in st.session_state:
        st.session_state.responses = []

    available_questions = [q for q in questions if q not in st.session_state.asked_questions]
    
    if available_questions:
        selected_question = st.selectbox("Выберите вопрос для допроса:", available_questions)
        
        if st.button("Задать вопрос"):
            with st.spinner("Подозреваемый обдумывает ответ..."):
                response = generate_response(selected_question, st.session_state.conversation_history)
                st.session_state.conversation_history.append({"role": "user", "content": f"Вопрос следователя: {selected_question}"})
                st.session_state.conversation_history.append({"role": "assistant", "content": response})
                
                rating, explanation = evaluate_response(selected_question, response)
            
            st.session_state.responses.append({
                "question": selected_question,
                "answer": response,
                "rating": rating,
                "explanation": explanation
            })
            
            st.session_state.asked_questions.append(selected_question)
            st.session_state.score += rating

    # Отображение истории допроса
    st.subheader("История допроса")
    for item in st.session_state.responses:
        st.write(f"**Вопрос:** {item['question']}")
        st.write(f"**Ответ подозреваемого:** {item['answer']}")
        st.write(f"**Подозрительность ответа:** {item['rating']}/5")
        st.write(f"**Анализ:** {item['explanation']}")
        st.write("---")

    if not available_questions:
        st.success("Допрос завершен. Все вопросы были заданы.")
    
    st.sidebar.title("Информация о допросе")
    st.sidebar.write(f"Заданных вопросов: {len(st.session_state.asked_questions)}")
    st.sidebar.write(f"Общий уровень подозрительности: {st.session_state.score}")
    
    st.sidebar.title("Заданные вопросы")
    for q in st.session_state.asked_questions:
        st.sidebar.write(q)

if __name__ == "__main__":
    main()
