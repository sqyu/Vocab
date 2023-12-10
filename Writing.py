import datetime
import os
import pytz
import Vars
from Help_funs import concatenateListNames, isInt


def writeTime(begin, timeBegan=None, mode=None, names=None):
    """
    writeTime(begin, timeBegan = None, mode = None, names = None):
    Writes the learning time to record file.

    Parameters
    __________
    begin: bool
    Whether it is the beginning or end of the session

    timeBegan: bool, must be None if begin == True, and must not be None if begin == False
    The beginning time of the session

    mode: string, must be None if begin == True, and must not be None if begin == False
    The mode (session)

    names: string
    Book name and list of words found if "find a word" mode, book name and "random XX words" if
        "random 50 words" mode, "similar words to WORD" if "similar words" mode, or book name and
        list numbers otherwise
    """
    assert (begin and timeBegan is None) or (not begin and timeBegan is not None)
    assert (begin and mode is None) or (not begin and mode is not None)
    assert (begin and names is None) or (not begin and names is not None)
    tz = pytz.timezone(Vars.parameters["TimeZone"].split(" ** ")[2])
    timeNow = datetime.datetime.now(tz.localize(datetime.datetime.now()).tzinfo)
    timeNowYM = timeNow.strftime("%Y-%m")
    timeNowFULL = timeNow.strftime("%m/%d/%Y %H:%M:%S %Z")
    if not os.path.exists(os.path.join(Vars.record_path, "Time")):
        os.makedirs(os.path.join(Vars.record_path, "Time"))
    if not os.path.exists(
        os.path.join(Vars.record_path, "Time", "Time " + timeNowYM + ".txt")
    ):
        f = open(
            os.path.join(Vars.record_path, "Time", "Time " + timeNowYM + ".txt"), "w"
        )
        if begin:
            f.write(timeNowFULL)
            f.close()
            return timeNowFULL
        else:
            f.close()
            return
    g = open(os.path.join(Vars.record_path, "Time", "Time " + timeNowYM + ".tmp"), "w")
    f = open(os.path.join(Vars.record_path, "Time", "Time " + timeNowYM + ".txt"), "r")
    try:
        if begin:
            freadlines = f.readlines()
            if freadlines != []:
                while "\n" in freadlines:
                    freadlines.pop(freadlines.index("\n"))
                if "\n" not in freadlines[len(freadlines) - 1]:
                    freadlines[len(freadlines) - 1] += "\n"
                g.write("".join(freadlines))
            g.write(timeNowFULL)
        if not begin:  # If end
            if (
                len(names) == 2
                and isinstance(names[1], str)
                and "random " in names[1]
                and " words" in names[1]
                and isInt(names[1].replace("random ", "").replace(" words", ""))
            ):  # Random 50 words
                book = Vars.acronym[names[0]] + " "
                lists = names[1]
            elif len(names) == 1 and "similar words to " in names[0]:  # Similar words
                book = ""
                lists = names[0]
            elif mode != "words found: ":
                book = (
                    Vars.acronym[names[0]] + " "
                )  # Replace the full name of the book by its Vars.acronym
                lists = concatenateListNames(names[1 : len(names)])
            for s in f:
                if timeBegan in s:
                    assert "-" not in s
                    if (mode == "words found: ") and (len(names) == 0):
                        g.write(
                            s.rstrip("\n") + " -- " + timeNowFULL + " no words found.\n"
                        )
                    elif mode == "words found: ":
                        g.write(
                            s.rstrip("\n")
                            + " -- "
                            + timeNowFULL
                            + " words found: "
                            + " & ".join(names)
                            + "\n"
                        )
                    else:
                        g.write(
                            s.rstrip("\n")
                            + " -- "
                            + timeNowFULL
                            + " "
                            + mode
                            + book
                            + lists
                            + "\n"
                        )
                else:
                    if s != "\n":
                        g.write(s)
        f.close()
        g.close()
        os.rename(
            os.path.join(Vars.record_path, "Time", "Time " + timeNowYM + ".tmp"),
            os.path.join(Vars.record_path, "Time", "Time " + timeNowYM + ".txt"),
        )
        if begin:
            return timeNowFULL
    except Exception:
        f.close()
        g.close()
        print(
            "Error occurred: {0} || {1} || {2} || {3}.".format(
                begin, timeBegan, mode, names
            )
        )
    return


def writeRecord(difficultWords, mode, names):
    """
    writeRecord(difficultWords, mode, names):
    Writes the record to the file.

    Parameters
    __________
    difficultWords: list
    A list of difficult words

    mode: string, must be "learn", "recite", "view" or "reciteconj"
    The mode

    names: string
    "similar words to WORD" if "similar word mode", book name and "random XX words" if
        "random 50 words" mode, the list that consists of the name of the book followed
        by the list numbers otherwise
    """
    assert mode in ["learn", "recite", "view", "reciteconj"]
    tz = pytz.timezone(Vars.parameters["TimeZone"].split(" ** ")[0])
    timeNow = datetime.datetime.now(tz.localize(datetime.datetime.now()).tzinfo)
    if "similar words to " in names[0]:
        pathToRecord = os.path.join(
            Vars.record_path, "Others", timeNow.strftime("%Y-%m")
        )
    else:
        pathToRecord = os.path.join(
            Vars.record_path, names[0], timeNow.strftime("%Y-%m")
        )
    if not os.path.exists(pathToRecord):
        os.makedirs(pathToRecord)
    if "similar words to " in names[0]:
        lists = names[0].replace("similar words to ", "").upper()
        fileName = pathToRecord + "/" + lists + " " + timeNow.strftime("%m-%d ") + mode
    elif (
        isinstance(names[1], str)
        and "random " in names[1]
        and " words" in names[1]
        and isInt(names[1].replace("random ", "").replace(" words", ""))
    ):  # Random 50 words
        lists = names[1]
        fileName = pathToRecord + "/" + timeNow.strftime("%m-%d ") + lists + " " + mode
    else:
        lists = concatenateListNames(names[1 : len(names)])
        fileName = pathToRecord + "/" + timeNow.strftime("%m-%d ") + lists + " " + mode
    if os.path.isfile(fileName + ".txt"):
        i = 2
        while os.path.isfile(fileName + " " + str(i) + ".txt"):
            i += 1
        fileName = fileName + " " + str(i) + ".txt"
    else:
        fileName = fileName + ".txt"
    f = open(fileName, "w")
    f.write("\n".join(difficultWords))
    f.close()
    return
