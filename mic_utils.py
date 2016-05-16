from random import choice
import re

DENY_WORDS = ["no", "nope", "not now", "deny"]
CONFIRM_WORDS = ["yes", "yeah", "yup", "ok", "okay", "al(l\s)?right(y)?", "(sounds\s)?good", "check", "cool", "confirm",
                 "affirm"]
CANCEL_WORDS = ["never(\s)?mind", "cancel"]
REPEAT_WORDS = ["repeat", "again", "what was that"]

DENY = re.compile(r"\b(%s)\b" % "|".join(DENY_WORDS), re.IGNORECASE)
CONFIRM = re.compile(r"\b(%s)\b" % "|".join(CONFIRM_WORDS), re.IGNORECASE)
CANCEL = re.compile(r"\b(%s)\b" % "|".join(CANCEL_WORDS), re.IGNORECASE)
REPEAT = re.compile(r"\b(%s)\b" % "|".join(REPEAT_WORDS), re.IGNORECASE)

NOT_UNDERSTOOD = ["I couldn't get that.", "What was that?"]


class MicUtils():
    def __init__(self, mic):
        self.question_retry_limit = 3
        self.mic = mic
        self.lastThingJasperSaid = ""
        self.lastThingUserSaid = ""

    def passiveListen(self, PERSONA):
        return self.mic.passiveListen(PERSONA)

    def say(self, phrase, OPTIONS=" -vdefault+m3 -p 40 -s 160 --stdout > say.wav", remember=True):
        if remember:
            self.lastThingJasperSaid = phrase
        if type(phrase) is list:
            something=None
            for words in phrase:
                something = self.mic.say(words, OPTIONS)
            return something
        else:
            return self.mic.say(phrase, OPTIONS)

    def activeListen(self, THRESHOLD=None, LISTEN=True, MUSIC=False):
        input = self.mic.activeListen(THRESHOLD, LISTEN, MUSIC)
        if input and bool(REPEAT.search(input)):
            self.sayLesser(self.lastThingJasperSaid)
            input = self.activeListen(THRESHOLD, LISTEN, MUSIC)
        if input:
            self.lastThingUserSaid = input
        return input

    def ask(self, question, ask_again=True):
        self.sayLesser(question)
        try_index = 1
        response = self.activeListen()
        while not response and ask_again:
            if try_index > self.question_retry_limit:
                return ""
            self.sayLesser(choice(NOT_UNDERSTOOD))
            response = self.activeListen()
            try_index += 1
        return response

    def sayLesser(self, phrase):
        return self.say(phrase, remember=False)

    def checkForCancel(self):
        return bool(CANCEL.search(self.lastThingUserSaid))

    def checkForConfirm(self):
        return bool(CONFIRM.search(self.lastThingUserSaid))

    def checkForDeny(self):
        return bool(DENY.search(self.lastThingUserSaid))
