from flask import Flask, request, render_template, send_from_directory, session
from flask_session import Session
from flask_socketio import SocketIO
import time
from MyOpenAI import MyOpenAI
from ConversationHandler import ConversationHandler
from BedrockHandler import Claude
from GeminiHandler import MyGemini
import threading
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
openai_api_key = os.environ.get('OPENAI_API_KEY')
aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
gemini_api_key = os.environ.get('GEMINI_API_KEY')



class WebSrvr:
    def __init__(self, host='127.0.0.1', port=5000):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'aswskjashdoi68aoiuhli76qijbnli7z6a'  # Change this to a random secret key
        self.app.config['SESSION_TYPE'] = 'filesystem'  # You can change this to other session types as per your requirement
        Session(self.app)

        self.host = host
        self.port = port
        self.socketio = SocketIO(self.app)

        self.conversations = ConversationHandler()
        self.openai = MyOpenAI(openai_api_key)
        self.claude = Claude(aws_access_key_id, aws_secret_access_key)
        self.gemini = MyGemini(gemini_api_key)



        @self.app.route('/', defaults={'path': 'index.html'})
        @self.app.route('/<path:path>')
        def render_html(path):
            return render_template(path)
        
        @self.app.route('/images/<path:filename>')
        def serve_images(filename):
            return send_from_directory('images', filename)
        
        @self.socketio.on('connect')
        def handle_connect():
            # Associate each client with a unique identifier (e.g., session ID)
            # You may need to modify this based on how you manage sessions in your application
            client_id = request.sid
            session['client_id'] = client_id
            print(f"Client connected: {client_id}")

        @self.socketio.on('disconnect')
        def handle_disconnect():
            client_id = session.get('client_id')
            if client_id:
                print(f"Client disconnected: {client_id}")
            
        @self.socketio.on('request')
        def getResponse(request):
            client_id = session.get('client_id')
            print("Received chat query:", request)
            print("Received chat query:", request['message'])  # Corrected line
            if request['message'].lower() in ["", "hi", "hello", "hey"]:  # Corrected line
                text = "Hello!"
                self.socketio.emit('reply', {'response': text}, room=client_id)
            else:
                self.socketio.emit('thinking', {'response': "One moment I'm thinking..."}, room=client_id)

                def process_claude():
                    claude_start_time = time.time()  
                    claude_conversation_id = self.conversations.create_conversation(f'{client_id}-claude')
                    self.conversations.add_message(claude_conversation_id, request['message'])
                    claude_conversation = self.conversations.get_conversation(claude_conversation_id)
                    claude_response = self.claude.process_message(request, claude_conversation)
                    self.conversations.add_message(claude_conversation_id, claude_response)
                    self.conversations.trunctate_history(claude_conversation_id)
                    claude_end_time = time.time()
                    claude_time_taken = claude_end_time - claude_start_time
                    self.socketio.emit('reply', {'llm': 'Claude', 'response': f"{claude_time_taken}s<br>{claude_response}"}, room=client_id)

                def process_gemini():
                    gemini_start_time = time.time()
                    gemini_conversation_id = self.conversations.create_conversation(f'{client_id}-gemini')
                    self.conversations.add_message(gemini_conversation_id, request['message'])
                    gemini_coversation = self.conversations.get_conversation(gemini_conversation_id)
                    gemini_response = self.gemini.get_response(request['message'])
                    self.conversations.add_message(gemini_conversation_id, gemini_response)
                    gemini_end_time = time.time()
                    gemini_time_taken = gemini_end_time - gemini_start_time
                    self.socketio.emit('reply', {'llm': 'Gemini', 'response': f"{gemini_time_taken}s<br>{gemini_response}"}, room=client_id)

                def process_openai():
                    openai_start_time = time.time()        
                    openai_conversation_id = self.conversations.create_conversation(f'{client_id}-openai')
                    self.conversations.add_message(openai_conversation_id, request['message'])
                    openai_conversation = self.conversations.get_conversation(openai_conversation_id)
                    openai_response = self.openai.process_message(request, openai_conversation)
                    self.conversations.add_message(openai_conversation_id, openai_response)
                    self.conversations.trunctate_history(openai_conversation_id)
                    openai_end_time = time.time()
                    openai_time_taken = openai_end_time - openai_start_time
                    self.socketio.emit('reply', {'llm': 'OpenAI', 'response': f"{openai_time_taken}s<br>{openai_response}"}, room=client_id)

                # Run each process in a separate thread
                threads = []
                threads.append(threading.Thread(target=process_claude))
                threads.append(threading.Thread(target=process_gemini))
                threads.append(threading.Thread(target=process_openai))

                for thread in threads:
                    thread.start()

                # Wait for all threads to complete
                for thread in threads:
                    thread.join()
                

        @self.socketio.on('chat_reset')
        def reset(query):
            client_id = session.get('client_id')
            print("Received chat reset")
     
    
    def run(self):
        print(f"Running Flask app on {self.host}:{self.port}")
        self.socketio.run(self.app, host=self.host, port=self.port, allow_unsafe_werkzeug=True)

if __name__ == "__main__":
    HOST = "0.0.0.0"
    PORT = 8080
    print("Initializing EvalAI")
    MyWebSrvr = WebSrvr(host=HOST, port=PORT)
    print("Starting EvalAI")
    MyWebSrvr.run()
