import random
import requests
import time
import regex as re
from typing import Callable
import smtplib
import datetime
import os
from email import message


class InvalidWordException(Exception):
    pass


def read_swe() -> list[str]:
    dic_file = open("sv_SE.dic", "rb").read()
    dic = dic_file.decode("utf-8").split("\n")
    dic_formatted = [line.split("/")[0] for line in dic]
    dic_valid_length = [line for line in dic_formatted if len(line) == 5]
    dic_valid_chars = [
        line for line in dic_valid_length if not re.search("[0-9]", line)
    ]
    dic_lower_case = [line.lower() for line in dic_valid_chars]
    return dic_lower_case


def ask_if_correct(word):
    start_time = time.time()
    r = requests.get("http://ordel.se/play?n=0&guess={}".format(word))
    elapsed_time = time.time() - start_time
    response = r.json()
    if "error" in response:
        if response["error"] == "INVALID_WORD":
            raise InvalidWordException()
    elif "letters" in response:
        return response["letters"], elapsed_time


def delete_all_except_condition(list_p: list[str], condition: Callable[[str], bool]):
    new_list = []
    for word in list_p:
        if condition(word):
            new_list.append(word)
    return new_list


def send_email(word):
    gmail_user = "mogge.ordel@gmail.com"
    gmail_password = os.getenv("GMAIL_PASSWORD")

    sent_from = "mogge.ordel@gmail.com"
    to = "morgan.a9904@gmail.com"
    subject = "Ordel word of the day {}".format(
        datetime.datetime.now().strftime("%Y-%m-%d")
    )
    body = "The word today is: {}".format(word)

    m = message.Message()
    m.add_header("from", sent_from)
    m.add_header("to", to)
    m.add_header("subject", subject)
    m.set_payload(body)

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, m.as_string())
        server.close()
    except Exception as e:
        print(e)
        print("Error sending email")


def ordel_finder():
    words = read_swe()
    known = [False] * 5
    found_letters = []
    try:
        while len(words) > 1:
            index = random.randint(0, len(words) - 1)
            word = words[index]
            try:
                response, sleep_time = ask_if_correct(word)
                for i, valid in enumerate(response):
                    if valid == 1 and not known[i]:
                        words = delete_all_except_condition(
                            words, lambda x: x[i] == word[i]
                        )
                        index = 0
                        known[i] = True
                    elif valid == 0 and word[i] not in found_letters:
                        words = delete_all_except_condition(
                            words, lambda x: word[i] in x
                        )
                        index = 0
                        found_letters.append(word[i])
                time.sleep(sleep_time * 1.5)
            except InvalidWordException:
                pass
    except IndexError:
        print("Word is: {}".format(words[0]))

    # send_email(words[0])
