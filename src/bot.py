from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, JobQueue
import os
from dotenv import load_dotenv
import datetime
import pytz

TOTAL_COFFEES = {}   
USERNAMES = {}

       
async def coffee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Add a coffee to the user's count and print the total number of coffees drunk today
    """
    user_id = update.effective_user.id
    #print(update.effective_chat.id)
    if user_id not in TOTAL_COFFEES:
        USERNAMES[user_id] = update.effective_user.first_name
        TOTAL_COFFEES[user_id] = []
    TOTAL_COFFEES[user_id].append(datetime.date.today().strftime("%Y-%m-%d"))
    today = datetime.date.today().strftime("%Y-%m-%d")
    coffees_today = [coffee for coffee in TOTAL_COFFEES[user_id] if coffee.startswith(today)]
    await update.message.reply_text(f'{update.effective_user.first_name}, you have drunk {len(coffees_today)} coffees today {'☕'*len(coffees_today)}')
    
async def uncoffee(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Remove a coffee from the user's count and print the total number of coffees drunk today
    """
    user_id = update.effective_user.id
    if user_id not in TOTAL_COFFEES:
        USERNAMES[user_id] = update.effective_user.first_name
        TOTAL_COFFEES[user_id] = []
    today = datetime.date.today().strftime("%Y-%m-%d")
    if today in TOTAL_COFFEES[user_id]:
        TOTAL_COFFEES[user_id].remove(today)
    coffees_today = [coffee for coffee in TOTAL_COFFEES[user_id] if coffee.startswith(today)]
    await update.message.reply_text(f'{update.effective_user.first_name}, you have drunk {len(coffees_today)} coffees today {'☕'*len(coffees_today)}')


async def month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Get a monthly recap of the coffees drunk by the user
    """
    user_id = update.effective_user.id
    if user_id not in TOTAL_COFFEES:
        USERNAMES[user_id] = update.effective_user.first_name
        TOTAL_COFFEES[user_id] = []
    today = datetime.date.today().strftime("%Y-%m")
    month_name = datetime.date.today().strftime("%B")
    coffees_month = [coffee for coffee in TOTAL_COFFEES[user_id] if coffee.startswith(today)]
    await update.message.reply_text(f'{update.effective_user.first_name}, you have drunk {len(coffees_month)} coffees this {month_name} ☕')
    


async def total(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Get the total number of coffees drunk by the user
    """
    user_id = update.effective_user.id
    if user_id not in TOTAL_COFFEES:
        USERNAMES[user_id] = update.effective_user.first_name
        TOTAL_COFFEES[user_id] = []
    await update.message.reply_text(f'{update.effective_user.first_name}, you have drunk {len(TOTAL_COFFEES[user_id])} coffees in total ☕')



async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Display some information about the bot
    """
    try:
        with open('src/info.txt', 'r') as file:
            await update.message.reply_text(file.read())
    except FileNotFoundError:
        await update.message.reply_text("No information available, please contact the bot owner") 
        
        
async def daily_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send a daily reminder to the group
    """
    await context.bot.send_message(os.getenv('GROUP_ID'), "Don't forget to log any coffee you've had today! ☕")

def schedule_daily_reminder(job_queue: JobQueue) -> None:
    target_time = datetime.time(hour=22, minute=0, tzinfo=pytz.timezone('Europe/Rome'))
    job_queue.run_daily(daily_reminder, time=target_time)
    
    
    
def monthly_report(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send a monthly report to the group
    """
    today = datetime.date.today().strftime("%Y-%m")
    month_name = datetime.date.today().strftime("%B")
    context.bot.send_message(os.getenv('GROUP_ID'), f"Monthly report for {month_name} ⚠️ ")
    for user_id, coffees in TOTAL_COFFEES.items():
        coffees_month = [coffee for coffee in coffees if coffee.startswith(today)]
        context.bot.send_message(os.getenv('GROUP_ID'), f'{USERNAMES[user_id]} has drunk {len(coffees_month)} coffees this {month_name} ☕')
            
def schedule_monthly_report(job_queue: JobQueue) -> None:
    target_time = datetime.time(hour=22, minute=00, tzinfo=pytz.timezone('Europe/Rome'))
    job_queue.run_monthly(monthly_report, when=target_time, day=-1)

   
def main(): 
    # Load the token from the .env file
    load_dotenv()
    token = os.getenv('BOT_TOKEN')
    group_id = os.getenv('GROUP_ID')
    
    if not token or not group_id:
        print("No token or group id provided")
        return

    # Create the bot
    app = ApplicationBuilder().token(token).build()
    
    app.add_handler(CommandHandler("coffee", coffee))
    app.add_handler(CommandHandler("uncoffee", uncoffee))
    app.add_handler(CommandHandler("month", month))
    app.add_handler(CommandHandler("total", total))
    app.add_handler(CommandHandler("info", info))

    # Schedule the daily reminder
    schedule_daily_reminder(app.job_queue)
    schedule_monthly_report(app.job_queue)

    # Start the bot
    print("Bot is running")
    app.run_polling()



if __name__ == '__main__':
    main()