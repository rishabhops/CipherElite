from telethon.tl.functions.users import GetFullUserRequest

async def get_user_from_event(event):
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_obj = await event.client(GetFullUserRequest(previous_message.sender_id))
    else:
        user = event.pattern_match.group(1)
        if user.isnumeric():
            user = int(user)
        try:
            user_obj = await event.client(GetFullUserRequest(user))
        except Exception as e:
            return None, e
    return user_obj, None
    