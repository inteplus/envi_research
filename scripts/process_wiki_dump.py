#!/usr/bin/python3

"""
Creates a word count dictionary from Wikipedia dump file.
Inspired by:
https://github.com/panyang/Wikipedia_Word2vec/blob/master/v1/process_wiki.py
"""

import sys
from mt.base import logger
import pandas as pd
import mt.pandas.csv as pc
from collections import Counter
from gensim.corpora import WikiCorpus

def make_corpus(in_f, out_f):

	"""Convert Wikipedia xml dump file to text corpus"""

	logger.info("Opening the Wikipedia dump '{}'...".format(in_f))
	wiki = WikiCorpus(in_f, token_min_len=1)

	i = 0
	w = 0
	counter = Counter()
	for text in wiki.get_texts():
		if (i % 10000 == 0):
			logger.info('Processed {} articles with {} words'.format(i,w))
		w += len(text)
		counter.update(text)
		i = i + 1
	logger.info('Processing {} articles with {} words complete!'.format(i,w))

	df = pd.DataFrame.from_dict(counter, orient='index').reset_index()
	df = df.rename(columns={'index':'word', 0:'count'})
	df.sort_values('count', axis=0, ascending=False, inplace=True)
	pc.to_csv(df, out_f, index=False)

if __name__ == '__main__':

	if len(sys.argv) != 3:
		logger.info('Usage: python process_wiki_dump.py <wikipedia_dump_file_that_ends_with_articles.xml.bz2> <processed_csv_file>')
		sys.exit(1)
	in_f = sys.argv[1]
	out_f = sys.argv[2]
	make_corpus(in_f, out_f)
