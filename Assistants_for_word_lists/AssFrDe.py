# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import glob
import inspect
import os
import re
import requests


import unidecode
from HelpersFr import get_conj_fr, to_pos
from collections import OrderedDict
from functools import reduce

SOUP_PARSER = "html.parser"


# # Functions from Help_funs.py; remember to sync # #
def unique_everseen(seq, key=lambda x: x):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (key(x) in seen or seen_add(key(x)))]

# # Functions from Help_funs.py; remember to sync # #


pathToWordList = os.path.join(
    "/".join(os.path.realpath(__file__).split("/")[:-1]), "../Word lists"
)


def printNames():
    Ass = __import__(inspect.getmodulename(__file__))
    for name in dir(Ass):
        obj = getattr(Ass, name)
        if inspect.isfunction(obj):
            print((obj.__name__))
    return


def process_plain(li):
    return "\n1\n" + "".join([i.replace("\n", "") + " ** [] ** \n" for i in li])
    # return "\n1\n" + "".join([i[0].replace("\n","") + " ** [] ** %s\n" % (i[1] if len(i)>1 else "") for i in (s.split("\t") for s in lines)]) # Treating the


def get_de_IPA_word(word):
    """
    Attempts to get the IPA of a word from de.wiktionary
    """
    try:
        r = requests.get(f"https://de.wiktionary.org/wiki/{word}")
        soup = BeautifulSoup(r.text, SOUP_PARSER)
        de_head = [
            x
            for x in soup.find_all("span", {"class": "mw-headline"})
            if x.text == word + " (Deutsch)"
        ]
        if not de_head:
            # Strings that have multiple words will be processed independently again
            if len(word.split(" ")) == 1:
                print(("In finding IPA, no Deutsch found for '%s'." % word))
            return None
        elif len(de_head) > 1:
            print(("Multiple Deutsch found for %s. Returning the first." % word))
        IPAs = []
        # The first IPA element
        next_IPA_elt = de_head[0].find_next("span", {"class": "ipa"})
        if not next_IPA_elt:
            return None
        IPAs.append(next_IPA_elt.text)
        # Keep adding if the next span elt is an IPA
        while (
            "class" in next_IPA_elt.find_next("span").attrs
            and "ipa" in next_IPA_elt.find_next("span")["class"]
        ):
            next_IPA_elt = next_IPA_elt.find_next("span")
            IPAs.append(next_IPA_elt.text)
        IPA = "/".join(IPAs)
        # Legacy for [...], not sure if will encounter again
        if IPA == "\u2026":
            print(("No IPA given for '%s'." % word))
            return None
        return "[" + IPA + "]"
    except Exception as e:
        print(
            ("Unable to get IPA for '%s' due to the following error: " % word + str(e))
        )
        return None


def get_de_IPA(string, IPA_dict={}):
    """
    Attempts to get the IPA of a string (could be made of multiple words)
    """
    # Need to pay attention to the ones with + after printing
    # print(string)
    # print(IPA_dict)
    if string in IPA_dict:
        return "[" + IPA_dict[string] + "]"
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
                    one_IPA = (
                        "MISSING" if one_IPA is None else one_IPA[1:-1]
                    )  # None -> Missing, [IPA] to IPA
                    IPAs.append(one_IPA)
                    IPA_dict[word] = IPAs[-1]
            IPA = "[" + "+".join(IPAs) + "]"  # [bɪs][ˈmɔʁɡŋ̍] -> [bɪs+ˈmɔʁɡŋ̍]
        else:
            IPA = "[MISSING]"
    IPA_dict[string] = IPA.lstrip("[").rstrip("]")
    if "MISSING" in IPA:
        print(("Some IPA(s) for %s is/are missing." % string))
    return IPA


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
    want_ind_tenses = ["Pr\xe4sens", "Pr\xe4teritum", "Perfekt"]
    want_aktiv = ["Aktiv"]
    want_imp_tenses = ["Pr\xe4sens Aktiv"]
    url = "https://de.wiktionary.org/wiki/Flexion:" + word
    r = requests.get(url)
    soup = BeautifulSoup(r.text, SOUP_PARSER)

    def is_blank(x):
        return len(x.strip()) == 1 and ord(x.strip()) in range(8208, 8214)

    def person_word(y):
        # ich werde sein -> ich+werde sein
        return y.split(" ")[0] + "+" + " ".join(y.split(" ")[1:])

    conj = OrderedDict()
    indkon = soup.find("span", {"id": "Indikativ_und_Konjunktiv"}).find_all_next(
        "table"
    )  # Tables for Indikativ und Konjuktiv
    for table in indkon:
        rows = table.find_all("tr")
        cutrow = [
            ri
            for ri, row in enumerate(rows)
            if row.text.strip().lower() in ["", "text"]
        ]  # Find the empty rows between two tables
        tablerows = [
            rows[cut + 1 : ([-1] + cutrow + [len(rows)])[ci + 1]]
            for ci, cut in enumerate([-1] + cutrow)
        ]  # List of lists of rows, one sublist for one table
        tablerows = [_ for _ in tablerows if _ != []]  # Remove empty tables
        for subtable in tablerows:
            tense = subtable[0].text.strip()  # tense
            if tense not in want_ind_tenses:  # only get the tenses we need
                continue
            conj[tense] = OrderedDict()
            headers = [
                (int(header.get("colspan", 1)), header.text.strip())
                for header in subtable[1].find_all(["th", "td"])
            ]  # e.g. [(1, ""), (1, "Person"), (2, "Aktiv"), ...]
            headers = reduce(
                lambda x, y: x + [y[1] for _ in range(y[0])], headers, []
            )  # e.g. ["", "Person", "Aktiv", "Aktiv", ...]
            # person_col = [hi for hi, head in enumerate(headers) if head == "Person"] # Column for persons
            # if person_col == []:
            #    person_col = [hi for hi, head in enumerate(subtable[2].find_all(["th", "td"])) if head.text.strip() == "Person"]
            #    person_col = person_col[0] if person_col else None
            # else: person_col = person_col[0]
            subtable[2:] = [
                row.find_all(["th", "td"]) for row in subtable[2:]
            ]  # Split the rest of the table into columns
            for aktiv in want_aktiv:
                conj[tense][aktiv] = OrderedDict()
                want_cols = [
                    hi for hi, head in enumerate(headers) if head == aktiv
                ]  # Columns for the aktiv/passive
                for col in want_cols:
                    indikativ = subtable[2][col].text.strip()  # Indikativ/Konjunktiv
                    conj[tense][aktiv][indikativ] = []
                    # conj[tense][aktiv][indikativ] = OrderedDict()
                    for row in subtable[3:]:
                        if not is_blank(row[col].text):
                            forms = row[col].text.split(
                                ","
                            )  # e.g. ["ich sammel", "ich sammele"]
                            conj[tense][aktiv][indikativ].append(
                                " %% ".join(
                                    [
                                        person_word(x.strip().split(": ")[-1])
                                        for x in forms
                                    ]
                                )
                            )  # ": " to avoid machen, "," to avoid sammeln
                            # conj[tense][aktiv][indikativ][row[person_col].text.strip()] = row[col].text.strip()
                            if tense == "Perfekt":
                                break  # Only need one
    s = []
    for tense in want_ind_tenses:
        for aktiv in want_aktiv:
            for indikativ, forms in list(conj[tense][aktiv].items()):
                if forms:
                    s.append(
                        indikativ + " " + tense + " " + aktiv + ": " + ", ".join(forms)
                    )
    conj["Imperativ"] = OrderedDict()
    imperativ = soup.find("span", {"id": "Imperativ"}).find_next("table")
    subtable = imperativ.find_all("tr")
    if (subtable[0].text.strip() != "Imperative") or len(subtable) != 5:
        print(("Bad imperative, ignored. Check out %s." % url))
    else:
        subtable[2:] = [row.find_all(["th", "td"]) for row in subtable[2:]]
        persons = ["du", "ihr", "Sie"]
        for tense in want_imp_tenses:
            col = [
                i
                for i, x in enumerate(subtable[1].find_all(["th", "td"]))
                if x.text.strip() == tense
            ][0]
            res = []
            for ri, row in enumerate(subtable[2:]):
                if not is_blank(row[col].text):
                    res.append(
                        " %% ".join(
                            [
                                persons[ri] + "+" + form.strip().split(": ")[-1]
                                for form in row[col].text.strip().strip("!").split("!")
                            ]
                        )
                    )
            if res:
                s.append("Imperativ " + tense + ": " + ", ".join(res))
    return s


def get_inf_and_conj_de(word):
    url = "https://de.wiktionary.org/wiki/" + word
    r = requests.get(url)
    soup = BeautifulSoup(r.text, SOUP_PARSER)
    de_head = list(
        [
            x
            for x in soup.find_all("span", {"class": "mw-headline"})
            if x.text == word + " (Deutsch)"
        ]
    )
    if not de_head:
        print(("In finding infinitive, no Deutsch found for '%s'." % word))
        return None
    elif len(de_head) > 1:
        print(("Multiple Deutsch found for %s. Returning the first." % word))
    konj_form = (
        len(soup.find_all("span", {"class": "mw-headline", "id": "Konjugierte_Form"}))
        == 1
    )
    alle_form = "Alle weiteren Formen" in str(
        soup
    )  # Not a good criteria for the verb being infinitive; could be conjugations for other languages
    if konj_form or not alle_form:
        try:
            infinitives = unique_everseen(
                [
                    entry.find("a")["title"]
                    for entry in de_head[0]
                    .find_next("span", id="Grammatische_Merkmale")
                    .find_next(["ul", "ol", "dl"])
                    .find_all(["dd", "li"])
                ]
            )
            if len(infinitives) == 0:
                print(("Unable to extract the infinitive of %s." % word))
            elif len(infinitives) > 1:
                print(
                    (
                        "Multiple infinitives found for %s: %s. Returning all"
                        % (word, ", ".join(infinitives))
                    )
                )
        except Exception:
            if konj_form:
                print(
                    (
                        "%s says Konjugierte Form, but unable to extract the infinitive of %s."
                        % (url, word)
                    )
                )
            else:
                print(("Unable to extract the infinitive of %s." % word))
            infinitives = []
    else:
        # print("Treating %s itself as the infinitive." % word)
        infinitives = [word]
    for i, inf in enumerate(infinitives):
        try:
            infinitives[i] = (inf, get_conj_de(inf))
        except Exception:
            print(("No conjugations found for %s. Removed." % inf))
            infinitives[i] = None
    infinitives = [pair for pair in infinitives if pair is not None]
    if infinitives:
        print(("%s -> %s" % (word, ", ".join([word for word, conj in infinitives]))))
    return infinitives


def word_and_IPA(x, IPA_dict={}):
    return x + " ** " + get_de_IPA(x, IPA_dict)


def conjugations_de(word, IPA_dict={}):
    list_conjs = get_inf_and_conj_de(word)
    if list_conjs is None:
        return [], []
    s = []
    infs = []
    for pair in list_conjs:  # Each entry in conjugations
        inf, conjs = pair
        infs.append(inf)
        for ci, conj in enumerate(conjs):
            conjs[ci] = (
                conj.split(": ")[0]
                + ": "
                + ", ".join(
                    [
                        " %% ".join(
                            oneform.split("+")[0]
                            + "+"
                            + word_and_IPA("+".join(oneform.split("+")[1:]), IPA_dict)
                            for oneform in form.split(" %% ")
                        )
                        for form in conj.split(": ")[1].split(", ")
                    ]
                )
            )
            # form: each person, e.g. ich sammle %% ich sammel %% ich sammele, OR du sammelst;  oneform: each one form, e.g. ich sammle
        s += [word_and_IPA(inf, IPA_dict) + ": " + "; ".join(conjs)]
    return infs, s


def process_duo_de(lines, filename, IPA_dict={}):
    """
    Takes the word list from Duolingo
    Assumes the file has the form "Word\tPart of speech\tAnything else"
    First loads the words already processed in the files located in Processed and avoids them in the processing
    Generates a word list as word ** [] ** part_of_speech_or_nothing, where [] is a placeholder for the IPA
    ##Old: If POS==Verb, conjugate the word to infinitive; if different, see if the infinitive is really in the verb list of pattern.de (not generated by some unrealiable rules); if so, replace the word by the infinite, otherwise keep the word
    ##Stores all verbs (including the ones whose conjugated infinitives are not in the verb list) and their conjugations in a separate file, where conjugations are automatically generated for the reliable words
    Use wiktionary to get the conjugations and corresponding IPAs for all verbs
    Finally removes the file to Processed/
    """
    words_processed = []
    if not os.path.exists("Processed"):
        os.mkdir("Processed")
    for processed_file in glob.glob("Processed/*.txt"):
        with open(processed_file) as f:
            words_processed.extend([x.split("\t")[0] for x in f.readlines()])
    words_processed = set(words_processed)
    new_list = []  # Allocate memory
    verbs = []
    for line in lines:
        s = line.split("\t")
        word, pos = s[0], s[1]
        if word in words_processed:
            continue
        words_processed.add(word)
        if pos == "Verb":
            """
            infinitive = pattern.de.conjugate(word)
            if infinitive != word:
                    if infinitive in pattern.de.verbs: # If the infinitive is really in the known list, not using some fallback general rule which might fail
                            print("%s changed to %s." % (word, pattern.de.conjugate(word)))
                            word = pattern.de.conjugate(word)
                    else:
                            print("%s changed to %s, but %s does not exist in the list of infinitives. Please double check." % (word, infinitive, infinitive))
                            verbs.append(word)
            """
            infs, conjs = conjugations_de(word, IPA_dict)
            verbs.extend(list(zip(infs, conjs)))
            new_list.extend([(inf, to_pos(pos)) for inf in infs])
        else:
            new_list.append((word, to_pos(pos)))
    new_list = unique_everseen(new_list, key=lambda x: x[0])
    verbs = unique_everseen(verbs, key=lambda x: x[0])
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
    with open(filename.replace(".txt", " conj.txt"), "w") as g:
        g.write("\n".join(conjus))
    os.rename(filename, "Processed/" + filename)
    return "\n1\n" + "\n".join([x[0] + " ** [] ** " + x[1] for x in new_list]) + "\n"


def choose_file(pattern, pattern_string):
    available_files = [
        f for f in os.listdir(".") if re.match(pattern, f)
    ]  # List of files that look like INTEGER.txt
    if len(available_files) == 0:
        print(
            (
                "No files found. Files to be processed for generation must be of the form %s."
                % pattern_string
            )
        )
        return
    elif len(available_files) == 1:
        available_files = list(available_files)
        print(("Only one file %s exists. Automatically chosen." % available_files[0]))
        filename = available_files[0]
    else:
        filename = input(
            "Please enter the file name:\n%s\n" % ", ".join(sorted(available_files))
        )
        while filename not in available_files:
            filename = input("Please enter a correct file number.\n")
            if filename.upper() in ["Q", "QUIT"]:
                return
    return filename


def main():
    os.chdir(pathToWordList)
    ls = list(filter(os.path.isdir, os.listdir(pathToWordList)))  # book names
    if len(ls) == 1:
        chosen = ls[0]
    else:
        ls = sorted(ls)
        r = ""
        while not any([unidecode.unidecode(r) == unidecode.unidecode(_) for _ in ls]):
            r = input(
                "Please choose a book number from the following: "
                + ", ".join(ls)
                + "\n"
            )
        r = [_ for _ in ls if unidecode.unidecode(r) == unidecode.unidecode(_)][0]
        chosen = r
    os.chdir(os.path.join(chosen, "Lists"))
    inp = ""
    IPA_dict = {}
    while not inp.upper() in ["Q", "QUIT"]:
        inp = input(
            "Please choose from the following: generate lists (G), get IPA for a generated list (I), sort lists (S), conjugate French (C), or quit (Q).\n"
        ).upper()
        if inp in ["Q", "QUIT"]:
            break
        elif inp == "G":
            filename = choose_file(r"[0-9]+.txt", '"NUMBER.txt"')
            if filename is None:
                print("No file found.")
                continue
            command = input(
                'Enter "S" to skip sorting, enter "O" to only make one copy.\n'
            )
            with open(filename, "r") as f:
                lines = f.readlines()
            if all([x in "".join(lines) for x in ["*", "[", "]"]]):
                print("The list has already been generated.")
                continue
            if "S" not in command.upper():
                lines = sorted(lines, key=lambda x: (unidecode.unidecode(x)).lower())
            if chosen == "Duo_de":
                s = process_duo_de(lines, filename, IPA_dict)
            else:
                s = process_plain(lines)
            if "O" in command.upper():
                lang = ["en"]
            else:
                lang = ["en", "ja", "zh-cn", "zh-hk"]
            for st in lang:
                with open(filename.replace(".txt", " %s.txt" % st), "w") as g:
                    g.write(s)
        elif inp == "I":
            filename = choose_file(r"[0-9]+.txt", '"NUMBER.txt"')
            with open(filename, "r", "utf-8") as f:
                s = [x.split(" ** ") for x in f.readlines()]
            assert set(map(len, s)).issubset(set([1, 3]))
            s2 = [
                x[0]
                if len(x) == 1
                else x[0] + " ** " + get_de_IPA(x[0], IPA_dict) + " ** " + x[2]
                for x in s
            ]
            with open(filename.replace(".txt", " 2.txt"), "w") as g:
                g.write("".join(s2))
        elif inp == "C":
            if unidecode.unidecode(r) != unidecode.unidecode("Français"):
                print("Currently supported for Français only. Stopped")
                continue
            filename = choose_file(r"[0-9]+ verbs.txt", '"NUMBER verbs.txt"')
            if filename is None:
                print("No file found.")
                continue
            if os.path.exists(filename.replace(" verbs.txt", " conj.txt")):
                print(
                    (
                        filename.replace(" verbs.txt", " conj.txt")
                        + " already exists. Please delete first."
                    )
                )
                continue
            with open(filename, "r") as f:
                lines = f.readlines()
            if (len(lines) > 1 and lines[1].strip() != "") or (
                " || " not in lines[0]
            ):  # also complains if only one verb
                print(
                    'Make sure your file has one line with verbs separated by " || ". Stopped.'
                )
                continue
            words = sorted(
                lines[0].strip().split(" || "),
                key=lambda x: (unidecode.unidecode(x)).lower(),
            )
            conjs = []
            for word in words:
                try:
                    conjs.append(get_conj_fr(word)[0])
                except Exception as e:
                    print(("Error occurred for %s: %s." % (word, e)))
            conjs = unique_everseen(conjs)
            with open(filename.replace(" verbs.txt", " conj.txt"), "w") as g:
                g.write("\n".join(conjs))


# NOTE: IPA must be added after generating a list
# NOTE: IPA for conjugation verbs should also be added only after a list is generated and is manually checked

if __name__ == "__main__":
    main()
