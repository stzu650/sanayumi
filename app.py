from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import Bot
import os
import re

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

def extract_cc_from_line(line):
    pattern = re.compile(
        r"(\d{15,16})\|"            
        r"(0?[1-9]|1[0-2])\|"       
        r"(\d{2}|\d{4})\|"          
        r"(\d{3,4})"
    )
    return [match.group(0) for match in pattern.finditer(line)]

def extract_cc_from_file(input_file, output_file):
    results = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            matches = extract_cc_from_line(line)
            results.extend(matches)

    with open(output_file, "w", encoding="utf-8") as f:
        for item in results:
            f.write(item + "\n")
    return len(results)

def start(update, context):
    update.message.reply_text("Send me a file to process.")

def handle_file(update, context):
    file = update.message.document
    file_path = f"./downloads/{file.file_name}"
    os.makedirs("./downloads", exist_ok=True)
    file.get_file().download(custom_path=file_path)

    output_path = f"./outputs/clean_{file.file_name}"
    os.makedirs("./outputs", exist_ok=True)

    count = extract_cc_from_file(file_path, output_path)

    if count > 0:
        context.bot.send_document(chat_id=update.message.chat_id, document=open(output_path, 'rb'))
        update.message.reply_text(f"{count} cards found and output sent.")
    else:
        update.message.reply_text("No credit card data matched in the file.")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, handle_file))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
