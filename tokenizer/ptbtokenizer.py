#!/usr/bin/env python
# 
# File Name : ptbtokenizer.py
#
# Description : Do the PTB Tokenization and remove punctuations.
#
# Creation Date : 29-12-2014
# Last Modified : Thu Mar 19 09:53:35 2015
# Authors : Hao Fang <hfang@uw.edu> and Tsung-Yi Lin <tl483@cornell.edu>

import logging
import os
import subprocess
import tempfile

# path to the stanford corenlp jar
STANFORD_CORENLP_3_4_1_JAR = 'stanford-corenlp-3.4.1.jar'

# punctuations to be removed from the sentences
PUNCTUATIONS = ["''", "'", "``", "`", "-LRB-", "-RRB-", "-LCB-", "-RCB-", \
        ".", "?", "!", ",", ":", "-", "--", "...", ";"] 

_logger = logging.getLogger('answerability')

class PTBTokenizer:
    """Python wrapper of Stanford PTBTokenizer"""

    def tokenize(self, captions_for_image):
        cmd = ['java', '-cp', STANFORD_CORENLP_3_4_1_JAR,
                'edu.stanford.nlp.process.PTBTokenizer',
                '-preserveLines', '-lowerCase']

        # ======================================================
        # prepare data for PTB Tokenizer
        # ======================================================
        final_tokenized_captions_for_image = {}
        image_id = [k for k, v in captions_for_image.items() for _ in range(len(v))]
        sentences = '\n'.join([c['caption'].replace('\n', ' ') for k, v in captions_for_image.items() for c in v])

        # ======================================================
        # save sentences to temporary file
        # ======================================================
        path_to_jar_dirname=os.path.dirname(os.path.abspath(__file__))
        tmp_file = tempfile.NamedTemporaryFile(delete=False, dir=path_to_jar_dirname)
        tmp_file.write(sentences.encode('utf-8'))
        tmp_file.close()

        # ======================================================
        # tokenize sentence
        # ======================================================
        cmd.append(os.path.basename(tmp_file.name))

        env = os.environ.copy()
        env['LC_ALL'] = "C"
        p_tokenizer = subprocess.Popen(cmd, cwd=path_to_jar_dirname,
                                       env=env,
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        token_lines, err = p_tokenizer.communicate(input=sentences.rstrip().encode('utf-8'))
        if err and _logger.isEnabledFor(logging.DEBUG):
            _logger.debug(err.decode('utf-8').rstrip())
        lines = token_lines.decode('utf-8').split('\n')
        # remove temp file
        os.remove(tmp_file.name)

        # ======================================================
        # create dictionary for tokenized captions
        # ======================================================
        for k, line in zip(image_id, lines):
            if not k in final_tokenized_captions_for_image:
                final_tokenized_captions_for_image[k] = []
            tokenized_caption = ' '.join([w for w in line.rstrip().split(' ') \
                    if w not in PUNCTUATIONS])
            final_tokenized_captions_for_image[k].append(tokenized_caption)

        return final_tokenized_captions_for_image
