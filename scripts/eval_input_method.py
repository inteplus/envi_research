#!/usr/bin/python3

"""
Given an input method, evaluate the false english rate and false vietnamese rate.

Input method: A string of English letters to replace "`^'-]+}.?[{~", which stands for grave, e-roof, acute, d-dash, o-roof, u-hook, a-roof, underdot, hook, o-hook, a-hook and tilde respectively.
"""

import sys
from random import randrange
from mt.base import logger
import pandas as _pd
import mt.pandas.csv as _pc


vi_code = "`^'-]+}.?[{~"
vi_alphabet = 'bdfjklqrsvwxzaeou'
vi_ch_alphabet = {
    "`": 'bdfjklqrsvwxz',
    "^": 'bdfjklqrsvwxze',
    "'": 'bdfjklqrsvwxz',
    "-": 'bdfjklqrsvwxz',
    "]": 'bdfjklqrsvwxzo',
    "+": 'bdfjklqrsvwxzu',
    "}": 'bdfjklqrsvwxza',
    ".": 'bdfjklqrsvwxz',
    "?": 'bdfjklqrsvwxz',
    "[": 'bdfjklqrsvwxzo',
    "{": 'bdfjklqrsvwxza',
    "~": 'bdfjklqrsvwxz',
}


def valid(input_method):
    '''Checks if an input method is valid.

    Parameters
    ----------
    input_method : str
        the string representing the input method. It is a string of lowercase English letters to replace "`^'-]+}.?[{~", which stands for grave, e-roof, acute, d-dash, o-roof, u-hook, a-roof, underdot, hook, o-hook, a-hook and tilde respectively.

    Returns
    -------
    bool
        whether or not the input method is valid
    '''
    for i, vi_ch in enumerate(input_method):
        if vi_ch not in vi_ch_alphabet[vi_code[i]]:
            #logger.warn("not in alphabet {} {}".format(vi_ch, vi_alphabet))
            return False
    tones = set([input_method[0], input_method[2], input_method[7], input_method[8], input_method[11]])
    if len(tones) < 5:
        #logger.warn("less tones")
        return False
    for i in [1,4,5,6,9,10]:
        if input_method[i] in tones:
            #logger.warn("in tones {} {}".format(input_method[i], tones))
            return False
    if input_method[4] == input_method[9]:
        #logger.warn("match {} {}".format(input_method[4], input_method[9]))
        return False
    if input_method[6] == input_method[10]:
        #logger.warn("match2 {} {}".format(input_method[6], input_method[10]))
        return False
    return True


class Evaluator(object):

    def __init__(self, viwiki_prefix_splitX_csv_file):
        self.df = _pc.read_csv(viwiki_prefix_splitX_csv_file)
        self.df['end'] = self.df['word'].str.slice(start=-1)
        self.dfs = {ch:self.df[self.df['end']==ch] for ch in vi_code}

    def apply_ch(self, vi_ch, en_ch, smart=False):
        df1 = self.dfs[vi_ch]

        word_s = df1['word'] # word prefixes
        vi_s = df1['vi_prob'] # prior probability that a prefix is vi
        en_s = df1[en_ch] # prior probability that a prefix is en

        if smart:
            vi_chosen_s = (vi_s >= en_s).astype(float)
            en_chosen_s = 1.0 - vi_chosen_s
        else:
            en_chosen_s = vi_s*0.0 # always 0
            vi_chosen_s = en_chosen_s + 1.0 # always 1
        return _pd.DataFrame(data={'word': word_s, 'vi_prob': vi_s, 'en_prob': en_s, 'vi_chosen': vi_chosen_s, 'en_chosen': en_chosen_s})

    def apply(self, input_method, smart=False):
        '''Applies a Vietnamese input method to `self.df`.
        
        Parameters
        ----------
        input_method : str
            the string representing the input method. It is a string of lowercase English letters to replace "`^'-]+}.?[{~", which stands for grave, e-roof, acute, d-dash, o-roof, u-hook, a-roof, underdot, hook, o-hook, a-hook and tilde respectively.
        smart : bool
            whether or not the method is smart enough to always choose the option with the higher probability
        
        Returns
        -------
        df : pandas.DataFrame(columns=['word', 'vi_prob', 'en_prob', 'vi_chosen', 'en_chosen'])
            dataframe of the same index as `self.df`. Column 'vi_prob' is the same as `self.df['vi_prob']`. Column 'en_prob' represents the prior probability that the prefix is English, for each input prefix. Column 'vi_chosen' represents which prefix is chosen as 'vi'. Column 'en_chosen' represents which prefix is chosen as 'en'.
        fer : float
            false english rate
        fvr : float
            false vietnamese rate
        '''
        dfs = []
        for i, vi_ch in enumerate(vi_code):
            en_ch = input_method[i]
            df = self.apply_ch(vi_ch, en_ch, smart=smart)
            dfs.append(df)
        df = _pd.concat(dfs, sort=False).sort_index()
        fer = (df['en_chosen']*df['vi_prob']).sum()
        fvr = (df['vi_chosen']*df['en_prob']).sum()
        return df, fer, fvr

    def analyse(self, vi_ch, smart=False):
        for en_ch in vi_ch_alphabet[vi_ch]:
            df = self.apply_ch(vi_ch, en_ch, smart=smart)
            fer = (df['en_chosen']*df['vi_prob']).sum()
            fvr = (df['vi_chosen']*df['en_prob']).sum()
            score = fer+fvr
            logger.info("{}: {}={}+{}".format(en_ch, score, fer, fvr))
            

    def search(self, initial_input_method, smart=False):
        '''Searches for the locally best input method.'''

        best_input_method = initial_input_method
        best_df, best_fer, best_fvr = self.apply(best_input_method, smart=smart)
        best_score = best_fer + best_fvr
        logger.info("Initial score {}={}+{} from {}".format(best_score, best_fer, best_fvr, best_input_method))
        
        while True:
            better = False
            for i in range(len(vi_code)):
                for ch in vi_alphabet:
                    input_method = best_input_method[:i] + ch + best_input_method[i+1:]
                    if not valid(input_method):
                        continue
                    df, fer, fvr = self.apply(input_method, smart=smart)
                    score = fer + fvr
                    if score < best_score:
                        best_df = df
                        best_fer = fer
                        best_fvr = fvr
                        best_score = score
                        best_input_method = input_method
                        logger.info("Better score {}={}+{} from {}".format(best_score, best_fer, best_fvr, best_input_method))
                        better = True
            if not better:
                break

        logger.info("Best input method: {}".format(best_input_method))
        return best_input_method, best_df, best_fer, best_fvr, best_score

    def search_all(self, attempt_count=100, smart=False):
        best_score = 100.0
        for i in range(attempt_count):
            input_method = ''
            for vi_ch in vi_code:
                s = vi_ch_alphabet[vi_ch]
                input_method += s[randrange(len(s))]
            input_method, df, fer, fvr, score = self.search(input_method, smart=smart)
            if score < best_score:
                best_df = df
                best_fer = fer
                best_fvr = fvr
                best_score = score
                best_input_method = input_method
            logger.info("------ Current best score {}={}+{} from {} -----".format(best_score, best_fer, best_fvr, best_input_method))
        return best_input_method, best_df, best_fer, best_fvr, best_score


if __name__ == '__main__':

    if len(sys.argv) != 3:
	logger.info('Usage: python process_wiki_dump.py <wikipedia_dump_file_that_ends_with_articles.xml.bz2> <processed_csv_file>')
	sys.exit(1)
    in_f = sys.argv[1]
    out_f = sys.argv[2]
    make_corpus(in_f, out_f)

    # currently, the best input method is "qzxdzuzjfkaw" with fer = 0.0009225985366192045 and fvr = 0.002716891565571517
    pass

