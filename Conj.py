import random
import re
from Help_funs import (
    comp_answers,
    comp_conj_answers,
    shuffle_if_random,
    unique_everseen,
    quitOrInput,
    QuitException,
)
from Vars import getInst, printInst, inpInst
from Writing import writeTime, writeRecord


class Conj:
    """
    class Conj: Class for conjugations.
    """

    def __init__(self, s, comments="", meanings=""):
        s = s.rstrip()
        self.infinitive = s.split(": ")[0].split(" ** ")[0]
        self.infinitive_IPA = s.split(": ")[0].split(" ** ")[1]
        conjugations = ": ".join(s.split(": ")[1:]).split("; ")
        conjugations = [c.split(": ") for c in conjugations]
        self.tenses = [tense for tense, cons in conjugations]  # To reserve the order
        self.conjs = {
            tense: [
                (
                    oneform.split("+")[0],
                    "+".join(oneform.split("+")[1:]).split(" ** ")[0],
                    "+".join(oneform.split("+")[1:]).split(" ** ")[1],
                )
                for forms in cons.split(", ")
                for oneform in forms.split(" %% ")
            ]
            for tense, cons in conjugations
        }  # forms: ich begänne %% ich begönne, oneform: ich begänne;
        # "+".join(oneform.split("+")[1:]) because + might appear in the IPA as well
        for (
            key,
            value,
        ) in (
            self.conjs.items()
        ):  # Change [(ich, begänne, [IPA1]), (ich, begönne, [IPA2]), (du, begännest, [IPA3])]
            # -> [(ich, [begänne, begönne], [IPA1, IPA2]), (du, [begännest], [IPA3])]
            new_value = []
            for val in value:
                if new_value and new_value[-1][0] == val[0]:
                    new_value[-1][1].append(val[1])
                    new_value[-1][2].append(val[2])
                else:
                    new_value.append((val[0], [val[1]], [val[2]]))
            self.conjs[key] = new_value
        self.comments = comments
        self.meanings = meanings
        self.group = "0"  # Group/class of the verb
        if re.search(r" \([1-9]\)$", self.infinitive):  # abattre (3)
            self.group = (
                re.search(r" \([1-9]\)$", self.infinitive)
                .group(0)
                .replace(" (", "")
                .replace(")", "")
            )
            self.infinitive = re.sub(r" \([1-9]\)$", "", self.infinitive)

    def format(self, tenses=None):
        if tenses is None:
            tenses = self.tenses
        assert set(tenses).issubset(self.tenses)
        s = [
            getInst("infinitive", rep=[("SPACE", "")])
            + self.infinitive
            + " "
            + self.infinitive_IPA
        ]
        if self.group != "0":
            s[-1] += ", group " + self.group
        if self.meanings:
            s.append(self.meanings)
        for tense in tenses:
            s.append(
                tense
                + ": \n"
                + "\n".join(
                    [
                        con[0]
                        + " "
                        + " %% ".join([x[0] + " " + x[1] for x in zip(con[1], con[2])])
                        for con in self.conjs[tense]
                    ]
                )
            )
        if self.comments:
            s.append(getInst("comments") + self.comments)
        s = ("\n" + "*" * 40 + "\n").join(s)
        return s


def reciteconj(Dictionary, rnr, wordListAndNames, readFromRecord=False):
    """
    recite(readFromRecord):
    Let user choose the book and list and recite all the words in the word list.

    Parameters
    __________
    Dictionary: dictionary
    The dictionary to be recited

    rnr: list of two bools
    Random and Record

    wordListAndNames: list
    Word lists and name, the list that contains the book name and list numbers. None if quitted.

    readFromRecord: bool
    Whether read from record or not
    """
    rand, record = rnr
    # Initialize random and record
    if (
        wordListAndNames is None
    ):  # If the user quitted during the creation of dictionary, quit
        return
    wordList, name = wordListAndNames
    wordList = [
        word for word in wordList if word in Dictionary
    ]  # words from record might not be verbs
    difficultWords = []
    MaxTimes = 2
    quit = False
    numberofwords = len(wordList)
    all_tenses = unique_everseen(
        [t for cj in Dictionary.values() for t in cj.tenses]
    )  # All tenses available
    if len(all_tenses) == 0:  # No tenses available
        printInst("noTense")
        return
    user_input = [""]
    try:
        while not all(
            [
                any(comp_answers(subinp, x) for x in all_tenses + ["A", "ALL"])
                for subinp in user_input
            ]
        ):
            user_input = (
                inpInst("chooseTense", rep="(" + ", ".join(all_tenses) + ")")
                .replace(", ", ",")
                .split(",")
            )
    except QuitException:
        return
    if len(user_input) == 1 and user_input[0].upper() in ["A", "ALL"]:
        tenses = all_tenses
    else:
        tenses = list(
            set(
                filter(
                    lambda x: any([comp_answers(subinp, x) for subinp in user_input]),
                    all_tenses,
                )
            )
        )
    printInst("startReciteConj")
    printInst("startRecite2")
    print()
    if rand:
        random.shuffle(wordList)
    else:
        wordList = sorted(wordList)
    # printList = formatList(wordList)
    timeBegan = writeTime(begin=True)
    try:
        for wi, word in enumerate(wordList):
            print("{0}/{1}".format(wi + 1, numberofwords))
            con = Dictionary[word]
            for tense in shuffle_if_random(tenses, rand):
                print(" ".join([con.infinitive, con.infinitive_IPA, con.meanings]))
                for person, forms, IPA in shuffle_if_random(con.conjs[tense], rand):
                    person = re.sub(
                        "^j'", "je", re.sub("^qu'", "", re.sub(r"^que\s", "", person))
                    )
                    user_input = inpInst(
                        "conjInPersonForTense",
                        rep=(("REPLACE1", tense), ("REPLACE2", person)),
                    )
                    wrongtimes = 0
                    while (not comp_conj_answers(user_input, forms)) and (
                        wrongtimes < MaxTimes
                    ):  # Try again until being wrong for MaxTimes times
                        wrongtimes += 1
                        printInst("tryAgain")
                        if wrongtimes < MaxTimes:
                            user_input = quitOrInput()
                    if wrongtimes == MaxTimes:
                        difficultWords.append(word)
                        print(" %% ".join(IPA))  # Show IPA first
                        user_input = inpInst("tryAgain")
                        if not comp_conj_answers(
                            user_input, forms
                        ):  # If still incorrect, show descriptions
                            print(con.format([]))
                            print(
                                tense
                                + ": "
                                + " %% ".join(
                                    [
                                        person + " " + x[0] + " " + x[1]
                                        for x in zip(forms, IPA)
                                    ]
                                )
                            )
                            user_input = inpInst("tryAgain")
                        while not comp_conj_answers(
                            user_input, forms
                        ):  # Enter until correct
                            user_input = inpInst("tryAgain")
                    printInst("correct")
    except QuitException:
        quit = True
    if difficultWords:  # If there is any difficult word
        difficultWords = sorted(set(difficultWords))
        print(
            getInst("difficultWordList"),
            ", ".join(difficultWords)
            + ", "
            + getInst("wordsInTotal")
            + str(len(difficultWords))
            + getInst("wordsInTotal2"),
        )
        if not quit:
            try:
                _ = inpInst("reviewRecite")
                lenDifficultWords = len(difficultWords)
                for index, word in enumerate(difficultWords):
                    print(
                        getInst("word", rep=[("SPACE", "")])
                        + "\n"
                        + "%d/%d" % (index + 1, lenDifficultWords)
                    )
                    print(Dictionary[word].format())
                    _ = quitOrInput()
            except QuitException:
                pass
    elif not quit:
        printInst("congratulations")
    if record and not quit:
        writeRecord(difficultWords, "reciteconj", name)
    writeTime(
        begin=False,
        timeBegan=timeBegan,
        mode="recite conjugation mode with tenses %s, " % (" & ".join(tenses))
        + readFromRecord * "(from record) ",
        names=name,
    )
    return
