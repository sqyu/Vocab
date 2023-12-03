# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import codecs
import glob
import os
import numpy as np
import re
import requests
import pattern.de, pattern.fr
import unidecode
from collections import OrderedDict

pathToWordList = os.path.join("/".join(os.path.realpath(__file__).split("/")[:-1]), "Word lists")

def input_function(prompt):
	return raw_input(prompt) ## To switch between python2 and python3

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

def process_plain(l):
	return "\n1\n" + "".join([i.replace("\n","") + " ** [] ** \n" for i in l])
	#return "\n1\n" + "".join([i[0].replace("\n","") + " ** [] ** %s\n" % (i[1] if len(i)>1 else "") for i in (s.split("\t") for s in l)]) ## Treating the

def unique_everseen(seq, key=lambda x:x):
	seen = set()
	seen_add = seen.add
	return [x for x in seq if not (key(x) in seen or seen_add(key(x)))]

def get_de_IPA_word(word):
	"""
		Attempts to get the IPA of a word from de.wiktionary
	"""
	try:
		r = requests.get("https://de.wiktionary.org/wiki/" + word)
		soup = BeautifulSoup(r.text)
		de_head = list(filter(lambda x:x.text == word + " (Deutsch)", soup.find_all("span", {"class":"mw-headline"})))
		if not de_head: ## Since strings that have multiple words will be processed independently again
			if len(word.split(" ")) == 1:
				print("In finding IPA, no Deutsch found for '%s'." % word)
			return None
		elif len(de_head) > 1:
			print("Multiple Deutsch found for %s. Returning the first." % word)
		IPA = de_head[0].find_next("span", id="Aussprache").find_next("dd").text
		IPA = IPA.replace("IPA: ", "")
		IPA = IPA.split("\n")[0] # e.g. for "ich"
		if IPA == u"[\u2026]": ## [...]
			print("No IPA given for '%s'." % word)
			return None
		if ", " in IPA: # If not just one IPA
			if all([x.startswith("[") and x.endswith("]") for x in IPA.split(", ")]): # e.g. [ˈfʀaʊ̯ən], [ˈfʀaʊ̯n̩]
				IPA = "/".join(IPA.split(", "))
			elif IPA.split(", ")[1].split(":")[0] in [u"Präteritum", "Femininum", "Genitiv", "regional auch", "auch"]:
				IPA = IPA.split(", ")[0]
			else:
				print("Cleaning needed for %s." % word) # e.g. [viːdɐˌzeːən], Präteritum: [ˌzaː ˈviːdɐ], Partizip II: [ˈviːdɐɡəˌzeːən]
				IPA += "CLEAN]"
		return IPA
	except Exception as e:
		print("Unable to get IPA for '%s' due to the following error: " % word + str(e))
		return None

def get_de_IPA(string, IPA_dict={}):
	"""
		Attempts to get the IPA of a string (could be made of multiple words)
		"""
	### Need to pay attention to the ones with + after printing
	#print(string)
	#print(IPA_dict)
	if string in IPA_dict:
		return "["+IPA_dict[string]+"]"
	IPA = get_de_IPA_word(string)
	if IPA is None:
		if " " in string:
			IPAs = []
			for word in string.split(" "):
				if word in IPA_dict:
					one_IPA = IPA_dict[word]
					IPAs.append(one_IPA)
				else:
					one_IPA = get_de_IPA_word(word)
					one_IPA = "MISSING" if one_IPA is None else one_IPA[1:-1] # None -> Missing, [IPA] to IPA
					IPAs.append(one_IPA)
					IPA_dict[word] = IPAs[-1]
			IPA = "["+"+".join(IPAs)+"]" # [bɪs][ˈmɔʁɡŋ̍] -> [bɪs+ˈmɔʁɡŋ̍]
		else:
			IPA = "[MISSING]"
	IPA_dict[string] = IPA.lstrip("[").rstrip("]")
	if "MISSING" in IPA:
		print("Some IPA(s) for %s is/are missing." % string)
	return IPA

def to_pos(pos):
	return {"Noun": "n.", "Verb": "v.", "Adjective": "adj.", "Adverb": "adv.", "Pronoun": "pron.", "Conjunction": "conj.", "Determiner": "det.", "Preposition": "prep.", "Interjection": "interj."}.get(pos, pos)


"""
def conjugations_de(verb):
	if verb is None:
		return u"Präsens: ich+?? ** [MISSING], du+?? ** [MISSING], er+?? ** [MISSING], wir+?? ** [MISSING], ihr+?? ** [MISSING], sie+?? ** [MISSING]; Partizip Perfekt: ?? ** [MISSING]"
	else:
		present = u"Präsens: "+", ".join([name+"+"+word_and_IPA(pattern.de.conjugate(verb, alias)) for name, alias in [("ich", "1sg"), ("du", "2sg"), ("er", "3sg"), ("wir","1pl"), ("ihr","2pl"), ("sie","3pl")]])
		past_participle = u"Partizip Perfekt: Partizip Perfekt+"+word_and_IPA(pattern.de.conjugate(verb, pattern.de.PAST+pattern.de.PARTICIPLE))
		return present + "; " + past_participle
"""


def get_conj_de(word):
	"""
		Gets conjugations of a verb from wiktionary
	"""
	want_ind_tenses = [u"Pr\xe4sens", u"Pr\xe4teritum", "Perfekt"]
	want_aktiv = ["Aktiv"]
	want_imp_tenses = [u"Pr\xe4sens Aktiv"]
	url = "https://de.wiktionary.org/wiki/Flexion:" + word
	r = requests.get(url)
	soup = BeautifulSoup(r.text)
	is_blank = lambda x:len(x.strip()) == 1 and ord(x.strip()) in range(8208, 8214)
	person_word = lambda y:y.split(" ")[0]+"+"+" ".join(y.split(" ")[1:]) ## ich werde sein -> ich+werde sein
	conj = OrderedDict()
	indkon = soup.find("span", {"id":"Indikativ_und_Konjunktiv"}).find_all_next("table") ## Tables for Indikativ und Konjuktiv
	for table in indkon:
		rows = table.find_all("tr")
		cutrow = [ri for ri, row in enumerate(rows) if row.text.strip().lower() in ["", "text"]] ## Find the empty rows between two tables
		tablerows = [rows[cut+1:([-1]+cutrow+[len(rows)])[ci+1]] for ci, cut in enumerate([-1] + cutrow)] ## List of lists of rows, one sublist for one table
		tablerows = [_ for _ in tablerows if _ != []] ## Remove empty tables
		for subtable in tablerows:
			tense = subtable[0].text.strip() ## tense
			if not tense in want_ind_tenses: ## only get the tenses we need
				continue
			conj[tense] = OrderedDict()
			headers = [(int(header.get("colspan",1)), header.text.strip()) for header in subtable[1].find_all(["th", "td"])] # e.g. [(1, ""), (1, "Person"), (2, "Aktiv"), ...]
			headers = reduce(lambda x,y:x+[y[1] for _ in range(y[0])], headers, []) # e.g. ["", "Person", "Aktiv", "Aktiv", ...]
					##person_col = [hi for hi, head in enumerate(headers) if head == "Person"] # Column for persons
			##if person_col == []:
			##	person_col = [hi for hi, head in enumerate(subtable[2].find_all(["th", "td"])) if head.text.strip() == "Person"]
			##	person_col = person_col[0] if person_col else None
			##else: person_col = person_col[0]
			subtable[2:] = [row.find_all(["th","td"]) for row in subtable[2:]] # Split the rest of the table into columns
			for aktiv in want_aktiv:
				conj[tense][aktiv] = OrderedDict()
				want_cols = [hi for hi, head in enumerate(headers) if head == aktiv] ## Columns for the aktiv/passive
				for col in want_cols:
					indikativ = subtable[2][col].text.strip() ## Indikativ/Konjunktiv
					conj[tense][aktiv][indikativ] = []
					##conj[tense][aktiv][indikativ] = OrderedDict()
					for row in subtable[3:]:
						if not is_blank(row[col].text):
							forms = row[col].text.split(",") ## e.g. ["ich sammel", "ich sammele"]
							conj[tense][aktiv][indikativ].append(" %% ".join([person_word(x.strip().split(": ")[-1]) for x in forms])) ## ": " to avoid machen, "," to avoid sammeln
							##conj[tense][aktiv][indikativ][row[person_col].text.strip()] = row[col].text.strip()
							if tense == "Perfekt":
								break ## Only need one
	s = []
	for tense in want_ind_tenses:
		for aktiv in want_aktiv:
			for indikativ, forms in conj[tense][aktiv].items():
				if forms:
					s.append(indikativ+" "+tense+" "+aktiv+": "+", ".join(forms))
	conj["Imperativ"] = OrderedDict()
	imperativ = soup.find("span", {"id":"Imperativ"}).find_next("table")
	subtable = imperativ.find_all("tr")
	if (subtable[0].text.strip() != "Imperative") or len(subtable) != 5:
		print("Bad imperative, ignored. Check out %s." % url)
	else:
		subtable[2:] = [row.find_all(["th","td"]) for row in subtable[2:]]
		persons = ["du", "ihr", "Sie"]
		for tense in want_imp_tenses:
			col = [i for i,x in enumerate(subtable[1].find_all(["th","td"])) if x.text.strip() == tense][0]
			res = []
			for ri, row in enumerate(subtable[2:]):
				if not is_blank(row[col].text):
					res.append(" %% ".join([persons[ri] + "+" + form.strip().split(": ")[-1] for form in row[col].text.strip().strip("!").split("!")]))
			if res:
				s.append("Imperativ "+tense+": "+", ".join(res))
	return s

def get_inf_and_conj_de(word):
	url = "https://de.wiktionary.org/wiki/" + word
	r = requests.get(url)
	soup = BeautifulSoup(r.text)
	de_head = list(filter(lambda x:x.text == word + " (Deutsch)", soup.find_all("span", {"class":"mw-headline"})))
	if not de_head:
		print("In finding infinitive, no Deutsch found for '%s'." % word)
		return None
	elif len(de_head) > 1:
		print("Multiple Deutsch found for %s. Returning the first." % word)
	konj_form = len(soup.find_all("span", {"class":"mw-headline", "id":"Konjugierte_Form"})) == 1
	alle_form = "Alle weiteren Formen" in str(soup) ## Not a good criteria for the verb being infinitive; could be conjugations for other languages
	if konj_form or not alle_form:
		try:
			infinitives = unique_everseen([entry.find("a")["title"] for entry in de_head[0].find_next("span", id="Grammatische_Merkmale").find_next(["ul","ol","dl"]).find_all(["dd","li"])])
			if len(infinitives) == 0:
				print("Unable to extract the infinitive of %s." % word)
			elif len(infinitives) > 1:
				print("Multiple infinitives found for %s: %s. Returning all" % (word, ", ".join(infinitives)))
		except:
			if konj_form:
				print("%s says Konjugierte Form, but unable to extract the infinitive of %s." % (url, word))
			else:
				print("Unable to extract the infinitive of %s." % word)
			infinitives = []
	else:
		#print("Treating %s itself as the infinitive." % word)
		infinitives = [word]
	for i, inf in enumerate(infinitives):
		try:
			infinitives[i] = (inf, get_conj_de(inf))
		except:
			print("No conjugations found for %s. Removed." % inf)
			infinitives[i] = None
	infinitives = [pair for pair in infinitives if pair is not None]
	if infinitives:
		print("%s -> %s" % (word, ", ".join([word for word, conj in infinitives])))
	return infinitives


word_and_IPA = (lambda x,IPA_dict={}:x+" ** "+get_de_IPA(x,IPA_dict))

def conjugations_de(word, IPA_dict={}):
	list_conjs = get_inf_and_conj_de(word)
	if list_conjs is None:
		return [], []
	s = []
	infs = []
	for pair in list_conjs: ## Each entry in conjugations
		inf, conjs = pair
		infs.append(inf)
		for ci, conj in enumerate(conjs):
			conjs[ci] = conj.split(": ")[0] + ": "+ ", ".join([" %% ".join(oneform.split("+")[0] + "+" + word_and_IPA("+".join(oneform.split("+")[1:]), IPA_dict) for oneform in form.split(" %% ")) for form in conj.split(": ")[1].split(", ")])
			# form: each person, e.g. ich sammle %% ich sammel %% ich sammele, OR du sammelst;  oneform: each one form, e.g. ich sammle
		s += [word_and_IPA(inf, IPA_dict) + ": " + "; ".join(conjs)]
	return infs, s


def process_duo_de(l, filename, IPA_dict={}):
	"""
		Takes the word list from Duolingo
		Assumes the file has the form "Word\tPart of speech\tAnything else"
		First loads the words already processed in the files located in Processed and avoids them in the processing
		Generates a word list as word ** [] ** part_of_speech_or_nothing, where [] is a placeholder for the IPA
		###Old: If POS==Verb, conjugate the word to infinitive; if different, see if the infinitive is really in the verb list of pattern.de (not generated by some unrealiable rules); if so, replace the word by the infinite, otherwise keep the word
		####Stores all verbs (including the ones whose conjugated infinitives are not in the verb list) and their conjugations in a separate file, where conjugations are automatically generated for the reliable words
		Use wiktionary to get the conjugations and corresponding IPAs for all verbs
		Finally removes the file to Processed/
	"""
	words_processed = []
	if not os.path.exists("Processed"):
		os.mkdir("Processed")
	for processed_file in glob.glob("Processed/*.txt"):
		words_processed.extend([x.split("\t")[0] for x in codecs.open(processed_file, "r", "utf-8").readlines()])
	words_processed = set(words_processed)
	new_list = [] ## Allocate memory
	verbs = []
	for line in l:
		s = line.split("\t")
		word, pos = s[0], s[1]
		if word in words_processed:
			continue
		words_processed.add(word)
		if pos == "Verb":
			"""
			infinitive = pattern.de.conjugate(word)
			if infinitive != word:
				if infinitive in pattern.de.verbs: ## If the infinitive is really in the known list, not using some fallback general rule which might fail
					print("%s changed to %s." % (word, pattern.de.conjugate(word)))
					word = pattern.de.conjugate(word)
				else:
					print("%s changed to %s, but %s does not exist in the list of infinitives. Please double check." % (word, infinitive, infinitive))
					verbs.append(word)
			"""
			infs, conjs = conjugations_de(word, IPA_dict)
			verbs.extend(zip(infs, conjs))
			new_list.extend([(inf, to_pos(pos)) for inf in infs])
		else:
			new_list.append((word, to_pos(pos)))
	new_list = unique_everseen(new_list, key=lambda x:x[0])
	verbs = unique_everseen(verbs, key=lambda x:x[0])
	"""
	conjus = ["" for _ in range(len(verbs))]
	for vi, verb in enumerate(verbs):
		if verb in pattern.de.verbs:
			conjus[vi] = verb + " ** " + get_de_IPA(verb, IPA_dict) + ": " + conjugations_de(verb)
		else:
			print("Fill in conjugations for %s." % verb)
			conjus[vi] = verb + " ** " + get_de_IPA(verb, IPA_dict) + ": " + "FILL IN CONJUGATIONS " + conjugations_de(None)
	"""
	conjus = [v[1] for v in verbs]
	g = codecs.open(filename.replace(".txt", " conj.txt"), 'w', "utf-8")
	g.write("\n".join(conjus))
	g.close()
	os.rename(filename, "Processed/"+filename)
	return "\n1\n" + "\n".join([x[0] + " ** [] ** " + x[1] for x in new_list]) + "\n"

def get_conj_fr(word):
	url = "https://fr.wiktionary.org/wiki/Annexe:Conjugaison_en_fran%C3%A7ais/" + word
	r = requests.get(url)
	if not r.ok:
		print("Cannot find the page for %s. Stopped." % word)
		return word+" MISSING", []
	soup = BeautifulSoup(r.text)
	groupes = {"premier groupe":1, u"deuxième groupe":2, u"troisième groupe":3}
	try:
		alt_word = soup.find(text=re.compile("Conjugaison de")).find_next().text.replace(u"\u2019", "'")
		if (word.startswith("se ") or word.startswith(u"s'")):
			if alt_word == re.sub("^s'","",re.sub("^se ","",word)):
				print("%s changed to %s." % (word, alt_word))
				word = alt_word
		else:
			if alt_word in ["se "+word, "s'"+word]:
				print("%s changed to %s." % (word, alt_word))
				word = alt_word
	except:
		pass
	try:
		groupe = groupes[soup.find(text=re.compile("Verbe du")).find_next().text]
	except Exception as e:
		print("Error occurred when finding the groupe of %s: %s" % (word, e))
		groupe = 0
	process_IPA = lambda x:"["+x.strip().strip("\\")+"]"
	conj = []
	table = soup.find("span", {"class":"mw-headline", "id":"Modes_impersonnels"}).find_next("table")
	rows = table.find_all("tr")
	headers = [(int(header.get("colspan",1)), header.text.strip()) for header in rows[0].find_all(["th", "td"])]
	inf_IPA = ["MISSING"]
	if headers != [(1, u'Mode'), (3, u'Pr\xe9sent'), (3, u'Pass\xe9')]:
		print("Bad header for modes impersonnels for %s: %s" % (word, headers))
	else:
		try:
			reflexive = word.startswith("se ") or word.startswith(u"s'") ## se souvenir
			infs = rows[1].find_all(["th","td"])
			if not (infs[0].text.strip() == "Infinitif" and (infs[2].text.strip() == word or (reflexive and infs[2].text.strip() == re.sub("^s'","", re.sub("^se ","",word))))):
				print("Sanity check 1 failed: infs[0]=%s, infs[2]=%s. AssertionError." % (infs[0].text.strip(), infs[2].text.strip()))
				assert False
			inf_IPA = process_IPA(infs[3].text)
			aux_verb = re.sub(u"^s\u2019", "", infs[4].text.strip())
			if not aux_verb in ["avoir", u"être"]:
				print(u"Auxiliary verb %s not in avoir or être. AssertionError." % aux_verb)
				assert False
			past_p = infs[5].text.strip()
			past_p_IPA = process_IPA(infs[6].text)
			conj.append(u"Passé: Infinitif+"+u"s'"*reflexive+aux_verb+" "+past_p+" ** "+past_p_IPA)
			pps = rows[3].find_all(["th","td"])
			if pps[0].text.strip() != "Participe":
				print("pps[0]=%s!=Participe. AssertionError." % pps[0].text.strip())
				assert False
			pres_p = pps[2].text.strip()
			pres_p_IPA = process_IPA(pps[3].text)
			conj.append(u"Participe présent: Participe+"+pres_p+" ** "+pres_p_IPA)
		except Exception as e:
			print("Error occurred when handling modes impersonnels for %s: %s" % (word, e))
	is_blank = lambda x:len(x.strip()) == 1 and ord(x.strip()) in range(8208, 8214)
	imp_persons = ["tu", "nous", "vous"]
	for indicatif in ["Indicatif", "Subjonctif", "Conditionnel", u"Impératif", u"Impératif_2"]:
		try:
			table = soup.find("span", {"class":"mw-headline", "id":indicatif}).find_next("table")
			contents = [x.text.strip() for x in table.find_all(["th","td"]) if x.text.startswith("\n\n")]
			for content in contents:
				subcontents = content.split("\n\n\n")
				tense = subcontents[0]
				if not tense: #### CHANGE TO SELECT TENSES
					continue
				forms = []
				for ri, personcontent in enumerate(subcontents[1:]):
					personcontent = personcontent.replace("\n\n", "\n")
					personcontents = personcontent.split("\n")
					IPA_start = [i for i,_ in enumerate(personcontents) if _.startswith("\\")][0]
					form = " ".join(map(lambda x:x.strip().replace("j'","j' ").replace(u"j\u2019",u"j\u2019 "), personcontents[0:IPA_start])).strip() ## j'ai -> j' ai
					##form = re.sub(u"^qu[e\u2019][ ]?", "", form) ## que je/qu'il -> je/il
					form = form.replace(u"\u2019", "'")
					if indicatif.startswith(u"Impératif"):
						form = imp_persons[ri] + " " + form ## tu sois
						if indicatif == u"Impératif_2": ## souviens-toi
							form = form.replace(" -", "-")
					if indicatif == u"Subjonctif" and form.startswith("que "):
						person = " ".join(form.split(" ")[0:2])
						form = " ".join(form.split(" ")[2:])
					else:
						person = form.split(" ")[0]
						form = " ".join(form.split(" ")[1:])
					if not is_blank(form):
						form = person.strip()+"+"+form.strip()
						IPA = process_IPA(" ".join(map(lambda x:x.strip(), personcontents[IPA_start:])))
						forms.append(form+" ** "+IPA)
				if forms:
					conj.append(indicatif.replace("_2","") + " " + tense.replace(" (rare)","") + ": " + ", ".join(forms)) ## Imperatif_2 -> Imperatif
			if indicatif == u"Impératif": ## If imperatives are in imperatif_2 only then an error would have occurred already
				break
		except Exception as e:
			print("Error occurred when extracting %s for %s: %s" % (indicatif, word, e))
	return word+" (%s) ** "%groupe+inf_IPA+": "+"; ".join(conj), conj



def choose_file(pattern, pattern_string):
	available_files = [f for f in os.listdir(".") if re.match(pattern, f)] ## List of files that look like INTEGER.txt
	if len(available_files) == 0:
		print("No files found. Files to be processed for generation must be of the form %s." % pattern_string)
		return
	elif len(available_files) == 1:
		available_files = list(available_files)
		print("Only one file %s exists. Automatically chosen." % available_files[0])
		filename = available_files[0]
	else:
		filename = input_function("Please enter the file name:\n%s\n" % ", ".join(sorted(available_files)))
		while not filename in available_files:
			filename = input_function("Please enter a correct file number.\n")
			if filename.upper() in ["Q", "QUIT"]:
				return
	return filename

def main():
	os.chdir(pathToWordList)
	ls = list(filter(os.path.isdir, os.listdir(pathToWordList))) ## book names
	if len(ls) == 1:
		chosen = ls[0]
	else:
		ls = sorted(ls)
		r = ""
		while not any([unidecode.unidecode(r.decode("utf-8"))==unidecode.unidecode(_.decode("utf-8")) for _ in ls]):
			r = input_function("Please choose a book number from the following: " + ", ".join(ls)+"\n")
		r = [_ for _ in ls if unidecode.unidecode(r.decode("utf-8"))==unidecode.unidecode(_.decode("utf-8"))][0]
		chosen = r
	os.chdir(os.path.join(chosen, "Lists"))
	inp = ""
	IPA_dict = {}
	while not inp.upper() in ["Q", "QUIT"]:
		inp = input_function("Please choose from the following: generate lists (G), get IPA for a generated list (I), sort lists (S), conjugate French (C), or quit (Q).\n").upper()
		if inp in ["Q", "QUIT"]:
			break
		elif inp == "G":
			filename = choose_file(r"[0-9]+.txt", "\"NUMBER.txt\"")
			if filename is None:
				print("No file found.")
				continue
			command = input_function("Enter \"S\" to skip sorting, enter \"O\" to only make one copy.\n")
			f = codecs.open(filename, "r", "utf-8")
			l = f.readlines()
			if all([x in "".join(l) for x in ["*","[","]"]]):
				print("The list has already been generated.")
				continue
			if not "S" in command.upper():
				l = sorted(l, key=lambda x:(unidecode.unidecode(x)).lower())
			if chosen == "Duo_de":
				s = process_duo_de(l, filename, IPA_dict)
			else:
				s = process_plain(l)
			if "O" in command.upper():
				lang = ["en"]
			else:
				lang = ["en", "ja", "zh-cn", "zh-hk"]
			for st in lang:
				g = codecs.open(filename.replace(".txt", " %s.txt" % st), 'w', "utf-8")
				g.write(s)
				g.close()
		elif inp == "I":
			filename = choose_file()
			s = [x.split(" ** ") for x in codecs.open(filename, "r", "utf-8").readlines()]
			assert set(map(len, s)).issubset(set([1,3]))
			s2 = [x[0] if len(x) == 1 else x[0] + " ** " + get_de_IPA(x[0], IPA_dict) + " ** " + x[2] for x in s]
			g = codecs.open(f, "w", "utf-8")
			g.write("".join(s2))
			g.close()
		elif inp == "C":
			if unidecode.unidecode(r.decode("utf-8")) != unidecode.unidecode(u"Français"):
				print(u"Currently supported for Français only. Stopped")
				continue
			filename = choose_file(r"[0-9]+ verbs.txt", "\"NUMBER verbs.txt\"")
			if filename is None:
				print("No file found.")
				continue
			if os.path.exists(filename.replace(" verbs.txt", " conj.txt")):
				print(filename.replace(" verbs.txt", " conj.txt") + " already exists. Please delete first.")
				continue
			f = codecs.open(filename, "r", "utf-8")
			l = f.readlines()
			if (len(l) > 1 and l[1].strip() != "") or (not " || " in l[0]): ## also complains if only one verb
				print("Make sure your file has one line with verbs separated by \" || \". Stopped.")
				continue
			words = sorted(l[0].strip().split(" || "), key=lambda x:(unidecode.unidecode(x)).lower())
			conjs = []
			for word in words:
				try:
					conjs.append(get_conj_fr(word)[0])
				except Exception as e:
					print("Error occurred for %s: %s." % (word, e))
			conjs = unique_everseen(conjs)
			g = codecs.open(filename.replace(" verbs.txt", " conj.txt"), "w", "utf-8")
			g.write("\n".join(conjs))
			g.close()
### IPA must be added after generating a list
### IPA for conjugation verbs should also be added only after a list is generated and is manually checked

if __name__ == "__main__":
	main()

