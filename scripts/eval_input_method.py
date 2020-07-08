#!/usr/bin/python3

"""
Given an input method, evaluate the false english rate and false vietnamese rate.

Input method: A string of English letters to replace "`^'-]*}.?[{~", which stands for grave, e-roof, acute, d-dash, o-roof, u-hook, a-roof, underdot, hook, o-hook, a-hook and tilde respectively.
"""

import sys
from mt.base import logger
import pandas as _pd
import mt.pandas.csv as _pc


class Evaluator(object):

    def __init__(self, viwiki_prefix_splitX_csv_file, smart=False):
        self.df = _pc.read_csv(viwiki_prefix_splitX_csv_file)
        self.smart = smart

    def eval(self, input_method):
        '''Evaluates a Vietnamese input method.
        
        Parameters
        ----------
        input_method : str
            the string representing the input method. See the documentation of the module.
        smart : bool
            whether or not the method is smart enough to always choose the option with the higher probability
        
        Returns
        -------
        fer : float
            false english rate
        fvr : float
            false vietnamese rate
        '''
        pass



if __name__ == '__main__':

	if len(sys.argv) != 3:
		logger.info('Usage: python process_wiki_dump.py <wikipedia_dump_file_that_ends_with_articles.xml.bz2> <processed_csv_file>')
		sys.exit(1)
	in_f = sys.argv[1]
	out_f = sys.argv[2]
	make_corpus(in_f, out_f)
