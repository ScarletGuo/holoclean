import torch
import re
import gensim
import pandas as pd
import numpy as np
from gensim.models.word2vec import LineSentence
from gensim.models import FastText
from gensim.test.utils import temporary_file

from dataset import AuxTables
from .featurizer import Featurizer
import logging

def normalize(s):
    """
    Given a cell val, cleans and normalizes it. 
    """
    s = str(s)
    # replace whitespace
    s = s.strip().replace(" ", "_")
    return s

class EmbeddingFeaturizer(Featurizer):
    def specific_setup(self):
        self.name = 'EmbeddingFeaturizer'
        self.emb_size = 10
        self.attrs_number = len(self.ds.attr_to_idx)
        self.attr_language_model = {}
        self.raw_data = self.ds.get_raw_data()
        self.model = FastText(iter=10, size=self.emb_size,)
        # train model using per row as a sentence
        with temporary_file("temp.txt") as tf, open(tf, 'w') as outfile:
            for row in self.raw_data.itertuples():
                line = " ".join(map(normalize,row))
                outfile.write(line + '\n')
            corpus = LineSentence(tf)
            self.model.build_vocab(corpus)
            self.model.train(corpus, size=self.emb_size, total_examples=self.model.corpus_count, 
                        epochs=self.model.epochs,window=self.raw_data.shape[1], min_count=1)
            
    def get_vec(self, word):
        try:
            vec = self.model[normalize(word)]
        except:
            logging.warning("{} is out-of-voc".format(word))
            return np.zeros((self.emb_size,))
        return vec

    def gen_feat_tensor(self, input, classes):
        vid = int(input[0])
        attribute = input[1]
        domain = input[2].split('|||')
        tid = input[3]
        attr_idx = self.ds.attr_to_idx[attribute]
        tensor = torch.zeros(1, classes, self.attrs_number*self.emb_size)
        row = self.raw_data.loc[tid]
        attributes = self.ds.get_attributes()
        # write other attr embedding to all domains: 
        for i, other_attr in enumerate(row.index.values):
            if other_attr in self.ds.raw_data.exclude_attr_cols:
                continue
            other_attr_idx = self.ds.attr_to_idx[other_attr]
            start = other_attr_idx*self.emb_size
            end = start+self.emb_size
            if other_attr_idx == attr_idx:
                # val different across domains
                for idx, val in enumerate(domain):
                    emb_val = self.get_vec(val)
                    tensor[0][idx][start:end] = torch.tensor(emb_val)
            else:
                # val same across domains
                emb_val = self.get_vec(row[other_attr])
                for idx in range(len(domain)):
                    tensor[0][idx][start:end] = torch.tensor(emb_val)
        return tensor

    def create_tensor(self):
        query = 'SELECT _vid_, attribute, domain, _tid_ FROM %s ORDER BY _vid_' % AuxTables.cell_domain.name
        results = self.ds.engine.execute_query(query)
        tensors = [self.gen_feat_tensor(res, self.classes) for res in results]
        combined = torch.cat(tensors)
        return combined
