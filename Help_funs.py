import random
import unidecode

class QuitException(Exception):
	pass

def quitOrInput(prompt=None):
	if prompt:
		print(prompt)
	s = input()
	if s.upper() == "EXIT":
		quit()
	elif s.upper() == "QUIT":
		raise QuitException
	else:
		return s
		
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
		lengths = [max(map(len, [wordList[i * k + j] for k in range(0, (numberOfWordList - 1 - j) // i + 1)])) for j in range(0, i)]
		if sum(lengths) + 6 * len(lengths) + 0 <= screenWidth:
			numberPerLine = i
		else:
			break
	lengths = [max(map(len, [wordList[numberPerLine * k + j] for k in range(0, (numberOfWordList - 1 - j) // numberPerLine + 1)])) for j in range(0, numberPerLine)]
	listOfList = [["{0:^{1}}".format(wordList[numberPerLine * k + j], lengths[j] + 4) for k in range(0, (numberOfWordList - 1 - j) // numberPerLine + 1)] for j in range(0, numberPerLine)]
	listOfList = "\n" + "\n\n".join(["|" + "||".join([listOfList[k][j] for k in range(0, min(numberPerLine, numberOfWordList - j * numberPerLine))]) + "|" for j in range(0, (numberOfWordList - 1) // numberPerLine + 1)]) + "|" * (numberOfWordList % numberPerLine != 0) + "\n"
	return listOfList
	

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


def unique_everseen(seq, key=lambda x:x):
	seen = set()
	seen_add = seen.add
	return [x for x in seq if not (key(x) in seen or seen_add(key(x)))]

def comp_answers(inp, word):
	return unidecode.unidecode(inp).lower() == unidecode.unidecode(word).lower()

def shuffle_if_random(l, rand):
	return random.sample(l, len(l)) if rand else l

def comp_conj_answers(inp, words):
	return any([comp_answers(inp, form) for form in words])
