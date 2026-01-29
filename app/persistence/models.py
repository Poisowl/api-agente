class ConversationState:
    def __init__(self, conversation_id: str, flow_id: str):
        self.conversation_id = conversation_id
        self.flow_id = flow_id
        self.current_node = None
        self.context = {}