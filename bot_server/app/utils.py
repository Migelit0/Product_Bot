def get_messages_by_tag(data: list, tag: str):
    for elem in data:
        if elem['tag'] == tag:
            return elem['responses']