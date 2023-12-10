import Help_funs

record_path = "Record"
sys_path = "System Files"
wordLists_path = "Word lists"

langs = ["zh-hk", "zh-cn", "ja", "en"]

acronym = {
    "Petit Livre Rouge": "PLR",
    "Trois Mille": "TM",
    "Le Français 1": "LF1",
    "Duo_de": "DE",
    "Français": "F",
    "IELTS": "IELTS",
    "Hyojun Nihongo": "HJNHG",
}
findAcronym = {value: key for key, value in acronym.items()}

listNumber = {
    "zh-hk": {
        "Petit Livre Rouge": list(range(1, 43)),
        "Trois Mille": list(range(1, 32)),
        "Le Français 1": list(range(1, 2)),
        "Duo_de": range(1, 2),
        "IELTS": range(1, 49),
        "Hyojun Nihongo": list(range(1, 2)),
    },
    "zh-cn": {
        "Petit Livre Rouge": list(range(1, 43)),
        "Trois Mille": list(range(1, 32)),
        "Le Français 1": list(range(1, 2)),
        "IELTS": range(1, 49),
    },
    "ja": {
        "Petit Livre Rouge": [3, 5, 11, 12, 13],
        "Le Français 1": list(range(1, 2)),
        "Français": [2],
    },
    "en": {"Le Français 1": range(1, 2), "Français": [2], "Duo_de": range(1, 2)},
}

conjNumber = {"Duo_de": range(1, 2), "Français": [2]}
lang = ""
parameters = {}
instructions = {}
instructions_All = {}
availableBooks = []

tzs = [
    "Hawaii",
    "Alaska",
    "LosAngeles",
    "Arizona",
    "Mountain",
    "Chicago",
    "NewYork",
    "UTC",
    "London",
    "Paris",
    "Shanghai",
    "Singapore",
    "Perth",
    "Tokyo",
    "Seoul",
    "Sydney",
]
tznames = [
    "US/Hawaii",
    "US/Alaska",
    "US/Pacific",
    "US/Arizona",
    "US/Mountain",
    "US/Central",
    "US/Eastern",
    "utc",
    "Europe/London",
    "Europe/Paris",
    "Asia/Shanghai",
    "Asia/Singapore",
    "Australia/Perth",
    "Asia/Tokyo",
    "Asia/Seoul",
    "Australia/Sydney",
]


def getInst(key, rep=None):
    s = instructions[key].rstrip("\n")
    if rep is not None:
        if isinstance(rep, str):
            s = s.replace("REPLACE", rep)
        else:
            for pair in rep:
                s = s.replace(pair[0], pair[1])
    return s


def printInst(key, rep=None, add=""):
    print(getInst(key, rep) + add)


def inpInst(key, rep=None, add="", handleQuit=True):
    if handleQuit:
        return Help_funs.quitOrInput(getInst(key, rep) + add)
    else:
        printInst(key, rep=rep, add="")
        return input()
