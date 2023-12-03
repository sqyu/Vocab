# -*- coding: utf-8 -*-


import datetime
import string
import os
import random
import time
import pytz
import re
import Settings
import Vars
import Word

from Conj import reciteconj, Conj
from Help_funs import *
from Vars import getInst, printInst, inpInst, conjNumber, listNumber
from Writing import writeTime

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
		printInst("book1")
		for book in sorted(booksToChoose):
			printInst("book2", (("REPLACE1", getInst("book" + Vars.acronym[book])), ("REPLACE2", Vars.acronym[book])))
		try:
			book = quitOrInput("\n").upper() # Select book
			while not book in Vars.findAcronym: # Book not found
				book = quitOrInput(getInst("wrongBook", rep="".join([getInst("guillemetLeft") + b + getInst("guillemetRight") for b in [getInst("book" + Vars.acronym[bo]) for bo in sorted(booksToChoose)]])) + "\n").upper()
		except QuitException:
			return
	return Vars.findAcronym[book]

def chooseList(listsinthebook, all, firstList):
	"""
		chooseList(listsinthebook, all, firstList):
		Returns the list number (int), and the bool all
		Notes: if there are at least two lists in the book, list number + "S" sets "all" to False, and "A" sets "all" to True
		
		Parameters
		__________
		listsinthebook: string
		A list of list numbers
		
		all: bool
		Read all words from the list or not
		
		firstList: bool
		The current list is the first list added or not
	"""
	if len(listsinthebook) == 1: # If there is only one list in the giveen list
		theList = listsinthebook[0] # Option to choose "select" or "all" not available
		return theList, all
	else:
		theList = inpInst("chooseList" if firstList else "chooseMoreLists").upper() # Select list; QuitException handled in createDictionary()
		while True: # If the user did not enter a number
			if not isInt(theList):
				if ("S" in theList): # List number + "S" to indicate that read the list of selected words only ("S" stands for "select")
					theList = theList.replace("S", "")
					all = False
				elif ("A" in theList): # List number + "A" to indicate that read the full list ("A" stands for "all")
					theList = theList.replace("A", "")
					all = True
				elif firstList == False and theList == "N":
					return None
				else:
					theList = inpInst("enterANumber" if firstList else "chooseMoreListsWrong", handleQuit=False).upper()
			if isInt(theList):
				theList = int(theList)
				if not theList in listsinthebook:
					theList = inpInst("chooseListNotExists" if firstList else "chooseMoreListsNotExists", add="{0}\n".format(listsinthebook), handleQuit=False).upper()
				else:
					return int(theList), all
			else:
				theList = inpInst("enterANumber" if firstList else "chooseMoreListsWrong", handleQuit=False).upper()
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
		allWordsFromLists.extend([w for w in (s.rstrip("\n").split(" ** ")[0] for s in f.readlines()) if w and not isInt(w)])
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
				printInst("warning", add=": " + word + getInst("notInList").replace("REPLACE", str(lists[0])))
			elif (not isinstance(book, list)) and sorted(lists) == sorted(Vars.listNumber[Vars.lang][book]):
				printInst("warning", add=": " + word + getInst("notInBook").replace("REPLACE", getInst("guillemetLeft") + getInst("book" + Vars.acronym[book]) + getInst("guillemetRight")))
			elif isinstance(book, list):
				printInst("warning", add=": " + word + getInst("notInBooks", rep=" & ".join([getInst("guillemetLeft") + getInst("book" + Vars.acronym[book]) + getInst("guillemetRight") for book in Vars.availableBooks])))
			else:
				printInst("warning", add=": " + word + getInst("notInLists", rep=" & ".join(map(str, lists))))
			wordList.pop(wordList.index(word))
			passed = False
	return passed


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
	if mode == 2:
		currentWordList = wordList
	elif mode != 2 and not all and (not os.path.exists(difficultWordFile)): # If normal mode and difficult word lists do not exist, read all words
		printInst("noDifficultWordList", rep=(("LIST", str(theList)), ("BOOK", getInst("book" + Vars.acronym[book]))))
		all = True
	elif mode != 2 and not all: # If normal mode but not reading all words
		g = open(difficultWordFile)
		currentWordList = re.split("\s*\|+\s*", g.readline().lower().rstrip("\n")) # Read the difficult word list # Far more efficient to use currentWordList to store the difficult word list for only the current list
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


def loadConj(all, book, comments, Dictionary, mode, theList, conjList):
	"""
		loadConj(all, book, comments, Dictionary, mode, theList, conjList):
		Adds Conjs to Dictionary and word strings to conjList
		
		Parameters
		__________
		all: bool
		Whether add all words or not
		
		book: string, must be an available book in the language
		The book chosen
		
		comments: dictionary whose keys and contents are both strings
		All comments for words in the whole book
		
		Dictionary: dictionary whose keys are strings (words) and contents are of class Conj
		The dictionary to which the conjs are to be added
		
		mode: 1, 2, or 3
		Mode 1: regular; Mode 2: read from record; Mode 3: read all words
		
		theList: integer, within the range of listNumber[lang][book]
		The list number
		
		conjList: lists of strings (words)
		The list of words loaded
		
		"""
	bookList = os.path.join(Vars.wordLists_path, book, 'Lists', str(theList) + ' conj.txt')
	f = open(bookList) # Read Only
	difficultWordFile = os.path.join(Vars.wordLists_path, book, 'Difficult Words', str(theList) + '.txt')
	if mode == 2:
		add_this_word = lambda word:word in set(conjList)
	elif mode != 2 and not all and (not os.path.exists(difficultWordFile)): # If normal mode and difficult word lists do not exist, read all words
		printInst("noDifficultWordList", rep=(("LIST", str(theList)), ("BOOK", getInst("book" + Vars.acronym[book]))))
		all = True
	elif mode != 2 and not all: # If normal mode
		g = open(difficultWordFile)
		difficultWords = set(re.split("\s*\|+\s*", g.readline().lower().rstrip("\n")))
		g.close()
		checkAllWordsInLists(difficultWords, book, [theList]) # Only need to check the difficult word list for the current list ## ??
		add_this_word = lambda word: word in difficultWords
	else:
		add_this_word = lambda word: True
	worddic = {}
	if Vars.lang in Vars.listNumber and book in Vars.listNumber[Vars.lang] and theList in Vars.listNumber[Vars.lang][book]:
		loadWords(True, book, {}, worddic, 3, theList, [])
	for s in f:
		if "**" in s:
			try:
				conj_obj = Conj(s)
				if add_this_word(conj_obj.infinitive):
					if conj_obj.infinitive in comments:
						conj_obj.comments = comments[conj_obj.infinitive]
					conj_obj.meanings = "\n".join(worddic[conj_obj.infinitive].meanings) if conj_obj.infinitive in worddic else ""
					Dictionary[conj_obj.infinitive] = conj_obj
					if mode != 2:
						conjList.append(conj_obj.infinitive)
			except Exception as e:
				print("Failed to load conjugations for %s: %s." % (s, e)) ## INSTRUCTIONS PENDING
	f.close()
	return

def read_conj(defaultAll = True):
	book = chooseBook(conjNumber.keys())
	firstList = True
	if book == None:
		return
	while True:
		all = defaultAll
		try:
			theListAndAll = chooseList(conjNumber[book], all, firstList)
		except QuitException:
				return
		if theListAndAll is None:
			break
		theList, all = theListAndAll
		theList = int(theList)
		lists.append(theList)
		alls.append(all)
		if len(Vars.listNumber[Vars.lang][book]) == 1:
			break
			firstList = False
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

def createDictionary(Dictionary, conj, readFromRecord = None, allLists = None, defaultAll = True):
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
	list_of_books = conjNumber if conj else Vars.listNumber[Vars.lang]
	assert((readFromRecord == None) or (allLists == None))
	if readFromRecord != None:
		mode = 2 # Mode 2
	elif allLists != None:
		mode = 3 # Mode 3
	else:
		mode = 1 # Mode 1
	if mode == 1:
		if conj:
			book = chooseBook(conjNumber.keys())
		else:
			book = chooseBook()
		firstList = True
		if book == None:
			return
		while True:
			all = defaultAll
			try:
				theListAndAll = chooseList(list_of_books[book], all, firstList)
			except QuitException:
				return
			if theListAndAll is None:
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
		lists = sorted(map(int, list_of_books[book]))
		alls = [defaultAll] * len(lists) # Not necessarily include all words even if all lists are loaded
	if isinstance(book, list):
		for books in book:
			comments = loadComments(books)
			Dictionary[books] = {}
			for theList in list_of_books[books]:
				if conj:
					loadConj(False, books, comments, Dictionary[books], mode, theList, wordList)
				else:
					loadWords(False, books, comments, Dictionary[books], mode, theList, wordList)
	else:
		comments = loadComments(book)
		for index, theList in enumerate(lists):
			if conj:
				loadConj(alls[index], book, comments, Dictionary, mode, theList, wordList)
			else:
				loadWords(alls[index], book, comments, Dictionary, mode, theList, wordList)
	names = [book] + sorted(lists)
	return (sorted(set(wordList)), names)

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
	if rand:
		random.shuffle(wordList)
	else:
		wordList = sorted(wordList)
	previousWord = ""
	learnOrView = "learn" if learnMode else "view"
	print("\n" + getInst("startDescribeList") + "\n")
	timeBegan = writeTime(begin = True)
	try:
		for wi, word in enumerate(wordList):
			s = quitOrInput().upper()
			if s != "":
				print()
				if Word.markWordorNot(s):
					if previousWord:
						difficultWords.append(previousWord)
						printInst("markedWordSuccessfully", rep=previousWord)
				elif s == "CM":
					if previousWord in Dictionary: # If not in "similar words" mode
						comments[previousWord] = inpInst("addComments", rep=previousWord)
						print()
				else:
					for w in re.split("\s*\|+\s*", s.lower()):
						if w != "":
							if w in wordList:
								difficultWords.append(w)
								printInst("markedWordSuccessfully", rep=w)
							else:
								printInst("markedWordUnsuccessfully", rep=w)
			if not word in Dictionary: # If Dictionary has sub-dictionaries, in "silimar words" mode
				Words = [Dictionary[dic][word] for dic in sorted(Dictionary) if word in Dictionary[dic]]
				if len(Words) > 1:
					WordsDics = [dic for dic in sorted(Dictionary) if word in Dictionary[dic]]
			else:
				Words = [Dictionary[word]]
			for Wi, Word_obj in enumerate(Words):
				if len(Words) > 1:
					printInst("findAWordMeaningsIn", rep=getInst("book" + Vars.acronym[WordsDics[Wi]]))
				s = Word.describeWord(word, Word_obj, learnMode, [wi + 1, numberofwords]) ## "QUIT" for quit, "MARK" for mark, "" for nothing
				if Word.markWordorNot(s):
					difficultWords.append(word)
					printInst("markedWordSuccessfully", rep=word)
				elif s != "": # If s is not empty, mark words in s
					for w in re.split("\s*\|+\s*", s): # Split s by | and add each word if they exist; already changed to lower case in describeWord()
						if w in wordList:
							difficultWords.append(w)
							printInst("markedWordSuccessfully", rep=w)
						else:
							printInst("markedWordUnsuccessfully", rep=w)
			previousWord = word
		s = quitOrInput().upper() # Last input after list finished
		if Word.markWordorNot(s):
			difficultWords.append(previousWord) # Last word
			printInst("markedWordSuccessfully", rep=previousWord)
		elif s == "CM":
			if previousWord in Dictionary: # If not in "similar words" mode
				comments[previousWord] = inpInst("addComments", rep=previousWord) # Add comment for the last word
				print()
		quit = False
	except QuitException:
		quit = True
	if record:
		try:
			difficultWordsInput = inpInst("difficultWordsInput").lower().strip()
		except QuitException: # Ignore
			difficultWordsInput = ""
		if difficultWordsInput != "":
			difficultWordsInput = re.split("\s*\|+\s*", difficultWordsInput) # Split words by |
			abandoned = []
			for wi, word in enumerate(difficultWordsInput):
				while not word in wordList:
					reword = input(word + " " + getInst("wrongDifficultWordsInput") + "\n").lower() # ignores quit
					if reword != "ab":
						difficultWordsInput[wi] = reword
						word = reword
					else:
						abandoned.append(wi)
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
		if not record: # Should have been sorted above if record == True
			difficultWords = sorted(set(difficultWords))
		print(getInst("difficultWordList"), ", ".join(difficultWords) + ", " + getInst("wordsInTotal") + str(len(difficultWords)) + getInst("wordsInTotal2", rep=[("SPACE", "")]))
		if quit == False:
			try:
				_ = inpInst("reviewRecite")
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
							printInst("findAWordMeaningsIn", rep=getInst("book" + Vars.acronym[WordsDics[index2]]))
						Word.describeWord(word, Word_obj, False, [index + 1, lenDifficultWords]) # learnMode == False, so QUIT ignored
					_ = quitOrInput(None)
			except QuitException:
				pass
	writeTime(begin = False, timeBegan = timeBegan, mode = learnOrView + " mode " + readFromRecord * "(from record) ", names = name)
	if comments != {}:
		updateComments(comments, name[0])
	return


def randomAndRecord():
	"""
		randomAndRecord():
		Returns two bools: true for the first one if random, and true for the second one if record. Or returns None if "quit" entered
	"""
	try:
		if Vars.parameters["Random"] != "A":
			r = Vars.parameters["Random"]
		else:
			r = inpInst("random").upper()
		while r not in ["Y", "N"]:
			r = inpInst("enterYOrN").upper()
		random = (r == "Y")
		if Vars.parameters["Record"] != "A":
			r = Vars.parameters["Record"]
		else:
			r = inpInst("record").upper()
		while r not in ["Y", "N"]:
			r = inpInst("enterYOrN").upper()
		record = (r == "Y")
		return (random, record)
	except QuitException:
		raise QuitException

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
	numberofwords = len(wordList)
	printInst("startRecite")
	printInst("startRecite2")
	print()
	if rand:
		random.shuffle(wordList)
	else:
		wordList = sorted(wordList)
	printList = formatList(wordList)
	timeBegan = writeTime(begin = True)
	try:
		for wi, word in enumerate(wordList):
			print("{0}/{1}".format(wi + 1, numberofwords))
			#print("{0}/{1}\t {2} {3}".format(wi + 1, numberofwords, len(word), getInst("letters"))
			Word.printMeanings(Dictionary[word])
			print()
			user_input = quitOrInput()
			wrongtimes = 0
			while (not comp_answers(user_input, word)) and (wrongtimes < MaxTimes): # Try again until being wrong for MaxTimes times; ignores accents
				if user_input.upper() == "HINT":
					print(printList)
					user_input = quitOrInput()
					continue
				elif user_input.upper() == "NUMBER":
					print("{0} {1}".format(len(word.replace("-", "")), getInst("letters")))
					user_input = quitOrInput()
					continue
				wrongtimes += 1
				printInst("tryAgain")
				if wrongtimes < MaxTimes:
					user_input = quitOrInput()
			if wrongtimes == MaxTimes:
				difficultWords.append(word)
				print(Dictionary[word].IPA) # Show IPA first
				user_input = inpInst("tryAgain")
				if not comp_answers(user_input, word): # If still incorrect, show descriptions
					Word.describeWord(word, Dictionary[word], False) # Does not raise QuitException since learnMode == False
					user_input = inpInst("tryAgain")
				while not comp_answers(user_input, word): # Enter until correct; ignores accents
					user_input = inpInst("tryAgain")
				printInst("markedWordSuccessfully", rep=word)
			printInst("correct")
		quit = False
	except QuitException:
		quit = True
	if difficultWords: # If there is any difficult word
		difficultWords = sorted(set(difficultWords))
		print(getInst("difficultWordList"), ", ".join(difficultWords) + ", " + getInst("wordsInTotal") + str(len(difficultWords)) + getInst("wordsInTotal2"))
		if quit == False:
			try:
				_ = inpInst("reviewRecite")
				lenDifficultWords = len(difficultWords)
				for index, word in enumerate(difficultWords):
					Word.describeWord(word, Dictionary[word], False, [index + 1, lenDifficultWords]) # Does not raise QuitException since learnMode == False
					_ = quitOrInput()
			except QuitException:
				pass
	elif quit == False:
		printInst("congratulations")
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
		wordListAndNames = createDictionary(Dictionary, conj=False, defaultAll = not learnMode)
		if wordListAndNames == None:
			return
	if Dictionary == {}:
		printInst("noWordsToStudy")
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
	try:
		pre = inpInst("findAWordChooseList").upper()
	except QuitException:
		return
	firstTime = True
	if pre == "Y":
		dics = [{}]
		wordListAndNames = createDictionary(dics[0], conj=False)
		if wordListAndNames is None:
			return
		wordList = wordListAndNames[0]
		books.append(wordListAndNames[1][0])
	else:
		dics = [{} for i in range(0, len(Vars.availableBooks))] # Cannot use [{}] * len(Vars.availableBooks) which would create pointers pointing to the same dic
		for index, dic in enumerate(dics):
			wordListAndNames = createDictionary(dic, conj=False, allLists = Vars.availableBooks[index])
			wordList += wordListAndNames[0]
			books.append(wordListAndNames[1][0])
	wordList = sorted(list(set(wordList)))
	wordsFound = []
	wordsContaining = []
	maxWordsContaining = 50
	timeBegan = writeTime(begin = True)
	try:
		while True:
			if firstTime:
				word = inpInst("promptFindAWordLong").lower()
				firstTime = False
			else:
				word = inpInst("promptFindAWordShort").lower()
			while not word in wordList:
				if word == "":
					word = inpInst("promptFindAWordShort").lower()
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
						word = inpInst("moreThanMANYResults", rep=str(maxWordsContaining)).lower()
						if word == "":
							print(getInst("chooseOneWord1") + " " + word_copy + " " + getInst("chooseOneWord2") + "\n" + "\n".join(sorted(wordsContaining)) + "\n")
							word = quitOrInput().lower()
					elif len(wordsContaining) > 1:
						print("\n" + getInst("chooseOneWord1") + " " + word + " " + getInst("chooseOneWord2") + "\n" + "\n".join(sorted(wordsContaining)) + "\n")
						word = quitOrInput().lower()
					elif len(wordsContaining) == 1:
						word = wordsContaining[0]
					else:
						word = inpInst("wrongWord")
					wordsContaining = [] # Clear words
			if word in wordList: # If not quitted
				wordsFound.append(word)
				print()
				inDics = [] # The indices of the dictionaries in list "dics" that contain the word
				for index, dic in enumerate(dics):
					if word in dic:
						inDics.append(index)
				print("".center(80, "*") + "\n")
				for dicIndex in inDics:
					printInst("findAWordMeaningsIn", rep=getInst("book" + Vars.acronym[books[dicIndex]]))
					Word.describeWord(word, dics[dicIndex][word], False) # Does not raise QuitException since learnMode == False
	except QuitException:
		writeTime(begin = False, timeBegan = timeBegan, mode = "words found: ", names = wordsFound)
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
	printInst("promptChooseRecord")
	for number, item in enumerate(lists):
		print("{0}: {1}\n".format(number + 1, item))
	try:
		item = quitOrInput().upper()
		while True:
			if isInt(item):
				item = int(item)
				if (item >= 1) & (item <= len(lists)):
					item = lists[item - 1]
					break
			if len(lists) > 1:
				item = inpInst("chooseRecord", rep=str(len(lists))).upper()
			else:
				item = inpInst("chooseRecord2").upper()
	except QuitException:
		return None
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
	try:
		date = inpInst("date").upper()
		while True:
			path = os.path.join(Vars.record_path, book)
			if date == "T" or date == "TODAY":
				date = datetime.datetime.now(tz.localize(datetime.datetime.now()).tzinfo).strftime("%m/%d/%Y")
				continue
			if date == "Y" or date == "YESTERDAY":
				date = (datetime.datetime.now(tz.localize(datetime.datetime.now()).tzinfo) - datetime.timedelta(1)).strftime("%m/%d/%Y")
				continue
			date = str.split(date, "/")
			if len(date) != 3:
				date = inpInst("date").upper()
				continue # If not three elements (YYYY/MM/DD)
			try:
				date = list(map(int, date))
			except ValueError:
				date = inpInst("date").upper()
				continue # If input not convertible to int
			path = os.path.join(path, str(date[2]) + "-" + str(date[0]).zfill(2))
			if not os.path.exists(path):
				date = inpInst("wrongDate").upper()
				continue
			# If passed all preliminary tests
			date = str(date[0]).zfill(2) + "-" + str(date[1]).zfill(2)
			for files in os.listdir(path):
				if os.path.isfile(os.path.join(path, files)) and date in files:
					recordsWithDate.append(files)
			if recordsWithDate != []:
				break
			else:
				date = inpInst("wrongDate").upper()
	except QuitException:
		return
	if len(recordsWithDate) == 1:
		record = recordsWithDate[0]
	record = chooseRecord(recordsWithDate)
	if record == None:
		return
	if " -- " in record: # If the list name of the record has the form "L1 -- L3"
		assert(not "&" in record)
		theLists = sorted([int(s.replace("L", "")) for s in record.split(" ") if "L" in s])
		assert(len(theLists) == 2)
		theLists = list(range(theLists[0], theLists[1] + 1))
	elif "random" in record: # Random 50 words mode
		theLists = Vars.listNumber[Vars.lang][book]
	else:
		theLists = sorted([int(s.replace("L", "")) for s in record.split(" ") if "L" in s])
	record = os.path.join(path, record)
	f = open(record)
	wordList = []
	for word in f:
		wordList.append(word.rstrip("\n").lower())
	f.close()
	wordListAndNames = [wordList, [book] + theLists]
	Dictionary = {}
	try:
		while True:
			s = quitOrInput("\n" + getInst("promptReadRecord")).upper()
			try: rnr = randomAndRecord()
			except QuitException: continue
			if s in ["RC", "CONJ", "CONJUGATION", "CONJUGATIONS"]:
				is_conj = True
			elif s in ["L", "LEARN", "R", "RECITE", "V", "VIEW", "VIEW LIST"]:
				is_conj = False
			else:
				is_conj = None
			if is_conj is not None:
				createDictionary(Dictionary, conj=is_conj, readFromRecord = wordListAndNames, defaultAll = False)
				if Dictionary == {}:
					printInst("noWordsToStudy")
					return True
				if is_conj:
					reciteconj(Dictionary, rnr, wordListAndNames, readFromRecord = True)
				elif s in ["L", "LEARN"]:
					learnAndView(learnMode = True, rnr = rnr, Dictionary = Dictionary, wordListAndNames = wordListAndNames, readFromRecord = True)
				elif s in ["R", "RECITE"]:
					recite(Dictionary, rnr, wordListAndNames, readFromRecord = True)
				elif s in ["V", "VIEW", "VIEW LIST"]:
					learnAndView(learnMode = False, rnr = rnr, Dictionary = Dictionary, wordListAndNames = wordListAndNames, readFromRecord = True)
				else:
					assert()
	except QuitException:
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
			printInst("noScheduleTodayAvailable")
	except IOError:
		printInst("noScheduleAvailable")
		open(sch, 'w').close()
	printInst("addOrCancelSchedule")
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
	dates = {1: range(1,32), 2: range(1,30), 3: range(1,32), 4: range(1,31), 5: range(1,32), 6: range(1,31), 7: range(1,32), 8: range(1,32), 9: range(1,31), 10: range(1,32), 11: range(1,31), 12: range(1,32)}
	sch = {}
	for s in f:
		if len(s.split(": ")) == 2:
			sch[s.split(": ")[0]] = s.split(": ")[1].rstrip("\n")
	try:
		user_input = inpInst("scheduleEnterDate").upper()
		while True:
			if user_input == "VIEW":
				if len(sch) == 0:
					printInst("noScheduleAvailable")
				for d in sortDate(list(sch)):
					print(d + ": " + sch[d].replace("SPACE", " "))
				user_input = inpInst("scheduleEnterDate").upper()
			elif not isInt(user_input.split("/")[0]) or not isInt(user_input.split("/")[1]):
				user_input = inpInst("scheduleEnterDate").upper()
				continue
			elif (not int(user_input.split("/")[0]) in range(1,13)) or (not int(user_input.split("/")[1]) in dates[int(user_input.split("/")[0])]):
				user_input = inpInst("dateNotValid").upper()
			elif action == "A" and user_input in sch:
				user_input = inpInst("dateAlreadyExists").upper()
			elif action == "C" and not user_input in sch:
				user_input = inpInst("dateDoesNotExist").upper()
			else:
				break
	except QuitException:
		f.close()
		return
	g = open(os.path.join(Vars.record_path, 'Schedule 0.txt'), 'w')
	try:
		if action == "A":
			user_input2 = inpInst("scheduleEnterTask")
			sch[user_input] = user_input2.replace(": ", ":SPACE")
			for d in sortDate(list(sch)):
				g.write(d + ": " + sch[d] + "\n")
			f.close()
			g.close()
			os.rename(os.path.join(Vars.record_path, 'Schedule 0.txt'), os.path.join(Vars.record_path, 'Schedule.txt'))
		if action == "C":
			cf = quitOrInput(user_input + ": " + sch[user_input].replace("SPACE", " ") + "\n" + getInst("confirmOrAbandon") + "\n").upper()
			while cf != "Y" and cf != "N":
				cf = inpInst("enterYOrN").upper()
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
	except QuitException:
		g.close()
		f.close()
	return

def allWordsOrDifficultWordListForRandom50Words():
	"""
		allWordsOrDifficultWordListForRandom50Words():
		Sets parameter "AllForRandom50Words"
	"""
	try:
		if Vars.parameters["AllForRandom50Words"] != "A":
			r = Vars.parameters["AllForRandom50Words"]
		else:
			r = inpInst("allForRandom50Words", rep=Vars.parameters["Random50Words"]).upper()
		while r not in ["Y", "N"]:
			r = inpInst("enterYOrN").upper()
		return (r == "Y")
	except QuitException:
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
		wordList, names = createDictionary(Dictionary, conj=False, allLists = book, defaultAll = a)
	names = [book, "random " + str(NUMBER) + " words"]
	random.shuffle(wordList)
	random.shuffle(wordList)
	try:
		while True:
			s = inpInst("promptRandom50Words", rep=Vars.parameters["Random50Words"]).upper()
			if s in ["L", "LEARN"]:
				try: rnr = randomAndRecord()
				except QuitException: continue
				learnAndView(learnMode = True, rnr = rnr, Dictionary = Dictionary, wordListAndNames = (wordList[0:NUMBER], names))
			elif s in ["R", "RECITE"]:
				try: rnr = randomAndRecord()
				except QuitException: continue
				recite(Dictionary = Dictionary, rnr = rnr, wordListAndNames = (wordList[0:NUMBER], names))
			elif s in ["V", "VIEW", "VIEW LIST"]:
				try: rnr = randomAndRecord()
				except QuitException: continue
				learnAndView(learnMode = False, rnr = rnr, Dictionary = Dictionary, wordListAndNames = (wordList[0:NUMBER], names))
			elif s in ["S", "SHUFFLE"]:
				random.shuffle(wordList)
				random.shuffle(wordList)
				printInst("random50WordsShuffleDone", rep=Vars.parameters["Random50Words"])
	except QuitException:
		return
	return

def similarWords():
	"""
		similarWords():
		Studies similar words.
	"""
	try:
		f = open(os.path.join(Vars.wordLists_path, 'Similar.txt'))
	except IOError:
		printInst("similarFileNotExists")
		return
	word = ""
	try:
		while True:
			f.seek(0)
			if word != "r": # For CHANGE RANDOM
				word = inpInst("promptSimilarWords").lower()
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
					printInst("similarWordsNotFound", rep=word)
				else:
					Dictionary = {}
					wordListAndNames = [found, [Vars.availableBooks, None]]
					createDictionary(Dictionary, conj=False, readFromRecord = wordListAndNames)
					name = ["similar words to {0}".format(word)]
					while True:
						s = quitOrInput("\n" + getInst("promptSimilarWords2", rep=word)).upper()
						if s == "A":
							f.seek(0)
							print("\n".join(f.readlines()))
						if s in ["C", "CHANGE"]:
							break
						elif s in ["CR", "CHANGE RANDOM"]:
							word = "r"
							break
						elif s in ["L", "LEARN"]:
							try: rnr = randomAndRecord()
							except QuitException: continue
							learnAndView(learnMode = True, rnr = rnr, Dictionary = Dictionary, wordListAndNames = (found, name))
						elif s in ["R", "RECITE"]:
							try: rnr = randomAndRecord()
							except QuitException: continue
							recite(Dictionary = Dictionary, rnr = rnr, wordListAndNames = (found, name))
						elif s in ["V", "VIEW", "VIEW LIST"]:
							try: rnr = randomAndRecord()
							except QuitException: continue
							learnAndView(learnMode = False, rnr = rnr, Dictionary = Dictionary, wordListAndNames = (found, name))
	except QuitException:
		return

def chooseOneList(book):
	"""
		chooseOneList(book):
		Chooses only one list from the book.
		Used in creating difficult word list for one word list.
		
		Parameters
		__________
		book: string, must be in the available books in the language.
		The book chosen.
	"""
	try:
		list = inpInst("chooseOneList")
		while True: # Choose one list only, so cannot use chooseList()
			if not isInt(list):
				list = inpInst("enterANumber")
				continue
			elif not int(list) in Vars.listNumber[Vars.lang][book]:
				printInst("chooseListNotExists")
				print(Vars.listNumber[Vars.lang][book])
				list = quitOrInput()
				continue
			return int(list)
	except QuitException:
		return

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
	printInst("createDifficultWords")
	try:
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
					user_input = quitOrInput()
					if user_input != "":
						print()
						if user_input.upper()[0] in ["M", ",", "N", "J", "K"] or Word.markWordorNot(user_input):
							new.append(word)
						else:
							add += re.split("\s*\|+\s*", user_input.lower())
	except QuitException:
		return
	try:
		add2 = re.split("\s*\|+\s*", inpInst("difficultWordsInput").lower())
		if add2 != [""]:
			add += add2
	except QuitException:
		pass
	add = list(set(add))
	for w in add:
		if w in all:
			new.append(w)
		else:
			w2 = input(w + " " + getInst("wrongDifficultWordsInput")) # ignores quit
			while not w2 in all:
				if w2.upper() == "AB":
					break
				w2 = input(w + " " + getInst("wrongDifficultWordsInput")) # ignores quit
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
		try:
			newOrExt = inpInst("chooseDifficultNewOrExtend").upper()
			while newOrExt != "Y" and newOrExt != "N":
				newOrExt = inpInst("chooseDifficultNewOrExtend").upper()
		except QuitException:
			return
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
	print("\n" + getInst("chooseDifficultNewlyAddedWords"))
	print(new)
	print("\n" + getInst("chooseDifficultNowList"))
	print(together)
	try:
		save = quitOrInput("\n" + getInst("confirmOrAbandon")).upper()
		while save != "Y" and save != "N":
			save = quitOrInput("\n" + getInst("confirmOrAbandon")).upper()
	except QuitException:
		return
	if save == "Y":
		if not os.path.exists(os.path.join(Vars.wordLists_path, book, 'Difficult Words')):
			os.mkdir(os.path.join(Vars.wordLists_path, book, 'Difficult Words'))
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
	s = inpInst("promptAddComments", handleQuit=False).lower() # ignores quit
	while s != "quit":
		if s == "":
			s = inpInst("promptAddComments", handleQuit=False).lower().replace(" ", "")
			continue
		elif not s in allWordsFromBook:
			print(s + getInst("notInBook", rep=getInst("guillemetLeft") + getInst("book" + Vars.acronym[book]) + getInst("guillemetRight") + getInst("reenter")))
			s = input("").lower().lower().replace(" ", "") # ignores quit
			continue
		else:
			c = inpInst("addComments", rep=s, handleQuit=False)
			if c.upper() == "QUIT":
				s2 = inpInst("addCommentsQuitted", rep=(("REPLACE1", c), ("REPLACE2", s)), handleQuit=False)
				if s2.upper() == "QUIT":
					comments[s] = s2
					s = inpInst("promptAddComments", handleQuit=False).lower()
				else:
					s = s2.lower()
				continue
			comments[s] = c
			s = inpInst("promptAddComments", handleQuit=False).lower()
	updateComments(comments, book)
	return

def moreOptions():
	"""
		moreOptions():
		Provides more options besides those shown in the main menu.
	"""
	prompt = "\n" + getInst("moreOptions", rep=Vars.parameters["Random50Words"])
	while True:
		try:
			s = quitOrInput(prompt).upper()
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
		elif s in ["RC", "CONJ", "CONJUGATION", "CONJUGATIONS"]:
			try:
				rnr = randomAndRecord()
			except QuitException:
				continue
			Dictionary = {}
			wordListAndNames = createDictionary(Dictionary, conj=True, defaultAll = False)
			if wordListAndNames == None:
				continue
			reciteconj(Dictionary, rnr, wordListAndNames)
	return

def study():
	"""
		study():
		Studies.
	"""
	prompt = "\n" + getInst("promptStudy")
	while True:
		try:
			s = quitOrInput(prompt).upper()
		except QuitException:
			printInst("bye")
			return
		if s in ["L", "LEARN"]:
			try: rnr = randomAndRecord()
			except QuitException: continue
			learnAndView(True, rnr)
		elif s in ["R", "RECITE"]:
			try: rnr = randomAndRecord()
			except QuitException: continue
			Dictionary = {}
			wordListAndNames = createDictionary(Dictionary, conj=False, defaultAll = False)
			if wordListAndNames == None:
				continue
			recite(Dictionary, rnr, wordListAndNames)
		elif s in ["F", "FIND", "FIND A", "FIND A WORD"]:
			findAWord()
		elif s in ["V", "VIEW", "VIEW LIST"]:
			try: rnr = randomAndRecord()
			except QuitException: continue
			learnAndView(False, rnr)
		elif s in ["RR", "READ", "READ FROM", "READ FROM RECORD"]:
			while readFromRecord():
				1
		elif s in ["M", "MORE", "MORE OPTIONS"]:
			moreOptions()
		elif s in ["S", "SP", "SET", "SET PARAMETERS"]:
			Settings.changeParameters()
			prompt = getInst("promptStudy")
	return


if __name__ == "__main__":
	os.chdir(os.path.dirname(os.path.abspath(__file__))) # Change current working directory to where this file is located
	Settings.initialization()
	study()
