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
import Vars
from Writing import writeTime, writeRecord
from enum import Enum, auto
from typing import List, Optional, Union
import string
from Word import get_pronunciation

STARS = "\n" + "*" * 40 + "\n"


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
        s = [Vars.getInst("infinitive") + self.infinitive + " " + self.infinitive_IPA]
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
            s.append(Vars.getInst("comments") + self.comments)
        s = ("\n" + "*" * 40 + "\n").join(s)
        return s


class Entry:
    def __init__(self, conjugated, IPA=None, person=None):
        self.word = conjugated
        self.IPA = IPA
        self.person = person

    def __str__(self):
        s = self.word
        if self.person is not None:
            if self.person == "j'":
                s = self.person + s
            else:
                s = self.person + " " + s
        if self.IPA is not None:
            s += f" [{get_pronunciation(self.IPA)}]"
        return s


class Tense:
    def __init__(
        self,
        tense_name: str,
        forms: Union[str, List[str]],
        IPAs: Optional[Union[str, List[Optional[str]]]] = None,
        persons: Optional[Union[str, List[Optional[str]]]] = None,
        comments: Optional[str] = None,
    ):
        self.tense = tense_name
        if isinstance(forms, str):
            forms = [forms]

        if isinstance(IPAs, str):
            IPAs = [IPAs]
        if IPAs is not None:
            assert len(forms) == len(
                IPAs
            ), f"len(forms) = {len(forms)} != {len(IPAs)} = len(IPAs)"
        else:
            IPAs = [None] * len(forms)

        if isinstance(persons, str):
            persons = [persons]
        if persons is not None:
            assert len(forms) == len(
                persons
            ), f"len(forms) = {len(forms)} != {len(persons)} = len(persons)"
        else:
            persons = [None] * len(forms)
        self.entries = [Entry(*s) for s in zip(forms, IPAs, persons)]
        self.comments = comments

    def __str__(self):
        s = self.tense + ":\n" + "\n".join(str(e) for e in self.entries)
        if self.comments is not None:
            s += "\n" + Vars.getInst("comments") + self.comments
        return s


class ConjObj:
    def __init__(
        self,
        infinitive: str,
        infinitive_name: str,
        infinitive_IPA: Optional[str] = None,
        pos: Optional[str] = None,
        comments: Optional[str] = None,
    ):
        self.infinitive = Tense(infinitive_name, infinitive, infinitive_IPA)
        self.pos = pos
        self.tenses = []
        self.comments = comments

    def add(self, tense: Tense):
        assert isinstance(
            tense, Tense
        ), f"The tense argument in ConjObj.add() must be a Tense object. Got {type(tense)}."
        self.tenses.append(tense)

    def __str__(self):
        s = str(self.infinitive)
        if self.pos is not None:
            s += f" ({self.pos})"
        if self.comments is not None:
            s += "\n" + Vars.getInst("comments") + self.comments
        s += STARS + STARS.join(str(tense) for tense in self.tenses)
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
        Vars.printInst("noTense")
        return
    user_input = [""]
    try:
        while not all(
            [
                any(
                    comp_answers(subinp, x, Vars.parameters["IgnoreDiacritics"])
                    for x in all_tenses + ["A", "ALL"]
                )
                for subinp in user_input
            ]
        ):
            user_input = (
                Vars.inpInst("chooseTense", rep="(" + ", ".join(all_tenses) + ")")
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
                    lambda x: any(
                        [
                            comp_answers(subinp, x, Vars.parameters["IgnoreDiacritics"])
                            for subinp in user_input
                        ]
                    ),
                    all_tenses,
                )
            )
        )
    Vars.printInst("startReciteConj")
    Vars.printInst("startRecite2")
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
                    user_input = Vars.inpInst(
                        "conjInPersonForTense",
                        rep=(("REPLACE1", tense), ("REPLACE2", person)),
                    )
                    wrongtimes = 0
                    while (
                        not comp_conj_answers(
                            user_input, forms, Vars.parameters["IgnoreDiacritics"]
                        )
                    ) and (
                        wrongtimes < MaxTimes
                    ):  # Try again until being wrong for MaxTimes times
                        wrongtimes += 1
                        Vars.printInst("tryAgain")
                        if wrongtimes < MaxTimes:
                            user_input = quitOrInput()
                    if wrongtimes == MaxTimes:
                        difficultWords.append(word)
                        print(" %% ".join(IPA))  # Show IPA first
                        user_input = Vars.inpInst("tryAgain")
                        if not comp_conj_answers(
                            user_input, forms, Vars.parameters["IgnoreDiacritics"]
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
                            user_input = Vars.inpInst("tryAgain")
                        while not comp_conj_answers(
                            user_input, forms, Vars.parameters["IgnoreDiacritics"]
                        ):  # Enter until correct
                            user_input = Vars.inpInst("tryAgain")
                    Vars.printInst("correct")
    except QuitException:
        quit = True
    if difficultWords:  # If there is any difficult word
        difficultWords = sorted(set(difficultWords))
        print(
            Vars.getInst("difficultWordList"),
            ", ".join(difficultWords)
            + ", "
            + Vars.getInst("wordsInTotal")
            + str(len(difficultWords))
            + Vars.getInst("wordsInTotal2"),
        )
        if not quit:
            try:
                _ = Vars.inpInst("reviewRecite")
                lenDifficultWords = len(difficultWords)
                for index, word in enumerate(difficultWords):
                    print(
                        Vars.getInst("word")
                        + "\n"
                        + "%d/%d" % (index + 1, lenDifficultWords)
                    )
                    print(Dictionary[word].format())
                    _ = quitOrInput()
            except QuitException:
                pass
    elif not quit:
        Vars.printInst("congratulations")
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


class JaVerbTypes(Enum):
    五段 = auto()
    四段 = auto()
    上一段 = auto()
    上二段 = auto()
    下一段 = auto()
    下二段 = auto()
    カ変 = auto()
    サ変 = auto()
    ナ変 = auto()
    ラ変 = auto()


def kana_offset(char: str, offset: int) -> str:
    # Used for 五段 in modern and 四段/上二段/下二段 in classic
    kanas = [
        # No need as あ not used; everything else covered in わ
        # "あいうえお",
        "かきくけこ",
        "がぎぐげご",
        "さしすせそ",
        "ざじずぜぞ",
        "たちつてと",
        "だぢづでど",
        "なにぬねの",
        "はひふへほ",
        "ばびぶべぼ",
        "まみむめも",
        # Function not intended to move from char = い or え
        "やいゆえよ",
        "らりるれろ",
        "わいうえお",
        # "わゐうゑを",
        # No pa-gyo
    ]
    for row in kanas:
        if char in row:
            if 0 <= row.index(char) + offset < len(row):
                return row[row.index(char) + offset]
            else:
                raise ValueError(f"{char} + {offset} out of (row) range")
    raise NotImplementedError(f"{char} + {offset} not found")


def offset_ending(word: str, offset: int) -> str:
    return word[:-1] + kana_offset(word[-1], offset)


い段 = "いきぎしじちぢにひびみり"
う段 = "うくぐすずつづぬふぶむゆる"
え段 = "えけげせぜてでねへべめれ"


def ja_modern_verb_conj(verb: str, kana: str, v_type: JaVerbTypes, conj: ConjObj):
    if not verb or not kana:
        raise ValueError("Empty verb or kana given.")
    if verb[-1] not in う段 or kana[-1] not in う段:
        raise ValueError(f"Verb/kana must both be in 終止形. {verb}/{kana} given.")
    if v_type == JaVerbTypes.五段:
        未然 = offset_ending(verb, -2)
        未然かな = offset_ending(kana, -2)
        conj.add(Tense("未然（〜ず）", 未然 + "ず", 未然かな + "ず"))
        conj.add(Tense("未然（〜ない）", 未然 + "ない", 未然かな + "ない"))
        conj.add(Tense("未然・受身", 未然 + "れる", 未然かな + "れる"))
        conj.add(Tense("未然・使役", 未然 + "せる", 未然かな + "せる"))
        ます = offset_ending(verb, -1)
        ますかな = offset_ending(kana, -1)
        if verb in ["いく", "ゆく", "行く", "逝く", "往く"] or verb[-1] in "うつる":
            suffix = "って"
        elif verb[-1] in "ぬぶむ":
            suffix = "んで"
        elif verb[-1] in "く":
            suffix = "いて"
        elif verb[-1] in "ぐ":
            suffix = "いで"
        elif verb[-1] in "す":
            suffix = "して"
        else:
            raise ValueError(verb)
        て = verb[:-1] + suffix
        てかな = kana[:-1] + suffix
        conj.add(Tense("連用（〜ます）", ます + "ます", ますかな + "ます"))
        conj.add(Tense("連用（〜て）", て, てかな))
        conj.add(Tense("連体", verb, kana))
        仮定 = offset_ending(verb, 1)
        仮定かな = offset_ending(kana, 1)
        conj.add(Tense("仮定・命令", 仮定, 仮定かな))
        conj.add(Tense("仮定・条件", 仮定 + "ば", 仮定かな + "ば"))
        conj.add(Tense("仮定・可能", 仮定 + "る", 仮定かな + "る"))
        conj.add(
            Tense(
                "未然・意向",
                offset_ending(verb, 2) + "う",
                offset_ending(kana, 2) + "う",
            )
        )
    elif v_type in [JaVerbTypes.上一段, JaVerbTypes.下一段]:
        assert len(verb) >= 2 and len(kana) >= 2 and verb[-1] == kana[-1] == "る"
        if v_type == JaVerbTypes.上一段:
            assert kana[-2] in い段, f"Double check if {verb} belongs to {v_type.name}"
        else:
            assert kana[-2] in え段, f"Double check if {verb} belongs to {v_type.name}"
        stem = verb[:-1]
        kana_stem = kana[:-1]
        conj.add(Tense("未然（〜ず）", stem + "ず", kana_stem + "ず"))
        conj.add(Tense("未然（〜ない）", stem + "ない", kana_stem + "ない"))
        conj.add(Tense("未然・受身", stem + "られる", kana_stem + "られる"))
        conj.add(Tense("未然・使役", stem + "させる", kana_stem + "させる"))
        conj.add(Tense("連用（〜ます）", stem + "ます", kana_stem + "ます"))
        conj.add(Tense("連用（〜て）", stem + "て", kana_stem + "て"))
        conj.add(Tense("連体", verb, kana))
        conj.add(Tense("仮定・命令（ろ）", stem + "ろ", kana_stem + "ろ"))
        conj.add(Tense("仮定・命令（よ）", stem + "よ", kana_stem + "よ"))
        conj.add(Tense("仮定・条件", stem + "れば", kana_stem + "れば"))
        conj.add(Tense("仮定・可能", stem + "られる", kana_stem + "られる"))
        conj.add(Tense("未然・意向", stem + "よう", kana_stem + "よう"))
    elif v_type == JaVerbTypes.カ変:
        assert (
            verb == "来る" and kana == "くる"
        ), f"カ変 can only be 来る/くる. Got {verb}/{kana}."
        conj.add(Tense("未然（〜ず）", "来ず", "こず"))
        conj.add(Tense("未然（〜ない）", "来ない", "こない"))
        conj.add(Tense("未然・受身", "来られる", "こられる"))
        conj.add(Tense("未然・使役", "来させる", "こさせる"))
        conj.add(Tense("連用（〜ます）", "来ます", "きます"))
        conj.add(Tense("連用（〜て）", "来て", "きて"))
        conj.add(Tense("連体", verb, kana))
        conj.add(Tense("仮定・命令", "来い", "こい"))
        conj.add(Tense("仮定・条件", "来れば", "くれば"))
        conj.add(Tense("仮定・可能", "来られる", "こられる"))
        conj.add(Tense("未然・意向", "来よう", "こよう"))
    elif v_type == JaVerbTypes.サ変:
        assert (
            verb.endswith("する") or verb.endswith("ずる") or verb == "為る"
        ), f"サ変 ends in する/ずる. Got {verb}."
        stem = verb[:-2]
        kana_stem = kana[:-2]
        is_zu = kana[-2] == "ず"
        is_ai = verb == "愛する"
        し = "じ" if is_zu else "し"
        せ = "ぜ" if is_zu else "せ"
        if is_ai:
            conj.add(Tense("未然（〜ず）", stem + "さず", kana_stem + "さず"))
            conj.add(Tense("未然（〜ない）", stem + "さない", kana_stem + "さない"))
        else:
            conj.add(Tense("未然（〜ず）", stem + せ + "ず", kana_stem + せ + "ず"))
            conj.add(Tense("未然（〜ない）", stem + し + "ない", kana_stem + し + "ない"))
        if is_zu:
            conj.add(Tense("未然・受身1", stem + "じられる", kana_stem + "じられる"))
            conj.add(Tense("未然・受身2", stem + "ぜられる", kana_stem + "ぜられる"))
            conj.add(Tense("未然・使役", stem + "じさせる", kana_stem + "じさせる"))
        else:
            conj.add(Tense("未然・受身", stem + "される", kana_stem + "される"))
            conj.add(Tense("未然・使役", stem + "させる", kana_stem + "させる"))
        conj.add(Tense("連用（〜ます）", stem + し + "ます", kana_stem + し + "ます"))
        conj.add(Tense("連用（〜て）", stem + し + "て", kana_stem + し + "て"))
        conj.add(Tense("連体", verb if verb != "為る" else "する", kana))
        if is_ai:
            conj.add(Tense("仮定・命令", stem + "せ", kana_stem + "せ"))
            conj.add(Tense("仮定・条件", stem + "せば", kana_stem + "せば"))
            conj.add(Tense("仮定・可能", stem + "せる", kana_stem + "せる"))
            conj.add(Tense("未然・意向", stem + "そう", kana_stem + "そう"))
        else:
            conj.add(Tense("仮定・命令（ろ）", stem + し + "ろ", kana_stem + し + "ろ"))
            conj.add(Tense("仮定・命令（よ）", stem + せ + "よ", kana_stem + せ + "よ"))
            conj.add(Tense("仮定・条件", stem + kana[-2] + "れば", kana_stem + kana[-2] + "れば"))
            if is_zu:
                conj.add(Tense("仮定・可能1", stem + "じられる", kana_stem + "じられる"))
                conj.add(Tense("仮定・可能2", stem + "ぜられる", kana_stem + "ぜられる"))
            else:
                conj.add(Tense("仮定・可能", stem + "できる", kana_stem + "できる"))
            conj.add(Tense("未然・意向", stem + し + "よう", kana_stem + し + "よう"))
    else:
        raise ValueError(f"Invalid verb type {v_type}")
    return conj

# print(ja_conj("言う", "いう0", "動五", True))
# print(ja_conj("行く", "いく0", "動五", True))
# print(ja_conj("起きる", "おきる2", "動上一", True))
# print(ja_conj("経る", "へる1", "動下一", True))
# print(ja_conj("論じる", "ろんじる0", "動上一", True))
# print(ja_conj("来る", "くる1", "動カ変", True))
# print(ja_conj("為る", "する0", "動サ変", True))
# print(ja_conj("看病する", "かんびょうする1", "動サ変", True))
# print(ja_conj("論ずる", "ろんずる3", "動サ変", True))
# print(ja_conj("愛する", "あいする3", "動サ変", True))


def ja_classic_verb_conj(verb, kana, v_type, conj):
    raise NotImplementedError


def ja_conj(word, kana, pos, modern):
    if "動" in pos:
        v_type = None
        if modern and "五" in pos:
            v_type = JaVerbTypes.五段
        elif "上一" in pos:
            v_type = JaVerbTypes.上一段
        elif "下一" in pos:
            v_type = JaVerbTypes.下一段
        elif "カ" in pos:
            v_type = JaVerbTypes.カ変
        elif "サ" in pos:
            v_type = JaVerbTypes.サ変
        elif not modern:
            if "四" in pos:
                v_type = JaVerbTypes.四段
            elif "ナ変" in pos:
                v_type = JaVerbTypes.ナ変
            elif "ラ変" in pos:
                v_type = JaVerbTypes.ラ変
            elif "上二" in pos:
                v_type = JaVerbTypes.上二段
            elif "下二" in pos:
                v_type = JaVerbTypes.下二段
        if v_type is None:
            raise ValueError(f"Invalid pos {pos}.")
        conj = ConjObj(word, "終止", kana, pos)
        # The accents are no longer valid
        kana = kana.rstrip(string.digits)
        if modern:
            return ja_modern_verb_conj(word, kana, v_type, conj)
        return ja_classic_verb_conj(word, kana, v_type, conj)
    raise NotImplementedError
