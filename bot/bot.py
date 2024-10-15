import os
import re
import logging
from dotenv import load_dotenv
from telegram import Update, error
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)
import paramiko
from telegram.utils.helpers import escape_markdown
import psycopg2

load_dotenv()

logging.basicConfig(
    filename="bot.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

TOKEN = os.getenv("TOKEN")
RM_HOST = os.getenv("RM_HOST")
RM_PORT = int(os.getenv("RM_PORT", 22))
RM_USER = os.getenv("RM_USER")
RM_PASSWORD = os.getenv("RM_PASSWORD")

logging.basicConfig(
    filename="bot.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# Регулярные выражения для поиска email и телефонов
email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
phone_regex = r"(\+7|8)[-\s]?(\(?\d{3}\)?)[-\s]?(\d{3})[-\s]?(\d{2})[-\s]?(\d{2})"


def start(update: Update, context):
    update.message.reply_text(
        "Привет! Я помогу вам найти email и номера телефонов, проверить пароль и мониторить систему."
    )


def find_email(update: Update, context):
    update.message.reply_text("Введите текст для поиска email-адресов:")
    return "FIND_EMAIL"


def process_email(update: Update, context):
    user_input = update.message.text
    emails = re.findall(email_regex, user_input)
    if emails:
        update.message.reply_text(f"Найденные email-адреса:\n" + "\n".join(emails))
        return ask_to_save(update, context, "email", emails)
    else:
        update.message.reply_text("Email-адреса не найдены.")
    return ConversationHandler.END


def find_phone_number(update: Update, context):
    update.message.reply_text("Введите текст для поиска номеров телефонов:")
    return "FIND_PHONE"


def process_phone(update: Update, context):
    user_input = update.message.text
    phones = re.findall(phone_regex, user_input)
    if phones:
        all_phones = ["".join(p) for p in phones]
        update.message.reply_text(
            f"Найденные номера телефонов:\n" + "\n".join(all_phones)
        )
        return ask_to_save(update, context, "phone", all_phones)
    else:
        update.message.reply_text("Номера телефонов не найдены.")
    return ConversationHandler.END


def verify_password(update: Update, context):
    update.message.reply_text("Введите пароль для проверки сложности:")
    return "VERIFY_PASSWORD"


def process_password(update: Update, context):
    password = update.message.text
    if (
        len(password) >= 8
        and re.search(r"[A-Z]", password)
        and re.search(r"[a-z]", password)
        and re.search(r"\d", password)
        and re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
    ):
        update.message.reply_text("Пароль сложный.")
    else:
        update.message.reply_text("Пароль простой.")
    return ConversationHandler.END


def ssh_execute_command(command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=RM_HOST, port=RM_PORT, username=RM_USER, password=RM_PASSWORD
    )
    stdin, stdout, stderr = client.exec_command(command)
    result = stdout.read().decode("utf-8")
    client.close()
    return result


def get_release(update: Update, context):
    result = ssh_execute_command("cat /etc/*release")
    escaped_result = escape_markdown(result, version=2)
    formatted_result = f"```\n{escaped_result}\n```"
    update.message.reply_text(formatted_result, parse_mode="MarkdownV2")


def get_uname(update: Update, context):
    result = ssh_execute_command("uname -a")
    escaped_result = escape_markdown(result, version=2)
    formatted_result = f"```\n{escaped_result}\n```"
    update.message.reply_text(formatted_result, parse_mode="MarkdownV2")


def get_uptime(update: Update, context):
    result = ssh_execute_command("uptime -p")
    escaped_result = escape_markdown(result, version=2)
    formatted_result = f"```\n{escaped_result}\n```"
    update.message.reply_text(formatted_result, parse_mode="MarkdownV2")


def get_df(update: Update, context):
    result = ssh_execute_command("df -h")
    escaped_result = escape_markdown(result, version=2)
    formatted_result = f"```\n{escaped_result}\n```"
    update.message.reply_text(formatted_result, parse_mode="MarkdownV2")


def get_free(update: Update, context):
    result = ssh_execute_command("free -h")
    escaped_result = escape_markdown(result, version=2)
    formatted_result = f"```\n{escaped_result}\n```"
    update.message.reply_text(formatted_result, parse_mode="MarkdownV2")


def get_mpstat(update: Update, context):
    result = ssh_execute_command("mpstat")
    escaped_result = escape_markdown(result, version=2)
    formatted_result = f"```\n{escaped_result}\n```"
    update.message.reply_text(formatted_result, parse_mode="MarkdownV2")


def get_w(update: Update, context):
    result = ssh_execute_command("w")
    escaped_result = escape_markdown(result, version=2)
    formatted_result = f"```\n{escaped_result}\n```"
    update.message.reply_text(formatted_result, parse_mode="MarkdownV2")


def get_auths(update: Update, context):
    result = ssh_execute_command("last -n 10")
    escaped_result = escape_markdown(result, version=2)
    formatted_result = f"```\n{escaped_result}\n```"
    update.message.reply_text(
        f"Последние 10 входов в систему:\n{formatted_result}", parse_mode="MarkdownV2"
    )


def get_critical(update: Update, context):
    result = ssh_execute_command("grep -i critical /var/log/syslog | tail -n 5")
    escaped_result = escape_markdown(result, version=2)
    formatted_result = f"```\n{escaped_result}\n```"
    update.message.reply_text(
        f"Последние 5 критических событий:\n{formatted_result}", parse_mode="MarkdownV2"
    )


def get_ps(update: Update, context):
    result = ssh_execute_command("ps aux")

    escaped_result = escape_markdown(result, version=2)
    formatted_result = f"```\n{escaped_result.strip()}\n```"

    chunk_size = 4000 - len("```\n\n```")

    for i in range(0, len(formatted_result), chunk_size):
        try:
            update.message.reply_text(
                formatted_result[i : i + chunk_size], parse_mode="MarkdownV2"
            )
        except error.BadRequest as e:
            print(f"Ошибка отправки сообщения: {e}")


def get_ss(update: Update, context):
    result = ssh_execute_command("ss -tuln")
    escaped_result = escape_markdown(result, version=2)
    formatted_result = f"```\n{escaped_result}\n```"
    update.message.reply_text(formatted_result, parse_mode="MarkdownV2")


def get_apt_list(update: Update, context):
    package_name = (
        context.args[0] if context.args else None
    )  # Получаем имя пакета из аргументов, если оно есть
    chunk_size = 4000

    if package_name:
        result = ssh_execute_command(f"dpkg -l | grep {package_name}")
        if result:
            message = f"Информация о пакете {package_name}:\n{escape_markdown(result, version=2)}"
        else:
            message = f"Пакет {package_name} не найден."
    else:
        result = ssh_execute_command("dpkg -l")
        if result:
            message = f"Все установленные пакеты:\n{escape_markdown(result, version=2)}"
        else:
            message = "Не удалось получить список установленных пакетов."

    for i in range(0, len(message), chunk_size):
        update.message.reply_text(message[i : i + chunk_size], parse_mode="MarkdownV2")


def get_services(update: Update, context):
    result = ssh_execute_command("systemctl list-units --type=service --state=running")
    escaped_result = escape_markdown(result, version=2)
    formatted_result = f"```\n{escaped_result}\n```"
    update.message.reply_text(formatted_result, parse_mode="MarkdownV2")


def get_repl_logs(update: Update, context):
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        cur = conn.cursor()

        cur.execute(
            "SELECT pg_read_file('/var/log/postgresql/postgresql.log', 0, 1000000)"
        )
        log_data = cur.fetchone()[0]

        replication_logs = [
            line for line in log_data.splitlines() if "replication" in line
        ]

        if replication_logs:
            formatted_logs = "\n".join(replication_logs)
            escaped_result = escape_markdown(formatted_logs, version=2)

            MAX_MESSAGE_LENGTH = 4096 - 6  # Оставляем место для кодового блока
            chunks = [
                escaped_result[i : i + MAX_MESSAGE_LENGTH]
                for i in range(0, len(escaped_result), MAX_MESSAGE_LENGTH)
            ]

            for chunk in chunks:
                formatted_chunk = f"```\n{chunk}\n```"
                update.message.reply_text(formatted_chunk, parse_mode="MarkdownV2")
        else:
            update.message.reply_text("Логи репликации не найдены.")

        cur.close()
        conn.close()
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении логов: {e}")


def get_emails(update: Update, context):
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute("SELECT email FROM emails")
        emails = cur.fetchall()
        if emails:
            update.message.reply_text("\n".join([email[0] for email in emails]))
        else:
            update.message.reply_text("Email-адреса не найдены.")
        cur.close()
        conn.close()
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении данных: {e}")


def get_phone_numbers(update: Update, context):
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_DATABASE"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        cur = conn.cursor()
        cur.execute("SELECT phone FROM phone_numbers")
        phones = cur.fetchall()
        if phones:
            update.message.reply_text("\n".join([phone[0] for phone in phones]))
        else:
            update.message.reply_text("Номера телефонов не найдены.")
        cur.close()
        conn.close()
    except Exception as e:
        update.message.reply_text(f"Ошибка при получении данных: {e}")


def ask_to_save(update: Update, context, data_type, data):
    update.message.reply_text(
        f"Хотите ли вы сохранить найденные {data_type} в базу данных? (да/нет)"
    )
    context.user_data["data_type"] = data_type
    context.user_data["data"] = data
    return "CONFIRM_SAVE"


def save_data(update: Update, context):
    response = update.message.text.lower()
    if response == "да":
        data_type = context.user_data.get("data_type")
        data = context.user_data.get("data")
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("DB_DATABASE"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
            )
            cur = conn.cursor()
            if data_type == "email":
                cur.executemany(
                    "INSERT INTO emails (email) VALUES (%s) ON CONFLICT DO NOTHING",
                    [(d,) for d in data],
                )
            elif data_type == "phone_numbers":
                cur.executemany(
                    "INSERT INTO phone_numbers (phone) VALUES (%s) ON CONFLICT DO NOTHING",
                    [(d,) for d in data],
                )
            conn.commit()
            cur.close()
            conn.close()
            update.message.reply_text(
                f"Данные успешно сохранены в таблицу {data_type}."
            )
        except Exception as e:
            update.message.reply_text(f"Ошибка при сохранении данных: {e}")
    else:
        update.message.reply_text("Данные не были сохранены.")
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("get_release", get_release))
    dp.add_handler(CommandHandler("get_uname", get_uname))
    dp.add_handler(CommandHandler("get_uptime", get_uptime))
    dp.add_handler(CommandHandler("get_df", get_df))
    dp.add_handler(CommandHandler("get_free", get_free))
    dp.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dp.add_handler(CommandHandler("get_w", get_w))
    dp.add_handler(CommandHandler("get_auths", get_auths))
    dp.add_handler(CommandHandler("get_critical", get_critical))
    dp.add_handler(CommandHandler("get_ps", get_ps))
    dp.add_handler(CommandHandler("get_ss", get_ss))
    dp.add_handler(CommandHandler("get_apt_list", get_apt_list))
    dp.add_handler(CommandHandler("get_services", get_services))
    dp.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dp.add_handler(CommandHandler("get_emails", get_emails))
    dp.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))

    # Обработчики диалогов для поиска email и телефонов
    email_conv = ConversationHandler(
        entry_points=[CommandHandler("find_email", find_email)],
        states={
            "FIND_EMAIL": [
                MessageHandler(Filters.text & ~Filters.command, process_email)
            ],
            "CONFIRM_SAVE": [
                MessageHandler(Filters.text & ~Filters.command, save_data)
            ],
        },
        fallbacks=[],
    )
    phone_conv = ConversationHandler(
        entry_points=[CommandHandler("find_phone_number", find_phone_number)],
        states={
            "FIND_PHONE": [
                MessageHandler(Filters.text & ~Filters.command, process_phone)
            ],
            "CONFIRM_SAVE": [
                MessageHandler(Filters.text & ~Filters.command, save_data)
            ],
        },
        fallbacks=[],
    )

    password_conv = ConversationHandler(
        entry_points=[CommandHandler("verify_password", verify_password)],
        states={
            "VERIFY_PASSWORD": [
                MessageHandler(Filters.text & ~Filters.command, process_password)
            ]
        },
        fallbacks=[],
    )

    save = ConversationHandler(
        entry_points=[],
        states={
            "CONFIRM_SAVE": [MessageHandler(Filters.text & ~Filters.command, save_data)]
        },
        fallbacks=[],
    )

    dp.add_handler(email_conv)
    dp.add_handler(phone_conv)
    dp.add_handler(password_conv)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
