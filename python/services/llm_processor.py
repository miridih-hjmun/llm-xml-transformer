import openai
from config import API_KEYS

class LLMProcessor:
    def __init__(self, test_mode=False):
        if not test_mode:
            # 실제 모드에서는 API 키 설정
            openai.api_key = API_KEYS["openai"]
        else:
            # 테스트 모드에서는 API 키 설정 생략
            print("Test mode: OpenAI API key is not set.")

    def generate_response(self, prompt):
        """LLM API 호출"""
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=256,
        )
        return response["choices"][0]["message"]["content"]

    def prompt_text(self, text):
        """Simulate a response from the OpenAI API"""
        # This is where you simulate the transformation of the text
        text = "프롬프트 테스트 입니다."
        return text