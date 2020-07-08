from Help_funs import isInt, QuitException, quitOrInput
import Vars

class Word:
	"""
		class Word:
		The IPA, meanings, number of meanings, and comments
	"""
	def __init__(self, s):
		self.IPA = s[0] # IPA
		self.meanings = str.split(s[1].rstrip('\n'), " %% ")
		self.numOfMeanings = len(self.meanings)
		self.comments = s[2]
		
def printMeanings(Word_obj):
	if Word_obj.numOfMeanings == 1:
		print(Vars.instructions["meaning"].rstrip('\n').replace("REPLACE", "") + Word_obj.meanings[0])
	else:
		for i in range(0, Word_obj.numOfMeanings):
			print(Vars.instructions["meaning"].rstrip('\n').replace("REPLACE", " {0}".format(i+1)) + Word_obj.meanings[i])
			
def markWordorNot(s):
	"""
		markWordorNot(s):
		Takes a user input and determines whether the user intends to mark the word.
		
		String s is first changed to upper case, and returns True if s contains exactly all letters in "MARK", first three letters are MAR, or s is equal to MAK, M, or MM.
	"""
	s = s.upper()
	return (set(s) == set("MARK")) | (s[0:3] == "MAR") | (s in ["MAK", "M", "MM"])

def describeWord(word, Word_obj, learnMode, number = None):
	"""
		describeWord(word, Word_obj, learnMode, number = None):
		Prints the descriptions of the word.
		Raises QuitException if learnMode == True and user inputs QUIT
		
		
		Parameters
		__________
		word: string
		A word in the dictionary.
		
		Word_obj: class Word
		The descriptions of word "word".
		
		learnMode: bool
		Whether the descriptions come after user presses the Enter key
		
		number: array of two integers Default: None
		The first number is the index of the current word, and the second one is the total number of words in the list.
	"""
	mark = False
	if number != None:
		assert len(number) == 2
		print("{word:{length}}{index}/{total_number_words}".format(word=word, length=50, index=number[0], total_number_words=number[1])) # word 30/150 means this word is the 30th in the list
	else:
		print(word) # Only prints out the word without the numbers
	print(Word_obj.IPA) # Prints out the IPA
	if learnMode == True: # If prints meanings after user inputs something
		s = quitOrInput(input()).upper()
		if markWordorNot(s):
			s = "MARK" # Mark the word
		else:
			s = s.lower()
	printMeanings(Word_obj)
	if Vars.parameters["ShowComments"] == "Y" and Word_obj.comments != "":
		print(Vars.instructions["comments"].rstrip('\n') + Word_obj.comments)
	print("".center(80, "*") + "\n")
	return s if learnMode else "" # Return an empty string under view mode with no input
