# -*- coding: utf-8 -*-


import os
import codecs
import collections
import shutil
import inspect

pathToVocab = "/Users/shimizumasami/Desktop/\xe6\xb8\x85\xe6\xb0\xb4\xe6\xad\xa3\xe5\xb7\xb3\xe3\x81\xae\xe3\x83\x95\xe3\x82\xa9\xe3\x83\xab\xe3\x82\xbf\xe3\x82\x99/\xe5\x80\x8b\xe4\xba\xba\xe7\x94\xa8/\xe5\x8b\x89\xe5\xbc\xb7/@Umich/GRE/Vocabulary/Vocabulary/"


def printNames():
    Ass = __import__(inspect.getmodulename(__file__))
    for name in dir(Ass):
        obj = getattr(Ass, name)
        if inspect.isfunction(obj):
            print(obj.__name__)
    return


def isInt(s):
    """
    isInt(s):
    Returns True if s can be converted to int, or False otherwise

    Parameters
    __________
    s: string
    """
    try:
        int(s)
        return True
    except ValueError:
        return False


def number(i):
    """ """
    f = open(
        pathToVocab + "Word list with no meaning/Petit Livre Rouge/" + str(i) + ".txt"
    )
    j = 0
    for s in f:
        if (s != "\n") & (not isInt(s.rstrip("\n"))):
            j += 1
    f.close()
    return j


def printNumber():
    sum = 0
    for i in range(1, 43):
        numberi = number(i)
        print("{0}: {1}".format(i, numberi))
        sum += numberi
    print("\nTotal: {0}".format(sum))
    return


def addWordListToJap(i):
    """
    Adds word list to the top of the txt file I typed in
    """
    f = open(
        pathToVocab + "Word list with no meaning/Petit Livre Rouge/" + str(i) + ".txt"
    )
    wordlist = []
    words = []
    for s in f:
        words.append(s)
        if "**" in s:
            wordlist.append(s.rstrip("\n").split("**")[0].replace(" ", ""))
    f.close()
    g = open(
        pathToVocab
        + "Word list with no meaning/Petit Livre Rouge/"
        + str(i)
        + " 2.txt",
        "w",
    )
    g.write(" || ".join(wordlist) + "\n" + "".join(words))
    g.close()
    return


def addWordListToChi(i):
    f = open(
        pathToVocab + "Word list with no meaning/Petit Livre Rouge/" + str(i) + " 2.txt"
    )
    wordlist = f.readline()
    gcn = codecs.open(
        pathToVocab
        + "Word lists/Petit Livre Rouge/Other/2 After adding page number before adding word list/"
        + str(i)
        + " zh-cn.txt",
        "r",
        "utf-16",
    )
    hcn = codecs.open(
        pathToVocab + "Word lists/Petit Livre Rouge/" + str(i) + " zh-cn.txt",
        "w",
        "utf-16",
    )
    ghk = codecs.open(
        pathToVocab
        + "Word lists/Petit Livre Rouge/Other/2 After adding page number before adding word list/"
        + str(i)
        + " zh-hk.txt",
        "r",
        "utf-16",
    )
    hhk = codecs.open(
        pathToVocab + "Word lists/Petit Livre Rouge/" + str(i) + " zh-hk.txt",
        "w",
        "utf-16",
    )
    hcn.write(wordlist)
    hhk.write(wordlist)
    for s in gcn:
        hcn.write(s)
    for s in ghk:
        hhk.write(s)
    return


def formatting(i):
    """
    Swaps '\t' with ' ** N/A ** ' in the raw vocabulary list taken from the excel (txt, utf-16)
    """
    f = codecs.open(
        pathToVocab
        + "Word lists/Petit Livre Rouge/0 Unformatted Chinese/"
        + str(i)
        + " zh-cn.txt",
        "r",
        "utf-16",
    )
    g = codecs.open(
        pathToVocab + "Word lists/Petit Livre Rouge/" + str(i) + " zh-cn.txt",
        "w",
        "utf-16",
    )
    for s in f:
        g.write(" ** N/A ** ".join(s.split("\t")))
    f.close()
    g.close()
    return


def unifyWordList(i):
    """
    Compares the Chinese raw list and the word list I typed and prints discrepancies
    """
    f = codecs.open(
        pathToVocab + "Word lists/Petit Livre Rouge/" + str(i) + " zh-cn.txt",
        "r",
        "utf-16",
    )
    g = codecs.open(
        pathToVocab + "Word list with no meaning/Petit Livre Rouge/" + str(i) + ".txt",
        "r",
        "utf-8",
    )
    wordsf = []
    wordsg = []
    for s in f:
        if (not isInt(s.rstrip("\n").rstrip(" "))) & (s != "\n") & (not ("||" in s)):
            wordsf.append(s.split(" ** ")[0].rstrip(" "))
    for s in g:
        if (not isInt(s.rstrip("\n").rstrip("\r").rstrip(" "))) & (s != "\n"):
            # '\r' because List 13 was typed in Windows
            wordsg.append(s.rstrip("\n").rstrip("\r").split(" **")[0].rstrip(" "))
    for word in wordsf:
        if word not in wordsg:
            print("{0} in Chinese but not in my word list.".format(word))
    if set(wordsf) != set(wordsg):
        print()
    for word in wordsg:
        if word not in wordsf:
            print("{0} in my word list but not in Chinese.".format(word))
    countf = collections.Counter(wordsf)
    countg = collections.Counter(wordsg)
    dupwordsinf = [word for word in countf if countf[word] > 1]
    dupwordsing = [word for word in countg if countg[word] > 1]
    if len(dupwordsinf) != 0:
        print("Duplicate words in Chinese:")
        print(dupwordsinf)
        print()
    if len(dupwordsing) != 0:
        print("Duplicate words in my list:")
        print(dupwordsing)
        print()
    if len(wordsf) != len(wordsg):
        print(
            "{0} words in Chinese but {1} words in my word list.".format(
                len(wordsf), len(wordsg)
            )
        )
    return


def copyAndChangeNameToHK(i):
    shutil.copy(
        pathToVocab + "Word lists/Petit Livre Rouge/" + str(i) + " zh-cn.txt",
        pathToVocab + "Word lists/Petit Livre Rouge/" + str(i) + " zh-hk.txt",
    )
    return


def addPageNumber(i):
    f = codecs.open(
        pathToVocab + "Word lists/Petit Livre Rouge/" + str(i) + " zh-cn.txt",
        "r",
        "utf-16",
    )
    g = codecs.open(
        pathToVocab + "Word list with no meaning/Petit Livre Rouge/" + str(i) + ".txt",
        "r",
        "utf-8",
    )
    toPrint = []
    sg = g.readline()
    while True:
        if sg == "":
            break
        elif (sg == "\n") | (sg == "\r"):
            toPrint.append("")
            sg = g.readline()
        elif isInt(sg.rstrip("\n").rstrip("\r")):
            toPrint.append(sg.rstrip("\n").rstrip("\r"))
            sg = g.readline()
        else:
            sf = f.readline()
            if sf.split(" **")[0] != sg.split("**")[0].rstrip(" ").rstrip("\n").rstrip(
                "\r"
            ):
                print(sf.split(" **")[0])
                print(sg.split("**")[0].rstrip(" ").rstrip("\n").rstrip("\r"))
                break
            else:
                toPrint.append(sf.rstrip("\n"))
                sg = g.readline()
    f.close()
    g.close()
    f = codecs.open(
        pathToVocab + "Word lists/Petit Livre Rouge/" + str(i) + " zh-cn.txt",
        "w",
        "utf-16",
    )
    f.write("\n".join(toPrint))
    return


def formatPOS(i):
    """
    Formats the part of speech and split the meanings by recognizing semicolons
    """
    files = [" zh-cn.txt", " zh-hk.txt"]
    for file in files:
        f = codecs.open(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/3 After adding word list before formatting part of speech and splitting meanings/"
            + str(i)
            + file,
            "r",
            "utf-16",
        )
        g = codecs.open(
            pathToVocab + "Word lists/Petit Livre Rouge/" + str(i) + file, "w", "utf-16"
        )
        pos = ["n.", "v.", "adj.", "adverb."]
        for s in f:
            s = (
                s.rstrip("\n")
                .rstrip("\r")
                .replace("&", "/")
                .replace("；", ";")
                .replace("  ", " ")
            )
            if (s == "") | isInt(s):
                g.write(s + "\n")
                continue
            posins = []  # Parts of speech in s
            posins2 = []
            ssplit = s.split("**")
            meanings = ssplit[len(ssplit) - 1]
            meanings = meanings.replace("a.", "adj.")
            meanings = meanings.replace("adv.", "adverb.")
            for p in pos:
                if p in meanings:
                    posins.append(p)
                    meanings = meanings.replace(p, p + " ")
            if len(posins) > 1:
                meaning = meanings
                while posins != []:
                    p = posins[0]
                    first = True
                    if posins.remove(p) == []:
                        posins2.append(p)
                        break
                    for q in posins:  # p removed
                        if q in meanings.split(p)[0]:
                            first = False
                            break
                    if first:
                        posins2.append(p)
                        meaning.replace(p, "")
                    else:
                        posins.append(p)
                posins = posins2
            meaningsbypos = []  # List of meanings seperated by pos
            for j in range(1, len(posins)):
                if " " + posins[j] in meanings:
                    meanings = meanings.replace(" " + posins[j], posins[j])
                if not "；" + posins[j] in meanings:
                    meanings = meanings.replace(posins[j], ";" + posins[j])
                previousmeaning = meanings.split(";" + posins[j])[0].rstrip(
                    ";"
                )  # The meaning with the previous pos # strip ";" because for example in list 22 "vest" has "；" right before next pos
                meanings = meanings.replace(
                    previousmeaning, ""
                )  # Remove the appended meaning from meanings
                meanings = meanings.lstrip(" ").lstrip(";")
                if "/" in previousmeaning:
                    previousmeaning = previousmeaning.replace(
                        "/", meanings.split(";")[0].replace(posins[j], "").rstrip("\n")
                    )
                if "&" in previousmeaning:
                    previousmeaning = previousmeaning.replace(
                        "&", meanings.split(";")[0].replace(posins[j], "").rstrip("\n")
                    )
                meaningsbypos.append(
                    previousmeaning
                )  # Append the meaning with the previous pos to meaningsbypos
            meaningsbypos.append(meanings)
            for j, meaning in enumerate(
                meaningsbypos
            ):  # Meanings with the same part of speech
                if (
                    ";" in meaning
                ):  # "；" recognized as \uff1b, and meaningsbypos when printed only show u'something'
                    meaningsbypos[j] = meaning.replace(";", " %% " + posins[j] + " ")
            ssplit[len(ssplit) - 1] = " %% ".join(meaningsbypos)
            ssplit[len(ssplit) - 1] = ssplit[len(ssplit) - 1].replace("adverb.", "adv.")
            ssplit[len(ssplit) - 1] = ssplit[len(ssplit) - 1].replace("  ", " ")
            ssplit[len(ssplit) - 1] = ssplit[len(ssplit) - 1].replace('"', " ")
            g.write("**".join(ssplit) + "\n")
        f.close()
        g.close()
    return


def formatIPA(ipa):
    if "KK" in ipa:
        ipa = (
            ipa.replace("(", "").replace(")", "").replace("KK", "")
        )  # Keep the segment inside the parentheses
    elif "(" in ipa:
        for i, c in enumerate(ipa):
            if c == "(":
                left = i
            elif c == ")":
                right = i
        ipa = (
            ipa[0:left] + ipa[right + 1 : len(ipa)]
        )  # Remove everything inside the parentheses and the parenthese themselves
    return (
        (
            "["
            + ipa.replace("|", "")
            .replace(" FOR", "] for")
            .replace("/ ", "/ [")
            .replace(" OR ", "] / [")
            + "]"
        )
        .replace(" AND ", "] & [")
        .replace(".]", ".")
        .replace("[ ", "[")
        .replace("[ ", "[")
        .replace(" ]", "]")
        .replace(" ]", "]")
        .replace("'", "ˈ")
        .replace('"', "ˌ")
        .replace("dʒ", "ʤ")
        .replace("E", "ə")
        .replace("I", "ɪ")
        .replace("DG", "ʤ")
        .replace("U", "ʊ")
        .replace("NG", "ŋ")
        .replace(":", "ː")
        .replace("SH", "ʃ")
    )


def addIPA(i, c="PLR"):
    fileExists = False
    dictionary = {}
    mispronounced = {}
    noMoreIPA = False
    previousWord = ""
    current = 0
    #
    h = open(pathToVocab + "Word lists/Petit Livre Rouge/" + str(i) + " zh-hk.txt")
    for s in h:
        if ("|" not in s) and (s != "\n") and (not isInt(s.rstrip("\n"))):
            dictionary[s.split(" ** ")[0]] = s.split(" ** ")[2].replace(
                " %% ", "\n"
            )  # "\n" in s.split(" ** ")[2]
    # Load all words and meanings of that list
    #
    if os.path.exists(
        pathToVocab
        + "Word lists/Petit Livre Rouge/Other/5 Lists with pronunciation/"
        + str(i)
        + ".txt"
    ):
        g = open(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/5 Lists with pronunciation/"
            + str(i)
            + ".txt"
        )
        s = "".join(g.readlines())
        for word in dictionary:
            if word not in s:
                print(
                    "Word {0} not in IPA'ed list!!\n".format(word)
                )  # Sanity check if any word is missing
        print("File already exists.\n")
        return
    # If file already exists
    #
    if os.path.exists(
        pathToVocab
        + "Word lists/Petit Livre Rouge/Other/5 Lists with pronunciation/"
        + str(i)
        + " 0.txt"
    ):  # If partially imported from Ja, or inputed partially before and quitted, reload
        f = open(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/5 Lists with pronunciation/"
            + str(i)
            + " 0.txt"
        )
        fileExists = True
    else:
        f = open(
            pathToVocab
            + "Word list with no meaning/Petit Livre Rouge/"
            + str(i)
            + ".txt"
        )
    g = open(
        pathToVocab
        + "Word lists/Petit Livre Rouge/Other/5 Lists with pronunciation/"
        + str(i)
        + ".txt",
        "w",
    )
    mispronounced = {}
    noMoreIPA = False
    previousWord = ""
    previousIPA = ""
    for s in f:
        s = s.replace("\r\n", "\n").replace("\r", "\n")  # For list 13
        if (s == "\n") | (isInt(s.rstrip("\n"))):
            g.write(s)
        else:
            current += 1
            s = s.rstrip("\n").split(" **")
            if ((not fileExists) or (len(s) == 1) or ("[" not in s[len(s) - 1])) and (
                not noMoreIPA
            ):
                print(
                    "\n"
                    + s[0]
                    + "\t\t"
                    + str(current)
                    + "/"
                    + str(len(dictionary))
                    + "\n"
                    + dictionary[s[0]]
                )  # input() does not support utf-16 # Cannot use format
                ipa = input()
                while ipa == "":
                    ipa = input(
                        "Re-enter the pronunciation for {0}.\n".format(s[0])
                    )  # If entered nothing
                if (ipa.upper() == "MISS") or (ipa.upper() == "PREVIOUS"):
                    previousWordipa = input(
                        "Please re-enter the IPA for the last word {0}.\n".format(
                            previousWord
                        )
                    )
                    if previousWordipa.upper() != "QUIT":
                        mispronounced[previousWord] = previousWordipa
                    else:
                        print("Abandoned.\n")
                    ipa = input("\nNow enter the IPA for {0}.\n".format(s[0]))
                #
                if ipa.upper() == "WRONG":
                    wrongWord = input(
                        "Please enter the word for which you want to correct the pronunciation.\n"
                    )
                    if wrongWord.upper() == "QUIT":
                        print("Abandoned.\n")
                    else:
                        wrongWordipa = input(
                            "Now enter the IPA for {0}.\n".format(wrongWord)
                        )
                        if wrongWordipa.upper() == "QUIT":
                            print("Abandoned.\n")
                        else:
                            mispronounced[wrongWord] = wrongWordipa
                    ipa = input("\nNow enter the IPA for {0}.\n".format(s[0]))
                if ipa.upper() == "QUIT":
                    noMoreIPA = (
                        True  # Quit entering IPA, but print the word list afterwards
                    )
                    g.write(s[0] + "\n")  # Print current word without IPA
                    continue
                # This also covers the case where quitted after re-entering
                if (
                    ipa == previousIPA
                ):  # If the pronunciation entered is the same as the previous one, which is likely a mistake
                    print(
                        "WARNING: Same pronunciation {0} entered as the previous one. Press enter to confirm, or enter the correct pronunciation.\n".format(
                            ipa
                        )
                    )
                    s2 = input()
                    if s2.upper() == "QUIT":
                        noMoreIPA = True
                        g.write(s[0] + "\n")
                        continue
                    elif s2 != "":
                        ipa = s2
                previousWord = s[0]
                g.write(s[0] + " ** " + formatIPA(ipa) + "\n")
                previousIPA = ipa
            else:
                if (len(s) != 1) and (
                    "[" not in s[len(s) - 1]
                ):  # If some word behind the point of quit has Chinese meaning but no IPA, only print the word
                    g.write(s[0] + "\n")
                else:
                    g.write(" **".join(s) + "\n")
    f.close()
    g.close()
    h.close()
    if mispronounced != {}:
        abandoned = []
        print(mispronounced)
        print("\n")
        for misword in mispronounced:
            while misword not in dictionary:
                reword = input(
                    '{0} not in the list. Please re-enter the word. Or enter "ab" to abandon.\n'.format(
                        misword
                    )
                )
                if reword.upper() != "AB":
                    mispronounced[reword] = mispronounced[misword]
                    if misword != reword:
                        mispronounced.pop(misword)
                        misword = reword
                else:
                    abandoned.append(misword)
                    break
        if (
            abandoned != []
        ):  # Cannot change size of the dictionary during iteration; have to pop the words abandoned after iteration
            for word in abandoned:
                mispronounced.pop(word)
        e = open(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/5 Lists with pronunciation/"
            + str(i)
            + " 2.txt",
            "w",
        )
        g = open(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/5 Lists with pronunciation/"
            + str(i)
            + ".txt"
        )
        for s in g:
            word = s.rstrip("\n").split(" **")[0]
            if word in mispronounced:
                s = word + " ** " + formatIPA(mispronounced[word]) + "\n"
            e.write(s)
        g.close()
        e.close()
        os.rename(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/5 Lists with pronunciation/"
            + str(i)
            + " 2.txt",
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/5 Lists with pronunciation/"
            + str(i)
            + ".txt",
        )
    g = open(
        pathToVocab
        + "Word lists/Petit Livre Rouge/Other/5 Lists with pronunciation/"
        + str(i)
        + ".txt"
    )
    s = "".join(g.readlines())
    for word in dictionary:
        if word not in s:
            print(
                "Word {0} not in IPA'ed list!!\n".format(word)
            )  # Check if any word is missing
    g.close()
    if noMoreIPA:
        os.rename(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/5 Lists with pronunciation/"
            + str(i)
            + ".txt",
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/5 Lists with pronunciation/"
            + str(i)
            + " 0.txt",
        )
    return


def IPAFromJa(i):
    assert i in [3, 5, 11, 12, 13, 14]
    f = open(pathToVocab + "Word lists/Petit Livre Rouge/" + str(i) + " ja.txt")
    g = open(
        pathToVocab
        + "Word lists/Petit Livre Rouge/Other/5 Lists with pronunciation/"
        + str(i)
        + " 0.txt",
        "w",
    )
    for s in f:
        s = s.rstrip("\n").split(" **")
        if len(s) == 3:
            if s[1] != " IPA":  # If not the header
                g.write(s[0] + " **" + s[1] + "\n")
            continue  # If is the header, do not write
        if ("||" in s[0]) | (s[0] == ""):
            continue  # If is the header or new line, do not write
        if isInt(s[0]):
            g.write("\n" + s[0] + "\n")
        else:
            g.write(s[0] + "\n")
    f.close()
    g.close()
    return


def combineIPA(i, proofread=False, c="z"):  # FOR UNICODE
    assert (c == "z") or (c == "j")
    if c == "z":
        langs = ["zh-cn", "zh-hk"]
    if c == "j":
        langs = ["ja"]
    for c in langs:
        if "zh" in c:
            try:
                f = open(
                    pathToVocab
                    + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
                    + str(i)
                    + " "
                    + c
                    + ".txt"
                )
                g = open(
                    pathToVocab
                    + "Word lists/Petit Livre Rouge/Other/FINAL LISTS/"
                    + str(i)
                    + " "
                    + c
                    + ".txt",
                    "w",
                )
            except IOError:
                f = open(
                    pathToVocab
                    + "Word lists/Petit Livre Rouge/Other/7 Initially proofread/"
                    + str(i)
                    + " "
                    + c
                    + ".txt"
                )
                g = open(
                    pathToVocab
                    + "Word lists/Petit Livre Rouge/Other/7 + IPA/"
                    + str(i)
                    + " "
                    + c
                    + ".txt",
                    "w",
                )
        else:
            f = open(
                pathToVocab
                + "Word lists/Petit Livre Rouge/Other/JA/"
                + str(i)
                + " ja.txt"
            )
        h = open(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/5 Lists with pronunciation/"
            + str(i)
            + ".txt"
        )
        if c == "ja":
            f.readline()
            f.readline()
        while True:
            sf = f.readline().replace("\r", "\n").replace("\n\n", "\n")
            sh = h.readline().replace("\r", "\n")
            if sf == "":
                break
            if (sf == "\n") or (isInt(sf.rstrip("\n"))):
                g.write(sf)
                continue
            if sf.split(" **")[0].rstrip("\n") != sh.split(" ** ")[0]:
                assert ()
            else:
                if len(sf.split(" ** ")) == 3:
                    sf = sf.split(" ** ")
                    sf[1] = sh.split(" ** ")[1].rstrip("\n")
                    sf = " ** ".join(sf)
                elif (len(sf.split(" ** ")) == 1) and c == "ja":
                    sf = (
                        sf.split(" **")[0].rstrip("\n")
                        + " ** "
                        + sh.split(" ** ")[1].rstrip("\n")
                        + " ** "
                        + "\n"
                    )
                else:
                    assert ()
                g.write(sf)
    f.close()
    g.close()
    h.close()
    return


def combineDifficultWordList(i):
    for c in ["zh-cn", "zh-hk"]:
        try:
            f = open(
                pathToVocab
                + "/Word lists/Petit Livre Rouge/Other/FINAL LISTS/"
                + str(i)
                + " "
                + c
                + ".txt"
            )
            print(str(i) + ": " + c + " from FINAL LISTS.\n")
        except IOError:
            f = open(
                pathToVocab
                + "/Word lists/Petit Livre Rouge/Other/7 + IPA/"
                + str(i)
                + " "
                + c
                + ".txt"
            )
            print(str(i) + ": From 7 + IPA.\n")
        g = open(
            pathToVocab
            + "/Word lists/Petit Livre Rouge/Other/-1 Difficult Words/"
            + str(i)
            + ".txt"
        )
        h = open(
            pathToVocab + "/Word lists/Petit Livre Rouge/" + str(i) + " " + c + ".txt",
            "w",
        )
        h.write("".join(g.readlines() + ["\n"] + f.readlines()))
        f.close()
        g.close()
        h.close()
    return


def formatWord3000(s):
    return (
        s.replace("\\\\", "SLASH")
        .replace("\\", "\\\\")
        .replace("SLASH", "\\\\")
        .replace('"', "")
        .replace("N/A", "not applicable")
        .replace("B", "\\" + "033[1m")
        .replace("N", "\\" + "033[0m")
        .replace("not applicable", "N/A")
    )


def input3000helper(s, meaning=None):
    meanings = []
    i = 1
    quit = False
    while True:
        if ((meaning is None) and (i == 1)) or (i > 1):
            print(
                "\nEnter the {0}st/th meaning for {1}. Or press enter to end this word.\n".format(
                    i, s
                )
            )
            meaning = input()
        elif (meaning == "") and (i > 1):
            print("".center(80, "*"))
            break
        elif meaning.upper() == "QUIT":
            quit = True
            break
        description = input("Enter the description.\n")
        if description.upper() == "QUIT":
            quit = True
            break
        synonym = (
            input("Enter the synonyms.\n").lstrip(" ").rstrip(" ").replace(" ", ",")
        )
        if synonym == "":
            synonym = "N/A"
        elif synonym.upper() == "QUIT":
            quit = True
            break
        antonym = input("Enter the antonyms.\n")
        if antonym == "":
            antonym = "N/A"
        elif antonym.upper() == "QUIT":
            quit = True
            break
        if "+" in antonym:
            der = antonym.split("+")[1].lstrip(" ").rstrip(" ")
            antonym = antonym.split("+")[0].rstrip(" ")
            antonym = antonym + " \\ " + der
        else:
            der = ""
        antonym = antonym.lstrip(" ").rstrip(" ").replace(" ", ",")
        meanings.append(
            meaning + " \\ " + description + " \\ " + synonym + " \\ " + antonym
        )
        i += 1
    if not quit:
        s = s + " ** N/A ** " + " %% ".join(meanings) + "\n"
    return s


def input3000():
    if not os.path.isfile(pathToVocab + "Word lists/Trois Mille/Backup/3000.txt"):
        shutil.copy(
            pathToVocab + "Word lists/Trois Mille/3000.txt",
            pathToVocab + "Word lists/Trois Mille/Backup/3000.txt",
        )
    else:
        i = 2
        while os.path.isfile(
            pathToVocab + "Word lists/Trois Mille/Backup/3000 " + str(i) + ".txt"
        ):
            i += 1
        shutil.copy(
            pathToVocab + "Word lists/Trois Mille/3000.txt",
            pathToVocab + "Word lists/Trois Mille/Backup/3000 " + str(i) + ".txt",
        )
    f = open(pathToVocab + "Word lists/Trois Mille/3000.txt")
    g = open(pathToVocab + "Word lists/Trois Mille/3000 0.txt", "w")
    quit = False
    for s in f:
        if quit:
            g.write(s)
            continue
        s = formatWord3000(s)
        s = s.replace("\r", "\n").replace("\n\n", "\n").rstrip("\n")
        s = s.split(" ** ")
        if len(s) == 3:
            g.write(" ** ".join(s) + "\n")
        elif len(s) > 3:  # If meanings entered but seperated by ** instead of %%
            g.write(s[0] + " ** " + s[1] + " ** " + " %% ".join(s[2 : len(s)]) + "\n")
        elif len(s) == 1:
            s = s[0].rstrip("\n")
            print(s + "   Please enter the first meaning.\n")
            meaning1 = input()
            if meaning1.upper() == "DELETE":
                continue
            elif meaning1.upper() == "QUIT":
                g.write(s + "\n")
                quit = True
                continue
            elif meaning1.upper() == "ADD":
                s2 = input("Please enter the word to be added.\n")
                if s2.upper() != "QUIT":
                    g.write(input3000helper(s2))
                g.write(input3000helper(s))
            else:
                g.write(input3000helper(s, meaning1))
    f.close()
    g.close()
    g = open(pathToVocab + "Word lists/Trois Mille/3000 0.txt")
    h = open(pathToVocab + "Word lists/Trois Mille/3000 empty.txt")
    wordlist = []
    for s in g:
        wordlist.append(s.rstrip("\r\n").rstrip(" ").split(" **")[0])
    for s in h:
        assert s.rstrip("\r\n").rstrip(" ") in wordlist
    os.rename(
        pathToVocab + "Word lists/Trois Mille/3000 0.txt",
        pathToVocab + "Word lists/Trois Mille/3000.txt",
    )
    return


# def encodeUTF16ToUTF8(directory):
# 	f = open(directory)
# 	g = open(directory.replace(".txt"," 0.txt"), 'w')
# 	converted = False
# 	for s in f:
# 		try:
# 			g.write(s.decode("utf-16"))
# 			converted = True
# 		except (UnicodeDecodeError, UnicodeEncodeError):
# 			try:
# 				g.write(s.decode("utf-8"))
# 				converted = True
# 			except (UnicodeDecodeError,UnicodeEncodeError):
# 				g.write(s)
# 	if not converted:
# 		print(directory + "Not converted.\n")
# 	f.close()
# 	g.close()
# 	os.rename(directory.replace(".txt"," 0.txt"), directory)
# 	return


def removeEmptyMeaningsAndDoubleSpaces(i):
    POS = ["n.", "v.", "adj.", "adv."]
    for c in ["cn", "hk"]:
        f = open(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/4 After formatting meanings by part of speech and seperating different meanings by semicolon/"
            + str(i)
            + " zh-"
            + c
            + ".txt"
        )
        g = open(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/6 Empty meanings and double spaces removed/"
            + str(i)
            + " zh-"
            + c
            + ".txt",
            "w",
        )
        for s in f:
            for pos in POS:
                if ("%% " + pos + "\n" in s) or ("%% " + pos + " \n" in s):
                    print(s)
                s = (
                    s.replace("%% " + pos + " %%", "%%")
                    .replace("%% " + pos + "\n", "\n")
                    .replace("%% " + pos + " \n", "\n")
                    .replace("  ", " ")
                    .replace("  ", " ")
                )
            g.write(s)
        f.close()
        g.close()
    return


def removeIPA(
    i,
):  # Removes the IPA mistakenly included in lists in 7 Initially proofread
    for c in ["zh-cn", "zh-hk"]:
        f = open(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/7 Initially proofread/"
            + str(i)
            + " "
            + c
            + ".txt"
        )
        g = open(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/7 Initially proofread/"
            + str(i)
            + " "
            + c
            + " 2.txt",
            "w",
        )
        for s in f:
            if len(s.split(" ** ")) > 1:
                s = s.split(" ** ")
                s[1] = "N/A"
                s = " ** ".join(s)
            g.write(s)
        f.close()
        g.close()
        os.rename(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/7 Initially proofread/"
            + str(i)
            + " "
            + c
            + " 2.txt",
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/7 Initially proofread/"
            + str(i)
            + " "
            + c
            + ".txt",
        )
    return


def extend(i):
    combineIPA(i)
    combineDifficultWordList(i)
    f = open(pathToVocab + "Word lists/Petit Livre Rouge/" + str(i) + " zh-hk.txt")
    wordList = f.readline().rstrip("\n").split(" || ")
    newList = []
    allWords = []
    add = []
    i = 0
    for s in f:
        if (s != "\n") and (not isInt(s.rstrip("\n"))):
            i += 1
            if not s.split(" ** ")[0] in wordList:
                s = s.split(" ** ")
                word = s[0]
                s[0] += "\t\t" + str(i)
                allWords.append(word)
                s[2] = s[2].split(" %% ")
                if len(s[2]) != 1:
                    for index, meaning in enumerate(s[2]):
                        s[2][index] = str(index + 1) + ". " + meaning
                s[2] = "\n".join(s[2])
                s = "\n".join(s)
                print(s)
                my_input = input()
                if my_input != "":
                    print()
                    if "MM" in my_input and len(my_input) > 2:
                        add.append(my_input[2 : len(my_input)])
                    elif (
                        my_input.upper()[0] in ["M", ",", "N", "J", "K"]
                        or my_input == "MM"
                    ):
                        newList.append(word)
                    elif my_input.upper() == "QUIT":
                        break
    add2 = (
        input("Enter all words you want to add, separated by spaces.\n")
        .replace("  ", " ")
        .replace("  ", " ")
        .split(" ")
    )
    if add2 != [""]:
        add += add2
    add = list(set(add))
    for w in add:
        if w in allWords:
            newList.append(w)
        else:
            w2 = input(w + " not in the list. Please re-enter.\n")
            while w2 not in allWords:
                if w2.upper() == "QUIT":
                    break
                w2 = input(w + " not in the list. Please re-enter.\n")
            if w2 in allWords:
                newList.append(w2)
    newList = sorted(list(set(newList)))
    print(newList)
    print("\n")
    print(" || ".join(sorted(list(set(wordList + newList)))))


def instructions():
    pathToSystemFiles = pathToVocab + "System Files/"
    en = open(pathToSystemFiles + "instructions_en.txt")
    enw = open(pathToSystemFiles + "instructions_en 2.txt", "w")
    cn = open(pathToSystemFiles + "instructions_hans.txt")
    cnw = open(pathToSystemFiles + "instructions_hans 2.txt", "w")
    hk = open(pathToSystemFiles + "instructions_hant.txt")
    hkw = open(pathToSystemFiles + "instructions_hant 2.txt", "w")
    ja = open(pathToSystemFiles + "instructions_ja.txt")
    jaw = open(pathToSystemFiles + "instructions_ja 2.txt", "w")
    reads = [en, cn, hk, ja]
    writes = [enw, cnw, hkw, jaw]
    ins_en = {}
    ins_cn = {}
    ins_hk = {}
    ins_ja = {}
    inss = [ins_en, ins_cn, ins_hk, ins_ja]
    for i in range(0, len(reads)):
        for s in reads[i]:
            s = s.rstrip("\n").split(": ")
            if len(s) == 1:
                s.append(
                    ""
                )  # If instruction is empty (possible because it might be non-empty for some other languages)
            inss[i][s[0]] = s[1]
    for i in range(0, len(reads)):  # Check if all have the same instructions (keys)
        for key in inss[i]:
            for ins in inss:
                if key not in ins:
                    print(key)
                    print(i)
                    assert ()
    while True:
        my_input = input(
            'To add or remove a new instruction, enter the name of the instruction. To see all instructions, enter "SEE".\n'
        )
        if my_input.upper() == "QUIT":
            break
        elif my_input.upper() == "SEE":
            number = input(
                "1. English\n2. Simplified Chinese\n3. Traditional Chinese\n4. Japanese\n"
            )
            while (not isInt(number)) or (not int(number) in range(1, len(reads) + 1)):
                if number.upper() == "QUIT":
                    continue
                number = input(
                    "1. English\n2. Simplified Chinese\n3. Traditional Chinese\n4. Japanese\n"
                )
            number = int(number)
            for key in sorted(inss[number - 1]):
                print(key + ": " + inss[number - 1][key] + "\n")
        elif my_input.upper() == "RENAME":
            my_input = input("Enter the key you want to rename.\n")
            if my_input not in ins_en:
                print("Key not found.\n")
            else:
                rename = input("Enter the new key you want to rename it to.\n")
                for ins in inss:
                    ins[rename] = ins[my_input]
                    ins.pop(my_input)
        elif (
            my_input in ins_en
            and my_input in ins_cn
            and my_input in ins_hk
            and my_input in ins_ja
        ):
            print(my_input + ":\n")
            print(ins_en.pop(my_input) + "\n")
            print(ins_cn.pop(my_input) + "\n")
            print(ins_hk.pop(my_input) + "\n")
            print(ins_ja.pop(my_input) + "\n")
        elif (
            (my_input not in ins_en)
            and (my_input not in ins_cn)
            and (my_input not in ins_hk)
            and (my_input not in ins_ja)
        ):
            print("Now enter the instructions for " + my_input + ":\n")
            ins_en[my_input] = input("English:\n")
            ins_cn[my_input] = input("\nSimplified Chinese:\n")
            ins_hk[my_input] = input("\nTraditional Chinese:\n")
            ins_ja[my_input] = input("\nJapanese:\n")
    for i in range(0, len(reads)):
        for key in sorted(inss[i]):
            writes[i].write(key + ": " + inss[i][key].replace(": ", ":SPACE") + "\n")
    for file in reads + writes:
        file.close()
    os.rename(
        pathToSystemFiles + "instructions_en 2.txt",
        pathToSystemFiles + "instructions_en.txt",
    )
    os.rename(
        pathToSystemFiles + "instructions_hans 2.txt",
        pathToSystemFiles + "instructions_hans.txt",
    )
    os.rename(
        pathToSystemFiles + "instructions_hant 2.txt",
        pathToSystemFiles + "instructions_hant.txt",
    )
    os.rename(
        pathToSystemFiles + "instructions_ja 2.txt",
        pathToSystemFiles + "instructions_ja.txt",
    )
    return


def formatChinese(word, my_input, noInput=False):
    if "NO" in my_input:
        output = (
            my_input.replace("NO", "")
            .replace("（", "(")
            .replace("）", ")")
            .replace("……", "…")
            .replace("···", "…")
            .replace("...", "…")
            .replace(",", "，")
            + "\n"
        )  # No transformation, just add the typed meaning literally
    if "%" in my_input or "." in my_input or noInput:
        if not noInput:
            print('\nDID YOU FORGET TO ADD "NO"?\n')
        output = (
            my_input.replace("NO", "")
            .replace("（", "(")
            .replace("）", ")")
            .replace("……", "…")
            .replace("···", "…")
            .replace("...", "…")
            .replace(",", "，")
            + "\n"
        )  # No transformation, just add the typed meaning literally
    else:
        output = (
            my_input.replace("  ", " ")
            .replace(" ", " %% ")
            .replace("n", "n. ")
            .replace("v", "v. ")
            .replace("v. i", "v. ")
            .replace("v. t", "v. ")
            .replace("a", "adj. ")
            .replace("adj. dj", "adj. ")
            .replace("adj. dv. ", "adv. ")
            .replace("p", "prep. ")
            .replace("c", "conj. ")
            .replace("in. t", "int. ")
            .replace("（", "(")
            .replace("）", ")")
            .replace("···", "…")
            .replace("……", "…")
            .replace("...", "…")
            .replace(" /", "/")
            .replace("shi", "使")
            .replace(",", "，")
            + "\n"
        )
    for m in output.split(" %% "):
        m = m.rstrip("\n")
        poss = ["n", "v", "ad", "prep", "conj", "int"]
        if all(pos not in m for pos in poss):
            print("\nWARNING: NO PART OF SPEECH for {0}.\n".format(m))
        if ("adj" in m and m[len(m) - 1] == "\xb0") or (
            "adv" in m and m[len(m) - 1] == "\x84"
        ):
            print('\nWARNING: Check "{0}". "的" or "地"?\n'.format(m))
    return word + " ** N/A ** " + output


def pr(i):  # proofread
    if not os.path.exists(
        pathToVocab
        + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
        + str(i)
        + " 0.txt"
    ):
        f = open(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/7 Initially proofread/"
            + str(i)
            + " zh-cn.txt"
        )
        g = open(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
            + str(i)
            + " 0.txt",
            "w",
        )
        g.write(
            f.readline()
            + f.readline()
            + f.readline().rstrip("\n")
            + "STARTED"
            + "\n"
            + "".join(f.readlines())
        )
        f.close()
        g.close()
    f = open(
        pathToVocab
        + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
        + str(i)
        + " 0.txt"
    )
    g = open(
        pathToVocab
        + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
        + str(i)
        + " zh-cn.txt",
        "w",
    )
    quitted = False
    started = False
    previousWord = None
    try:
        for s in f:
            s = s.replace("（", "(").replace("）", ")")
            if quitted or (not started):
                if "STARTED" in s:
                    started = True
                    s = s.replace("STARTED", "")
                else:
                    g.write(s)
                    continue
            if not quitted and started:  # The line started now changed started to True
                if s == "\n" or isInt(s.rstrip("\n")):
                    g.write(s)
                else:
                    s = s.rstrip("\n").split(" ** ")
                    assert len(s) == 3
                    my_input = input("\n" + "\n".join(s) + "\n")
                    if my_input.upper() == "":
                        g.write(
                            formatChinese(
                                s[0], " %% ".join(s[2 : len(s)]), noInput=True
                            )
                        )
                    elif my_input.upper() == "QUIT" or my_input.upper() == "Q":
                        quitted = True
                        g.write(" ** ".join(s) + "STARTED\n")
                        continue
                    elif (
                        my_input.upper() == "MISS"
                        or my_input.upper() == "MIS"
                        or my_input.upper() == "MI"
                        or my_input.upper() == "M"
                    ):
                        g.write(" ** ".join(s) + "\n")  # Current word
                        for ss in f:
                            g.write(ss)
                        f.close()
                        g.close()
                        os.rename(
                            pathToVocab
                            + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
                            + str(i)
                            + " zh-cn.txt",
                            pathToVocab
                            + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
                            + str(i)
                            + " 0.txt",
                        )
                        f = open(
                            pathToVocab
                            + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
                            + str(i)
                            + " 0.txt"
                        )
                        g = open(
                            pathToVocab
                            + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
                            + str(i)
                            + " zh-cn.txt",
                            "w",
                        )
                        for ss in f:
                            if ss.split(" ** ")[0] == previousWord:
                                g.write(ss.rstrip("\n") + "STARTED\n")
                            else:
                                g.write(ss)
                        f.close()
                        g.close()
                        os.rename(
                            pathToVocab
                            + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
                            + str(i)
                            + " zh-cn.txt",
                            pathToVocab
                            + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
                            + str(i)
                            + " 0.txt",
                        )
                        pr(i)
                        break
                    else:
                        g.write(formatChinese(s[0], my_input))
                    previousWord = s[0]
        f.close()
        g.close()
        if quitted:
            os.rename(
                pathToVocab
                + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
                + str(i)
                + " zh-cn.txt",
                pathToVocab
                + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
                + str(i)
                + " 0.txt",
            )
        elif os.path.exists(
            pathToVocab
            + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
            + str(i)
            + " zh-cn.txt"
        ):
            shutil.copy(
                pathToVocab
                + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
                + str(i)
                + " zh-cn.txt",
                pathToVocab
                + "Word lists/Petit Livre Rouge/Other/8 Completely proofread/"
                + str(i)
                + " zh-hk.txt",
            )
    except Exception:
        print("Error occurred.\n")
        f.close()
        g.close()
        try:
            print(s[0] + "\n")
        except Exception:
            print("Nothing to print.\n")
    return
