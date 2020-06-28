#!/usr/bin/python3

"""
Expands a viwiki-prefix-split{1,L} corpus.
"""

import sys
from mt.base import logger
import pandas as pd
import mt.pandas.csv as pc
from trie import Trie

def make_corpus(in_f, trie_f, out_f):
    logger.info("Loading the enwiki trie '{}'...".format(trie_f))
    trie = Trie.from_file(trie_f)

    logger.info("Loading the viwiki split csv '{}'...".format(in_f))
    df = pc.read_csv(in_f)
    df.columns = ['word', 'count', 'vi_prob']

    alphabet = 'bdfklqrsvwzadeou'
    s = df['word'].str.slice(stop=-1)
    for ch in alphabet:
        logger.info(ch)
        df[ch] = s.apply(lambda x: trie.prob(x+ch))
    
    pc.to_csv(df, out_f, index=False)


if __name__ == '__main__':

    if len(sys.argv) != 4:
        logger.info('Usage: python expand_split_corpus.py <viwiki_prefix_splitX-....csv> <enwiki_restricted_....trie> <viwiki_prefix_splitX_expanded....csv>')
        sys.exit(1)
    in_f = sys.argv[1]
    trie_f = sys.argv[2]
    out_f = sys.argv[3]
    make_corpus(in_f, trie_f, out_f)
