from memory import Memory

memory = Memory()

memory.add_user(
    "Hello"
)

memory.add_assistant(
    "Hi!"
)

print(memory.history())

memory.clear()

print(memory.history())