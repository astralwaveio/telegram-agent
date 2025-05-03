# 消息模型
class Message:
    def __init__(self, message_id, user_id, text):
        self.message_id = message_id
        self.user_id = user_id
        self.text = text
