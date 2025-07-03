async def update_bot_profile(bot_client, user_client):
    """Update bot profile picture only (name/bio must be set via @BotFather)"""
    try:
        # Get user information
        user = await user_client.get_me()
        user_first_name = user.first_name
        
        # Get bot information
        bot_me = await bot_client.get_me()
        current_bot_name = bot_me.first_name
        
        print(f"\033[1;33mUser: {user_first_name}\033[0m")
        print(f"\033[1;33mCurrent bot name: {current_bot_name}\033[0m")
        
        # Show instructions for manual setup
        print("\033[1;36m" + "="*50)
        print("IMPORTANT: Bot name must be set manually via @BotFather")
        print(f"Recommended name: '{user_first_name}'s Assistant'")
        print(f"Recommended bio: '🤖 Personal Assistant Bot for {user_first_name}'")
        print("="*50 + "\033[0m")
        
        # Update bot profile picture
        await update_bot_profile_picture(bot_client, user_client)
        
        return True
        
    except Exception as e:
        print(f"\033[1;31mError updating bot profile: {e}\033[0m")
        return False
