#!/usr/bin/python3

"""
Given an input method, evaluate the false english rate and false vietnamese rate.

Input method: A string of English letters to replace "`^'-]*}.?[{~", which stands for grave, e-roof, acute, d-dash, o-roof, u-hook, a-roof, underdot, hook, o-hook, a-hook and tilde respectively.
"""

import sys
from mt.base import logger
import pandas as _pd
import mt.pandas.csv as _pc


vi_code = "`^'-]*}.?[{~"


class Evaluator(object):

    def __init__(self, viwiki_prefix_splitX_csv_file):
        self.df = _pc.read_csv(viwiki_prefix_splitX_csv_file)
        self.df['end'] = self.df['word'].str.slice(start=-1)
        self.dfs = {ch:self.df[self.df['end']==ch] for ch in vi_code}

    def apply(self, input_method, smart=False):
        '''Applies a Vietnamese input method to `self.df`.
        
        Parameters
        ----------
        input_method : str
            the string representing the input method. It is a string of lowercase English letters to replace "`^'-]*}.?[{~", which stands for grave, e-roof, acute, d-dash, o-roof, u-hook, a-roof, underdot, hook, o-hook, a-hook and tilde respectively.
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
            df = _pd.DataFrame(data={'word': word_s, 'vi_prob': vi_s, 'en_prob': en_s, 'vi_chosen': vi_chosen_s, 'en_chosen': en_chosen_s})
            dfs.append(df)
        df = _pd.concat(dfs, sort=False).sort_index()
        fer = (df['en_chosen']*df['vi_prob']).sum()
        fvr = (df['vi_chosen']*df['en_prob']).sum()
        return df, fer, fvr


if __name__ == '__main__':

	if len(sys.argv) != 3:
		logger.info('Usage: python process_wiki_dump.py <wikipedia_dump_file_that_ends_with_articles.xml.bz2> <processed_csv_file>')
		sys.exit(1)
	in_f = sys.argv[1]
	out_f = sys.argv[2]
	make_corpus(in_f, out_f)
