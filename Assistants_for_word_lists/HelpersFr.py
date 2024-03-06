# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup, element
import requests
import re
from typing import Optional, Tuple
from tqdm import tqdm

SOUP_PARSER = "html.parser"
UNKNOWN = "UNKNOWN"

POS_EN = {
    "Verb": "v.",
    "Noun": "n.",
    "Adjective": "a.",
    "Adverb": "adv.",
    "Contraction": "cont.",
    "Article": "art.",
    "Pronoun": "pron.",
    "Conjunction": "conj.",
    "Determiner": "det.",
    "Preposition": "prep.",
    "Interjection": "interj.",
    "Participle": "part.",
}


fr_IPA_dict = {}


# # Functions from Help_funs.py; remember to sync # #
def isInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def line_is_a_word_entry(row):
    return not (row.isspace() or isInt(row) or row.strip().startswith("##"))


# # Functions from Help_funs.py; remember to sync # #


def to_pos(pos):
    return POS_EN.get(pos, pos)


def get_fr_head(word, page_lang):
    """
    Attempts to get the head element for Français from fr.wiktionary
    """
    assert page_lang in ["en", "fr"]
    try:
        r = requests.get(f"https://{page_lang}.wiktionary.org/wiki/{word}")
        soup = BeautifulSoup(r.text, SOUP_PARSER)
        fr_head = soup.find_all(
            "span",
            {
                "class": "mw-headline",
                "id": "Français" if page_lang == "fr" else "French",
            },
        )
        if not fr_head:
            # Strings that have multiple words will be processed independently again
            if len(word.split(" ")) == 1:
                print(("In finding IPA, no Français found for '%s'." % word))
            return None
        elif len(fr_head) > 1:
            print(("Multiple Français found for %s. Returning the first." % word))
        return fr_head[0]
    except Exception as e:
        print(
            (
                "Unable to get the head element for '%s' due to the following error: "
                % word
                + str(e)
            )
        )


def get_fr_IPA_word(word):
    """
    Attempts to get the IPA of a word from fr.wiktionary
    """
    if word in fr_IPA_dict:
        return fr_IPA_dict[word]
    IPAs = []
    try:
        r = requests.get(f"https://fr.wiktionary.org/wiki/{word}")
        soup = BeautifulSoup(r.text, SOUP_PARSER)
        titres = [
            s
            for s in soup.find_all("span", {"class": "titredef"})
            if s.get("id").startswith("fr-")
        ]
        for elt in titres:
            while not elt.findChildren("span", {"class": "API"}):
                elt = elt.find_next("p")
            IPA_elts = elt.findChildren("span", {"class": "API"})
            for IPA_elt in IPA_elts:
                if IPA_elt.text not in IPAs:
                    IPAs.append(IPA_elt.text)
        IPA = "/".join(ipa.strip("\\") for ipa in IPAs)
        fr_IPA_dict[word] = IPA
        return IPA
    except Exception as e:
        print(
            ("Unable to get IPA for '%s' due to the following error: " % word + str(e))
        )
    return None


def span_text(elt: element.Tag) -> Optional[str]:
    if elt is None:
        return None
    span = elt.find_next("span")
    if span:
        return span.text
    return None


def additional_verb_pos(text: str) -> Tuple[str, str]:
    """ """
    for pattern, verb_type in [
        ("transitive", "t."),
        ("intransitive", "i."),
        ("reflexive", "pr."),
    ]:
        if text.startswith(f"({pattern})"):
            return verb_type, text.lstrip(f"({pattern})").strip()
        if text.startswith(f"({pattern},"):
            return verb_type, "(" + text.lstrip(f"({pattern},").strip()
    return "", text


def get_meaning_under_elt(
    pos: str,
    elt: element.Tag,
) -> str:
    """
    ol: List[Tuple[str, bs4.element.Tag]] whose elements are tuples of
        part of speech followed by an ol tag
    """
    res = []
    ol = elt.find_next("ol")
    lis = ol.findChildren("li", recursive=False)
    if pos == "n.":
        gender = elt.find_next("abbr").text
        if gender not in ["m", "f"]:
            raise Exception(f"Expecting gender to be m or f for a noun. Found {gender}")
        pos += gender + "."
    # Example phrases come after \n for each item
    subres = [li.text.split("\n")[0] for li in lis]
    for r in subres:
        if not r:
            continue
        if pos == "v.":
            # If the entry is a conjugation of a verb, remove this meaning
            if re.match("inflection of.+:", r):
                continue
            verb_type, text = additional_verb_pos(r)
            res.append(f"{pos}{verb_type} {text}")
        else:
            res.append(f"{pos} {r}")
    return res


def get_en_french_meanings(word: str) -> str:
    head = get_fr_head(word, "en")
    # Good keywords include those in ignores (just ignore) and parts of speech in POS_EN
    # If other keywords appear in h4, then search for h3; if h3 still contains a bad
    # keyword, stop
    ignores = ["Etymology", "Pronunciation", "Alternative forms"]
    # Check: coco, yaourt, lui, ouf, faire, plus
    meanings = []
    # Try to find h4 first
    while head:
        if span_text(head) is None:
            break
        next_node = head.find_next("h4")
        next_text = span_text(next_node)
        if next_text in ignores:
            head = next_node
            continue
        if next_text in POS_EN:
            head = next_node
            meanings.extend(get_meaning_under_elt(POS_EN[next_text], head))
            continue
        head = head.find_next("h3")
        next_text = span_text(head)
        if next_text in ignores:
            continue
        if next_text in POS_EN:
            meanings.extend(get_meaning_under_elt(POS_EN[next_text], head))
            continue
        break
    if not meanings:
        print(f"No en meanings found for {word}.")
    return " %% ".join(meanings)


def create_fr_IPA_and_en_meaning(word: str) -> str:
    ipa = get_fr_IPA_word(word)
    # If a phrase without IPA result, try each word in the phrase
    if not ipa and len(word.split()) > 1:
        ipas = [get_fr_IPA_word(w) for w in word.split()]
    else:
        ipas = [ipa]
    # Replace the null IPAs with UNKNOWN
    IPA = "[" + " ".join([ipa or UNKNOWN for ipa in ipas]) + "]"
    meaning = get_en_french_meanings(word) or UNKNOWN
    meaning = meaning.replace(word, "~")
    return word + " ** " + IPA + " ** " + meaning


def generate_fr_en_list(filename, lang="en") -> None:
    if lang != "en":
        raise ValueError("Only en supported for now.")
    new_filename = filename.replace(".txt", " en.txt")
    with open(filename) as f:
        with open(new_filename, "w") as g:
            f_lines = f.readlines()
            # To show a progress bar
            for line in tqdm(f_lines):
                # If a line is not a word
                if not line_is_a_word_entry(line):
                    if not line.isspace():
                        # Printing a all the non-word lines to show progress
                        print(line)
                    g.write(line)
                # If a line is a word
                else:
                    word = line.strip().lower()
                    try:
                        g.write(create_fr_IPA_and_en_meaning(word) + "\n")
                    except Exception as e:
                        print(f"Error encountered for word {word}: {e}")
    print("Done generating " + new_filename + ".")


def get_conj_fr(word):
    r = requests.get(f"https://fr.wiktionary.org/wiki/Conjugaison:français/{word}")
    if not r.ok:
        print(("Cannot find the page for %s. Stopped." % word))
        return word + " MISSING", []
    soup = BeautifulSoup(r.text, SOUP_PARSER)
    groupes = {"premier groupe": 1, "deuxième groupe": 2, "troisième groupe": 3}
    try:
        alt_word = (
            soup.find(text=re.compile("Conjugaison de"))
            .find_next()
            .text.replace("\u2019", "'")
        )
        if word.startswith("se ") or word.startswith("s'"):
            if alt_word == re.sub("^s'", "", re.sub("^se ", "", word)):
                print(("%s changed to %s." % (word, alt_word)))
                word = alt_word
        else:
            if alt_word in ["se " + word, "s'" + word]:
                print(("%s changed to %s." % (word, alt_word)))
                word = alt_word
    except Exception:
        pass
    try:
        groupe = groupes[soup.find(text=re.compile("Verbe du")).find_next().text]
    except Exception as e:
        print(("Error occurred when finding the groupe of %s: %s" % (word, e)))
        groupe = 0

    def process_IPA(x):
        return "[" + x.strip().strip("\\") + "]"

    conj = []
    table = soup.find(
        "span", {"class": "mw-headline", "id": "Modes_impersonnels"}
    ).find_next("table")
    rows = table.find_all("tr")
    headers = [
        (int(header.get("colspan", 1)), header.text.strip())
        for header in rows[0].find_all(["th", "td"])
    ]
    inf_IPA = ["MISSING"]
    if headers != [(1, "Mode"), (3, "Pr\xe9sent"), (3, "Pass\xe9")]:
        print(("Bad header for modes impersonnels for %s: %s" % (word, headers)))
    else:
        try:
            reflexive = word.startswith("se ") or word.startswith("s'")  # se souvenir
            infs = rows[1].find_all(["th", "td"])
            if not (
                infs[0].text.strip() == "Infinitif"
                and (
                    infs[2].text.strip() == word
                    or (
                        reflexive
                        and infs[2].text.strip()
                        == re.sub("^s'", "", re.sub("^se ", "", word))
                    )
                )
            ):
                print(
                    (
                        "Sanity check 1 failed: infs[0]=%s, infs[2]=%s. AssertionError."
                        % (infs[0].text.strip(), infs[2].text.strip())
                    )
                )
                assert False
            inf_IPA = process_IPA(infs[3].text)
            aux_verb = re.sub("^s\u2019", "", infs[4].text.strip())
            if aux_verb not in ["avoir", "être"]:
                print(
                    (
                        "Auxiliary verb %s not in avoir or être. AssertionError."
                        % aux_verb
                    )
                )
                assert False
            past_p = infs[5].text.strip()
            past_p_IPA = process_IPA(infs[6].text)
            conj.append(
                "Passé: Infinitif+"
                + "s'" * reflexive
                + aux_verb
                + " "
                + past_p
                + " ** "
                + past_p_IPA
            )
            pps = rows[3].find_all(["th", "td"])
            if pps[0].text.strip() != "Participe":
                print(("pps[0]=%s!=Participe. AssertionError." % pps[0].text.strip()))
                assert False
            pres_p = pps[2].text.strip()
            pres_p_IPA = process_IPA(pps[3].text)
            conj.append("Participe présent: Participe+" + pres_p + " ** " + pres_p_IPA)
        except Exception as e:
            print(
                (
                    "Error occurred when handling modes impersonnels for %s: %s"
                    % (word, e)
                )
            )

    def is_blank(x):
        return len(x.strip()) == 1 and ord(x.strip()) in range(8208, 8214)

    imp_persons = ["tu", "nous", "vous"]
    for indicatif in [
        "Indicatif",
        "Subjonctif",
        "Conditionnel",
        "Impératif",
        "Impératif_2",
    ]:
        try:
            table = soup.find(
                "span", {"class": "mw-headline", "id": indicatif}
            ).find_next("table")
            contents = [
                x.text.strip()
                for x in table.find_all(["th", "td"])
                if x.text.startswith("\n\n")
            ]
            for content in contents:
                subcontents = content.split("\n\n\n")
                tense = subcontents[0]
                if not tense:  # CHANGE TO SELECT TENSES
                    continue
                forms = []
                for ri, personcontent in enumerate(subcontents[1:]):
                    personcontent = personcontent.replace("\n\n", "\n")
                    personcontents = personcontent.split("\n")
                    IPA_start = [
                        i for i, _ in enumerate(personcontents) if _.startswith("\\")
                    ][0]
                    form = " ".join(
                        [
                            x.strip()
                            .replace("j'", "j' ")
                            .replace("j\u2019", "j\u2019 ")
                            for x in personcontents[0:IPA_start]
                        ]
                    ).strip()  # j'ai -> j' ai
                    # form = re.sub(u"^qu[e\u2019][ ]?", "", form) # que je/qu'il -> je/il
                    form = form.replace("\u2019", "'")
                    if indicatif.startswith("Impératif"):
                        form = imp_persons[ri] + " " + form  # tu sois
                        if indicatif == "Impératif_2":  # souviens-toi
                            form = form.replace(" -", "-")
                    if indicatif == "Subjonctif" and form.startswith("que "):
                        person = " ".join(form.split(" ")[0:2])
                        form = " ".join(form.split(" ")[2:])
                    else:
                        person = form.split(" ")[0]
                        form = " ".join(form.split(" ")[1:])
                    if not is_blank(form):
                        form = person.strip() + "+" + form.strip()
                        IPA = process_IPA(
                            " ".join([x.strip() for x in personcontents[IPA_start:]])
                        )
                        forms.append(form + " ** " + IPA)
                if forms:
                    conj.append(
                        indicatif.replace("_2", "")
                        + " "
                        + tense.replace(" (rare)", "")
                        + ": "
                        + ", ".join(forms)
                    )  # Imperatif_2 -> Imperatif
            if (
                indicatif == "Impératif"
            ):  # If imperatives are in imperatif_2 only then an error would have occurred already
                break
        except Exception as e:
            print(
                ("Error occurred when extracting %s for %s: %s" % (indicatif, word, e))
            )
    return word + " (%s) ** " % groupe + inf_IPA + ": " + "; ".join(conj), conj
