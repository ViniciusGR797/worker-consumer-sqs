from controllers.messages import message_handler

def handler(event, context):
    return message_handler(event)

