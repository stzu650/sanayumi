import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN")

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
            results.extend(extract_cc_from_line(line))

    with open(output_file, "w", encoding="utf-8") as f:
        for item in results:
            f.write(item + "\n")
    return len(results)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Halo! Kirim file yang ingin diproses.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    os.makedirs("downloads", exist_ok=True)
    file_path = f"downloads/{file.file_name}"
    await file.get_file().download_to_drive(custom_path=file_path)

    os.makedirs("outputs", exist_ok=True)
    output_path = f"outputs/clean_{file.file_name}"
    count = extract_cc_from_file(file_path, output_path)

    if count > 0:
        await context.bot.send_document(chat_id=update.message.chat.id, document=open(output_path, 'rb'))
        await update.message.reply_text(f"{count} kartu berhasil diekstrak dan dikirim.")
    else:
        await update.message.reply_text("Tidak ada data kartu yang cocok ditemukan.")

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    application.run_polling()

if __name__ == "__main__":
    main()
