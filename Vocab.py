# -*- coding: utf-8 -*-

from __future__ import print_function
import datetime
import string
import os
import random
import time
import pytz

os.chdir(os.path.dirname(os.path.abspath(__file__))) # Change current working directory to where this file is located

acronym = {"Petit Livre Rouge": "PLR", "Trois Mille": "TM", "Le Français 1": "LF1"}
findAcronym = {"PLR": "Petit Livre Rouge", "TM": "Trois Mille", "LF1": "Le Français 1"}
listNumber = {"zh-hk": {"Petit Livre Rouge": range(1,43), "Trois Mille": range(1,32), "Le Français 1": range(1,2)}, "zh-cn": {"Petit Livre Rouge": range(1,43), "Trois Mille": range(1,32), "Le Français 1": range(1,2)}, "ja": {"Petit Livre Rouge": [3, 5, 11, 12, 13], "Le Français 1": range(1,2)}}
lang = ""

def quitOrInput(i):
    if i.upper() == "EXIT":
        quit()
    else:
        return i

def chooseLanguage(current = None):
    """
        chooseLanguage(current = None):
        Returns language code "zh-hk", "zh-cn", or "ja"
        
        Parameters
        __________
        current: string "zh-hk", "zh-cn", or "ja"
        The current language code
    """
    langs = ["zh-hk", "zh-cn", "ja"]
    lang = raw_input("\n" + instructions_All["chooseLanguage"] + "\n").lower()
    while not lang in langs:
        if current and lang.upper() == "QUIT":
            return current
        lang = raw_input("\n" + instructions_All["chooseLanguage"] + "\n").lower()
    return lang

def chooseYorN(current = None):
    """
        choosesetYorN(current = None):
        Returns "Y" or "N"
        
        Parameters
        __________
        current: string "Y" or "N"
        The current setting
    """
    choose = ["Y", "N"]
    input = raw_input(instructions["setYorN"]).upper()
    while not input in choose:
        if current and input == "QUIT":
            return current
        input = raw_input(instructions["setYorN"]).upper()
    return input

def chooseYorNorA(current = None):
    """
        choosesetYorNorA(current = None):
        Returns "Y", "N', or "A"
        
        Parameters
        __________
        current: string "Y", "N", or "A"
        The current setting
    """
    choose = ["Y", "N", "A"]
    input = raw_input(instructions["setYorNorA"]).upper()
    while not input in choose:
        if current and input == "QUIT":
            return current
        input = raw_input(instructions["setYorNorA"]).upper()
    return input

def chooseOneTimeZone(current = None): # Choose one time zone, returns one time zone
    """
       chooseOneTimeZone(current = None)
       Chooses the time zone for one functionality (record, schedule, time), returns (1) string for time zone code and (2) bool for quitted or not
       
       Parameters
       __________
       current: string, must be in tznames below
       The current time zone
    """
    tzs = ["Hawaii", "Alaska", "LosAngeles", "Arizona", "Mountain", "Chicago", "NewYork", "UTC", "London", "Paris", "Shanghai", "Singapore", "Perth", "Tokyo", "Seoul", "Sydney"]
    tznames = ["US/Hawaii", "US/Alaska", "US/Pacific", "US/Arizona", "US/Mountain", "US/Central", "US/Eastern", "utc", "Europe/London", "Europe/Paris", "Asia/Shanghai", "Asia/Singapore", "Australia/Perth", "Asia/Tokyo", "Asia/Seoul", "Australia/Sydney"]
    choose = ""
    print("\n" + "".join(["{0:>2}. {1}".format(str(index + 1), instructions["timeZone" + tz]) for index, tz in enumerate(tzs)]))
    while (not isInt(choose)) or (not int(choose) in range(1, len(tzs) + 1)):
        if current and choose == "QUIT":
            return current, True
        choose = raw_input(instructions["setTimeZone"].replace("REPLACE", str(len(tzs)))).upper()
    return tznames[int(choose) - 1], False

def chooseTimeZone(current): # Choose one time zone in the three options, returns all three time zones
    """
        chooseTimeZone(current
        Chooses all time zones
        
        Parameters
        __________
        current: the string composed of three time zone strings joined by " ** "
        The current time zones
    """
    print("\n" + instructions["promptSetParameters"])
    print("1. {0}".format(instructions["paraTimeZoneRecord"]))
    print("2. {0}".format(instructions["paraTimeZoneSchedule"]))
    print("3. {0}".format(instructions["paraTimeZoneTime"]))
    print("4. {0}".format(instructions["paraTimeZoneUnify"]))
    choose = raw_input().upper()
    while (not isInt(choose)) or (not int(choose) in range(1, 5)):
        if choose == "QUIT":
            return current
        choose = raw_input(instructions["chooseFromAbove"].replace("REPLACE", "4")).upper()
    current = current.split(" ** ")
    choose = int(choose) - 1
    if choose in range(0,3):
        current[choose], quit = chooseOneTimeZone(current[choose])
    elif choose == 3: # If unify all time zones
        tz, quit = chooseOneTimeZone(current[0]) # current[0] is meaningless, but needed to enable the user to quit from chooseOneTimeZone()
        if quit: # If quitted
            return " ** ".join(current)
        else:
            return " ** ".join([tz] * 3)
    else:
        assert()
    return " ** ".join(current) # Record, Schedule, Time

def chooseRandom50Words(current):
    """
        chooseLanguage(current = None):
        Returns language code "zh-hk", "zh-cn", or "ja"
        
        Parameters
        __________
        current: string "zh-hk", "zh-cn", or "ja"
        The current language code
    """
    num = raw_input("\n" + instructions["chooseRandom50Words"] + "\n")
    while not (isInt(num) and int(num) >= 1) :
        if num.upper() == "QUIT":
            return current
        if not isInt(num):
            num = raw_input("\n" + instructions["enterANumber"] + "\n")
        else: # int(num) >= 1
            num = raw_input("\n" + instructions["enterAPositiveNumber"] + "\n")
    return num
                    
def getAllInstructions():
    """
        getAllInstructions()
        Returns the instructions needed to be shown before letting the user chooses system language
    """
    instructions_All = {}
    f = open(os.getcwd() + '/System Files/Instructions_all.txt')
    for s in f:
        s = s.split(": ")
        if len(s) == 1:
            s.append("") # If instruction is empty (possible because it might be non-empty for some other languages)
        instructions_All[s[0]] = s[1].replace("RETURN", "\n").replace("SPACE", " ") # With '\n'
    f.close()
    return instructions_All

def getInstructions(lang):
    """
        getInstructions(lang):
        Returns the instructions in the chosen language
        
        Paramters
        _________
        lang : string "zh-hk", "zh-cn", or "ja"
        Language code
    """
    instructions = {}
    if lang == "zh-hk":
        f = open(os.getcwd() + '/System Files/Instructions_hant.txt')
    elif lang == "zh-cn":
        f = open(os.getcwd() + '/System Files/Instructions_hans.txt')
    elif lang == "ja":
        f = open(os.getcwd() + '/System Files/Instructions_ja.txt')
    else:
        assert()
    for s in f:
        s = s.split(": ")
        if len(s) == 1:
            s.append("") # If instruction is empty (possible because it might be non-empty for some other languages)
        instructions[s[0]] = s[1].replace("RETURN", "\n").replace("SPACE", " ") # With '\n'
    f.close()
    return instructions

def setParameters():
    """
        setParameters()
        Returns the system parameters set by user, or set by default if first time of use.
    """
    par = os.getcwd() + "/System Files/Parameters.txt"
    parameters = {}
    global instructions
    global availableBooks
    if not os.path.exists(par):
        print("\n" + instructions_All["greetings"])
        lang = chooseLanguage()
        availableBooks = list(listNumber[lang])
        instructions = getInstructions(lang)
        allForRandom50Words = "A"
        comments = "Y"
        rand = "A"
        random50Words = "50"
        record = "A"
        timeZoneQuitted = True
        while timeZoneQuitted:
            timeZone, timeZoneQuitted = chooseOneTimeZone()
        parameters["AllForRandom50Words"] = allForRandom50Words
        parameters["Language"] = lang
        parameters["Random"] = rand
        parameters["Random50Words"] = random50Words
        parameters["Record"] = record
        parameters["ShowComments"] = comments
        parameters["TimeZone"] = " ** ".join([timeZone] * 3)
        f = open(par, 'w')
        for para in sorted(parameters):
            f.write(para + ": " + parameters[para] + "\n")
        f.close()
    else:
        f = open(par)
        for s in f:
            s = s.split(": ")
            if len(s) == 1:
                s.append("")
            parameters[s[0]] = s[1].rstrip("\n")
        f.close()
        instructions = getInstructions(parameters["Language"])
        availableBooks = list(listNumber[parameters["Language"]])
    return parameters

def initialization():
    """
        initialization()
        Initializes the program: set the parameters, defines global variable "lang", and makes "Record" directory
    """
    global parameters
    global lang
    global instructions_All
    instructions_All = getAllInstructions() # Top
    parameters = setParameters()
    lang = parameters["Language"]
    #instructions = getInstructions(parameters["Language"])
    if not os.path.exists(os.getcwd() + "/Record/"):
        os.makedirs(os.getcwd() + "/Record/")
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

class Word:
    """
        class Word:
        The IPA, meanings, number of meanings, and comments
    """
    def __init__(self, s):
        self.IPA = s[0] # IPA
        self.meanings = string.split(s[1].rstrip('\n'), " %% ")
        self.numOfMeanings = len(self.meanings)
        self.comments = s[2]

def chooseBook(booksToChoose = None):
    """
        chooseBook(booksToChoose = None):
        Chooses a book from the books available in the language, and returns its full name
        
        booksToChoose: list
        The list of books to choose from. If None, then choose from all available books.
    """
    if booksToChoose == None:
        booksToChoose = availableBooks
    if len(booksToChoose) == 1: # If there is only one book
        return booksToChoose[0]
    else:
        print(instructions["book1"].rstrip("\n"))
        for book in sorted(booksToChoose):
            print(instructions["book2"].replace("REPLACE1", instructions["book" + acronym[book]].rstrip("\n")).replace("REPLACE2", acronym[book]).rstrip("\n"))
        book = raw_input("\n").upper() # Select book
        while not book in findAcronym: # Book not found
            if book == 'QUIT':
                return
            book = raw_input(instructions["wrongBook"].replace("REPLACE", "".join([instructions["guillemetLeft"].rstrip("\n") + b + instructions["guillemetRight"].rstrip("\n") for b in [instructions["book" + acronym[bo]].rstrip("\n") for bo in sorted(booksToChoose)]]))).upper()
    return findAcronym[book]

def chooseList(book, all, firstList): # all: Whether load the full list or list of selected words only; theBook: the book chosen
    """
        chooseList(book, all, firstList):
        Returns the list number (int), and the bool all
        Notes: if there are at least two lists in the book, list number + "S" sets "all" to False, and "A" sets "all" to True
        
        Parameters
        __________
        book: string
        Full name of the book chosen
        
        all: bool
        Read all words from the list or not
        
        firstList: bool
        The current list is the first list added or not
    """
    if len(listNumber[lang][book]) == 1: # If there is only one list in the book
        theList = listNumber[lang][book][0] # Option to choose "select" or "all" not available
        return theList, all
    else:
        if firstList:
            theList = raw_input(instructions["chooseList"]).upper() # Select list
        else:
            theList = raw_input(instructions["chooseMoreLists"]).upper()
        while True: # If the user did not enter a number
            if not isInt(theList):
                if theList == 'QUIT':
                    print("\n")
                    return "QUIT"
                elif ("S" in theList) and isInt(theList.replace("S","")): # List number + "S" to indicate that read the list of selected words only ("S" stands for "select")
                    theList = theList.replace("S", "")
                    all = False
                    return int(theList), all
                elif ("A" in theList) and isInt(theList.replace("A","")): # List number + "A" to indicate that read the full list ("A" stands for "all")
                    theList = theList.replace("A", "")
                    all = True
                    return int(theList), all
                elif firstList == False and theList == 'N':
                    return "NO MORE"
                else:
                    if firstList:
                        theList = raw_input(instructions["enterANumber"]).upper()
                    else:
                        theList = raw_input(instructions["chooseMoreListsWrong"]).upper()
            if isInt(theList):
                theList = int(theList)
                if not theList in listNumber[lang][book]:
                    if firstList:
                        theList = raw_input(instructions["chooseListNotExists"] + "{0}\n".format(listNumber[lang][book])).upper()
                    else:
                        theList = raw_input(instructions["chooseMoreListsNotExists"] + "{0}\n".format(listNumber[lang][book])).upper()
                else:
                    return int(theList), all
    return

def addWordsFromLists(allWordsFromLists, book, lists): # Helper function of checkAllWordsInLists
    """
        addWordsFromLists(allWordsFromLists, book, lists):
        Modifies allWordsFromLists by adding all words from lists "lists" in book "book"
        
        Parameters
        __________
        allWordsFromLists: list of strings
        The list to be modified
        
        book: string, must be an available book in the language
        The full name of the book chosen
        
        lists: list
        The lists from which all words will be loaded
    """
    for enumerateList in lists:
        f = open(os.getcwd() + '/Word lists/' + book + '/lists/' + str(enumerateList) + ' ' + lang + '.txt')
        for s in f:
            s = s.rstrip("\n").split(" ** ")[0]
            if not isInt(s) and s != "":
                allWordsFromLists.append(s)
        f.close()
    return

def checkAllWordsInLists(wordList, book, lists): # Check if all words in the record or the difficult word list are in the word lists
    """
        checkAllWordsInLists(wordList, book, lists):
        Checks if all words in wordList are from lists "lists" in book "book"
        
        Parameters
        __________
        wordList: list of strings
        Words to be checked
        
        book: string, must be an available book in the language
        
        lists: list
        The lists inside which the words will be checked
    """
    allWordsFromLists = []
    passed = True
    if isinstance(book, list): # For "similar words" mode only
        for books in book:
            addWordsFromLists(allWordsFromLists, books, listNumber[lang][books])
    else:
        addWordsFromLists(allWordsFromLists, book, lists)
    for word in wordList: # Check if all the words are in the lists
        if not word in allWordsFromLists:
            if len(lists) == 1:
                print(instructions["warning"].rstrip('\n') + ": " + word + instructions["notInList"].replace("REPLACE", str(lists[0])))
            elif (not isinstance(book, list)) and sorted(lists) == sorted(listNumber[lang][book]):
                print(instructions["warning"].rstrip('\n') + ": " + word + instructions["notInBook"].replace("REPLACE", instructions["guillemetLeft"].rstrip("\n") + instructions["book" + acronym[book]].rstrip("\n") + instructions["guillemetRight"].rstrip("\n")))
            elif isinstance(book, list):
                print(instructions["warning"].rstrip('\n') + ": " + word + instructions["notInBooks"].replace("REPLACE", " & ".join([instructions["guillemetLeft"].rstrip("\n") + instructions["book" + acronym[book]].rstrip("\n") + instructions["guillemetRight"].rstrip("\n") for book in availableBooks]).rstrip("\n")))
            else:
                print(instructions["warning"].rstrip('\n') + ": " + word + instructions["notInLists"].replace("REPLACE", " & ".join(map(str, lists))))
            wordList.pop(wordList.index(word))
            passed = False
    return passed

def concatenateListNames(names):
    """
        concatenateListNames(names):
        Returns formated list names, e.g. "L1 & L2 & L4" or "L1 -- L3"
        
        Parameters
        __________
        names: list
        A list of integer list numbers
    """
    lists = sorted(names)
    if lists == range(min(lists), max(lists) + 1) and max(lists) - min(lists) >= 2:
        lists = "L" + str(min(lists)) + " -- L" + str(max(lists))
    else:
        lists = " & ".join(["L" + str(n) for n in lists])
    return lists

def loadWords(all, book, comments, Dictionary, mode, theList, wordList):
    """
        loadWords(all, book, comments, Dictionary, mode, theList, wordList):
        Adds words to Dictionary
        
        Parameters
        __________
        all: bool
        Whether add all words or not
        
        book: string, must be an available book in the language
        The book chosen
        
        comments: dictionary whose keys and contents are both strings
        All comments for words in the whole book
        
        Dictionary: dictionary whose keys are strings (words) and contents are of class Word
        The dictionary to which the words are to be added
        
        mode: 1, 2, or 3
        Mode 1: regular; Mode 2: read from record; Mode 3: read all words
        
        theList: integer, within the range of listNumber[lang][book]
        The list number
        
        wordList: lists of strings (words)
        The list of words loaded
        
    """
    bookList = os.getcwd() + '/Word lists/' + book + '/Lists/' + str(theList) + ' ' + lang + '.txt' # Directory of word list
    f = open(bookList) # Read Only
    if mode == 2:
        currentWordList = wordList
    elif mode != 2 and not all: # If normal mode
        g = open(os.getcwd() + '/Word lists/' + book + '/Difficult Words/' + str(theList) + '.txt')
        currentWordList = g.readline().rstrip('\n').split(" || ") # Read the difficult word list # Far more efficient to use currentWordList to store the difficult word list for only the current list
        g.close()
        checkAllWordsInLists(currentWordList, book, [theList]) # Only need to check the difficult word list for the current list
        wordList += currentWordList
    f.readline() # Skip the newline right after the wordlist
    if all:
        for s in f:
            s = s.split(" ** ")
            if len(s) == 3:
                word = s[0]
                s.pop(0)
                if word in comments:
                    s.append(comments[word])
                else:
                    s.append("")
                Dictionary[word] = Word(s)
                wordList.append(word)
    else:
        for s in f:
            s = s.split(" ** ")
            if s[0] in currentWordList:
                if len(s) != 3:
                    print(s)
                    assert()
                word = s[0]
                s.pop(0)
                if word in comments:
                    s.append(comments[word])
                else:
                    s.append("")
                Dictionary[word] = Word(s)
    f.close()
    return

def loadComments(book):
    """
        loadComments(book):
        Returns all comments for words in the book
        
        Parameters
        __________
        book: string, must be an available book in the language
        The book chosen
    """
    comments = {}
    if os.path.exists(os.getcwd() + '/Word lists/' + book + '/Comments.txt'):
        g = open(os.getcwd() + '/Word lists/' + book + '/Comments.txt')
        for s in g:
            if len(s.split(": ")) >= 2:
                ss = s.split(": ")
                comments[ss[0]] = ": ".join(ss[1:len(ss)]).rstrip("\n")
        g.close()
        if not checkAllWordsInLists(list(comments), book, listNumber["zh-hk"][book]):
            print("------ Sanity check for comments.------\n") # Will never happen if comments entered through addComments()
    return comments

def updateComments(update, book):
    """
        updateComments(update, book):
        Updates the comments by adding new ones and modifying old ones
        
        Parameters
        __________
        update: dictionary whose keys are all in the book and contents are the comments
        The dictionary of updated comments
        
        book: string, must be an available book in the language
        The book chosen
    """
    try:
        comments = loadComments(book)
        for w in update:
            if update[w] == '':
                if w in comments:
                    comments.pop(w)
            else:
                comments[w] = update[w]
        g = open(os.getcwd() + '/Word lists/' + book + '/Comments 2.txt', 'w')
        g.write("\n".join(["{0}: {1}".format(w, comments[w]) for w in sorted(comments)]))
        g.close()
        os.rename(os.getcwd() + '/Word lists/' + book + '/Comments 2.txt', os.getcwd() + '/Word lists/' + book + '/Comments.txt')
    except:
        print("Error occurred.\n")

def createDictionary(Dictionary, readFromRecord = None, allLists = None, defaultAll = True):
    """
        createDictionary(Dictionary, wordList):
        Creates a dictionary by asking the user to choose the book and the list, and returns the word list and the list composed of full book name and list numbers (integers)
        
        Parameters
        __________
        Dictionary: dictionary
        The dictionary the user needs to expand.
        
        readFromRecord: list. Default: None
        The list that comprises the list of words to be loaded, the book and the list number.
        
        allLists: string. Default: None
        Name of the book all of whose lists are to be loaded.
        
        defaultAll: bool. Default: True
        Whether read all words from the list BY DEFAULT or not (can be changed by user input through chooseList())
    """
    wordList = []
    book = ""
    lists = []
    alls = []
    names = []
    assert((readFromRecord == None) or (allLists == None))
    if readFromRecord != None:
        mode = 2 # Mode 2
    elif allLists != None:
        mode = 3 # Mode 3
    else:
        mode = 1 # Mode 1
    if mode == 1:
        book = chooseBook()
        firstList = True
        if book == None:
            return
        while True:
            all = defaultAll
            theListAndAll = chooseList(book, all, firstList)
            if theListAndAll == "QUIT": # Quitted
                return
            if theListAndAll == "NO MORE":
                break
            theList, all = theListAndAll
            theList = int(theList)
            lists.append(theList)
            alls.append(all)
            if len(listNumber[lang][book]) == 1:
                break
            firstList = False
    if mode == 2:
        wordList = readFromRecord[0]
        currentWordList = wordList # To comply with currentWordList used for efficiency for (mode != 2 and not all)
        book = readFromRecord[1][0]
        if isinstance(book, list): # "Similar words" mode ONLY
            assert(readFromRecord[1][1] == None)
        else:
            lists = sorted(readFromRecord[1][1:len(readFromRecord[1])])
        checkAllWordsInLists(wordList, book, lists)
        alls = [False] * len(lists)
    if mode == 3:
        assert(allLists in availableBooks)
        book = allLists
        lists = sorted(map(int, listNumber[lang][book]))
        alls = [defaultAll] * len(lists) # Not necessarily include all words even if all lists are loaded
    if isinstance(book, list):
        for books in book:
            comments = loadComments(books)
            Dictionary[books] = {}
            for theList in listNumber[lang][books]:
                loadWords(False, books, comments, Dictionary[books], mode, theList, wordList)
    else:
        comments = loadComments(book)
        for index, theList in enumerate(lists):
            loadWords(alls[index], book, comments, Dictionary, mode, theList, wordList)
    names = [book] + sorted(lists)
    return (sorted(set(wordList)), names)

def writeTime(begin, timeBegan = None, mode = None, names = None):
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
        Book name and list of words found if "find a word" mode, book name and "random XX words" if "random 50 words" mode, "similar words to WORD" if "similar words" mode, or book name and list numbers otherwise
    """
    assert((begin and timeBegan == None) or (not begin and timeBegan != None))
    assert((begin and mode == None) or (not begin and mode != None))
    assert((begin and names == None) or (not begin and names != None))
    tz = pytz.timezone(parameters["TimeZone"].split(" ** ")[2])
    timeNow = datetime.datetime.now(tz.localize(datetime.datetime.now()).tzinfo)
    timeNowYM = timeNow.strftime("%Y-%m")
    timeNowFULL = timeNow.strftime("%m/%d/%Y %H:%M:%S %Z")
    if not os.path.exists(os.getcwd() + '/Record/Time/'):
        os.makedirs(os.getcwd() + '/Record/Time/')
    if not os.path.exists(os.getcwd() + '/Record/Time/Time ' + timeNowYM + '.txt'):
        f = open(os.getcwd() + '/Record/Time/Time ' + timeNowYM + '.txt', 'w')
        if begin:
            f.write(timeNowFULL)
            f.close()
            return timeNowFULL
        else:
            f.close()
            return
    g = open(os.getcwd() + '/Record/Time/Time ' + timeNowYM + '.tmp', 'w')
    f = open(os.getcwd() + '/Record/Time/Time ' + timeNowYM + '.txt', 'r')
    try:
        if begin:
            freadlines = f.readlines()
            if freadlines != []:
                while "\n" in freadlines:
                    freadlines.pop(freadlines.index("\n"))
                if not "\n" in freadlines[len(freadlines) - 1]:
                    freadlines[len(freadlines) - 1] += "\n"
                g.write(''.join(freadlines))
            g.write(timeNowFULL)
        if not begin: # If end
            if len(names) == 2 and isinstance(names[1], str) and "random " in names[1] and " words" in names[1] and isInt(names[1].replace("random ", "").replace(" words", "")): # Random 50 words
                book = acronym[names[0]] + " "
                lists = names[1]
            elif len(names) == 1 and "similar words to " in names[0]: # Similar words
                book = ""
                lists = names[0]
            elif mode != "words found: ":
                book = acronym[names[0]] + " " # Replace the full name of the book by its acronym
                lists = concatenateListNames(names[1:len(names)])
            for s in f:
                if timeBegan in s:
                    assert(not "-" in s)
                    if (mode == "words found: ") and (len(names) == 0):
                        g.write(s.rstrip("\n") + " -- " + timeNowFULL + " no words found.\n")
                    elif mode == "words found: ":
                        g.write(s.rstrip('\n') + " -- " + timeNowFULL + " words found: " + " & ".join(names) + "\n")
                    else:
                        g.write(s.rstrip('\n') + " -- " + timeNowFULL + " " + mode + book + lists + "\n")
                else:
                    if s!= "\n":
                        g.write(s)
        f.close()
        g.close()
        os.rename(os.getcwd() + '/Record/Time/Time ' + timeNowYM + '.tmp', os.getcwd() + '/Record/Time/Time ' + timeNowYM + '.txt')
        if begin:
            return timeNowFULL
    except:
        f.close()
        g.close()
        print("Error occurred: {0} || {1} || {2} || {3}.".format(begin, timeBegan, mode, names))
    return

def describeWord(word, Word, learnMode, number = None):
    """
        describeWord(word, word, learnMode, number = None):
        Prints the descriptions of the word.
        
        Parameters
        __________
        word: string
        A word in the dictionary.
        
        Word: class Word
        The descriptions of word "word".
        
        learnMode: bool
        Whether the descriptions come after user presses enter
        
        number: array of two integers Default: None
        The first number is the number of the current word, and the second one is the total number of words in the list.
    """
    mark = False
    if number != None:
        assert len(number) == 2
        print("{0:50}{1}/{2}".format(word, number[0], number[1]))
    else:
        print(word)
    print(Word.IPA)
    if learnMode == True:
        s = raw_input().upper()
        if s == "QUIT":
            return "QUIT"
        elif (set(s) == set("MARK")) | (s[0:3] == "MAR") | (s == "MAK") | (s == 'M') | (s == 'MM'):
            s = "MARK"
        #elif s == "CM": ## Actually adding comments before meanings are shown are useless in practice, so commented out
        #    s = "COMMENTS" + raw_input(instructions["addComments"].replace("REPLACE", word)).rstrip("\n")
        #    print()
        else:
            s = s.lower()
    if Word.numOfMeanings == 1:
        print(instructions["meaning"].rstrip('\n').replace("REPLACE", "") + Word.meanings[0])
    else:
        for i in range(0, Word.numOfMeanings):
            print(instructions["meaning"].rstrip('\n').replace("REPLACE", " {0}".format(i+1)) + Word.meanings[i])
    if parameters["ShowComments"] == "Y" and Word.comments != "":
        print(instructions["comments"].rstrip('\n') + Word.comments)
    print(''.center(80, '*'))
    print()
    if learnMode == True:
        return s
    else: # Return an empty string under view mode with no input
        return ""

def writeRecord(difficultWords, mode, names):
    """
        writeRecord(difficultWords, mode, names):
        Writes the record to the file.
        
        Parameters
        __________
        difficultWords: list
        A list of difficult words
        
        mode: string, must be "learn", "recite" or "view"
        The mode
        
        names: string
        "similar words to WORD" if "similar word mode", book name and "random XX words" if "random 50 words" mode, the list that consists of the name of the book followed by the list numbers otherwise
    """
    assert (mode == 'learn') | (mode == 'recite') | (mode == 'view')
    tz = pytz.timezone(parameters["TimeZone"].split(" ** ")[0])
    timeNow = datetime.datetime.now(tz.localize(datetime.datetime.now()).tzinfo)
    if "similar words to " in names[0]:
        pathToRecord = os.getcwd() + '/Record/Others/' + timeNow.strftime("%Y-%m")
    else:
        pathToRecord = os.getcwd() + '/Record/' + names[0] + '/' + timeNow.strftime("%Y-%m")
    if not os.path.exists(pathToRecord):
        os.makedirs(pathToRecord)
    if "similar words to " in names[0]:
        lists = names[0].replace("similar words to ", "").upper()
        fileName = pathToRecord + '/' + lists + ' ' + timeNow.strftime("%m-%d ") + mode
    elif isinstance(names[1], str) and "random " in names[1] and " words" in names[1] and isInt(names[1].replace("random ", "").replace(" words", "")): # Random 50 words
        lists = names[1]
        fileName = pathToRecord + '/' + timeNow.strftime("%m-%d ") + lists + ' ' + mode
    else:
        lists = concatenateListNames(names[1:len(names)])
        fileName = pathToRecord + '/' + timeNow.strftime("%m-%d ") + lists + ' ' + mode
    if os.path.isfile(fileName + ".txt"):
        i = 2
        while os.path.isfile(fileName + " " + str(i) + ".txt"):
            i += 1
        fileName = fileName + " " + str(i) + ".txt"
    else:
        fileName = fileName + ".txt"
    f = open(fileName, 'w')
    f.write('\n'.join(difficultWords))
    f.close()
    return

def describeList(Dictionary, wordListAndNames, learnMode, rand, record, readFromRecord = False):
    """
        describeList(Dictionary, wordListAndNames, learnMode, rand, record, readFromRecord = False):
        Let user choose the book and list and prints the descriptions of the word list.
        
        Parameters
        __________
        Dictionary: dictionary
        The dictionary to be described
        
        wordListAndNames: list
        Word lists and name, the list that contains the book name and list numbers. None if quitted.
        
        learnMode: bool
        Whether the descriptions come after user presses enter
        
        rand: bool
        Whether describe the list randomly
        
        record: bool
        Whether record the difficult list
        
        readFromRecord: bool
        Whether read from record or not
    """
    if wordListAndNames == None: # If the user quitted during the creation of dictionary, quit
        return
    comments = {}
    wordList, name = wordListAndNames
    numberofwords = len(wordList)
    difficultWords = []
    quit = False
    print()
    if rand:
        random.shuffle(wordList)
    else:
        wordList = sorted(wordList)
    previousWord = ""
    i = 0
    if learnMode:
        learnOrView = "learn"
    else:
        learnOrView = "view"
    print(instructions["startDescribeList"])
    timeBegan = writeTime(begin = True)
    for word in wordList:
        i += 1
        s = raw_input().upper()
        if s != "":
            print()
            if s == "QUIT":
                quit = True
                break
            elif (set(s) == set("MARK")) | (s[0:3] == "MAR") | (s == "MAK") | (s == 'M') | (s == 'MM'):
                if previousWord:
                    difficultWords.append(previousWord)
            elif s == "CM":
                if previousWord in Dictionary: # If not in "similar words" mode
                    comments[previousWord] = raw_input(instructions["addComments"].replace("REPLACE", previousWord)).rstrip("\n")
                    print()
            elif s.upper() != s.lower():
                s = s.lower().split(" ")
                for w in s:
                    if w != "" and w != " ":
                        if w in wordList:
                            difficultWords.append(w)
                            print(instructions["markedWordSuccessfully"].replace("REPLACE", w))
                        else:
                            print(instructions["markedWordUnsuccessfully"].replace("REPLACE", w))
        if not word in Dictionary: # If Dictionary has sub-dictionaries, in "silimar words" mode
            Words = [Dictionary[dic][word] for dic in sorted(Dictionary) if word in Dictionary[dic]]
            if len(Words) > 1:
                WordsDics = [dic for dic in sorted(Dictionary) if word in Dictionary[dic]]
        else:
            Words = [Dictionary[word]]
        for index, Word in enumerate(Words):
            if len(Words) > 1:
                print(instructions["findAWordMeaningsIn"].replace("REPLACE", instructions["book" + acronym[WordsDics[index]]].rstrip("\n")))
            desc = describeWord(word, Word, learnMode, [i, numberofwords]) ## "QUIT" for quit, "MARK" for mark, "" for nothing
            if desc == "QUIT":
                quit = True
                print()
                break
            if desc == "MARK":
                difficultWords.append(word)
            #elif len(Words) == 1 and "COMMENTS" in desc: # If not in "similar words" mode ## Actually adding comments before meanings are shown are useless in practice, so commented out
            #    comments[word] = desc[len("COMMENTS"):len(desc)]
            elif desc != "" and desc.upper() != desc.lower(): # If desc is not empty and does contain English letters, mark word
                desc = desc.split(" ") # Already lower case
                for w in desc:
                    if w != "" and w != " ":
                        if w in wordList:
                            difficultWords.append(w)
                            print(instructions["markedWordSuccessfully"].replace("REPLACE", w))
                        else:
                            print(instructions["markedWordUnsuccessfully"].replace("REPLACE", w))
        if quit:
            break
        previousWord = word
    if quit == False: # If quitted, no need to input
        s = raw_input().upper() # Last input after list finished
        if (set(s) == set("MARK")) | (s[0:3] == "MAR") | (s == "MAK") | (s == 'M') | (s == 'MM'):
            difficultWords.append(previousWord) # Last word
        elif s == "CM":
            if word in Dictionary: # If not in "similar words" mode
                comments[word] = raw_input(instructions["addComments"].replace("REPLACE", word)).rstrip("\n")
                print()
    if record:
        difficultWordsInput = raw_input(instructions["difficultWordsInput"]).lower().replace("  ", " ").lstrip(" ").rstrip(" ")
        if difficultWordsInput == "quit":
            difficultWordsInput = ""
        if difficultWordsInput != "":
            difficultWordsInput = "*".join(difficultWordsInput.split(" ")).replace(" ", "").split("*") # Remove spaces
            abandoned = []
            for i, word in enumerate(difficultWordsInput):
                while not word in wordList:
                    reword = raw_input(word + instructions["wrongDifficultWordsInput"]).lower()
                    if reword != "ab":
                        difficultWordsInput[i] = reword
                        word = reword
                    else:
                        abandoned.append(i)
                        break
            if abandoned != []: # Cannot change size of the dictionary during iteration; have to pop the words abandoned after iteration
                for i, j in enumerate(abandoned):
                    j -= i
                    difficultWordsInput.pop(j)
        difficultWords += difficultWordsInput
        difficultWords = sorted(list(set(difficultWords)))
        if difficultWords:
            writeRecord(difficultWords, learnOrView, name)
    if difficultWords: # If there is any difficult word
        for i, word in enumerate(difficultWords):
            difficultWords[i] = word
        difficultWords = sorted(set(difficultWords))
        print(instructions["difficultWordList"], difficultWords, ", " + instructions["wordsInTotal"].rstrip('\n') + str(len(difficultWords)) + instructions["wordsInTotal2"])
        if quit == False:
            if raw_input(instructions["reviewRecite"]).upper() != "QUIT":
                lenDifficultWords = len(difficultWords)
                for index, word in enumerate(difficultWords):
                    if not word in Dictionary: # If Dictionary has sub-dictionaries, under "silimar words" mode
                        Words = [Dictionary[dic][word] for dic in sorted(Dictionary) if word in Dictionary[dic]]
                        if len(Words) > 1:
                            WordsDics = [dic for dic in sorted(Dictionary) if word in Dictionary[dic]]
                    else:
                        Words = [Dictionary[word]]
                    for index2, Word in enumerate(Words):
                        if len(Words) > 1:
                            print(instructions["findAWordMeaningsIn"].replace("REPLACE", instructions["book" + acronym[WordsDics[index2]]].rstrip("\n")))
                        describeWord(word, Word, False, [index + 1, lenDifficultWords])
                    if raw_input().upper() == "QUIT":
                        break
    writeTime(begin = False, timeBegan = timeBegan, mode = learnOrView + " mode " + readFromRecord * "(from record) ", names = name)
    if comments != {}:
        updateComments(comments, name[0])
    return

def formatList(wordList):
    """
        formatList(wordList):
        Formats a list of word into a nicer-looking string.
        
        Parameters
        __________
        wordList: list of strings
        A word list to be formatted
    """
    screenWidth = 80
    numberOfWordList = len(wordList)
    wordList = sorted(set(wordList))
    if sum(map(len, wordList)) + 6 * len(wordList) + 0 <= screenWidth:
        return "|" + "||".join(["  {0}  ".format(word) for word in wordList]) + "|\n"
    maxNumber = (screenWidth + 0)/(min(map(len, wordList)) + 6)
    minNumber = (screenWidth + 0)/(max(map(len, wordList)) + 6)
    numberPerLine = minNumber
    for i in range(minNumber, maxNumber + 1):
        lengths = [max(map(len, [wordList[i * k + j] for k in range(0, (numberOfWordList - 1 - j)/i + 1)])) for j in range(0, i)]
        if sum(lengths) + 6 * len(lengths) + 0 <= screenWidth:
            numberPerLine = i
        else:
            break
    lengths = [max(map(len, [wordList[numberPerLine * k + j] for k in range(0, (numberOfWordList - 1 - j)/numberPerLine + 1)])) for j in range(0, numberPerLine)]
    listOfList = [["{0:^{1}}".format(wordList[numberPerLine * k + j], lengths[j] + 4) for k in range(0, (numberOfWordList - 1 - j)/numberPerLine + 1)] for j in range(0, numberPerLine)]
    listOfList = "\n" + "\n\n".join(["|" + "||".join([listOfList[k][j] for k in range(0, min(numberPerLine, numberOfWordList - j * numberPerLine))]) + "|" for j in range(0, (numberOfWordList - 1)/numberPerLine + 1)]) + "|" * (numberOfWordList % numberPerLine != 0) + "\n"
    return listOfList

def randomAndRecord():
    """
        randomAndRecord():
        Returns two bools: true for the first one if random, and true for the second one if record. Or returns None if "quit" entered
    """
    if parameters["Random"] != "A":
        r = parameters["Random"]
    else:
        r = raw_input(instructions["random"]).upper()
    while (r != 'Y') & (r != 'N') & (r != 'QUIT'):
        r = raw_input(instructions["enterYOrN"]).upper()
    if r == 'Y':
        random = True
    elif r == 'N':
        random = False
    else:
        return
    if parameters["Record"] != "A":
        r = parameters["Record"]
    else:
        r = raw_input(instructions["record"]).upper()
    while (r != 'Y') & (r != 'N') & (r != 'QUIT'):
        r = raw_input(instructions["enterYOrN"]).upper()
    if r == 'Y':
        record = True
    elif r == 'N':
        record = False
    else:
        return
    return (random,record)

def recite(Dictionary, rnr, wordListAndNames, readFromRecord = False):
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
    if wordListAndNames is None: # If the user quitted during the creation of dictionary, quit
        return
    wordList, name = wordListAndNames
    difficultWords = []
    MaxTimes = 5
    quit = False
    numberofwords = len(wordList)
    j = 0
    print(instructions["startRecite"])
    print(instructions["startRecite2"])
    print()
    if rand:
        random.shuffle(wordList)
    else:
        wordList = sorted(wordList)
    printList = formatList(wordList)
    timeBegan = writeTime(begin = True)
    for word in wordList:
        j += 1
        print("{0}/{1}".format(j, numberofwords))
        #print("{0}/{1}\t {2} {3}".format(j, numberofwords, len(word), instructions["letters"]))
        if Dictionary[word].numOfMeanings == 1:
            print(instructions["meaning"].rstrip('\n').replace("REPLACE", "") + Dictionary[word].meanings[0])
        else:
            for i in range(0, Dictionary[word].numOfMeanings):
                print(instructions["meaning"].rstrip('\n').replace("REPLACE", " {0}".format(i+1)) + Dictionary[word].meanings[i])
        print()
        input = raw_input()
        if input.upper() == "QUIT":
            quit = True
            break
        wrongtimes = 0
        while (input.replace("é","e").replace("ï","i") != word.replace("é","e").replace("ï","i")) & (wrongtimes < MaxTimes): # Try again until being wrong for MaxTimes times
            if input.upper() == "QUIT":
                quit = True
                break
            elif input.upper() == "HINT":
                print(printList)
                input = raw_input()
                continue
            elif input.upper() == "NUMBER":
                print("{0} {1}".format(len(word.replace("-", "")), instructions["letters"]))
                input = raw_input()
                continue
            wrongtimes += 1
            print(instructions["tryAgain"])
            if wrongtimes < MaxTimes:
                input = raw_input()
        if wrongtimes == MaxTimes:
            difficultWords.append(word)
            print(Dictionary[word].IPA) # Show IPA first
            input = raw_input(instructions["tryAgain"] + "\n")
            if input.replace("é","e").replace("ï","i") != word.replace("é","e").replace("ï","i"): # If still incorrect, show descriptions
                describeWord(word, Dictionary[word], False)
                input = raw_input(instructions["tryAgain"] + "\n")
            while input.replace("é","e").replace("ï","i") != word.replace("é","e").replace("ï","i"): # Enter until correct
                if input.upper() == "QUIT":
                    quit = True
                    break
                print(instructions["tryAgain"] + "\n")
                input = raw_input()
        if quit:
            break
        print(instructions["correct"])
    if difficultWords: # If there is any difficult word
        for i, word in enumerate(difficultWords):
            difficultWords[i] = word
        difficultWords = sorted(set(difficultWords))
        print(instructions["difficultWordList"], difficultWords, ", " + instructions["wordsInTotal"].rstrip('\n') + str(len(difficultWords)) + instructions["wordsInTotal2"])
        if quit == False:
            if raw_input(instructions["reviewRecite"]).upper() != "QUIT":
                lenDifficultWords = len(difficultWords)
                for index, word in enumerate(difficultWords):
                    describeWord(word, Dictionary[word], False, [index + 1, lenDifficultWords])
                    if raw_input().upper() == "QUIT":
                        break
    elif quit == False:
        print(instructions["congratulations"])
    if record and quit == False:
        writeRecord(difficultWords, "recite", name)
    writeTime(begin = False, timeBegan = timeBegan, mode = "recite mode " + readFromRecord * "(from record) ", names = name)
    return

def learnAndView(learnMode, rnr, Dictionary = None, wordListAndNames = None, readFromRecord = False):
    """
        learnAndView(learnMode, rnr, Dictionary = None, wordListAndNames = None, readFromRecord = False):
        Learns or views.
        
        Parameters
        __________
        learnMode: bool
        Whether the learn mode (True) or the view mode (False)
        
        rnr: list of two bools
        Random and Record
        
        Dictionary: dictionary
        The dictionary to be studied.
        Must come together with wordListAndNames if a particular word list is predermined; cannot be non-None at the same time as readFromRecord
        
        wordListAndNames: list
        Word list and name.
        Must come together with Dictionary if a particular word list is predermined; cannot be non-None at the same time as readFromRecord
        
        readFromRecord: bool
        Whether read from record or not
    """
    random, record = rnr
    assert((Dictionary and (wordListAndNames and wordListAndNames[0])) or (not Dictionary and not (wordListAndNames and wordListAndNames[0]))) # The dictionary and the first item in wordListAndNames must be None or not None at the same time; TypeError would occur if only check wordListAndNames[0] when wordListAndNames = None
    if not Dictionary and not (wordListAndNames and wordListAndNames[0]) and readFromRecord == False: # Word List not assigned: not read from record and not random 50 words
        Dictionary = {}
        wordListAndNames = createDictionary(Dictionary, defaultAll = not learnMode)
        if wordListAndNames == None:
            return
    if Dictionary == {}:
        print(instructions["noWordsToStudy"])
        return
    if learnMode:
        describeList(Dictionary, wordListAndNames, True, random, record, readFromRecord = readFromRecord)
    else:
        describeList(Dictionary, wordListAndNames, False, random, record, readFromRecord = readFromRecord)
    return

def findAWord():
    """
        findAWord():
        Find a word.
    """
    wordList = []
    books = []
    pre = raw_input(instructions["findAWordChooseList"]).upper()
    firstTime = True
    if pre == "QUIT":
        return
    elif pre == "Y":
        dics = [{}]
        wordListAndNames = createDictionary(dics[0])
        if wordListAndNames is None:
            return
        wordList = wordListAndNames[0]
        books.append(wordListAndNames[1][0])
    else:
        dics = [{} for i in range(0,len(availableBooks))] # Cannot use [{}] * len(availableBooks) which would create pointers pointing to the same dic
        for index, dic in enumerate(dics):
            wordListAndNames = createDictionary(dic, allLists = availableBooks[index])
            wordList += wordListAndNames[0]
            books.append(wordListAndNames[1][0])
    wordList = sorted(list(set(wordList)))
    wordsFound = []
    wordsContaining = []
    maxWordsContaining = 50
    timeBegan = writeTime(begin = True)
    while True:
        if firstTime:
            word = raw_input(instructions["promptFindAWordLong"] + "\n").lower().split(" ")[0]
            firstTime = False
        else:
            word = raw_input(instructions["promptFindAWordShort"]).lower().split(" ")[0]
        while not word in wordList:
            if word == "quit":
                writeTime(begin = False, timeBegan = timeBegan, mode = "words found: ", names = wordsFound)
                return
            if word == "":
                word = raw_input(instructions["promptFindAWordShort"]).lower().split(" ")[0]
            else:
                tmp = ""
                if word[0:2] == "bg" or word[0:2] == "ct" or word[0:2] == "nd":
                    tmp = word[0:2]
                    word = word[2:len(word)]
                    for dic in dics:
                        for words in dic:
                            if (tmp == "bg" and words[0:len(word)] == word) or (tmp == "nd" and words[len(words)-len(word):len(words)] == word):
                                wordsContaining.append(words)
                if tmp == "" or tmp == "ct":
                    for dic in dics:
                        for words in dic:
                            if word in words or word in "\n".join(dic[words].meanings).replace("n.", "").replace("v.", "").replace("vi.", "").replace("vt.", "").replace("adj.", "").replace("adv.", "").replace("prep.", "").replace("num.", "").replace(" ", ""):
                                wordsContaining.append(words)
                wordsContaining = sorted(list(set(wordsContaining)))
                if len(wordsContaining) > maxWordsContaining:
                    word_copy = word
                    word = raw_input(instructions["moreThanMANYResults"].replace("MANY",str(maxWordsContaining))).lower().split(" ")[0]
                    if word == "":
                        print(instructions["chooseOneWord1"].rstrip("\n") + " " + word_copy + " " + instructions["chooseOneWord2"] + "\n".join(sorted(wordsContaining)) + "\n")
                        word = raw_input().lower().split(" ")[0] # Far more efficient than raw_input("\n".join(sorted(wordsContaining)))
                elif len(wordsContaining) > 1:
                    print("\n" + instructions["chooseOneWord1"].rstrip("\n") + " " + word + " " + instructions["chooseOneWord2"] + "\n".join(sorted(wordsContaining)) + "\n")
                    word = raw_input().lower().split(" ")[0]
                elif len(wordsContaining) == 1:
                    word = wordsContaining[0]
                else:
                    word = raw_input(instructions["wrongWord"]).lower().split(" ")[0]
                wordsContaining = [] # Clear words
        if word in wordList: # If not quitted
            wordsFound.append(word)
            print()
            inDics = [] # The indices of the dictionaries in list "dics" that contain the word
            for index, dic in enumerate(dics):
                if word in dic:
                    inDics.append(index)
            print(''.center(80, '*') + "\n")
            for dicIndex in inDics:
                print(instructions["findAWordMeaningsIn"].replace("REPLACE", instructions["book" + acronym[books[dicIndex]]].rstrip("\n")))
                describeWord(word, dics[dicIndex][word], False)
    return

def chooseRecord(lists):
    """
        chooseRecord(lists):
        Chooses a record
    
        Parameters
        __________
        lists: list
        List of record names
    """
    print(instructions["promptChooseRecord"])
    for number, item in enumerate(lists):
        print("{0}: {1}\n".format(number + 1, item))
    item = raw_input().upper()
    while True:
        if item == "QUIT":
            return None
        if isInt(item):
            item = int(item)
            if (item >= 1) & (item <= len(lists)):
                item = lists[item - 1]
                break
        if len(lists) > 1:
            item = raw_input(instructions["chooseRecord"].replace("REPLACE", str(len(lists)))).upper()
        else:
            item = raw_input(instructions["chooseRecord2"]).upper()
    return item

def readFromRecord():
    """
        readFromRecord():
        Chooses a record and studies.
    """
    booksInRecord = []
    path0 = os.getcwd() + '/Record/'
    for books in availableBooks:
        if os.path.exists(path0 + books + '/'):
            booksInRecord.append(books)
    book = chooseBook(booksInRecord)
    if book == None:
        return
    recordsWithDate = []
    tz = pytz.timezone(parameters["TimeZone"].split(" ** ")[0])
    date = raw_input(instructions["date"]).upper()
    while True:
        path = path0 + book + '/'
        if date == "QUIT":
            return
        if date == "T" or date == "TODAY":
            date = datetime.datetime.now(tz.localize(datetime.datetime.now()).tzinfo).strftime("%m/%d/%Y")
            continue
        if date == "Y" or date == "YESTERDAY":
            date = (datetime.datetime.now(tz.localize(datetime.datetime.now()).tzinfo) - datetime.timedelta(1)).strftime("%m/%d/%Y")
            continue
        date = string.split(date, "/")
        if len(date) != 3:
            date = raw_input(instructions["date"]).upper()
            continue # If not three elements (YYYY/MM/DD)
        try:
            date = map(int, date)
        except ValueError:
            date = raw_input(instructions["date"]).upper()
            continue # If input not convertible to int
        path = path + str(date[2]) + "-" + str(date[0]).zfill(2) + "/"
        if not os.path.exists(path):
            date = raw_input(instructions["wrongDate"]).upper()
            continue
        # If passed all preliminary tests
        date = str(date[0]).zfill(2) + "-" + str(date[1]).zfill(2)
        for files in os.listdir(path):
            if os.path.isfile(os.path.join(path, files)) and date in files:
                recordsWithDate.append(files)
        if recordsWithDate != []:
            break
        else:
            date = raw_input(instructions["wrongDate"]).upper()
    if len(recordsWithDate) == 1:
        record = recordsWithDate[0]
    record = chooseRecord(recordsWithDate)
    if record == None:
        return
    if " -- " in record: # If the list name of the record has the form "L1 -- L3"
        assert(not "&" in record)
        theLists = sorted([int(s.replace("L","")) for s in record.split(" ") if "L" in s])
        assert(len(theLists) == 2)
        theLists = range(theLists[0], theLists[1] + 1)
    elif "random" in record: # Random 50 words mode
        theLists = listNumber[lang][book]
    else:
        theLists = sorted([int(s.replace("L","")) for s in record.split(" ") if "L" in s])
    record = path + record
    f = open(record)
    wordList = []
    for word in f:
        wordList.append(word.rstrip('\n'))
    f.close()
    prompt = "\n" + instructions["promptReadRecord"]
    wordListAndNames = [wordList, [book] + theLists]
    Dictionary = {}
    createDictionary(Dictionary, readFromRecord = wordListAndNames, defaultAll = False)
    if Dictionary == {}:
        print(instructions["noWordsToStudy"])
        return True
    while True:
        s = raw_input(prompt).upper()
        if (s == "L") | (s == "LEARN"):
            rnr = randomAndRecord()
            if rnr is None:
                continue
            learnAndView(learnMode = True, rnr = rnr, Dictionary = Dictionary, wordListAndNames = wordListAndNames, readFromRecord = True)
        elif (s == "R") | (s == "RECITE"):
            rnr = randomAndRecord()
            if rnr is None:
                continue
            recite(Dictionary, rnr, wordListAndNames, readFromRecord = True)
        elif (s == "V") | (s == "VIEW") | (s == "VIEW LIST"):
            rnr = randomAndRecord()
            if rnr is None:
                continue
            learnAndView(learnMode = False, rnr = rnr, Dictionary = Dictionary, wordListAndNames = wordListAndNames, readFromRecord = True)
        elif (s == "QUIT"):
            return
    return

def viewSchedule():
    """
        viewSchedule():
        Views the schedule.
    """
    sch = os.getcwd() + "/Record/Schedule.txt"
    tz = pytz.timezone(parameters["TimeZone"].split(" ** ")[1])
    timeNow = datetime.datetime.now(tz.localize(datetime.datetime.now()).tzinfo)
    found = False
    try:
        f = open(sch)
        for s in f:
            if timeNow.strftime("%m").lstrip("0") + "/" + timeNow.strftime("%d").lstrip("0") in s or time.strftime("%m/%d") in s:
                print(s.replace("SPACE", " "))
                found = True
        if not found:
            print(instructions["noScheduleTodayAvailable"])
    except IOError:
        print(instructions["noScheduleAvailable"])
        open(sch, 'w').close()
    print(instructions["addOrCancelSchedule"])
    return

def sortDate(dateList):
    """
        sortDate(dateList):
        Sorts the dates in dateList.
        
        dateList: list of strings
        A list of dates in the format "(M)M/(D)D"
    """
    for index1 in range(0, len(dateList)):
        for index2 in range(0, len(dateList)):
            d1 = dateList[index1].split("/")
            d2 = dateList[index2].split("/")
            if (int(d2[0]) > int(d1[0])) or (int(d1[0]) == int(d2[0]) and int(d2[1]) > int(d1[1])):
                d = dateList[index1]
                dateList[index1] = dateList[index2]
                dateList[index2] = d
    return dateList

def addOrCancelSchedule(action):
    """
        addOrCancelSchedule(action):
        Adds or cancels a schedule.
        
        Parameters
        __________
        action: character "A" or "C"
        Adds a schedule if action == "A", and cancels a schedule if action == "C"
    """
    assert action == "A" or action == "C"
    f = open(os.getcwd() + "/Record/Schedule.txt")
    dates = {1: range(1,32), 2: range(1,30), 3: range(1,32), 4: range(1,31), 5: range(1,32), 6: range(1,31), 7: range(1,32), 8: range(1,32), 9: range(1,31), 10: range(1,32), 11: range(1,31), 12: range(1,32)}
    sch = {}
    for s in f:
        if len(s.split(": ")) == 2:
            sch[s.split(": ")[0]] = s.split(": ")[1].rstrip("\n")
    input = raw_input(instructions["scheduleEnterDate"]).upper()
    while True:
        if input == "QUIT":
            f.close()
            return
        elif input == "VIEW":
            for d in sortDate(list(sch)):
                print(d + ": " + sch[d].replace("SPACE", " "))
            input = raw_input(instructions["scheduleEnterDate"]).upper()
        elif not isInt(input.split("/")[0]) or not isInt(input.split("/")[1]):
            input = raw_input(instructions["scheduleEnterDate"]).upper()
            continue
        elif (not int(input.split("/")[0]) in range(1,13)) or (not int(input.split("/")[1]) in dates[int(input.split("/")[0])]):
            input = raw_input(instructions["dateNotValid"]).upper()
        elif action == "A" and input in sch:
            input = raw_input(instructions["dateAlreadyExists"]).upper()
        elif action == "C" and not input in sch:
            input = raw_input(instructions["dateDoesNotExist"]).upper()
        else:
            break
    g = open(os.getcwd() + "/Record/Schedule 0.txt", 'w')
    if action == "A":
        input2 = raw_input(instructions["scheduleEnterTask"])
        sch[input] = input2.replace(": ", ":SPACE")
        for d in sortDate(list(sch)):
            g.write(d + ": " + sch[d] + "\n")
        f.close()
        g.close()
        os.rename(os.getcwd() + "/Record/Schedule 0.txt", os.getcwd() + "/Record/Schedule.txt")
    if action == "C":
        cf = raw_input(input + ": " + sch[input].replace("SPACE", " ") + "\n" + instructions["confirmOrAbandon"]).upper()
        while cf != "Y" and cf != "N":
            cf = raw_input(instructions["enterYOrN"]).upper()
        if cf == "Y":
            sch.pop(input)
            for d in sortDate(list(sch)):
                g.write(d + ": " + sch[d] + "\n")
            g.close()
            f.close()
            os.rename(os.getcwd() + "/Record/Schedule 0.txt", os.getcwd() + "/Record/Schedule.txt")
        else:
            g.close()
            f.close()
            os.remove(os.getcwd() + "/Record/Schedule 0.txt")
    return

def allWordsOrDifficultWordListForRandom50Words():
    """
        allWordsOrDifficultWordListForRandom50Words():
        Sets parameter "AllForRandom50Words"
    """
    if parameters["AllForRandom50Words"] != "A":
        r = parameters["AllForRandom50Words"]
    else:
        r = raw_input(instructions["allForRandom50Words"].replace("REPLACE", parameters["Random50Words"])).upper()
    while (r != 'Y') & (r != 'N') & (r != 'QUIT'):
        r = raw_input(instructions["enterYOrN"]).upper()
    if r == 'Y':
        return True
    elif r == 'N':
        return False
    else:
        return

def random50Words():
    """
        random50Words():
        Studies 50 (changeable) words randomly from one book chosen.
    """
    NUMBER = int(parameters["Random50Words"])
    book = chooseBook()
    if book == None:
        return
    Dictionary = {}
    a = allWordsOrDifficultWordListForRandom50Words()
    if a == None:
        return
    else:
        wordList, names = createDictionary(Dictionary, allLists = book, defaultAll = a)
    names = [book, "random " + str(NUMBER) + " words"]
    random.shuffle(wordList)
    random.shuffle(wordList)
    prompt = "\n" + instructions["promptRandom50Words"].replace("REPLACE", parameters["Random50Words"])
    while True:
        s = raw_input(prompt).upper()
        if (s == "L") | (s == "LEARN"):
            rnr = randomAndRecord()
            if rnr is None:
                continue
            learnAndView(learnMode = True, rnr = rnr, Dictionary = Dictionary, wordListAndNames = (wordList[0:NUMBER], names))
        elif (s == "R") | (s == "RECITE"):
            rnr = randomAndRecord()
            if rnr is None:
                continue
            recite(Dictionary = Dictionary, rnr = rnr, wordListAndNames = (wordList[0:NUMBER], names))
        elif (s == "V") | (s == "VIEW") | (s == "VIEW LIST"):
            rnr = randomAndRecord()
            if rnr is None:
                continue
            learnAndView(learnMode = False, rnr = rnr, Dictionary = Dictionary, wordListAndNames = (wordList[0:NUMBER], names))
        elif (s == "S") | (s == "SHUFFLE"):
            random.shuffle(wordList)
            random.shuffle(wordList)
            print(instructions["random50WordsShuffleDone"].replace("REPLACE", parameters["Random50Words"]))
        elif (s == "QUIT"):
            return
    return

def similarWords():
    """
        similarWords():
        Studies similar words.
    """
    prompt1 = instructions["promptSimilarWords"]
    prompt2 = instructions["promptSimilarWords2"]
    try:
        f = open(os.getcwd() + "/Word lists/Similar.txt")
    except IOError:
        print(instructions["similarFileNotExists"])
        return
    word = ""
    while True:
        f.seek(0)
        if word != "r": # For CHANGE RANDOM
            word = raw_input(prompt1).lower()
        if word == "quit":
            return
        elif word == "a":
            print("\n".join(f.readlines()))
            f.seek(0)
        else:
            found = []
            if word == "random" or word == "r":
                words = [s.split(" ")[0] for s in f if len(s.split(" ")) > 1]
                random.shuffle(words)
                random.shuffle(words)
                word = words[0]
                f.seek(0)
            for s in f:
                if word in s.rstrip("\n").split(" "):
                    found += s.rstrip("\n").split(" ")
            if found == []:
                print(instructions["similarWordsNotFound"].replace("REPLACE", word))
            else:
                Dictionary = {}
                wordListAndNames = [found, [availableBooks, None]]
                createDictionary(Dictionary, readFromRecord = wordListAndNames)
                name = ["similar words to {0}".format(word)]
                while True:
                    s = raw_input("\n" + instructions["promptSimilarWords2"].replace("REPLACE", word)).upper()
                    if (s == "A"):
                        f.seek(0)
                        print("\n".join(f.readlines()))
                    if (s == "C") | (s == "CHANGE"):
                        break
                    elif (s == "CR") | (s == "CHANGE RANDOM"):
                        word = "r"
                        break
                    elif (s == "L") | (s == "LEARN"):
                        rnr = randomAndRecord()
                        if rnr is None:
                            continue
                        learnAndView(learnMode = True, rnr = rnr, Dictionary = Dictionary, wordListAndNames = (found, name))
                    elif (s == "R") | (s == "RECITE"):
                        rnr = randomAndRecord()
                        if rnr is None:
                            continue
                        recite(Dictionary = Dictionary, rnr = rnr, wordListAndNames = (found, name))
                    elif (s == "V") | (s == "VIEW") | (s == "VIEW LIST"):
                        rnr = randomAndRecord()
                        if rnr is None:
                            continue
                        learnAndView(learnMode = False, rnr = rnr, Dictionary = Dictionary, wordListAndNames = (found, name))
                    elif (s == "QUIT"):
                        return

def chooseOneList(book):
    """
        chooseOneList(book):
        Chooses only one list from the book.
        
        Parameters
        __________
        book: string, must be in the available books in the language.
        The book chosen.
    """
    list = raw_input(instructions["chooseList"])
    while True: # Choose one list only, so cannot use chooseList()
        if list.upper() == "QUIT":
            return
        elif not isInt(list):
            list = raw_input(instructions["enterANumber"])
            continue
        elif not int(list) in listNumber[lang][book]:
            print(instructions["chooseListNotExists"].rstrip("\n"))
            print(listNumber[lang][book])
            list = raw_input()
            continue
        return int(list)

def extend(book, theList, current):
    """
        extend(book, theList, current):
        Adds new difficult words from list "theList" in book "book" to the word list "current".
        
        Parameters
        __________
        book: string, must be in the available books in the language.
        The book chosen.
        
        theList: string, must be in the range of the available lists in the book in the language.
        The list chosen.
        
        current: list of strings
        The current difficult word list.
    """
    new = []
    all = []
    add = []
    i = 0
    f = open(os.getcwd() + '/Word lists/' + book + '/Lists/' + str(theList) + ' ' + lang + '.txt')
    for s in f:
        if (s != '\n') and (not isInt(s.rstrip('\n'))):
            i += 1
            word = s.split(" ** ")[0]
            all.append(word)
            if (not word in current):
                s = s.split(" ** ")
                s[0] += "\t\t" + str(i)
                s[2] = s[2].split(" %% ")
                if len(s[2]) != 1:
                    for index, meaning in enumerate(s[2]):
                        s[2][index] = str(index + 1) + ". " + meaning
                s[2] = "\n".join(s[2])
                s = "\n".join(s)
                print(s)
                input = raw_input()
                if input != "":
                    print()
                    if input.upper() == "QUIT":
                        return
                    elif input.upper()[0] in ["M", ",", "N", "J", "K"] or input == "MM":
                        new.append(word)
                    elif input.upper() != input.lower():
                        add += input.lower().split(" ")
    add2 = raw_input(instructions["difficultWordsInput"]).lower().replace("  "," ").replace("  "," ").split(" ")
    if add2 != [""] and add2 != ["quit"]:
        add += add2
    add = list(set(add))
    for w in add:
        if w in all:
            new.append(w)
        else:
            w2 = raw_input(w + instructions["wrongDifficultWordsInput"])
            while not w2 in all:
                if w2.upper() == "AB":
                    break
                w2 = raw_input(w + instructions["wrongDifficultWordsInput"])
            if w2 in all:
                new.append(w2)
    new = sorted(list(set(new)))
    return new, " || ".join(sorted(list(set(current + new))))

def chooseDifficultWordList():
    """
        chooseDifficultWordList():
        Adds new or re-select difficult word lists.
    """
    book = chooseBook()
    if book == None:
        return
    theList = chooseOneList(book)
    if theList == None:
        return
    if not os.path.exists(os.getcwd() + '/Word lists/' + book + '/Difficult Words/' + str(theList) + '.txt'):
        newOrExt = "Y"
    else:
        newOrExt = raw_input(instructions["chooseDifficultNewOrExtend"]).upper()
        while newOrExt != "Y" and newOrExt != "N":
            if newOrExt == "QUIT":
                return
            newOrExt = raw_input(instructions["chooseDifficultNewOrExtend"]).upper()
    if newOrExt == "N":
        f = open(os.getcwd() + '/Word lists/' + book + '/Difficult Words/' + str(theList) + '.txt')
        current = f.readline().rstrip("\n").split(" || ")
        f.close()
    else:
        current = []
    newAndTogether = extend(book, theList, current)
    if newAndTogether == None:
        return
    else:
        new, together = newAndTogether
    print("\n" + instructions["chooseDifficultNewlyAddedWords"].rstrip("\n"))
    print(new)
    print("\n" + instructions["chooseDifficultNowList"].rstrip("\n"))
    print(together)
    save = raw_input("\n" + instructions["confirmOrAbandon"]).upper()
    while save != "Y" and save != "N":
        if save == "QUIT":
            return
        else:
            save = raw_input("\n" + instructions["confirmOrAbandon"]).upper()
    if save == "Y":
        f = open(os.getcwd() + '/Word lists/' + book + '/Difficult Words/' + str(theList) + '.txt', 'w')
        f.write(together)
        f.close()
    return

def addComments():
    """
        addComments():
        Adds comments to words from one chosen book.
    """
    book = chooseBook()
    if book == None:
        return
    allWordsFromBook = []
    addWordsFromLists(allWordsFromBook, book, listNumber["zh-hk"][book])
    comments = {}
    s = raw_input(instructions["promptAddComments"]).lower()
    while s != "quit":
        if s == "":
            s = raw_input(instructions["promptAddComments"]).lower().replace(" ", "")
            continue
        elif not s in allWordsFromBook:
            print(s + instructions["notInBook"].rstrip("\n").replace("REPLACE", instructions["guillemetLeft"].rstrip("\n") + instructions["book" + acronym[book]].rstrip("\n") + instructions["guillemetRight"].rstrip("\n")) + instructions["reenter"].rstrip("\n"))
            s = raw_input("").lower().lower().replace(" ", "")
            continue
        else:
            c = raw_input(instructions["addComments"].replace("REPLACE", s))
            if c.upper() == "QUIT":
                s2 = raw_input(instructions["addCommentsQuitted"].replace("REPLACE1", c).replace("REPLACE2", s))
                if s2.upper() == "QUIT":
                    comments[s] = s2
                    s = raw_input(instructions["promptAddComments"]).lower()
                else:
                    s = s2.lower()
                continue
            comments[s] = c
            s = raw_input(instructions["promptAddComments"]).lower()
    updateComments(comments, book)
    return

def moreOptions():
    """
        moreOptions():
        Provides more options besides those shown in the main menu.
    """
    prompt = "\n" + instructions["moreOptions"].replace("REPLACE", parameters["Random50Words"])
    while True:
        s = quitOrInput(raw_input(prompt)).upper()
        if (s == "C") | (s == "COMMENT") | (s == "COMMENTS"):
            addComments()
        elif (s == "D") | (s == "DIFFICULT") | (s == "DIFFICULT WORD LIST"):
            chooseDifficultWordList()
        elif (s == "SC") | (s == "SCHEDULE") | (s == "VIEW SCHEDULE"):
            viewSchedule()
        elif (s == "SCA"):
            addOrCancelSchedule("A")
        elif (s == "SCC"):
            addOrCancelSchedule("C")
        elif (s == "SI") | (s == "SIMILAR") | (s == "SIMILAR WORDS"):
            similarWords()
        elif (s == "R") | (s == "RANDOM") | (s == "RANDOM 50 WORDS"):
            random50Words()
        elif (s == "QUIT"):
            return
    return

def changeParameters():
    """
        changeParameters():
        Changes one system parameter.
    """
    global instructions
    global parameters
    global lang
    instructions["paraAllForRandom50Words"] = instructions["paraAllForRandom50Words"].replace("REPLACE", parameters["Random50Words"])
    instructions["paraRandom50Words"] = instructions["paraRandom50Words"].replace("REPLACE", parameters["Random50Words"])
    prompt = "\n" + instructions["promptSetParameters"] + "".join([str(index + 1) + ". " + instructions["para" + par] + "\n" for index, par in enumerate(sorted(parameters))])
    choose = quitOrInput(raw_input(prompt)).upper()
    if choose == "QUIT":
        return
    while not (isInt(choose) and int(choose) >= 1 and int(choose) <= len(parameters)):
        choose = quitOrInput(raw_input(prompt)).upper()
        if choose == "QUIT":
            return
    choose = sorted(parameters)[int(choose) - 1]
    if choose == "AllForRandom50Words":
        setChoose = chooseYorNorA(parameters["AllForRandom50Words"])
    elif choose == "Language":
        setChoose = chooseLanguage(parameters["Language"])
    elif choose == "Random":
        setChoose = chooseYorNorA(parameters["Random"])
    elif choose == "Random50Words":
        setChoose = chooseRandom50Words(parameters["Random50Words"])
    elif choose == "Record":
        setChoose = chooseYorNorA(parameters["Record"])
    elif choose == "ShowComments":
        setChoose = chooseYorN(parameters["ShowComments"])
    elif choose == "TimeZone":
        setChoose = chooseTimeZone(parameters["TimeZone"])
    else:
        assert()
    f = open(os.getcwd() + "/System Files/Parameters.txt")
    g = open(os.getcwd() + "/System Files/Parameters 2.txt", 'w')
    for s in f:
        if s.split(": ")[0] == choose:
            s = choose + ": " + setChoose + "\n"
        g.write(s)
    f.close()
    g.close()
    os.rename(os.getcwd() + "/System Files/Parameters 2.txt", os.getcwd() + "/System Files/Parameters.txt")
    parameters = setParameters()
    lang = parameters["Language"]
    instructions = getInstructions(lang)
    print(instructions["changesSaved"])
    return

def study():
    """
        study():
        Studies.
    """
    global instructions
    prompt = "\n" + instructions["promptStudy"]
    while True:
        s = quitOrInput(raw_input(prompt)).upper()
        if (s == "L") | (s == "LEARN"):
            rnr = randomAndRecord()
            if rnr is None:
                continue
            learnAndView(True, rnr)
        elif (s == "R") | (s == "RECITE"):
            rnr = randomAndRecord()
            if rnr is None:
                continue
            Dictionary = {}
            wordListAndNames = createDictionary(Dictionary, defaultAll = False)
            if wordListAndNames == None:
                continue
            recite(Dictionary, rnr, wordListAndNames)
        elif (s == "F") | (s == "FIND") | (s == "FIND A") | (s == "FIND A WORD"):
            findAWord()
        elif (s == "V") | (s == "VIEW") | (s == "VIEW LIST"):
            rnr = randomAndRecord()
            if rnr is None:
                continue
            learnAndView(False, rnr)
        elif (s == "RR") | (s == "READ") | (s == "READ FROM") | (s == "READ FROM RECORD"):
            while readFromRecord():
                1
        elif (s == "M") | (s == "MORE") | (s == "MORE OPTIONS"):
            moreOptions()
        elif (s == "S") | (s == "SP") | (s == "SET") | (s == "SET PARAMETERS"):
            changeParameters()
            prompt = instructions["promptStudy"]
        elif (s == "QUIT"):
            print(instructions["bye"])
            return
    return

initialization()
study()
