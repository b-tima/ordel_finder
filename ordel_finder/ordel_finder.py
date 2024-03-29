import random
import requests
import time
import regex as re
from typing import Callable
import smtplib
import datetime
import os
from email import message

SWE_ALPH = "abcdefghijklmnopqrstuvwxyzåäö"


class InvalidWordException(Exception):
    pass


class WordNotFoundException(Exception):
    pass


class NotWorthTheEffortException(Exception):
    pass


class WordFound(Exception):
    def __init__(self, word):
        self.word = word


def delete_all_except_condition(list_p: list[str], condition: Callable[[str], bool]):
    new_list = []
    for word in list_p:
        if condition(word):
            new_list.append(word)
    return new_list


class WordReducer:
    def __init__(self, dictionary):
        self.__words = dictionary
        self.__known = [None] * 5
        self.__found_letter = {}
        self.__bad_letters = []

    def make_random_attempt(self):
        self.__check_effort()
        response = []
        while True:
            if not self.__words:
                raise WordNotFoundException()
            index = random.randint(0, len(self.__words) - 1)
            word = self.__words[index]
            self.__words.remove(word)
            try:
                response = self.__ask_if_correct(word)
                if all(i == 1 for i in response):
                    raise WordFound(word)
                break
            except InvalidWordException:
                pass
        self.__reduce_words(word, response)
        return word, response

    def expand_words_unconstrained(self):
        swe_alph_left = [l for l in SWE_ALPH if l not in self.__bad_letters]
        letter_cols = []
        banned_letters = []

        # Step 1: Generate all possible search lists
        for i in range(5):
            if self.__known[i]:
                letter_cols.append([self.__known[i]])
                banned_letters.append(None)
            else:
                letter_cols.append(swe_alph_left)

        # Step 2: Generate all combinations of letters
        def comb(i):
            if i == 5:
                return [""]
            results = []
            for l in letter_cols[i]:
                other_results = comb(i + 1)
                for ll in other_results:
                    results.append(l + ll)
            return results

        self.__words = comb(0)

    def __check_effort(self):
        # Approximate effort to find the word
        if len(self.__words) * 0.4 > 3600 * 60 * 12:
            raise NotWorthTheEffortException()

    def __reduce_words(self, word, response):
        for i, valid in enumerate(response):
            if valid == 1:
                self.__correct_letter_and_position(word, i)
            elif valid == 0:
                self.__correct_letter_wrong_position(word, i)
            elif valid == -1:
                self.__letter_not_in_word(word, i, response)

    def __correct_letter_and_position(self, word, index):
        if not self.__known[index]:
            self.__words = delete_all_except_condition(
                self.__words, lambda x: x[index] == word[index]
            )
            self.__known[index] = word[index]

    def __correct_letter_wrong_position(self, word, index):
        self.__words = delete_all_except_condition(
            self.__words, lambda x: word[index] in x and x[index] != word[index]
        )
        if word[index] not in self.__found_letter:
            self.__found_letter[word[index]] = [index]
        else:
            if index not in self.__found_letter[word[index]]:
                self.__found_letter[word[index]].append(index)

    def __letter_not_in_word(self, word, index, response):
        if word[index] not in self.__bad_letters:
            self.__bad_letters.append(word[index])
        count = 0
        for j in range(5):
            if word[index] == word[j] and response[j] == -1:
                count += 1
        if count > 1:
            self.__words = delete_all_except_condition(
                self.__words, lambda x: word[index] not in x
            )

    def __ask_if_correct(self, word):
        r = requests.get("http://ordel.se/play?n=0&guess={}".format(word))
        response = r.json()
        if "error" in response:
            raise InvalidWordException()
        elif "letters" in response:
            return response["letters"]


def read_swe() -> list[str]:
    dic_file = open("sv_SE.dic", "rb").read()
    dic = dic_file.decode("utf-8").split("\n")
    dic_formatted = [line.split("/")[0] for line in dic]
    dic_valid_length = [line for line in dic_formatted if len(line) == 5]
    dic_valid_chars = [
        line for line in dic_valid_length if not re.search("[0-9]", line)
    ]
    dic_lower_case = [line.lower() for line in dic_valid_chars]
    dic_no_repeat = list(dict.fromkeys(dic_lower_case))
    return dic_no_repeat


def send_email(
    word, attempts, attempted_words, responses=[], error=False, no_effort=False
):
    gmail_sender = os.getenv("GMAIL_SENDER")
    gmail_receiver = os.getenv("GMAIL_RECEIVER")
    gmail_password = os.getenv("GMAIL_PASSWORD")

    sent_from = gmail_sender
    to = gmail_receiver
    subject = "Ordel word of the day {}".format(
        datetime.datetime.now().strftime("%Y-%m-%d")
    )
    if no_effort:
        body = "The worst case computation of the word is more than 12 hours, so no attempts to solve to word will be made.\n\nPlease speak to the host of the ordel finder for more information"
    else:
        body = (
            "The word today is: {}.\n\nIt took {} attempts. The following attempts were made before getting the correct word:".format(
                word, attempts
            )
            if not error
            else 'Unable to find todays word by looking in the dictionary. The word was found to be "{}" from brute force. The following attempts were made:'.format(
                word
            )
        )
        for i, word in enumerate(attempted_words[:-1]):
            body += "\n\t{}. {} {}".format(
                i + 1, word, responses[i] if responses else ""
            )

    m = message.Message()
    m.add_header("from", sent_from)
    m.add_header("to", to)
    m.add_header("subject", subject)
    m.set_payload(body, charset="UTF-8")

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(gmail_sender, gmail_password)
        server.sendmail(sent_from, to, m.as_string())
        server.close()
    except Exception as e:
        print(e)
        print("Error sending email", flush=True)


def ordel_finder():
    words = read_swe()
    attempted_words = []
    attempted_responses = []
    word_reducer = WordReducer(words)
    brute_force = False

    try:
        while True:
            try:
                word, response = word_reducer.make_random_attempt()
            except WordNotFoundException:
                print(
                    "Todays word was not found in dictionary.\nGenerating random constrained words",
                    flush=True,
                )
                brute_force = True
                word_reducer.expand_words_unconstrained()
                continue
            print("{}\t{}".format(word, response), flush=True)
            attempted_words.append(word)
            attempted_responses.append(response)
    except WordFound as e:
        print("Word is: {}".format(e.word), flush=True)

        if os.getenv("ENABLE_EMAIL") == "1":
            if not brute_force:
                send_email(e.word, len(attempted_words), attempted_words)
            else:
                send_email(
                    e.word,
                    len(attempted_words),
                    attempted_words,
                    attempted_responses,
                    error=True,
                )
    except NotWorthTheEffortException:
        if os.getenv("ENABLE_EMAIL") == "1":
            send_email(
                None,
                len(attempted_words),
                attempted_words,
                attempted_responses,
                error=True,
                no_effort=True,
            )
