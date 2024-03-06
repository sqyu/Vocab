from Help_funs import quitOrInput, format_text
from typing import List
import Vars


EMPHASIZE_DELIMITER = "*"


class Word:
    """
    class Word:
    The IPA, meanings, number of meanings, and comments
    """

    def __init__(self, s: List[str]):
        assert len(s) == 3 and all(isinstance(ss, str) for ss in s)
        self.IPA = s[0]  # IPA
        # Examples are not new meaning, but sometimes one may mistakenly add %% to it
        meanings = s[1].rstrip("\n").replace("%% [EX]", "[EX]")
        # Meanings are separated by " %% "
        self.meanings = str.split(meanings, " %% ")
        self.numOfMeanings = len(self.meanings)
        self.comments = s[2]


def emphasize_bracketed(
    text: str,
    normal_font: str,
    emphasis_font: str,
    delimiter: str = EMPHASIZE_DELIMITER,
) -> str:
    """
    Emphasizes text surrounded by a delimiter with emphasis_font while leaving
    the rest of the text in normal_font
    """
    chunks = text.strip().split(delimiter)
    formatted = ""
    for i, s in enumerate(chunks):
        if i % 2:
            formatted += format_text(s, emphasis_font)
        else:
            formatted += format_text(s, normal_font)
    return formatted


def emphasize_exact(
    text: str, text_to_emphasize: str, normal_font: str, emphasis_font: str
) -> str:
    """
    Emphasizes text surrounded by a delimiter with emphasis_font while leaving
    the rest of the text in normal_font
    """
    chunks = text.strip().split(text_to_emphasize)
    return format_text(text_to_emphasize, emphasis_font).join(
        format_text(s, normal_font) for s in chunks
    )


def formatExamples(examples: List[str]) -> str:
    """
    examples: A list of examples, each being a phrase, or having the form
        phrase in foreign language || translation in system language
        where in the translation keywords can be surrounded as *KEYWORD*
    """
    ORIGINAL_TEXT_FORMAT = "bold"
    ORIGINAL_EMPHASIS_FORMAT = "bold,bg.green"
    TRANSLATION_FORMAT = "disable,underline"
    TRANSLATION_EMPHASIS_FORMAT = "bold,underline"
    example_prompt = Vars.instructions["exampleUsage"].rstrip("\n")
    text = []
    for example in examples:
        example = example.strip()
        if "||" in example:
            orig, translation = example.split("||")
        else:
            orig, translation = example, ""
        # Example: on *souligne* les *mots clés* avec des astérisques
        orig = emphasize_bracketed(orig, ORIGINAL_TEXT_FORMAT, ORIGINAL_EMPHASIS_FORMAT)
        # Highlight the "~" in the original phrase
        orig = emphasize_exact(orig, "~", ORIGINAL_TEXT_FORMAT, ORIGINAL_EMPHASIS_FORMAT)
        text.append("\t" + example_prompt + format_text(orig, ORIGINAL_TEXT_FORMAT))
        if translation.strip():
            # Example: we *emphasize* the *keywords* with asterisks
            translation = emphasize_bracketed(
                translation, TRANSLATION_FORMAT, TRANSLATION_EMPHASIS_FORMAT
            )
            # To indent the same amount of space as the original phrase
            text.append("\t" + format_text(example_prompt, "invisible") + translation)
    return "\n" + "\n".join(text) + "\n"


def printMeanings(Word_obj):
    for i in range(0, Word_obj.numOfMeanings):
        meaning = Word_obj.meanings[i]
        has_examples = "[EX]" in meaning
        if has_examples:
            meaning, examples = meaning.split("[EX]", 1)
        meaning = emphasize_bracketed(meaning, "", "bold,blink")
        if has_examples:
            meaning += formatExamples(examples.split("[EX]"))
        print(
            Vars.instructions["meaning"]
            .rstrip("\n")
            .replace("REPLACE", "" if Word_obj.numOfMeanings == 1 else f" {i + 1}")
            + meaning
        )


def markWordorNot(s):
    """
    markWordorNot(s):
    Takes a user input and determines whether the user intends to mark the word.

    String s is first changed to upper case, and returns True if s contains exactly all letters
        in "MARK", first three letters are MAR, or s is equal to MAK, M, or MM.
    """
    s = s.upper()
    return (set(s) == set("MARK")) | (s[0:3] == "MAR") | (s in ["MAK", "M", "MM"])


def describeWord(word, Word_obj, learnMode, number=None):
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
    The first number is the index of the current word, and the second one is the total number of
        words in the list.
    """
    # mark = False
    # Print a new line after the previous word
    print()
    if number is not None:
        assert len(number) == 2
        print(
            "{word:{length}}{index}/{total_number_words}".format(
                word=word, length=50, index=number[0], total_number_words=number[1]
            )
        )  # word 30/150 means this word is the 30th in the list
    else:
        print(word)  # Only prints out the word without the numbers
    print(Word_obj.IPA)  # Prints out the IPA
    if learnMode:  # If prints meanings after user inputs something
        s = quitOrInput(None).upper()
        if markWordorNot(s):
            s = "MARK"  # Mark the word
        else:
            s = s.lower()
    printMeanings(Word_obj)
    if Vars.parameters["ShowComments"] == "Y" and Word_obj.comments != "":
        print(Vars.instructions["comments"].rstrip("\n") + Word_obj.comments)
    print("".center(80, "*") + "\n")
    return (
        s if learnMode else ""
    )  # Return an empty string under view mode with no input
