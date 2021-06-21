# encoding: cp850
# -*- coding: utf-8 -*-

from pymystem3 import Mystem
from preprocessing.stopwords import get_stopwords_by_language
from syntactic_unit import SyntacticUnit
import re  # http://regex101.com/#python to test regex
import logging
import string
import unicodedata

import snowballstemmer

logger = logging.getLogger('preprocessing.cleaner')

SEPARATOR = r"@"
RE_SENTENCE = re.compile('(\S.+?[.!?])(?=\s+|$)|(\S.+?)(?=[\n]|$)')  # backup (\S.+?[.!?])(?=\s+|$)|(\S.+?)(?=[\n]|$)
AB_SENIOR = re.compile("([A-Z][a-z]{1,2}\.)\s(\w)")
AB_ACRONYM = re.compile("(\.[a-zA-Z]\.)\s(\w)")
AB_ACRONYM_LETTERS = re.compile("([a-zA-Z])\.([a-zA-Z])\.")
UNDO_AB_SENIOR = re.compile("([A-Z][a-z]{1,2}\.)" + SEPARATOR + "(\w)")
UNDO_AB_ACRONYM = re.compile("(\.[a-zA-Z]\.)" + SEPARATOR + "(\w)")
STEMMER = None
STOPWORDS = None
mystem = Mystem()


def set_stemmer_language():
    global STEMMER
    STEMMER = snowballstemmer.stemmer("russian")


def set_stopwords_by_language():
    global STOPWORDS
    words = get_stopwords_by_language("russian")
    STOPWORDS = frozenset(to_unicode(w) for w in words.split() if w)


def init_textcleanner():
    set_stemmer_language()
    set_stopwords_by_language()


def split_sentences(text):
    processed = replace_abbreviations(text)
    return [undo_replacement(sentence) for sentence in get_sentences(processed)]


def replace_abbreviations(text):
    return replace_with_separator(text, SEPARATOR, [AB_SENIOR, AB_ACRONYM])


def undo_replacement(sentence):
    return replace_with_separator(sentence, r" ", [UNDO_AB_SENIOR, UNDO_AB_ACRONYM])


def replace_with_separator(text, separator, regexs):
    replacement = r"\1" + separator + r"\2"
    result = text
    for regex in regexs:
        result = regex.sub(replacement, result)
    return result


def get_sentences(text):
    for match in RE_SENTENCE.finditer(text):
        yield match.group()


# Taken from gensim
def to_unicode(text, encoding='utf-8', errors='strict'):
    """Convert a string (bytestring in `encoding` or unicode), to unicode."""
    if isinstance(text, str):
        return text
    return str(text, encoding=encoding, errors=errors)


# Taken from gensim
RE_PUNCT = re.compile('([%s])+' % re.escape(string.punctuation), re.UNICODE)


def strip_punctuation(s):
    s = to_unicode(s)
    return RE_PUNCT.sub(" ", s)


# Taken from gensim
RE_NUMERIC = re.compile(r"[0-9]+", re.UNICODE)


def strip_numeric(s):
    s = to_unicode(s)
    return RE_NUMERIC.sub("", s)


def remove_stopwords(sentence):
    return " ".join(w for w in sentence.split() if w not in STOPWORDS)


def stem_sentence(sentence):
    word_stems = STEMMER.stemWords(sentence.split())
    return " ".join(word_stems)


def apply_filters(sentence, filters):
    for f in filters:
        sentence = f(sentence)
    return sentence


def filter_words(sentences):
    filters = [lambda x: x.lower(), strip_numeric, strip_punctuation, remove_stopwords,
               stem_sentence]
    return map(lambda token: apply_filters(token, filters), sentences)


# Taken from gensim
def deaccent(text):
    """
    Remove accentuation from the given string. Input text is either a unicode string or utf8
    encoded bytestring.
    """
    if not isinstance(text, str):
        # assume utf8 for byte strings, use default (strict) error handling
        text = text.decode('utf-8')
    norm = unicodedata.normalize("NFD", text)
    result = to_unicode('').join(ch for ch in norm if unicodedata.category(ch) != 'Mn')
    return unicodedata.normalize("NFC", result)


# Taken from gensim
PAT_ALPHABETIC = re.compile('(((?![\d])\w)+)', re.UNICODE)


def tokenize(text, lowercase=False, deacc=False, errors="strict", to_lower=False, lower=False):
    """
    Iteratively yield tokens as unicode strings, optionally also lowercasing them
    and removing accent marks.
    """
    lowercase = lowercase or to_lower or lower
    text = to_unicode(text, errors=errors)
    if lowercase:
        text = text.lower()
    if deacc:
        text = deaccent(text)
    for match in PAT_ALPHABETIC.finditer(text):
        yield match.group()


def merge_syntactic_units(original_units, filtered_units, tags=None):
    units = []
    filtered_units = list(filtered_units)
    for i in range(len(original_units)):
        if filtered_units[i] == '':
            continue

        text = original_units[i]
        token = filtered_units[i]
        tag = tags[i][1] if tags else None
        sentence = SyntacticUnit(text, token, tag)
        sentence.index = i

        units.append(sentence)

    return units


def clean_text_by_sentences(text):
    """ Tokenizes a given text into sentences, applying filters and lemmatizing them.
    Returns a SyntacticUnit list. """
    init_textcleanner()
    original_sentences = split_sentences(text)
    filtered_sentences = filter_words(original_sentences)

    return merge_syntactic_units(original_sentences, filtered_sentences)


def clean_text_by_word(text):
    """ Tokenizes a given text into words, applying filters and lemmatizing them.
    Returns a dict of word -> syntacticUnit. """
    init_textcleanner()
    text_without_acronyms = replace_with_separator(text, "", [AB_ACRONYM_LETTERS])
    original_words = list(tokenize(text_without_acronyms, to_lower=True, deacc=True))
    filtered_words = filter_words(original_words)
    tags = russian_tag(original_words)
    units = merge_syntactic_units(original_words, filtered_words, tags)
    return {unit.text: unit for unit in units}


def tokenize_by_word(text):
    text_without_acronyms = replace_with_separator(text, "", [AB_ACRONYM_LETTERS])
    return tokenize(text_without_acronyms, to_lower=True, deacc=True)


def russian_tag(words):
    tags = []
    for word in words:
        analyze = mystem.analyze(word)
        tag = u''
        if analyze[0] and analyze[0].get("analysis"):
            tag = analyze[0].get("analysis")[0].get("gr").replace('=', ',').split(',')[0]
            if tag in ['S', 'COM']:
                tag = u'NN'
            if tag == 'A':
                tag = u'JJ'
        tags.append((word, tag))
    return tags
