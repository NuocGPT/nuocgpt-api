import re
from datetime import datetime
from typing import Tuple

from ai.core.message_shortener import shorten_message
from ai.schemas.schemas import QARequest
from fastapi import HTTPException


def preprocess_suggestion_request(request_body: QARequest):
    messages = request_body.messages
    language = request_body.language
    metadata = request_body.metadata

    if len(messages):
        chat_history, question, previous_response = preprocess_chat_history(messages)
    else:
        raise HTTPException(status_code=400, detail="message is missing")

    match = re.search(
        "([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])$|^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\.|-|/)([1-9]|0[1-9]|1[0-2])(\.|-|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])",
        question,
    )

    if match:
        date = match.group()

        question = question.replace(
            date,
            str(int(datetime.timestamp(datetime.strptime(date, "%d/%m/%Y")))),
        )

    return {
        "question": question,
        "chat_history": chat_history,
        "previous_response": previous_response,
        "metadata": metadata,
        "language": language,
    }


def preprocess_chat_history(
    chat_history: list,
    max_words_each_message: int = 800,
    max_recent_chat_history: int = 30,
) -> Tuple[list, str, str]:
    new_chat_history = []
    question = ""
    previous_response = ""

    if len(chat_history) > max_recent_chat_history:
        chat_history = chat_history[-max_recent_chat_history:]

    if len(chat_history):
        current_item = None

        for item in chat_history:
            if current_item is None or item["role"] != current_item["role"]:
                if current_item is not None:
                    new_chat_history.append(current_item)
                current_item = {
                    "role": item["role"],
                    "content": item["content"].strip(),
                }
            else:
                current_item["content"] += "\n " + item["content"].strip()

        if current_item is not None:
            # Normalize the message string
            current_item["content"] = (
                current_item["content"].replace("\xa0", " ").replace("\\xa0", " ")
            )

            # Shorten message if it is too long
            content_word_len = len(re.findall(r"\w+", current_item["content"]))
            if content_word_len > max_words_each_message:
                current_item["content"] = shorten_message(
                    current_item["content"], max_words_each_message
                )

            new_chat_history.append(current_item)

    if new_chat_history[-1]["role"] == "user":
        question = new_chat_history[-1]["content"]
    else:
        if len(new_chat_history) == 1:
            question = new_chat_history[-1]["content"]
            del new_chat_history[-1]
        elif len(new_chat_history) > 1:
            previous_response = new_chat_history[-1]["content"]
            question = new_chat_history[-2]["content"]
            del new_chat_history[-1]

    chat_history = []

    if len(new_chat_history):
        index = 0
        start_role = new_chat_history[0]["role"]
        if start_role == "assistant":
            chat_history.append(("", new_chat_history[0]["content"]))
            index += 1

        while index < len(new_chat_history) - 1:
            if new_chat_history[index]["role"] == "user":
                chat_history.append(
                    (
                        new_chat_history[index]["content"],
                        new_chat_history[index + 1]["content"],
                    )
                )
            index += 2

    if question:
        question = list(question)
        question[0] = question[0].upper()
        question = "".join(question)

    return chat_history, question, previous_response


def check_hello(message):
    lower_message = message.lower()
    question_words = [
        "who",
        "what",
        "when",
        "where",
        "why",
        "how",
        "is",
        "are",
        "can",
        "could",
        "do",
        "does",
        "did",
        "will",
        "would",
        "should",
        "may",
        "might",
    ]

    hello_words = [
        "hello",
        "hi",
        "xin chao",
        "chào",
    ]

    thank_words = ["thank", "thanks", "cám ơn", "cảm ơn", "cam on"]

    if any(
        hello_word in lower_message.split(" ") for hello_word in hello_words
    ) and not any(thank_word in lower_message for thank_word in thank_words):
        if not lower_message.endswith("?"):
            if not any(lower_message.startswith(word) for word in question_words):
                return True

    return False


def check_goodbye(message):
    lower_message = message.lower()
    question_words = [
        "who",
        "what",
        "when",
        "where",
        "why",
        "how",
        "is",
        "are",
        "can",
        "could",
        "do",
        "does",
        "did",
        "will",
        "would",
        "should",
        "may",
        "might",
    ]

    hello_words = [
        "xin chao",
        "chào",
    ]

    thank_words = ["thank", "thanks", "cám ơn", "cảm ơn", "cam on"]

    bye_words = ["goodbye", "bye", "tạm biệt"]

    if (
        any(hello_word in lower_message.split(" ") for hello_word in hello_words)
        and any(thank_word in lower_message for thank_word in thank_words)
    ) or (any(bye_word in lower_message for bye_word in bye_words)):
        if not lower_message.endswith("?"):
            if not any(lower_message.startswith(word) for word in question_words):
                return True

    return False
