import os

from Help_funs import isInt, QuitException, quitOrInput
import Vars
from Vars import getInst, printInst, inpInst


def chooseOrReturnCurrent(valid_list, instruction, lower, current=None):
    """
    chooseOrReturnCurrent(valid_list, instruction, lower, current = None):
    Returns an input from valid_list.

    Parameters
    __________
    valid_list: list, List of available options
    instruction: str, Prompt.
    lower: True or False, if change input to lower case
    current: None or one option from valid_list, the current setting
    """
    if current is not None and current not in valid_list:
        raise Exception(
            "In chooseOrReturnCurrent: Argument 'current' must be None or one of the allowed "
            "inputs in valid_list."
        )

    def trans(x):
        return x.lower() if lower else x.upper()

    inp = trans(input("\n" + instruction + "\n"))
    while inp not in valid_list:
        if current and inp.upper() == "QUIT":
            return current
        inp = trans(input("\n" + instruction + "\n"))
    return inp


def chooseOneTimeZone(current=None):  # Choose one time zone, returns one time zone
    """
    chooseOneTimeZone(current = None)
    Chooses the time zone for one functionality (record, schedule, time), returns (1) string for
    time zone code and (2) bool for quitted or not

    Parameters
    __________
    current: string, must be in tznames below
    The current time zone
    """
    choose = ""
    print(
        "\n"
        + "\n".join(
            [
                "{0:>2}. {1}".format(str(index + 1), getInst("timeZone" + tz))
                for index, tz in enumerate(Vars.tzs)
            ]
        )
    )  # Print all possible time zones
    while (not isInt(choose)) or (not int(choose) in range(1, len(Vars.tzs) + 1)):
        if current and choose == "QUIT":
            return current, True  # Do not change settings
        choose = inpInst("setTimeZone", rep=str(len(Vars.tzs))).upper()
    return Vars.tznames[int(choose) - 1], False


def chooseTimeZone(
    current,
):  # Choose one time zone in the three options, returns all three time zones
    """
    chooseTimeZone(current)
    Chooses all time zones

    Parameters
    __________
    current: the string composed of three time zone strings joined by " ** "
    The current time zones
    """
    print("\n" + getInst("promptSetParameters"))
    print("1. {0}".format(getInst("paraTimeZoneRecord")))
    print("2. {0}".format(getInst("paraTimeZoneSchedule")))
    print("3. {0}".format(getInst("paraTimeZoneTime")))
    print("4. {0}".format(getInst("paraTimeZoneUnify")))
    choose = input().upper()
    while (not isInt(choose)) or (not int(choose) in range(1, 5)):
        if choose == "QUIT":
            return current
        choose = inpInst("chooseFromAbove", rep="4").upper()
    current = current.split(" ** ")
    choose = int(choose) - 1
    if choose in range(0, 3):
        current[choose], quit = chooseOneTimeZone(current[choose])
    elif choose == 3:  # If unify all time zones
        # current[0] is meaningless, but needed to enable the user to quit from chooseOneTimeZone
        tz, quit = chooseOneTimeZone(current[0])
        if quit:  # If quitted
            return " ** ".join(current)
        else:
            return " ** ".join([tz] * 3)
    else:
        assert ()
    return " ** ".join(current)  # Record, Schedule, Time


def chooseRandom50Words(current):
    """
    chooseRandom50Words(current = None):
    Returns the number of random words in the Random50Words mode.

    Parameters
    __________
    current: An integer, the current setting.
    """
    print()
    num = inpInst("chooseRandom50Words")
    while not (isInt(num) and int(num) >= 1):
        if num.upper() == "QUIT":
            return current
        print()
        if not isInt(num):
            num = inpInst("enterANumber")
        else:  # int(num) >= 1
            num = inpInst("enterAPositiveNumber")
    return num


def setParameters():
    """
    setParameters()
    Returns the system parameters set by user, or set by default if first time of use.
    """
    par = os.path.join(Vars.sys_path, "Parameters.txt")
    Vars.parameters = {}
    if not os.path.exists(par):
        print("\n" + Vars.instructions_All["greetings"])
        Vars.lang = chooseOrReturnCurrent(
            Vars.langs,
            Vars.instructions_All["chooseLanguage"],
            True,
            Vars.parameters["Language"],
        )
        Vars.availableBooks = list(Vars.listNumber[Vars.lang])
        Vars.instructions = readSystemFile(Vars.lang)
        timeZoneQuitted = True
        while timeZoneQuitted:
            timeZone, timeZoneQuitted = chooseOneTimeZone()
        Vars.parameters = {
            "AllForRandom50Words": "A",
            "IgnoreDiacritics": "N",
            "Language": Vars.lang,
            "Random": "A",
            "Random50Words": "50",
            "Record": "A",
            "ShowComments": "Y",
            "TimeZone": " ** ".join([timeZone] * 3),
        }
        open(par, "w").write(
            "\n".join([s[0] + ": " + s[1] for s in sorted(Vars.parameters.items())])
        )
    else:
        Vars.parameters = readSystemFile("parameters")
        Vars.instructions = readSystemFile(Vars.parameters["Language"])
        Vars.availableBooks = list(Vars.listNumber[Vars.parameters["Language"]])
    return Vars.parameters


def changeParameters():
    """
    changeParameters():
    Changes one system parameter.
    """
    Vars.instructions["paraAllForRandom50Words"] = getInst(
        "paraAllForRandom50Words", rep=Vars.parameters["Random50Words"]
    )
    Vars.instructions["paraRandom50Words"] = getInst(
        "paraRandom50Words", rep=Vars.parameters["Random50Words"]
    )
    prompt = (
        "\n"
        + getInst("promptSetParameters")
        + "\n"
        + "\n".join(
            [
                str(index + 1) + ". " + getInst("para" + par) + "\n"
                for index, par in enumerate(sorted(Vars.parameters))
            ]
        )
    )
    try:
        choose = quitOrInput(prompt).upper()
    except QuitException:
        return
    while not (
        isInt(choose) and int(choose) >= 1 and int(choose) <= len(Vars.parameters)
    ):
        try:
            choose = quitOrInput(prompt).upper()
        except QuitException:
            return
    choose = sorted(Vars.parameters)[int(choose) - 1]
    if choose in ["AllForRandom50Words", "Random", "Record"]:
        setChoose = chooseOrReturnCurrent(
            ["Y", "N", "A"], getInst("setYorNorA"), False, Vars.parameters[choose]
        )
    elif choose == "Language":
        setChoose = chooseOrReturnCurrent(
            Vars.langs,
            Vars.instructions_All["chooseLanguage"],
            True,
            Vars.parameters["Language"],
        )
    elif choose == "Random50Words":
        setChoose = chooseRandom50Words(Vars.parameters["Random50Words"])
    elif choose in ["ShowComments", "IgnoreDiacritics"]:
        setChoose = chooseOrReturnCurrent(
            ["Y", "N"], getInst("setYorN"), False, Vars.parameters[choose]
        )
    elif choose == "TimeZone":
        setChoose = chooseTimeZone(Vars.parameters["TimeZone"])
    else:
        assert ()
    f = open(os.path.join(Vars.sys_path, "Parameters.txt"))
    g = open(os.path.join(Vars.sys_path, "Parameters 2.txt"), "w")
    for s in f:
        if s.split(": ")[0] == choose:
            s = choose + ": " + setChoose + "\n"
        g.write(s)
    f.close()
    g.close()
    os.rename(
        os.path.join(Vars.sys_path, "Parameters 2.txt"),
        os.path.join(Vars.sys_path, "Parameters.txt"),
    )
    Vars.parameters = setParameters()
    Vars.lang = Vars.parameters["Language"]
    Vars.instructions = readSystemFile(Vars.lang)
    printInst("changesSaved")
    return


def readSystemFile(mode):
    """
    readSystemFile(mode):
    Returns the instructions in the chosen language

    Paramters
    _________
    mode : string "zh-hk", "zh-cn", "ja", "all", "parameters"
    Language code
    """
    if mode == "parameters":
        file = "Parameters.txt"
    elif mode == "all" or mode in Vars.langs:
        file = "Instructions_%s.txt" % mode
    else:
        raise Exception(
            "In readSystemFile(), mode most be 'all', 'parameters', or one of the languages from"
            f"Vars.langs. Given {mode}."
        )
    f = open(os.path.join(Vars.sys_path, file))
    Vars.instructions = {
        sp[0]: sp[1].strip().replace("RETURN", "\n").replace("SPACE", " ")
        for sp in (s.split(": ") for s in f.readlines())
    }  # Keep in mind that some instructions are empty
    f.close()
    return Vars.instructions


def initialization():
    """
    initialization()
    Initializes the program: set the parameters, defines global variable "Vars.lang", and makes
    "Record" directory
    """
    Vars.instructions_All = readSystemFile("all")  # Top
    Vars.parameters = setParameters()
    Vars.lang = Vars.parameters["Language"]
    # Vars.instructions = readSystemFile(Vars.parameters["Language"])
    if not os.path.exists(Vars.record_path):
        os.makedirs(Vars.record_path)
    return
