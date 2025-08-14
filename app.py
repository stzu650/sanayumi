import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")  # GET THE BOT TOKEN FROM ENVIRONMENT VARIABLE

def EXTRACT_CC_FROM_LINE(line):
    PATTERN = re.compile(
        r"(\d{15,16})\|"
        r"(0?[1-9]|1[0-2])\|"
        r"(\d{2}|\d{4})\|"
        r"(\d{3,4})"
    )
    return [MATCH.group(0) for MATCH in PATTERN.finditer(line)]

def EXTRACT_CC_FROM_FILE(INPUT_FILE, OUTPUT_FILE):
    RESULTS = []
    with open(INPUT_FILE, "r", encoding="utf-8") as F:
        for LINE in F:
            LINE = LINE.strip()
            RESULTS.extend(EXTRACT_CC_FROM_LINE(LINE))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as F:
        for ITEM in RESULTS:
            F.write(ITEM + "\n")
    return len(RESULTS)

async def START(UPDATE: Update, CONTEXT: ContextTypes.DEFAULT_TYPE):
    await UPDATE.message.reply_text("HELLO! SEND ME A FILE TO PROCESS.")

async def HANDLE_FILE(UPDATE: Update, CONTEXT: ContextTypes.DEFAULT_TYPE):
    FILE = UPDATE.message.document
    os.makedirs("downloads", exist_ok=True)
    FILE_PATH = f"downloads/{FILE.file_name}"

    NEW_FILE = await FILE.get_file()
    await NEW_FILE.download_to_drive(custom_path=FILE_PATH)

    os.makedirs("outputs", exist_ok=True)
    OUTPUT_PATH = f"outputs/clean_{FILE.file_name}"
    COUNT = EXTRACT_CC_FROM_FILE(FILE_PATH, OUTPUT_PATH)

    if COUNT > 0:
        await CONTEXT.bot.send_document(chat_id=UPDATE.message.chat.id, document=open(OUTPUT_PATH, 'rb'))
        await UPDATE.message.reply_text(f"{COUNT} CARDS SUCCESSFULLY EXTRACTED AND SENT.")
    else:
        await UPDATE.message.reply_text("NO MATCHING CARD DATA FOUND IN THE FILE.")

def MAIN():
    APPLICATION = ApplicationBuilder().token(TOKEN).build()
    APPLICATION.add_handler(CommandHandler("start", START))
    APPLICATION.add_handler(MessageHandler(filters.Document.ALL, HANDLE_FILE))
    APPLICATION.run_polling()

if __name__ == "__main__":
    MAIN()
