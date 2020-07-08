# -*- coding: utf-8 -*-


import datetime
import string
import os
import random
import time
import pytz
import re
import unidecode

from Help_funs import isInt, QuitException, quitOrInput, sortDate
import Settings
import Vars
import Word

def chooseBook(booksToChoose = None):
	"""
		chooseBook(booksToChoose = None):
		Chooses a book from the books available in the language, and returns its full name
		
		booksToChoose: list
		The list of books to choose from. If None, then choose from all available books.
	"""
	if booksToChoose == None:
		booksToChoose = Vars.availableBooks
	if len(booksToChoose) == 1: # If there is only one book
		return booksToChoose[0]
	else:
		print(Vars.instructions["book1"].rstrip("\n"))
		for book in sorted(booksToChoose):
			print(Vars.instructions["book2"].replace("REPLACE1", Vars.instructions["book" + Vars.acronym[book]].rstrip("\n")).replace("REPLACE2", Vars.acronym[book]).rstrip("\n"))
		book = input("\n").upper() # Select book
		while not book in Vars.findAcronym: # Book not found
			if book == 'QUIT':
				return
			book = input(Vars.instructions["wrongBook"].replace("REPLACE", "".join([Vars.instructions["guillemetLeft"].rstrip("\n") + b + Vars.instructions["guillemetRight"].rstrip("\n") for b in [Vars.instructions["book" + Vars.acronym[bo]].rstrip("\n") for bo in sorted(booksToChoose)]]))).upper()
	return Vars.findAcronym[book]

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
	if len(Vars.listNumber[Vars.lang][book]) == 1: # If there is only one list in the book
		theList = Vars.listNumber[Vars.lang][book][0] # Option to choose "select" or "all" not available
		return theList, all
	else:
		if firstList:
			theList = input(Vars.instructions["chooseList"]).upper() # Select list
		else:
			theList = input(Vars.instructions["chooseMoreLists"]).upper()
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
						theList = input(Vars.instructions["enterANumber"]).upper()
					else:
						theList = input(Vars.instructions["chooseMoreListsWrong"]).upper()
			if isInt(theList):
				theList = int(theList)
				if not theList in Vars.listNumber[Vars.lang][book]:
					if firstList:
						theList = input(Vars.instructions["chooseListNotExists"] + "{0}\n".format(Vars.listNumber[Vars.lang][book])).upper()
					else:
						theList = input(Vars.instructions["chooseMoreListsNotExists"] + "{0}\n".format(Vars.listNumber[Vars.lang][book])).upper()
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
		f = open(os.path.join(Vars.wordLists_path, book, 'lists', str(enumerateList) + ' ' + Vars.lang + '.txt'))
		for s in f:
			s = s.rstrip("\n").split(" ** ")[0].lower()
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
			addWordsFromLists(allWordsFromLists, books, Vars.listNumber[Vars.lang][books])
	else:
		addWordsFromLists(allWordsFromLists, book, lists)
	for word in wordList: # Check if all the words are in the lists
		if not word in allWordsFromLists:
			if len(lists) == 1:
				print(Vars.instructions["warning"].rstrip('\n') + ": " + word + Vars.instructions["notInList"].replace("REPLACE", str(lists[0])))
			elif (not isinstance(book, list)) and sorted(lists) == sorted(Vars.listNumber[Vars.lang][book]):
				print(Vars.instructions["warning"].rstrip('\n') + ": " + word + Vars.instructions["notInBook"].replace("REPLACE", Vars.instructions["guillemetLeft"].rstrip("\n") + Vars.instructions["book" + Vars.acronym[book]].rstrip("\n") + Vars.instructions["guillemetRight"].rstrip("\n")))
			elif isinstance(book, list):
				print(Vars.instructions["warning"].rstrip('\n') + ": " + word + Vars.instructions["notInBooks"].replace("REPLACE", " & ".join([Vars.instructions["guillemetLeft"].rstrip("\n") + Vars.instructions["book" + Vars.acronym[book]].rstrip("\n") + Vars.instructions["guillemetRight"].rstrip("\n") for book in Vars.availableBooks]).rstrip("\n")))
			else:
				print(Vars.instructions["warning"].rstrip('\n') + ": " + word + Vars.instructions["notInLists"].replace("REPLACE", " & ".join(map(str, lists))))
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
	if lists == list(range(min(lists), max(lists) + 1)) and max(lists) - min(lists) >= 2:
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
		
		theList: integer, within the range of Vars.listNumber[Vars.lang][book]
		The list number
		
		wordList: lists of strings (words)
		The list of words loaded
		
	"""
	bookList = os.path.join(Vars.wordLists_path, book, 'Lists', str(theList) + ' ' + Vars.lang + '.txt') # Directory of word list
	f = open(bookList) # Read Only
	difficultWordFile = os.path.join(Vars.wordLists_path, book, 'Difficult Words', str(theList) + '.txt')
	if mode != 2 and not all and (not os.path.exists(difficultWordFile)): # If normal mode and difficult word lists do not exist, read all words
		print(Vars.instructions["noDifficultWordList"].rstrip('\n').replace("LIST", str(theList)).replace("BOOK", Vars.instructions["book" + Vars.acronym[book]].rstrip('\n')))
		all = True
	if mode == 2:
		currentWordList = wordList
	elif mode != 2 and not all: # If normal mode but not reading all words
		g = open(difficultWordFile)
		currentWordList = re.split("\s*\|+\s*", g.readline().lower().rstrip('\n')) # Read the difficult word list # Far more efficient to use currentWordList to store the difficult word list for only the current list
		g.close()
		checkAllWordsInLists(currentWordList, book, [theList]) # Only need to check the difficult word list for the current list
		wordList += currentWordList
	f.readline() # Skip the newline right after the wordlist
	if all:
		for s in f:
			s = s.split(" ** ")
			if len(s) == 3:
				word = s[0].lower()
				s.pop(0)
				if word in comments:
					s.append(comments[word])
				else:
					s.append("")
				Dictionary[word] = Word.Word(s)
				wordList.append(word)
	else:
		for s in f:
			s = s.split(" ** ")
			if s[0].lower() in currentWordList:
				if len(s) != 3:
					print(s)
					assert()
				word = s[0].lower()
				s.pop(0)
				if word in comments:
					s.append(comments[word])
				else:
					s.append("")
				Dictionary[word] = Word.Word(s)
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
	if os.path.exists(os.path.join(Vars.wordLists_path, book, 'Comments.txt')):
		g = open(os.path.join(Vars.wordLists_path, book, 'Comments.txt'))
		for s in g:
			if len(s.split(": ")) >= 2:
				ss = s.split(": ")
				comments[ss[0].lower()] = ": ".join(ss[1:len(ss)]).rstrip("\n")
		g.close()
		if not checkAllWordsInLists(list(comments), book, Vars.listNumber[Vars.lang][book]):
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
			w = w.lower()
			if update[w] == '':
				if w in comments:
					comments.pop(w)
			else:
				comments[w] = update[w]
		g = open(os.path.join(Vars.wordLists_path, book, 'Comments 2.txt'), 'w')
		g.write("\n".join(["{0}: {1}".format(w, comments[w]) for w in sorted(comments)]))
		g.close()
		os.rename(os.path.join(Vars.wordLists_path, book, 'Comments 2.txt'), os.path.join(Vars.wordLists_path, book, 'Comments.txt'))
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
			if len(Vars.listNumber[Vars.lang][book]) == 1:
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
		assert(allLists in Vars.availableBooks)
		book = allLists
		lists = sorted(map(int, Vars.listNumber[Vars.lang][book]))
		alls = [defaultAll] * len(lists) # Not necessarily include all words even if all lists are loaded
	if isinstance(book, list):
		for books in book:
			comments = loadComments(books)
			Dictionary[books] = {}
			for theList in Vars.listNumber[Vars.lang][books]:
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
	tz = pytz.timezone(Vars.parameters["TimeZone"].split(" ** ")[2])
	timeNow = datetime.datetime.now(tz.localize(datetime.datetime.now()).tzinfo)
	timeNowYM = timeNow.strftime("%Y-%m")
	timeNowFULL = timeNow.strftime("%m/%d/%Y %H:%M:%S %Z")
	if not os.path.exists(os.path.join(Vars.record_path, 'Time')):
		os.makedirs(os.path.join(Vars.record_path, 'Time'))
	if not os.path.exists(os.path.join(Vars.record_path, 'Time', 'Time ' + timeNowYM + '.txt')):
		f = open(os.path.join(Vars.record_path, 'Time', 'Time ' + timeNowYM + '.txt'), 'w')
		if begin:
			f.write(timeNowFULL)
			f.close()
			return timeNowFULL
		else:
			f.close()
			return
	g = open(os.path.join(Vars.record_path, 'Time', 'Time ' + timeNowYM + '.tmp'), 'w')
	f = open(os.path.join(Vars.record_path, 'Time', 'Time ' + timeNowYM + '.txt'), 'r')
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
				book = Vars.acronym[names[0]] + " "
				lists = names[1]
			elif len(names) == 1 and "similar words to " in names[0]: # Similar words
				book = ""
				lists = names[0]
			elif mode != "words found: ":
				book = Vars.acronym[names[0]] + " " # Replace the full name of the book by its Vars.acronym
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
		os.rename(os.path.join(Vars.record_path, 'Time', 'Time ' + timeNowYM + '.tmp'), os.path.join(Vars.record_path, 'Time', 'Time ' + timeNowYM + '.txt'))
		if begin:
			return timeNowFULL
	except:
		f.close()
		g.close()
		print("Error occurred: {0} || {1} || {2} || {3}.".format(begin, timeBegan, mode, names))
	return

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
	tz = pytz.timezone(Vars.parameters["TimeZone"].split(" ** ")[0])
	timeNow = datetime.datetime.now(tz.localize(datetime.datetime.now()).tzinfo)
	if "similar words to " in names[0]:
		pathToRecord = os.path.join(Vars.record_path, 'Others', timeNow.strftime("%Y-%m"))
	else:
		pathToRecord = os.path.join(Vars.record_path, names[0], timeNow.strftime("%Y-%m"))
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
	print()
	if rand:
		random.shuffle(wordList)
	else:
		wordList = sorted(wordList)
	previousWord = ""
	i = 0
	learnOrView = "learn" if learnMode else "view"
	print(Vars.instructions["startDescribeList"])
	timeBegan = writeTime(begin = True)
	try:
		for word in wordList:
			i += 1
			s = input().upper()
			if s != "":
				print()
				if s == "QUIT":
					raise QuitException
				elif Word.markWordorNot(s):
					if previousWord:
						difficultWords.append(previousWord)
						print(Vars.instructions["markedWordSuccessfully"].replace("REPLACE", previousWord))
				elif s == "CM":
					if previousWord in Dictionary: # If not in "similar words" mode
						comments[previousWord] = input(Vars.instructions["addComments"].replace("REPLACE", previousWord)).rstrip("\n")
						print()
				else:
					for w in re.split("\s*\|+\s*", s.lower()):
						if w != "" and w != " ":
							if w in wordList:
								difficultWords.append(w)
								print(Vars.instructions["markedWordSuccessfully"].replace("REPLACE", w))
							else:
								print(Vars.instructions["markedWordUnsuccessfully"].replace("REPLACE", w))
			if not word in Dictionary: # If Dictionary has sub-dictionaries, in "silimar words" mode
				Words = [Dictionary[dic][word] for dic in sorted(Dictionary) if word in Dictionary[dic]]
				if len(Words) > 1:
					WordsDics = [dic for dic in sorted(Dictionary) if word in Dictionary[dic]]
			else:
				Words = [Dictionary[word]]
			for index, Word_obj in enumerate(Words):
				if len(Words) > 1:
					print(Vars.instructions["findAWordMeaningsIn"].replace("REPLACE", Vars.instructions["book" + Vars.acronym[WordsDics[index]]].rstrip("\n")))
				s = Word.describeWord(word, Word_obj, learnMode, [i, numberofwords]) ## "QUIT" for quit, "MARK" for mark, "" for nothing
				if Word.markWordorNot(s):
					difficultWords.append(word)
					print(Vars.instructions["markedWordSuccessfully"].replace("REPLACE", word))
				elif s != "": # If s is not empty, mark words in s
					for w in re.split("\s*\|+\s*", s): # Split s by | and add each word if they exist; already changed to lower case in describeWord()
						if w in wordList:
							difficultWords.append(w)
							print(Vars.instructions["markedWordSuccessfully"].replace("REPLACE", w))
						else:
							print(Vars.instructions["markedWordUnsuccessfully"].replace("REPLACE", w))
			previousWord = word
		s = input().upper() # Last input after list finished
		if Word.markWordorNot(s):
			difficultWords.append(previousWord) # Last word
			print(Vars.instructions["markedWordSuccessfully"].replace("REPLACE", previousWord))
		elif s == "CM":
			if previousWord in Dictionary: # If not in "similar words" mode
				comments[previousWord] = input(Vars.instructions["addComments"].replace("REPLACE", previousWord)).rstrip("\n") # Add comment for the last word
				print()
		quit = False
	except QuitException:
		quit = True
	if record:
		difficultWordsInput = input(Vars.instructions["difficultWordsInput"]).lower().strip()
		if difficultWordsInput == "quit": # Ignore
			difficultWordsInput = ""
		if difficultWordsInput != "":
			difficultWordsInput = re.split("\s*\|+\s*", difficultWordsInput) # Split words by |
			abandoned = []
			for i, word in enumerate(difficultWordsInput):
				while not word in wordList:
					reword = input(word + Vars.instructions["wrongDifficultWordsInput"]).lower()
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
		difficultWords = sorted(set(difficultWords))
		if difficultWords:
			writeRecord(difficultWords, learnOrView, name)
	if difficultWords: # If there is any difficult word
		for i, word in enumerate(difficultWords):
			difficultWords[i] = word
		if not record: # Should have been sorted above if record == True
			difficultWords = sorted(set(difficultWords))
		print(Vars.instructions["difficultWordList"], difficultWords, ", " + Vars.instructions["wordsInTotal"].rstrip('\n') + str(len(difficultWords)) + Vars.instructions["wordsInTotal2"])
		if quit == False:
			if input(Vars.instructions["reviewRecite"]).upper() != "QUIT":
				lenDifficultWords = len(difficultWords)
				for index, word in enumerate(difficultWords):
					if not word in Dictionary: # If Dictionary has sub-dictionaries, under "silimar words" mode
						Words = [Dictionary[dic][word] for dic in sorted(Dictionary) if word in Dictionary[dic]]
						if len(Words) > 1:
							WordsDics = [dic for dic in sorted(Dictionary) if word in Dictionary[dic]]
					else:
						Words = [Dictionary[word]]
					for index2, Word_obj in enumerate(Words):
						if len(Words) > 1:
							print(Vars.instructions["findAWordMeaningsIn"].replace("REPLACE", Vars.instructions["book" + Vars.acronym[WordsDics[index2]]].rstrip("\n")))
						Word.describeWord(word, Word_obj, False, [index + 1, lenDifficultWords]) # learnMode == False, so QUIT ignored
					if input().upper() == "QUIT":
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
	maxNumber = (screenWidth + 0) // (min(list(map(len, wordList))) + 6)
	minNumber = (screenWidth + 0) // (max(list(map(len, wordList))) + 6)
	numberPerLine = minNumber
	for i in range(minNumber, maxNumber + 1):
		lengths = [max(list(map(len, [wordList[i * k + j] for k in range(0, (numberOfWordList - 1 - j) // i + 1)]))) for j in range(0, i)]
		if sum(lengths) + 6 * len(lengths) + 0 <= screenWidth:
			numberPerLine = i
		else:
			break
	lengths = [max(list(map(len, [wordList[numberPerLine * k + j] for k in range(0, (numberOfWordList - 1 - j) // numberPerLine + 1)]))) for j in range(0, numberPerLine)]
	listOfList = [["{0:^{1}}".format(wordList[numberPerLine * k + j], lengths[j] + 4) for k in range(0, (numberOfWordList - 1 - j) // numberPerLine + 1)] for j in range(0, numberPerLine)]
	listOfList = "\n" + "\n\n".join(["|" + "||".join([listOfList[k][j] for k in range(0, min(numberPerLine, numberOfWordList - j * numberPerLine))]) + "|" for j in range(0, (numberOfWordList - 1) // numberPerLine + 1)]) + "|" * (numberOfWordList % numberPerLine != 0) + "\n"
	return listOfList

def randomAndRecord():
	"""
		randomAndRecord():
		Returns two bools: true for the first one if random, and true for the second one if record. Or returns None if "quit" entered
	"""
	if Vars.parameters["Random"] != "A":
		r = Vars.parameters["Random"]
	else:
		r = input(Vars.instructions["random"]).upper()
	while (r != 'Y') & (r != 'N') & (r != 'QUIT'):
		r = input(Vars.instructions["enterYOrN"]).upper()
	if r == 'Y':
		random = True
	elif r == 'N':
		random = False
	else:
		return
	if Vars.parameters["Record"] != "A":
		r = Vars.parameters["Record"]
	else:
		r = input(Vars.instructions["record"]).upper()
	while (r != 'Y') & (r != 'N') & (r != 'QUIT'):
		r = input(Vars.instructions["enterYOrN"]).upper()
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
	print(Vars.instructions["startRecite"])
	print(Vars.instructions["startRecite2"])
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
		#print("{0}/{1}\t {2} {3}".format(j, numberofwords, len(word), Vars.instructions["letters"]))
		Word.printMeanings(Dictionary[word])
		print()
		user_input = input()
		if user_input.upper() == "QUIT":
			quit = True
			break
		wrongtimes = 0
		while (unidecode.unidecode(user_input).lower() != unidecode.unidecode(word).lower()) & (wrongtimes < MaxTimes): # Try again until being wrong for MaxTimes times; ignores accents
			if user_input.upper() == "QUIT":
				quit = True
				break
			elif user_input.upper() == "HINT":
				print(printList)
				user_input = input()
				continue
			elif user_input.upper() == "NUMBER":
				print("{0} {1}".format(len(word.replace("-", "")), Vars.instructions["letters"]))
				user_input = input()
				continue
			wrongtimes += 1
			print(Vars.instructions["tryAgain"])
			if wrongtimes < MaxTimes:
				user_input = input()
		if wrongtimes == MaxTimes:
			difficultWords.append(word)
			print(Dictionary[word].IPA) # Show IPA first
			user_input = input(Vars.instructions["tryAgain"] + "\n")
			if unidecode.unidecode(user_input).lower() != unidecode.unidecode(word).lower(): # If still incorrect, show descriptions
				Word.describeWord(word, Dictionary[word], False) # Does not raise QuitException since learnMode == False
				user_input = input(Vars.instructions["tryAgain"] + "\n")
			while unidecode.unidecode(user_input).lower() != unidecode.unidecode(word).lower(): # Enter until correct; ignores accents
				if user_input.upper() == "QUIT":
					quit = True
					break
				print(Vars.instructions["tryAgain"] + "\n")
				user_input = input()
			print(Vars.instructions["markedWordSuccessfully"].replace("REPLACE", word))
		if quit:
			break
		print(Vars.instructions["correct"])
	if difficultWords: # If there is any difficult word
		for i, word in enumerate(difficultWords):
			difficultWords[i] = word
		difficultWords = sorted(set(difficultWords))
		print(Vars.instructions["difficultWordList"], difficultWords, ", " + Vars.instructions["wordsInTotal"].rstrip('\n') + str(len(difficultWords)) + Vars.instructions["wordsInTotal2"])
		if quit == False:
			if input(Vars.instructions["reviewRecite"]).upper() != "QUIT":
				lenDifficultWords = len(difficultWords)
				for index, word in enumerate(difficultWords):
					Word.describeWord(word, Dictionary[word], False, [index + 1, lenDifficultWords]) # Does not raise QuitException since learnMode == False
					if input().upper() == "QUIT":
						break
	elif quit == False:
		print(Vars.instructions["congratulations"])
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
		print(Vars.instructions["noWordsToStudy"])
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
	pre = input(Vars.instructions["findAWordChooseList"]).upper()
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
		dics = [{} for i in range(0, len(Vars.availableBooks))] # Cannot use [{}] * len(Vars.availableBooks) which would create pointers pointing to the same dic
		for index, dic in enumerate(dics):
			wordListAndNames = createDictionary(dic, allLists = Vars.availableBooks[index])
			wordList += wordListAndNames[0]
			books.append(wordListAndNames[1][0])
	wordList = sorted(list(set(wordList)))
	wordsFound = []
	wordsContaining = []
	maxWordsContaining = 50
	timeBegan = writeTime(begin = True)
	while True:
		if firstTime:
			word = input(Vars.instructions["promptFindAWordLong"] + "\n").lower()
			firstTime = False
		else:
			word = input(Vars.instructions["promptFindAWordShort"]).lower()
		while not word in wordList:
			if word == "quit":
				writeTime(begin = False, timeBegan = timeBegan, mode = "words found: ", names = wordsFound)
				return
			if word == "":
				word = input(Vars.instructions["promptFindAWordShort"]).lower()
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
					word = input(Vars.instructions["moreThanMANYResults"].replace("MANY",str(maxWordsContaining))).lower()
					if word == "":
						print(Vars.instructions["chooseOneWord1"].rstrip("\n") + " " + word_copy + " " + Vars.instructions["chooseOneWord2"] + "\n".join(sorted(wordsContaining)) + "\n")
						word = input().lower()
				elif len(wordsContaining) > 1:
					print("\n" + Vars.instructions["chooseOneWord1"].rstrip("\n") + " " + word + " " + Vars.instructions["chooseOneWord2"] + "\n".join(sorted(wordsContaining)) + "\n")
					word = input().lower()
				elif len(wordsContaining) == 1:
					word = wordsContaining[0]
				else:
					word = input(Vars.instructions["wrongWord"])
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
				print(Vars.instructions["findAWordMeaningsIn"].replace("REPLACE", Vars.instructions["book" + Vars.acronym[books[dicIndex]]].rstrip("\n")))
				Word.describeWord(word, dics[dicIndex][word], False) # Does not raise QuitException since learnMode == False
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
	print(Vars.instructions["promptChooseRecord"])
	for number, item in enumerate(lists):
		print("{0}: {1}\n".format(number + 1, item))
	item = input().upper()
	while True:
		if item == "QUIT":
			return None
		if isInt(item):
			item = int(item)
			if (item >= 1) & (item <= len(lists)):
				item = lists[item - 1]
				break
		if len(lists) > 1:
			item = input(Vars.instructions["chooseRecord"].replace("REPLACE", str(len(lists)))).upper()
		else:
			item = input(Vars.instructions["chooseRecord2"]).upper()
	return item

def readFromRecord():
	"""
		readFromRecord():
		Chooses a record and studies.
	"""
	booksInRecord = []
	for books in Vars.availableBooks:
		if os.path.exists(os.path.join(Vars.record_path, books)):
			booksInRecord.append(books)
	book = chooseBook(booksInRecord)
	if book == None:
		return
	recordsWithDate = []
	tz = pytz.timezone(Vars.parameters["TimeZone"].split(" ** ")[0])
	date = input(Vars.instructions["date"]).upper()
	while True:
		path = os.path.join(Vars.record_path, book)
		if date == "QUIT":
			return
		if date == "T" or date == "TODAY":
			date = datetime.datetime.now(tz.localize(datetime.datetime.now()).tzinfo).strftime("%m/%d/%Y")
			continue
		if date == "Y" or date == "YESTERDAY":
			date = (datetime.datetime.now(tz.localize(datetime.datetime.now()).tzinfo) - datetime.timedelta(1)).strftime("%m/%d/%Y")
			continue
		date = str.split(date, "/")
		if len(date) != 3:
			date = input(Vars.instructions["date"]).upper()
			continue # If not three elements (YYYY/MM/DD)
		try:
			date = list(map(int, date))
		except ValueError:
			date = input(Vars.instructions["date"]).upper()
			continue # If input not convertible to int
		path = os.path.join(path, str(date[2]) + "-" + str(date[0]).zfill(2))
		if not os.path.exists(path):
			date = input(Vars.instructions["wrongDate"]).upper()
			continue
		# If passed all preliminary tests
		date = str(date[0]).zfill(2) + "-" + str(date[1]).zfill(2)
		for files in os.listdir(path):
			if os.path.isfile(os.path.join(path, files)) and date in files:
				recordsWithDate.append(files)
		if recordsWithDate != []:
			break
		else:
			date = input(Vars.instructions["wrongDate"]).upper()
	if len(recordsWithDate) == 1:
		record = recordsWithDate[0]
	record = chooseRecord(recordsWithDate)
	if record == None:
		return
	if " -- " in record: # If the list name of the record has the form "L1 -- L3"
		assert(not "&" in record)
		theLists = sorted([int(s.replace("L","")) for s in record.split(" ") if "L" in s])
		assert(len(theLists) == 2)
		theLists = list(range(theLists[0], theLists[1] + 1))
	elif "random" in record: # Random 50 words mode
		theLists = Vars.listNumber[Vars.lang][book]
	else:
		theLists = sorted([int(s.replace("L","")) for s in record.split(" ") if "L" in s])
	record = os.path.join(path, record)
	f = open(record)
	wordList = []
	for word in f:
		wordList.append(word.rstrip('\n').lower())
	f.close()
	prompt = "\n" + Vars.instructions["promptReadRecord"]
	wordListAndNames = [wordList, [book] + theLists]
	Dictionary = {}
	createDictionary(Dictionary, readFromRecord = wordListAndNames, defaultAll = False)
	if Dictionary == {}:
		print(Vars.instructions["noWordsToStudy"])
		return True
	while True:
		s = input(prompt).upper()
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
	sch = os.path.join(Vars.record_path, 'Schedule.txt')
	tz = pytz.timezone(Vars.parameters["TimeZone"].split(" ** ")[1])
	timeNow = datetime.datetime.now(tz.localize(datetime.datetime.now()).tzinfo)
	found = False
	try:
		f = open(sch)
		for s in f:
			if timeNow.strftime("%m").lstrip("0") + "/" + timeNow.strftime("%d").lstrip("0") in s or time.strftime("%m/%d") in s:
				print(s.replace("SPACE", " "))
				found = True
		if not found:
			print(Vars.instructions["noScheduleTodayAvailable"])
	except IOError:
		print(Vars.instructions["noScheduleAvailable"])
		open(sch, 'w').close()
	print(Vars.instructions["addOrCancelSchedule"])
	return

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
	f = open(os.path.join(Vars.record_path, 'Schedule.txt'))
	dates = {1: list(range(1,32)), 2: list(range(1,30)), 3: list(range(1,32)), 4: list(range(1,31)), 5: list(range(1,32)), 6: list(range(1,31)), 7: list(range(1,32)), 8: list(range(1,32)), 9: list(range(1,31)), 10: list(range(1,32)), 11: list(range(1,31)), 12: list(range(1,32))}
	sch = {}
	for s in f:
		if len(s.split(": ")) == 2:
			sch[s.split(": ")[0]] = s.split(": ")[1].rstrip("\n")
	user_input = input(Vars.instructions["scheduleEnterDate"]).upper()
	while True:
		if user_input == "QUIT":
			f.close()
			return
		elif user_input == "VIEW":
			if len(sch) == 0:
				print(Vars.instructions["noScheduleAvailable"])
			for d in sortDate(list(sch)):
				print(d + ": " + sch[d].replace("SPACE", " "))
			user_input = input(Vars.instructions["scheduleEnterDate"]).upper()
		elif not isInt(user_input.split("/")[0]) or not isInt(user_input.split("/")[1]):
			user_input = input(Vars.instructions["scheduleEnterDate"]).upper()
			continue
		elif (not int(user_input.split("/")[0]) in range(1,13)) or (not int(user_input.split("/")[1]) in dates[int(user_input.split("/")[0])]):
			user_input = input(Vars.instructions["dateNotValid"]).upper()
		elif action == "A" and user_input in sch:
			user_input = input(Vars.instructions["dateAlreadyExists"]).upper()
		elif action == "C" and not user_input in sch:
			user_input = input(Vars.instructions["dateDoesNotExist"]).upper()
		else:
			break
	g = open(os.path.join(Vars.record_path, 'Schedule 0.txt'), 'w')
	if action == "A":
		user_input2 = input(Vars.instructions["scheduleEnterTask"])
		sch[user_input] = user_input2.replace(": ", ":SPACE")
		for d in sortDate(list(sch)):
			g.write(d + ": " + sch[d] + "\n")
		f.close()
		g.close()
		os.rename(os.path.join(Vars.record_path, 'Schedule 0.txt'), os.path.join(Vars.record_path, 'Schedule.txt'))
	if action == "C":
		cf = input(user_input + ": " + sch[user_input].replace("SPACE", " ") + "\n" + Vars.instructions["confirmOrAbandon"]).upper()
		while cf != "Y" and cf != "N":
			cf = input(Vars.instructions["enterYOrN"]).upper()
		if cf == "Y":
			sch.pop(user_input)
			for d in sortDate(list(sch)):
				g.write(d + ": " + sch[d] + "\n")
			g.close()
			f.close()
			os.rename(os.path.join(Vars.record_path, 'Schedule 0.txt'), os.path.join(Vars.record_path, 'Schedule.txt'))
		else:
			g.close()
			f.close()
			os.remove(os.path.join(Vars.record_path, 'Schedule 0.txt'))
	return

def allWordsOrDifficultWordListForRandom50Words():
	"""
		allWordsOrDifficultWordListForRandom50Words():
		Sets parameter "AllForRandom50Words"
	"""
	if Vars.parameters["AllForRandom50Words"] != "A":
		r = Vars.parameters["AllForRandom50Words"]
	else:
		r = input(Vars.instructions["allForRandom50Words"].replace("REPLACE", Vars.parameters["Random50Words"])).upper()
	while (r != 'Y') & (r != 'N') & (r != 'QUIT'):
		r = input(Vars.instructions["enterYOrN"]).upper()
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
	NUMBER = int(Vars.parameters["Random50Words"])
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
	prompt = "\n" + Vars.instructions["promptRandom50Words"].replace("REPLACE", Vars.parameters["Random50Words"])
	while True:
		s = input(prompt).upper()
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
			print(Vars.instructions["random50WordsShuffleDone"].replace("REPLACE", Vars.parameters["Random50Words"]))
		elif (s == "QUIT"):
			return
	return

def similarWords():
	"""
		similarWords():
		Studies similar words.
	"""
	prompt1 = Vars.instructions["promptSimilarWords"]
	prompt2 = Vars.instructions["promptSimilarWords2"]
	try:
		f = open(os.path.join(Vars.wordLists_path, 'Similar.txt'))
	except IOError:
		print(Vars.instructions["similarFileNotExists"])
		return
	word = ""
	while True:
		f.seek(0)
		if word != "r": # For CHANGE RANDOM
			word = input(prompt1).lower()
		if word == "quit":
			return
		elif word == "a":
			print("\n".join(f.readlines()))
			f.seek(0)
		else:
			found = []
			if word == "random" or word == "r":
				words = [re.split("\s*\|+\s*", s)[0] for s in f if "|" in s]
				random.shuffle(words)
				random.shuffle(words)
				word = words[0]
				f.seek(0)
			for s in f:
				words = re.split("\s*\|+\s*", s.rstrip("\n").lower())
				if word in words:
					found += words
			if found == []:
				print(Vars.instructions["similarWordsNotFound"].replace("REPLACE", word))
			else:
				Dictionary = {}
				wordListAndNames = [found, [Vars.availableBooks, None]]
				createDictionary(Dictionary, readFromRecord = wordListAndNames)
				name = ["similar words to {0}".format(word)]
				while True:
					s = input("\n" + Vars.instructions["promptSimilarWords2"].replace("REPLACE", word)).upper()
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
	list = input(Vars.instructions["chooseList"])
	while True: # Choose one list only, so cannot use chooseList()
		if list.upper() == "QUIT":
			return
		elif not isInt(list):
			list = input(Vars.instructions["enterANumber"])
			continue
		elif not int(list) in Vars.listNumber[Vars.lang][book]:
			print(Vars.instructions["chooseListNotExists"].rstrip("\n"))
			print(Vars.listNumber[Vars.lang][book])
			list = input()
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
	f = open(os.path.join(Vars.wordLists_path, book, 'Lists', str(theList) + ' ' + Vars.lang + '.txt'))
	print(Vars.instructions["createDifficultWords"])
	for s in f:
		if (s != '\n') and (not isInt(s.rstrip('\n'))):
			i += 1
			word = s.split(" ** ")[0].lower()
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
				user_input = input()
				if user_input != "":
					print()
					if user_input.upper() == "QUIT":
						return
					elif user_input.upper()[0] in ["M", ",", "N", "J", "K"] or Word.markWordorNot(user_input):
						new.append(word)
					elif user_input.upper() != user_input.lower():
						add += re.split("\s*\|+\s*", user_input.lower())
	add2 = re.split("\s*\|+\s*", input(Vars.instructions["difficultWordsInput"]).lower())
	if add2 != [""] and add2 != ["quit"]:
		add += add2
	add = list(set(add))
	for w in add:
		if w in all:
			new.append(w)
		else:
			w2 = input(w + Vars.instructions["wrongDifficultWordsInput"])
			while not w2 in all:
				if w2.upper() == "AB":
					break
				w2 = input(w + Vars.instructions["wrongDifficultWordsInput"])
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
	difficultWordListPath = os.path.join(Vars.wordLists_path, book, 'Difficult Words', str(theList) + '.txt')
	if not os.path.exists(difficultWordListPath):
		newOrExt = "Y"
	else:
		newOrExt = input(Vars.instructions["chooseDifficultNewOrExtend"]).upper()
		while newOrExt != "Y" and newOrExt != "N":
			if newOrExt == "QUIT":
				return
			newOrExt = input(Vars.instructions["chooseDifficultNewOrExtend"]).upper()
	if newOrExt == "N":
		f = open(difficultWordListPath)
		current = re.split("\s*\|+\s*", f.readline().lower().rstrip("\n"))
		f.close()
	else:
		current = []
	newAndTogether = extend(book, theList, current)
	if newAndTogether == None:
		return
	else:
		new, together = newAndTogether
	print("\n" + Vars.instructions["chooseDifficultNewlyAddedWords"].rstrip("\n"))
	print(new)
	print("\n" + Vars.instructions["chooseDifficultNowList"].rstrip("\n"))
	print(together)
	save = input("\n" + Vars.instructions["confirmOrAbandon"]).upper()
	while save != "Y" and save != "N":
		if save == "QUIT":
			return
		else:
			save = input("\n" + Vars.instructions["confirmOrAbandon"]).upper()
	if save == "Y":
		f = open(difficultWordListPath, 'w')
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
	addWordsFromLists(allWordsFromBook, book, Vars.listNumber[Vars.lang][book])
	comments = {}
	s = input(Vars.instructions["promptAddComments"]).lower()
	while s != "quit":
		if s == "":
			s = input(Vars.instructions["promptAddComments"]).lower().replace(" ", "")
			continue
		elif not s in allWordsFromBook:
			print(s + Vars.instructions["notInBook"].rstrip("\n").replace("REPLACE", Vars.instructions["guillemetLeft"].rstrip("\n") + Vars.instructions["book" + Vars.acronym[book]].rstrip("\n") + Vars.instructions["guillemetRight"].rstrip("\n")) + Vars.instructions["reenter"].rstrip("\n"))
			s = input("").lower().lower().replace(" ", "")
			continue
		else:
			c = input(Vars.instructions["addComments"].replace("REPLACE", s))
			if c.upper() == "QUIT":
				s2 = input(Vars.instructions["addCommentsQuitted"].replace("REPLACE1", c).replace("REPLACE2", s))
				if s2.upper() == "QUIT":
					comments[s] = s2
					s = input(Vars.instructions["promptAddComments"]).lower()
				else:
					s = s2.lower()
				continue
			comments[s] = c
			s = input(Vars.instructions["promptAddComments"]).lower()
	updateComments(comments, book)
	return

def moreOptions():
	"""
		moreOptions():
		Provides more options besides those shown in the main menu.
	"""
	prompt = "\n" + Vars.instructions["moreOptions"].replace("REPLACE", Vars.parameters["Random50Words"])
	while True:
		try:
			s = quitOrInput(input(prompt)).upper()
		except QuitException:
			return
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
	return

def study():
	"""
		study():
		Studies.
	"""
	prompt = "\n" + Vars.instructions["promptStudy"]
	while True:
		try:
			s = quitOrInput(input(prompt)).upper()
		except QuitException:
			print(Vars.instructions["bye"])
			return
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
			Settings.changeParameters()
			prompt = Vars.instructions["promptStudy"]
	return


if __name__ == "__main__":
	os.chdir(os.path.dirname(os.path.abspath(__file__))) # Change current working directory to where this file is located
	Settings.initialization()
	study()
