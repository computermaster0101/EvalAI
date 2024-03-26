debug = False

class ConversationHandler:

    def __init__(self) -> None:
        print("ConversationHandler.__init__") if debug else None
        self.max_history = 40
        self.conversations = {}
        self.conversation = []

    def __str__(self):
        print("ConversationHandler.__str__") if debug else None
        return self.__dict__
    
    def create_conversation(self, id=None):
        print("ConversationHandler.create_history") if debug else None
        if id in self.conversations:
            conversation_id = id
        else: 
            conversation_id = id or (len(self.conversations) + 1)
            self.conversations[conversation_id] = []

        return conversation_id 
    
    def get_conversation(self, conversation_id):
        print("ConversationHandler.get_conversation") if debug else None
        return self.conversations[conversation_id]
    
    def add_message(self, conversation_id, message):
        print("ConversationHandler.add_message") if debug else None
        self.conversations[conversation_id].append(message)
        self.trunctate_history(conversation_id)
        return self.conversations[conversation_id]
    
    def trunctate_history(self, conversation_id) -> None:
        print("ConversationHandler.trunctate_history") if debug else None
        if len(self.conversations[conversation_id]) > self.max_history:
            self.conversations[conversation_id] = self.conversations[conversation_id][-self.max_history:]

    def reset_conversation(self, conversation_id) -> None:
        print("ConversationHandler.reset_conversation") if debug else None
        # In this application we can just reset the conversation object
        # self.conversations[conversation_id] = []
        self.conversation = []



