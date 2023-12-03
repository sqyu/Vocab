import os
import numpy as np

pathToWordList = "/Users/shimizumasami/Desktop/\xe6\xb8\x85\xe6\xb0\xb4\xe6\xad\xa3\xe5\xb7\xb3\xe3\x81\xae\xe3\x83\x95\xe3\x82\xa9\xe3\x83\xab\xe3\x82\xbf\xe3\x82\x99/\xe5\x80\x8b\xe4\xba\xba\xe7\x94\xa8/\xe5\x8b\x89\xe5\xbc\xb7/@Umich/GRE/Vocabulary/Vocabulary/Word lists/"

def printNames():
    Ass = __import__(inspect.getmodulename(__file__))
    for name in dir(Ass):
        obj = getattr(Ass, name)
        if inspect.isfunction(obj):
            print(obj.__name__)
    return

def isInt(s, min = 1, max = np.inf):
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

def strip(s):
    return s.lower().replace("\xc3\xa0", "a").replace("\xc3\xa1", "a").replace("\xc3\xa2", "a").replace("\xc3\xa7", "c").replace("\xc3\xa8", "e").replace("\xc3\xa9", "e").replace("\xc3\xaa", "e").replace("\xc3\xab", "e").replace("\xc3\xae", "i").replace("\xc3\xaf", "i").replace("\xc3\xb4", "o").replace("\xc5\x93", "oe").replace("\xc3\xbb", "u")

def main():
    os.chdir(pathToWordList)
    ls = os.listdir(pathToWordList) ## book names
    lsn = [] ## possible Francais book names
    for i, e in enumerate(ls):
        if "Fran" in e: ## if belongs to le francais
            lsn += [e.replace("Le Franc\xcc\xa7ais ", "")]
    if len(lsn) == 1:
        chosen = "1"
    else:
        lsn = sorted(lsn)
        r = ""
        while not r in lsn:
            r = raw_input("Please choose a book number from the following: " + ", ".join(lsn))
        chosen = r
    os.chdir(os.getcwd() + "/Le Franc\xcc\xa7ais " + chosen + "/Lists/")
    inp = ""
    while inp.upper() != 'Q' and inp.upper() != "QUIT":
        inp = raw_input("Please choose from the following: generate lists (G), sort lists (S), or quit (Q).\n").upper()
        if inp == 'Q' or inp == "QUIT":
            break
        if inp == "G":
            filename = raw_input("Please enter the list number.\n")
            while not os.path.exists(filename + ".txt"):
                filename = raw_input("Please enter a correct list number.\n")
                if filename.upper() == "Q" or filename.upper() == "QUIT":
                    break
            command = raw_input("Enter \"S\" to skip sorting, enter \"O\" to only make one copy.\n")
            f = open(filename + ".txt")
            l = f.readlines()
            if not "S" in command.upper():
                l = sorted(l, cmp = lambda x, y: cmp(strip(x), strip(y)))
            l = "\n1\n" + "".join([i.replace("\n","") + " ** [] ** \n" for i in l])
            if "O" in command.upper():
                lang = ["en"]
            else:
                lang = ["en", "ja", "zh-cn", "zh-hk"]
            for st in lang:
                g = open(filename + " {0}.txt".format(st), 'w')
                g.write(l)
                g.close()

if __name__ == "__main__":
    main()


