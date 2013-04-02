import re

import nltk
from nltk.corpus import cmudict

import fleschkincaid
import queries


cmu = cmudict.dict()

def reduce(word):
    return ''.join([x for x in word.lower() if re.match(r'\w', x)])


def syllable_count(word):
    reduced = reduce(word)
    if (not len(reduced)) or (not reduced in cmu):
        return 0
    return len([x for x in list(''.join(list(cmu[reduced])[-1])) if re.match(r'\d', x)])


def sentences(executor, nick):
    all_sentences = list()
    for row in queries.get_lines_by_nick(executor, nick):
        text = row[0]
        all_sentences.extend(nltk.tokenize.sent_tokenize(text))

    return all_sentences


def distinct_sentences(executor, nick):
    all_sentences = list()
    for row in queries.get_distinct_lines_by_nick(executor, nick):
        text = row[0]
        all_sentences.extend(nltk.tokenize.sent_tokenize(text))

    return all_sentences
