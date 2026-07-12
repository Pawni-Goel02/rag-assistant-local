class Memory:

    def __init__(self):

        self.messages = []

    def add_user(self, message):

        self.messages.append(
            {
                "role": "user",
                "content": message
            }
        )

    def add_assistant(self, message):

        self.messages.append(
            {
                "role": "assistant",
                "content": message
            }
        )

    def history(self):

        return self.messages

    def clear(self):

        self.messages.clear()
    
    def clear(self):
        self.messages = []