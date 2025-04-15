## Configuration
• Adjust settings in config.py according to your environment.

   • Update allowed_users.json with the list of authorized Telegram user IDs.

   
1. Running the Bot  

   • The main entry point is in bot/main.py. Ensure you run the script (or the Docker container) in the appropriate context:
     
     python bot/main.py
     

   
2. Interacting with the Bot  

   • Once the bot is running, interact with it on Telegram:

     • Use the provided commands to perform OSINT searches.

     • Admins can use additional commands to manage the bot and user settings.

   
3. Extending Functionality  

   • Developers can add new handlers or utilities by following the existing module structure. New functionalities should integrate seamlessly due to the modular design.
