import re
import pandas as pd
import re
import ast
from gensim import models, corpora
import nltk
from fastnumbers import isfloat
from nltk import word_tokenize
from nltk.corpus import stopwords
from gensim.corpora import MmCorpus
from gensim.models.ldamodel import LdaModel
from nltk import bigrams
from nltk import trigrams
from nltk.stem import WordNetLemmatizer
from gensim.corpora import Dictionary
import numpy as np
from nltk.corpus import wordnet
from nltk import ngrams
import more_itertools
import gc

import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('omw')

NUM = "_NUM_"
UNIT_OF_LENGTH = "_UNIT_OF_LENGTH_"
UNIT_OF_VOLUME = "_UNIT_OF_VOLUME_"
UNIT_OF_TIME = "_UNIT_OF_TIME_"
UNIT_OF_MASS = "_UNIT_OF_MASS_"
UNIT_OF_ELECTRICITY = "_UNIT_OF_ELECTRICITY_"

stopwords_list = stopwords.words('english')
stopwords_list.extend(["ul","li","br","hr","h1","h2","h3","h4","h5","h6"])
stopwords_list = set(stopwords_list)

def get_number_base_words():
    numbers = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
               "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty",
               "twenty-one", "twenty-two", "twenty-three", "twenty-four", "twenty-five", "twenty-six", "twenty-seven",
               "twenty-eight", "twenty-nine", "thirty", "thirty-one", "thirty-two", "thirty-three", "thirty-four",
               "thirty-five", "thirty-six", "thirty-seven", "thirty-eight", "thirty-nine", "forty", "forty-one",
               "forty-two", "forty-three", "forty-four", "forty-five", "forty-six", "forty-seven", "forty-eight",
               "forty-nine", "fifty", "fifty-one", "fifty-two", "fifty-three", "fifty-four", "fifty-five", "fifty-six",
               "fifty-seven", "fifty-eight", "fifty-nine", "sixty", "sixty-one", "sixty-two", "sixty-three",
               "sixty-four", "sixty-five", "sixty-six", "sixty-seven", "sixty-eight", "sixty-nine", "seventy",
               "seventy-one", "seventy-two", "seventy-three", "seventy-four", "seventy-five", "seventy-six",
               "seventy-seven", "seventy-eight", "seventy-nine", "eighty", "eighty-one", "eighty-two", "eighty-three",
               "eighty-four", "eighty-five", "eighty-six", "eighty-seven", "eighty-eight", "eighty-nine", "ninety",
               "ninety-one", "ninety-two", "ninety-three", "ninety-four", "ninety-five", "ninety-six", "ninety-seven",
               "ninety-eight", "ninety-nine", ]

    nums = list(range(0, 100))
    n2 = [l.replace("-", "") for l in numbers]
    n3 = [l.replace("-", " ") for l in numbers]
    scales = ["hundred", "thousand", "lakh", "million", "crore", "billion", "trillion"]
    scale_nums = [1e2, 1e3, 1e5, 1e6, 1e7, 1e9, 1e12]

    d1 = {tupl[0]: tupl[1] for tupl in zip(numbers, nums)}
    d2 = {tupl[0]: tupl[1] for tupl in zip(n2, nums)}
    d3 = {tupl[0]: tupl[1] for tupl in zip(n3, nums)}
    d4 = {tupl[0]: int(tupl[1]) for tupl in zip(scales, scale_nums)}
    nw = merge_dicts(d1,d2,d3,d4)
    return nw


def get_number_words():
    numbers = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven",
               "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty",
               "twenty-one", "twenty-two", "twenty-three", "twenty-four", "twenty-five", "twenty-six", "twenty-seven",
               "twenty-eight", "twenty-nine", "thirty", "thirty-one", "thirty-two", "thirty-three", "thirty-four",
               "thirty-five", "thirty-six", "thirty-seven", "thirty-eight", "thirty-nine", "forty", "forty-one",
               "forty-two", "forty-three", "forty-four", "forty-five", "forty-six", "forty-seven", "forty-eight",
               "forty-nine", "fifty", "fifty-one", "fifty-two", "fifty-three", "fifty-four", "fifty-five", "fifty-six",
               "fifty-seven", "fifty-eight", "fifty-nine", "sixty", "sixty-one", "sixty-two", "sixty-three",
               "sixty-four", "sixty-five", "sixty-six", "sixty-seven", "sixty-eight", "sixty-nine", "seventy",
               "seventy-one", "seventy-two", "seventy-three", "seventy-four", "seventy-five", "seventy-six",
               "seventy-seven", "seventy-eight", "seventy-nine", "eighty", "eighty-one", "eighty-two", "eighty-three",
               "eighty-four", "eighty-five", "eighty-six", "eighty-seven", "eighty-eight", "eighty-nine", "ninety",
               "ninety-one", "ninety-two", "ninety-three", "ninety-four", "ninety-five", "ninety-six", "ninety-seven",
               "ninety-eight", "ninety-nine", ]
    nums = list(range(0, 100))
    n2 = [l.replace("-", "") for l in numbers]
    n3 = [l.replace("-", " ") for l in numbers]
    scales = ["hundred", "thousand", "lakh", "million", "crore", "billion", "trillion"]
    scale_nums = [1e2, 1e3, 1e5, 1e6, 1e7, 1e9, 1e12]
    nw = {}
    for i in range(len(scales)):
        for j in range(len(numbers)):
            number = numbers[j]
            scale = scales[i]
            num = nums[j]
            scs = scale_nums[i]
            value = int(num * scs)
            nw[number + " " + scale] = value
            nw[number + "-" + scale] = value
            nw[number + "" + scale] = value

            nw[n2[j] + " " + scale] = value
            nw[n2[j] + "-" + scale] = value
            nw[n2[j] + "" + scale] = value

            nw[n3[j] + " " + scale] = value
            nw[n3[j] + "-" + scale] = value
            nw[n3[j] + "" + scale] = value

    d1 = {tupl[0]: tupl[1] for tupl in zip(numbers, nums)}
    d2 = {tupl[0]: tupl[1] for tupl in zip(n2, nums)}
    d3 = {tupl[0]: tupl[1] for tupl in zip(n3, nums)}
    nw = merge_dicts(nw,d1,d2,d3)
    return nw


def remove_html_tags(text):
    """Remove html tags from a string"""
    if type(text) is pd.core.series.Series or type(text) is str:
        text = text.replace("'", " ").replace('"', " ")
        clean = re.compile('<.*?>')
        return re.sub(clean, ' ', text)
    return text


def clean_text(text):
    EMPTY = ''
    text = text.replace("\n", " ").replace("(", " ").replace(")", " ").replace("\r", " ").replace("\t", " ").lower()
    text = re.sub('<pre><code>.*?</code></pre>', EMPTY, text)
    text = re.sub('<code>.*?</code>', EMPTY, text)

    def replace_link(match):
        EMPTY = ''
        return EMPTY if re.match('[a-z]+://', match.group(1)) else match.group(1)

    text = re.sub('<a[^>]+>(.*)</a>', replace_link, text)
    return text


def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    elif treebank_tag.startswith('S'):
        return 's'
    else:
        return wordnet.NOUN


def is_stopword(word):
    return word in stopwords_list



def translate(text, kw, ignore_case=False):
    """Translate by changing keys mentioned in kw to values in passed text"""
    search_keys = sorted(map(lambda x: re.escape(x), kw.keys()), key = len,reverse=True)
    if ignore_case:
        kw = {k.lower(): kw[k] for k in kw}
        regex = re.compile('|'.join(search_keys), re.IGNORECASE)
        res = regex.sub(lambda m: kw[m.group().lower()], text)
    else:
        regex = re.compile('|'.join(search_keys))
        res = regex.sub(lambda m: kw[m.group()], text)

    return res


def __replace(match):
    return " _NUM"+str(int(np.clip(np.log2(float(match.group())+1),-10,30)))+"_ "




def replace_numbers(text):
    if text is None or type(text) is not str:
        return text
    base_words = get_number_base_words()
    text = re.sub(r"[0-9]+\.[0-9]+|[0-9]+", __replace, text)
    text = translate(text, {" "+k+" ": " _NUM"+str(int(np.log2(v+1)))+"_ " for k, v in base_words.items()})
    return text


def __get_translator_from_representation(representations, unit):
    l2 = [l.replace("-", "") for l in representations]
    l3 = [l.replace("-", " ") for l in representations]
    representations.extend(l2)
    representations.extend(l3)
    representations = set(representations)
    representations = list(
        more_itertools.flatten([[NUM + l + " ", NUM + " " + l + " ", NUM + "-" + l + " "] for l in representations]))
    translator = {k: NUM + " " + unit + " " for k in representations}
    return translator


def get_measurement_translators():
    length_representations = ["m", "cm", "mm", "km", "meter", "metre", "centi-meter", "milli-meter", "centi-metre",
                              "milli-metre","mili-meter","mili-metre","mili-meters","mili-metres"
                              "kilo-meter", "kilo-metre", "meters", "metres", "centi-meters", "milli-meters",
                              "centi-metres", "milli-metres","mtr",
                              "kilo-meters", "kilo-metres", "mile", "miles","inch","inches","in","cms","foot","feet","ft"]
    length_translator = __get_translator_from_representation(length_representations, UNIT_OF_LENGTH)
    volume_representations = ["ml", "l","lt","ltrs","ltr", "liter", "litre", "liters", "litres", "meter-cube", "m3", "cm3", "metre-cube",
                              "cubic-meter", "cubic-metre","lit","mili-liters","mili-liter","milli-litres","milli-liters",
                              "milli-litre", "milli-liter","barrel","barrels","cc"]
    volume_translator = __get_translator_from_representation(volume_representations, UNIT_OF_VOLUME)
    time_representations = ["s", "secs", "second", "seconds", "min", "minute", "minutes", "hour", "hours", "hr", "hrs",
                            "day", "days", "d", "week", "weeks", "month", "months", "year", "y", "years","yrs","yr","monhs"]
    time_translator = __get_translator_from_representation(time_representations, UNIT_OF_TIME)
    mass_representations = ["mg", "milli-gram", "milli-grams", "gram", "gm", "grams", "gms", "g", "kilo", "kilos", "kg",
                            "kgs","lb","ounce","ounces",
                            "kilo-gram", "kilo-grams", "ton", "tonnes", "quintal", "quintals","oz","pound","pounds"]
    mass_translator = __get_translator_from_representation(mass_representations, UNIT_OF_MASS)
    electricity_representations = ["watt", "w", "kw", "kilo-watt", "kilo-watts", "v", "volt", "volts", "ampere", "a",
                                   "amperes", "kwh", "wh",
                                   "w-h"]
    electricity_translator = __get_translator_from_representation(electricity_representations, UNIT_OF_ELECTRICITY)

    translators = merge_dicts(length_translator, volume_translator, time_translator, mass_translator,
                   electricity_translator)

    return {"translators": translators, "electricity_translator": electricity_translator,
            "mass_translator": mass_translator,
            "time_translator": time_translator, "volume_translator": volume_translator,
            "length_translator": length_translator}


def replace_measurement(text):
    text = " "+text + " "
    # adding above line here since we check space before and after adding units
    # so if the number+unit occur at start or end of string they may get missed
    if text is None or type(text) is not str:
        return text
    text = replace_numbers(text)
    translators = get_measurement_translators()

    volume_translator = translators["volume_translator"]
    electricity_translator = translators["electricity_translator"]
    mass_translator = translators["mass_translator"]
    time_translator = translators["time_translator"]
    length_translator = translators["length_translator"]

    text = translate(text, volume_translator)
    text = translate(text, electricity_translator)
    text = translate(text, time_translator)
    text = translate(text, mass_translator)
    text = translate(text, length_translator)
    return text



def tokenize_lemmatize(text,word_length_filter=3,
                       external_text_processing_funcs=None,
                       lemmatize=True, token_postprocessor=None):
    if text is None or type(text) is not str:
        return []
    if external_text_processing_funcs is not None:
        for fn in external_text_processing_funcs:
            text = fn(text)

    tokens = word_tokenize(text)
    tokens = [w if len(w) >= word_length_filter and not is_stopword(w) else " " for w in tokens]
    if lemmatize:
        lemmatizer = WordNetLemmatizer()
        pos_tags = nltk.pos_tag(tokens)
        tokens = list(map(lambda x: lemmatizer.lemmatize(x[0], get_wordnet_pos(x[1])), pos_tags))
    if token_postprocessor is not None:
        for fn in token_postprocessor:
            tokens = [fn(token) for token in tokens]
    return tokens



def ngram_stopword(tokens, ngram_limit=[1]):
    ngram_limit = set(ngram_limit)
    # tokens = list(map(lambda x: re.sub('[^ a-zA-Z0-9]', '', x.lower()), tokens))
    if ngram_limit is not None and len(ngram_limit-{1}) > 0:
        grams = list(more_itertools.flatten([ngrams(tokens, i) for i in ngram_limit - {1}]))
    else:
        grams = []
    all_words = []
    if 1 in ngram_limit:
        all_words = list(filter(lambda x: len(x) > 0,map(lambda x: x.strip(), tokens)))

    for w in grams:
        is_acceptable = not any([True for spw in w if spw == " "])
        if is_acceptable:
            all_words.append(' '.join(w))
    return all_words


def combined_text_processing(text, external_text_processing_funcs=[replace_numbers], lemmatize=True,
                             word_length_filter=3, ngram_limit=[1],token_postprocessor=[]):
    tokens = tokenize_lemmatize(text,word_length_filter, external_text_processing_funcs, lemmatize,token_postprocessor)
    tokens = ngram_stopword(tokens, ngram_limit)
    return tokens




from gensim import models, corpora
from nltk import word_tokenize
from nltk.corpus import stopwords
from gensim.corpora import MmCorpus
from gensim.models.ldamodel import LdaModel
from nltk import bigrams
from nltk import trigrams
from nltk.stem import WordNetLemmatizer
from data_science_utils import dataframe as df_utils


class LDATransformer:
    def __init__(self, token_column="tokens", lda_prefix="lda_", no_below=10, no_above=0.2,
                 iterations=100, num_topics=100, passes=10,inplace=True):
        """
        For pca strategy n_components,n_iter parameters are used. n_components determine
        how many columns resulting transformation will have

        :param strategy determines which strategy to take for reducing categorical variables
            Supported values are pca and label_encode

        :param n_components Valid for strategy="pca"

        :param n_iter Valid for strategy="pca"

        :param label_encode_combine Decides whether we combine all categorical column into 1 or not.
        """

        self.token_column = token_column
        self.lda_prefix = lda_prefix
        import multiprocessing
        self.cpus = int((multiprocessing.cpu_count() / 2) - 1)
        self.dictionary = None
        self.model = None
        self.no_below = no_below
        self.no_above = no_above
        self.iterations = iterations
        self.num_topics = num_topics
        self.passes = passes
        self.inplace=inplace

    def fit(self, X, y=None):
        tokens = list(X[self.token_column].values)
        dictionary = corpora.Dictionary(tokens)
        self.dictionary = dictionary
        self.dictionary.filter_extremes(no_below=self.no_below, no_above=self.no_above, keep_n=1000000,)
        print('Number of unique tokens after filtering for LDA: %d' % len(dictionary))
        if not self.inplace:
            X = X.copy()
        X['bow'] = X[self.token_column].apply(dictionary.doc2bow)
        from gensim.models.ldamulticore import LdaMulticore
        eval_every = int(self.iterations/20)+1
        temp = dictionary[0]
        id2word = dictionary.id2token
        corpus = list(X['bow'].values)
        num_topics = 120

        model = LdaMulticore(corpus=corpus, id2word=id2word, chunksize=750, \
                             eta='auto', \
                             iterations=self.iterations, num_topics=self.num_topics, \
                             passes=self.passes, eval_every=eval_every, workers=self.cpus)
        self.model = model

    def partial_fit(self, X, y=None):
        self.fit(X, y)

    def transform(self, X, y='deprecated', copy=None):
        import pandas as pd
        if not self.inplace:
            X = X.copy()
        dictionary = self.dictionary
        X['bow'] = X[self.token_column].apply(dictionary.doc2bow)

        def bow_to_topics(bow):
            return self.model[bow]

        X['lda_topics'] = X.bow.apply(bow_to_topics)

        lda_df = pd.DataFrame.from_records(X['lda_topics'].apply(lambda x: {k: v for k, v in x}).values)
        lda_df.index = X['lda_topics'].index
        lda_df.columns = [self.lda_prefix + str(i) for i in range(0, self.num_topics)]
        X[list(lda_df.columns)] = lda_df
        df_utils.drop_columns_safely(X, ['bow', 'lda_topics', self.token_column], inplace=True)
        return X

    def inverse_transform(self, X, copy=None):
        raise NotImplementedError()

    def fit_transform(self, X, y=None):
        self.fit(X, y)
        return self.transform(X, y)

from gensim.test.utils import common_texts
from gensim.models import FastText
import multiprocessing
import pandas as pd

from data_science_utils.misc import deep_map, load_list_per_line, merge_dicts


class FasttextTransformer:
    def __init__(self, size=128, window=3, min_count=1, iter=20, min_n=2, max_n=5, word_ngrams=1,
                 workers=int(multiprocessing.cpu_count() / 2), ft_prefix="ft_", token_column=None, model=None):
        self.size = size
        self.window = window
        self.min_count = min_count
        self.iter = iter
        self.min_n = min_n
        self.max_n = max_n
        self.word_ngrams = word_ngrams
        self.workers = workers
        self.token_column = token_column
        self.model = model
        assert type(self.token_column) == str
        self.ft_prefix = ft_prefix

    def fit(self, X, y='ignored'):
        if type(X) == pd.DataFrame:
            X = X[self.token_column].values

        if self.model is None:
            self.model = FastText(sentences=X, size=self.size, window=self.window, min_count=self.min_count,
                                  iter=self.iter, min_n=self.min_n, max_n=self.max_n, word_ngrams=self.word_ngrams,
                                  workers=self.workers)

    def partial_fit(self, X, y=None):
        self.fit(X, y='ignored')

    def transform(self, X, y='ignored'):
        if type(X) == pd.DataFrame:
            Input = X[self.token_column].values
        else:
            raise ValueError()
        tnsfr = lambda t: self.model.wv[t]
        X = X.copy()
        results = deep_map(tnsfr, Input)

        X[self.token_column] = results
        return X

    def inverse_transform(self, X, copy=None):
        raise NotImplementedError()

    def fit_transform(self, X, y='ignored'):
        self.fit(X)
        return self.transform(X)



from gensim.test.utils import common_texts
from gensim.models import FastText
import multiprocessing
import pandas as pd
import numpy as np
from gensim import models, corpora
from data_science_utils import dataframe as df_utils
from gensim.test.utils import get_tmpfile
import os.path

class FasttextTfIdfTransformer:
    def __init__(self,model=None,dictionary=None,corpus_file=None,size=256, window=7, min_count=4, iter=30, min_n=4, max_n=5, word_ngrams=1,
                 no_above=0.5, filter_n_most_frequent=100,do_filter_tokens=True,
                 workers=multiprocessing.cpu_count()-1, ft_prefix="ft_", token_column=None,
                 inplace=True,store_train_data=False,
                 skip_fit=False, skip_transform=False,normalize_word_vectors=True):
        self.size = size
        self.window = window
        self.min_count = min_count
        self.iter = iter
        self.min_n = min_n
        self.max_n = max_n
        self.word_ngrams = word_ngrams
        self.workers = workers
        self.token_column = token_column
        self.model = None
        assert type(self.token_column) == str
        self.ft_prefix = ft_prefix
        self.skip_fit = skip_fit
        self.skip_transform = skip_transform
        self.inplace = inplace
        self.normalize_word_vectors = normalize_word_vectors
        self.store_train_data = store_train_data
        self.train = None
        self.model = model
        self.no_above = no_above
        self.word_set = None
        self.filter_n_most_frequent = filter_n_most_frequent
        self.do_filter_tokens = do_filter_tokens
        self.dictionary = dictionary
        if model is None and corpus_file is not None:
            self.dictionary = Dictionary(map(lambda s: s.split(), load_list_per_line(corpus_file)))
            print("Total Unique Tokens = %s" % (len(self.dictionary)))
            self.dictionary.filter_extremes(no_below=self.min_count, no_above=self.no_above, keep_n=1000000)
            self.dictionary.filter_n_most_frequent(self.filter_n_most_frequent)
            print("Total Unique Tokens after filtering = %s" % (len(self.dictionary)))
            self.word_set = set(self.dictionary.values())
            self.model = FastText(corpus_file=corpus_file, size=self.size, window=self.window, min_count=self.min_count,
                                  iter=self.iter, min_n=self.min_n, max_n=self.max_n, word_ngrams=self.word_ngrams,
                                  workers=self.workers, bucket=8000000, alpha=0.03, negative=10, ns_exponent=0.5)

        if (model is None or dictionary is None) and corpus_file is None:
            raise ValueError("No data given to initialise FastText Model")
        assert self.dictionary is not None and self.model is not None

    def fit(self, X, y='ignored'):
        gc.collect()
        if self.store_train_data:
            self.train = (X,y)
        if self.skip_fit:
            return self
        if type(X) == pd.DataFrame:
            X = X[self.token_column].values
        else:
            raise ValueError()

        assert self.dictionary is not None and self.model is not None

        self.dictionary.add_documents(X)
        dct = self.dictionary
        print("Total Unique Tokens = %s"%(len(dct)))
        dct.filter_extremes(no_below=self.min_count, no_above=self.no_above, keep_n=1000000)
        dct.filter_n_most_frequent(self.filter_n_most_frequent)
        print("Total Unique Tokens after filtering = %s"%(len(dct)))
        self.word_set = set(dct.values())

        print("FastText Modelling Started at %s"%(str(pd.datetime.now())))
        self.model.build_vocab(X,update=True)
        self.model.train(X, total_examples=self.model.corpus_count, epochs=self.model.epochs)
        print("FastText Modelling done at %s" % (str(pd.datetime.now())))
        print("FastText Vocab Length = %s, Ngrams length = %s"%(len(self.model.wv.vectors_ngrams),len(self.model.wv.vectors_vocab)))

        gc.collect()
        return self

    def fit_stored(self):
        X,y = self.train
        return self.fit(X,y)

    def partial_fit(self, X, y=None):
        self.fit(X, y='ignored')

    def transform_one(self,token_array):
        tokens2vec = [self.model.wv[token] if token in self.model.wv else np.full(self.size, 0) for token in token_array]
        if np.sum(tokens2vec) == 0:
            return np.full(self.size, 0)
        return np.average(tokens2vec, axis=0)

    def transform(self, X, y='ignored'):
        print("Fasttext Transforms start at: %s" % (str(pd.datetime.now())))
        if self.skip_transform:
            return X
        if type(X) == pd.DataFrame:
            Input = X[self.token_column].values
        else:
            raise ValueError()
        if not self.inplace:
            X = X.copy()

        uniq_tokens = set(more_itertools.flatten(Input))
        print("Number of Unique Test Tokens for Fasttext transform %s"%len(uniq_tokens))
        if self.do_filter_tokens:
            uniq_tokens = uniq_tokens.intersection(self.word_set)
        print("Number of Unique Test Tokens after filtering for Fasttext transform %s" % len(uniq_tokens))
        empty = np.full(self.size, 0)
        token2vec = {k: self.model.wv[k] if k in self.model.wv else empty for k in uniq_tokens}
        token2vec = {k: v / np.linalg.norm(v) for k, v in token2vec.items()}


        def tokens2vec(token_array):
            empty = np.full(self.size, 0)
            if len(token_array) == 0:
                return empty
            return [token2vec[token] if token in uniq_tokens else empty for token in token_array]

        ft_vecs = list(map(tokens2vec, Input))

        results = list(map(lambda x: np.average(x, axis=0,) if np.sum(x) != 0 else np.full(300, 0), ft_vecs))

        text_df = pd.DataFrame(list(map(list, results)))
        text_df.columns = [self.ft_prefix + str(i) for i in range(0, self.size)]
        text_df.index = X.index
        X[list(text_df.columns)] = text_df
        gc.collect()
        print("Fasttext Transforms done at: %s" % (str(pd.datetime.now())))
        return X

    def inverse_transform(self, X, copy=None):
        raise NotImplementedError()

    def fit_transform(self, X, y='ignored'):
        self.fit(X)
        return self.transform(X)


class TextProcessorTransformer:
    def __init__(self, source_cols, word_length_filter=2, ngram_limit=[1],
                 combined_token_column="tokens",
                 text_fns=[], column_text_fns=None,
                 skip_fit=True, skip_transform=False,
                 token_postprocessor=[], parallel=True,
                 inplace=True):
        """
        """
        from data_science_utils import nlp as nlp_utils
        self.word_length_filter=word_length_filter
        self.ngram_limit=ngram_limit
        self.text_fns=text_fns
        self.token_postprocessor=token_postprocessor
        self.parallel=parallel
        self.source_cols=source_cols
        self.combined_token_column=combined_token_column
        import multiprocessing
        self.cpus = int((multiprocessing.cpu_count()/2)-1)
        self.column_text_fns = column_text_fns
        assert column_text_fns is None or type(column_text_fns)==dict
        self.inplace=inplace
        self.skip_transform = skip_transform


    def fit(self, X, y=None):
        pass

    def partial_fit(self, X, y=None):
        pass

    def transform(self, X, y='deprecated', copy=None):
        if self.skip_transform:
            return X
        if type(X)!=pd.DataFrame:
            raise TypeError()
        if not self.inplace:
            X=X.copy()
        from joblib import Parallel, delayed
        jobs = min(self.cpus,int(np.log2(len(X))+6))
        combined_token_column = self.combined_token_column
        extra_cols = []
        for col in self.source_cols:
            vals = list(X[col].values)

            if self.column_text_fns is not None and col in self.column_text_fns.keys():
                text_processor_ = lambda text: combined_text_processing(text,word_length_filter=self.word_length_filter,
                                                  ngram_limit=self.ngram_limit,
                                                  external_text_processing_funcs=self.column_text_fns[col],
                                         token_postprocessor=self.token_postprocessor)
                vals = Parallel(n_jobs=jobs, backend="loky")(delayed(text_processor_)(x) for x in vals)
            else:
                text_processor_ = lambda text: combined_text_processing(text,word_length_filter=self.word_length_filter,
                                                               ngram_limit=self.ngram_limit,
                                                               external_text_processing_funcs=self.text_fns,
                                                               token_postprocessor=self.token_postprocessor)
                vals = Parallel(n_jobs=jobs,backend="loky")(delayed(text_processor_)(x) for x in vals)
            X[col+"_tokens"]=vals
            extra_cols.append(col+"_tokens")
        X[combined_token_column] = X[self.source_cols[0]+"_tokens"]
        for col in self.source_cols[1:]:
            X[combined_token_column] = X[combined_token_column] + X[col+"_tokens"]
        df_utils.drop_columns_safely(X,extra_cols,inplace=True)
        gc.collect()
        return X

    def inverse_transform(self, X, copy=None):
        raise NotImplementedError()

    def fit_transform(self, X,y=None):
        print("TextProcessor fit-transforms start at: %s" % (str(pd.datetime.now())))
        self.fit(X,y)
        res = self.transform(X,y)
        print("TextProcessor fit-transforms done at: %s" % (str(pd.datetime.now())))
        return res


