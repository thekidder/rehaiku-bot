# Flesch-Kincaid Grade level analysis of text.
import nltk

import text_utils


def grade_level(text):
    sentences = nltk.tokenize.sent_tokenize(text)
    totalwords = 0
    totalsyllables = 0
    totalsentences = len(sentences)
    for sentence in sentences:
        words = nltk.tokenize.word_tokenize(sentence)
        words = [text_utils.reduce(word) for word in words]
        words = [word for word in words if word != '']
        totalwords += len(words)
        syllables = [text_utils.syllable_count(word) for word in words]
        totalsyllables += sum(syllables)
        totalwords = float(totalwords)

        if totalwords <= 1 or totalsentences == 0:
            return 0.0

        return ( # Flesh-Kincaid Grade Level formula. Thanks, Wikipedia!
            0.39 * (totalwords / totalsentences)
            + 11.8 * (totalsyllables / totalwords)
            - 15.59 )
