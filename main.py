import time

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, GameHighScore
from telegram.ext import  CommandHandler,  CallbackContext, Application, \
    CallbackQueryHandler


global highScore,game_short_name,is_game_start,start_stop,game_score_time



game_short_name = "rocketBlaster"
is_game_start = False
start_stop = False
highScore: tuple[GameHighScore, ...] = []
game_score_time = {}

# 6488565585

admin_user_ids = [925780911]


async def only_admin(user_id:int,update:Update):

    # print(user_id)

    if user_id not in admin_user_ids:
        await update.message.reply_text("You haven't auth!")
        return False
    return True


async def setScore(update: Update, context: CallbackContext ):

    global is_game_start,highScore,game_score_time

    query: CallbackQuery = update.callback_query


    print(query.data)

    [_,new_score, game_time,api_user_id] = [int(x) if x.isdigit() else x for x in query.data.split(":")]


    # print(new_score)
    # print(game_time)

    chat_id = update.effective_chat.id
    user_id = context._user_id
    message_id = query.message.reply_to_message.message_id


    if (is_game_start and api_user_id == user_id):

        try:
            await context.bot.setGameScore(user_id, new_score, chat_id=chat_id, message_id=message_id)
            game_score_time[user_id] = game_time
            await context.bot.answer_callback_query(query.id, text="score recorded")
        except Exception as e:
            print(e)


        # get score

        highScore = await context.bot.getGameHighScores(user_id, chat_id=chat_id,message_id=message_id)


        # print(highScore)
    else:
        if(api_user_id == user_id):
            await context.bot.answer_callback_query(query.id, text="this is not your score")
        else:
            await context.bot.answer_callback_query(query.id, text="cant add score game is not started")


async def sendGame(update: Update, context: CallbackContext):

    global is_game_start

    query: CallbackQuery = update.callback_query

    chat_id = update.effective_chat.id
    game_url = "https://react-games-b6177.firebaseapp.com/tic-tac-toe/chatid/messageid/name"
    message_id = update.effective_message.message_id

    print("chatid: ",chat_id)
    print("message id : ",message_id)

    if(is_game_start):


        # print("Message id: ",message_id)
        # print("chat id: ", chat_id)

        await context.bot.answer_callback_query(query.id, url=game_url)
    else:
        await context.bot.answer_callback_query(query.id,text="game not already started")


async def start_game(update: Update, context: CallbackContext):

    global is_game_start

    if not is_game_start and await only_admin(update.effective_user.id,update):

        is_game_start = True
        await context.bot.send_game(chat_id=update.effective_chat.id, game_short_name=game_short_name)

    else:
        await context.bot.answer_callback_query(update.callback_query.id,text="game already started")


async def stop_game(update: Update, context: CallbackContext):
    global is_game_start, start_stop
    query: CallbackQuery = update.callback_query
    user_id = update.effective_user.id
    if await only_admin(user_id,update) and not start_stop and is_game_start:
        start_stop = True
        is_game_start = False

        await context.bot.send_message(update.effective_message.chat_id, text="game will stop in 5 second starting now")

        for i in range(5,0,-1):
            await context.bot.send_message(update.effective_message.chat_id, text=f"game will stop in {i} ")
            time.sleep(1)

        await context.bot.send_message(update.effective_message.chat_id, text="game stopped")
    else:
        await context.bot.answer_callback_query(query.id, text="you can not stop the game")

    start_stop = False


async def callback_handler(update: Update, context: CallbackContext):
    global is_game_start

    query: CallbackQuery = update.callback_query

    [callBackType, data] = ["",""]

    if query.game_short_name is not None:
        callBackType = query.game_short_name
    else:
        arr = query.data.split(":")
        callBackType = arr[0]




    if (callBackType == game_short_name):
        await sendGame(update, context)
    elif (callBackType == "score"):
        await setScore(update, context)
    elif (callBackType == "start_game"):
        await start_game(update,context)
    elif (callBackType == "stop_game"):
        await stop_game(update,context)
        pass
    elif (callBackType == "leaderboard"):
        await get_leaderboard_command(update,context)


async def start_command(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    if await only_admin(user_id,update):
        chat_id = update.effective_chat.id

        start_game_button = InlineKeyboardButton("Start game", callback_data="start_game")
        stop_game_button = InlineKeyboardButton("Stop game", callback_data="stop_game")
        leaderboard_button = InlineKeyboardButton("Leaderboard", callback_data="leaderboard")


        reply_markup = InlineKeyboardMarkup([[
            start_game_button,stop_game_button
        ],[leaderboard_button]])
        await context.bot.sendMessage(chat_id=chat_id,text="welcome",reply_markup=reply_markup)
        # await context.bot.send_game(chat_id=chat_id, game_short_name=game_short_name)

    pass

async def get_leaderboard_command(update: Update, context: CallbackContext):

    global highScore,game_score_time,is_game_start

    message = ""

    if(not is_game_start):
        # print(game_score_time)
        for i in range(len(highScore)):
            # print(highScore[i])
            message+= f"{highScore[i].position}. {highScore[i].user.name} => {highScore[i].score} , time => {game_score_time[highScore[i].user.id]} ms \n"


        if len(message) == 0:
            await context.bot.answer_callback_query(update.callback_query.id,text="no leaderboard ")
        else:
            await update.effective_chat.send_message(text=message)
    else:
        await context.bot.answer_callback_query(update.callback_query.id,text="game still running")




# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print("start bot...");
    token = "6038213239:AAFr-3kUV8qlbC_84e6cCRdNI1cseCdvJkM"

    application: Application = Application.builder().token(token).build()


    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("leaderboard", get_leaderboard_command))

    # application.add_handler(ext.CommandHandler("help", help))
    #
    application.add_handler(CallbackQueryHandler(callback_handler))


    application.run_polling()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
