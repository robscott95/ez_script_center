import spacy
import nltk
import re

from spacy.tokenizer import Tokenizer

# Important in final version of script
# for now, in google collaboratory, the english pact is downloaded.
# Ask Adrian how this error should be handled.
try:
    spacy.load("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise OSError("Please make sure that you've ran `python -m spacy download en_core_web_sm` via the console")

####################
# HELPER FUNCTIONS #
####################


def clean_input_data(input_str, lemmatize=False):
    """Helper function for cleaning the main text column
    (default: first one).

    Deletes stop characters. And in the event of numbers or
    Dynamic Keyword Insertations - removes spaces between the words
    inside of curly braces or spaces between digits.

    Supports lemmatization.

    Args:
        - input_str (DataFrame): The DF in which the first column
            contains the text that will be tokenized.
        - lemmatize (bool, optional): If set to True the cleaned data
            will also be very conservatively lemmatized, trying to
            normalize only words that are more or less sure with
            omitting word that have special characters in them.
            Defaults to False.

    Returns:
        - str: Cleaned and lemmatized string.

    Notes:
        - Current version of Spacy (v2.1.4) is known to have some issues
            with lemmatization
            see (https://github.com/explosion/spaCy/issues/3665).
            So please keep in mind it's more of "experimental" although
            still quite useful.
    """

    def delete_spaces_in_substrings(s, pat=r"{.*?}|\d[\d ]*\d"):
        """Helper inner function for removing spaces in a substring of
        a given string. Substrings are determined by the pat argument,
        which is a regex pattern.

        The default pattern removes spaces between the {} and in-between
        numbers.

        Examples:
            >>> from ngram_analysis import delete_spaces_in_substrings
            >>> test = "test stuff {=venueprice venue} and 1 800 800"
            >>> delete_spaces_in_substrings(test)
            "test stuff {=venuepricevenue} and 1800800"
        """
        matches = re.findall(pat, s)

        if matches:
            for match in matches:
                match_replacement = re.sub(r"\s+", "", match)
                s = re.sub(match, match_replacement, s)

        return s

    # -----------------------
    # Parent's Function Logic
    # -----------------------

    # Leave out curly braces and | sign which denotes DKI and the end of
    # the headline/description in AdWords.
    # We just want to remove the most popular punctuation to remove
    # redundant duplicate ngrams while also want to have an insight
    # into how less common characters influence the performance.
    stop_characters = '.,:;?!()"'

    cleaned_str = input_str.lower()
    cleaned_str = re.sub(f"[{stop_characters}]", " ", cleaned_str)
    cleaned_str = delete_spaces_in_substrings(cleaned_str)
    cleaned_str = re.sub(r"\s+", " ", cleaned_str)

    if lemmatize:
        # We don't want to seperate anything that wasn't specified
        # in stop_characters
        supress_re = re.compile(r"""[\.]""")
        nlp.tokenizer = Tokenizer(
            nlp.vocab,
            infix_finditer=supress_re.finditer,
            suffix_search=supress_re.search,
            prefix_search=supress_re.search,
        )

        # Weird bug present in current v2.1.4 of Spacy fix
        nlp.tokenizer.add_special_case(
            "who's", [{spacy.attrs.ORTH: "who's", spacy.attrs.LEMMA: "who's"}]
        )

        cleaned_str = " ".join(
            [word.lemma_ if word.lemma_ != "-PRON-" else word.lower_
             for word in nlp(cleaned_str)]
        )

    return cleaned_str


def create_ngrams(cleaned_str, start=1, end=4):
    """Helper function for creating n-grams.
    n is range between start and end (inclusive).

    Examples:
        >>> cleaned_text = "jack and jill"
        >>> from ngram_analysis import create_ngrams

        df["1-gram"]: {"jack", "and", "jill"}
        df["2-gram"]: {"jack and", "and jill"}
        df["3-gram"]: {"jack and jill"}
        df["4-gram"]: set()
    """

    ngram_dict = {}

    for n in range(start, end + 1):
        n_gram = f"{n}-gram"

        # set(nltk.ngrams(...)) returns a tuple of ngrams, that's why
        # we join them.
        # The second set might be redundant -test it.
        ngram_dict[n_gram] = set(" ".join(gram) for gram in
                                 nltk.ngrams(cleaned_str.split(), n))

        # Transform it back to a list because you "set" object isn't
        # serializable, thus, not able to make it to json.
        ngram_dict[n_gram] = list(ngram_dict[n_gram])

    return ngram_dict


#################
# MAIN FUNCTION #
#################

def tokenize_string_to_ngrams(input_str, lemmatize=True, start=1, end=4):
    """Function that takes in an input string and return a key-value
    pair.
    The key is the type of gram returned and the value is a list of
    those grams.

    Args:
        - input_str (str): The string we want to tokenize into ngrams.
        - lemmatize (bool, optional): Do you want to lemmatize?
            In some cases it might be buggy, as the Spacy module has
            multiple issues raised (albeit quite small).
            Defaults to True.
        - start (int, optional): From how big n-grams we should start?
            Defaults to 1.
        - end (int, optional): To how big of n-grams we should make?
            Defaults to 4.

    Returns:
        - json: The dictionary in json form that contains key-value
            info. The key is the type of gram returned and the value
            is a list of those grams.

    Examples:
        >>> text = "Jack, and jill!"
        >>> tokenize_string_to_ngrams(text)

        {
            "1-gram": ["and", "jack", "jill"],
            "2-gram": ["jack and", "and jill"],
            "3-gram": ["jack and jill"],
            "4-gram": []
        }

    Notes:
        - Emojis are returned in an UTF-16 encoding on my machine.
    """

    cleaned_str = clean_input_data(input_str, lemmatize=lemmatize)
    ngram_dict = create_ngrams(cleaned_str, start=1, end=4)

    return ngram_dict


if __name__ == "__main__":
    #print(tokenize_string_to_ngrams("lost your card card card is lost"))
    pass
