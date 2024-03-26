import google.generativeai as genai

class MyGemini:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.chat = self.model.start_chat(history=[])

    def get_response(self, question):
        response = self.chat.send_message(question, stream=False)
        for candidate in response._result.candidates:
            generated_text = candidate.content.parts[0].text
            return generated_text    
