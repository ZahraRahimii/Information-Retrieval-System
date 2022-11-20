from cmath import log
import json
from pydoc import doc
import queue
from re import T
from trace import Trace
from turtle import pos
from parsivar import FindStems
from hazm import Normalizer, stopwords_list, word_tokenize
import math
from functools import reduce
import collections
from collections import OrderedDict
import matplotlib.pyplot as plt
from copy import copy


my_normalizer = Normalizer()
my_stemmer = FindStems()
stopwords = stopwords_list()

def extract_contents():
    with open("G:\downloads\\IR_data_news_12k.json", 'r', encoding='utf8') as fp:
        #Reading file line by line
        line = json.load(fp)
        for i in line:
            all_docs_contents.append(line[i]["content"])
            all_doc_URLs.append(line[i]["url"])
            all_doc_titles.append(line[i]["title"])

    fp.close()

################################################## PreProcessing  ###############################################
punctuations = [
    ".",
    "،",
    "؛",
    ":",
    "؟",
    "!",
    "»",
    "«",
    "(",
    ")"
]
jams = [
    "ای"
]

def doc_pre_processing(doc):
    # doc = doc.translate(str.maketrans('', '', ''.join(punctuations))) 
    doc_tokens = word_tokenize(my_normalizer.normalize(doc))

    new_tokens = []
    for token in doc_tokens:
        new_tokens.append(str(token).replace("\u200c", ""))

    doc_tokens = new_tokens
    new_tokens = []
    for token in doc_tokens:
        if not token in stopwords:
            new_tokens.append(token)
    doc_tokens = new_tokens
    
    stem_tokens = []
    for token in doc_tokens:
        stem_tokens.append(my_stemmer.convert_to_stem(token))

    doc_tokens = stem_tokens
    return doc_tokens
    

def idInArrDicts(id, term, pos_index):
    for dict in pos_index[term][1]:
        for doc_id, list in dict.items():
            if str(doc_id) == str(id):
                return True 

def create_inverted_index(contents):
    pos_index = {}
    N = len(all_docs_contents)
    # pre_processed_tokens = pre_process(contents)
    for id, content in enumerate(contents):
        # print(id)
        tokens = doc_pre_processing(content)
        for pos, term in enumerate(tokens):
            
            if not term in pos_index:
                pos_index[term] = []
                pos_index[term].append(1)
                pos_index[term].append([])
                
                dict = {}
                dict[id] = []
                tf_idf = math.log(N)
                dict[id].append(tf_idf) #tfidf(term, id, N)
                dict[id].append(1)
                dict[id].append([])
                dict[id][2] = [pos]  
                pos_index[term][1].append(dict)

            else:     
                if idInArrDicts(id, term, pos_index):
                    dictsOfTerm = pos_index[term][1]
                    idDict = {}
                    for dict in dictsOfTerm:
                        for key in dict.keys():
                            if key == id:
                                idDict = dict
                    idDict[id][1] = idDict[id][1] + 1
                    idDict[id][2].append(pos)
                    #tfidf(term, id, N)
                    ft_d = idDict[id][1]
                    nt = pos_index[term][0] + 1
                    tf_idf = (1 + math.log(ft_d)) * math.log(N/nt) 
                    idDict[id][0] = tf_idf

                    pos_index[term][1] = dictsOfTerm

                else:
                    dictsOfTerm = pos_index[term]                    
                    new_dict = {}
                    new_dict[id] = []
                    new_dict[id].append(1)
                    new_dict[id].append(1)
                    new_dict[id].append([])
                    new_dict[id][2] = [pos]
                    #tfidf(term, id, N)
                    nt = pos_index[term][0] + 1
                    tf_idf = math.log(N/nt) 
                    new_dict[id][0] = tf_idf

                    dictsOfTerm[1].append(new_dict)
                    pos_index[term] = dictsOfTerm
                   
                pos_index[term][0] = pos_index[term][0] + 1
            print(pos_index[term])
        
    return pos_index

def create_champion_list(k):
    champion_list = dict()
    for term, postings_list in positional_index.items():
        sorted_index = sorting_postings(term, postings_list[1])
        top_k = sorted_index[:k]
        champion_list[term] = copy(top_k)
    return champion_list

def sorting_postings(term, postings_list):
    # tmp_champ_list = dict()
    tmp_champ_list = {}
    tmp_champ_list[term] = {}
    # print(postings_list)
    for posting in postings_list:
        doc_id = int(list(posting.keys())[0])
        # print(posting)
        tmp_champ_list[term][doc_id] = []
        tmp_champ_list[term][doc_id].append(posting[str(doc_id)][0]) #tfidf
        tmp_champ_list[term][doc_id].append(posting[str(doc_id)][2]) #pos list
    
    sorted_index = sorted(tmp_champ_list[term].items(), key=lambda x:x[1][0], reverse=True)
    return sorted_index

class QueryExtraction:
    def __init__(self, k=50, type="normal"):
        self.pontu = ["'", "!"]
        query = input("Please Enter your Query!")
        # query = "'تحریم هسته ای' آمریکا ! ایران"
        # query = "تحریم آمریکا علیه ایران"
        # query = "تحریم های آمریکا ! ایران"
        # query = "کنگره ضدتروریست"
        # query = "صهیونیست ! فلسطین "
        query = "ایران" #a
        # query = "ورزشکاران ملی" #b
        # query = "اوکراین"
        # query = "تحریم آبراموویچ"
        # query = "توافق هسته ای"
        # query = "کمیته المپیک "
        query = doc_pre_processing(query)
        self.k = k
        for token in query:
            if token not in positional_index:
                print("Are you sure? \nPlease try again", token)
                exit()
        self.query = query
        self.vectorized_query = self.vectorize_query()
        ranked_doc_ids = similarity_TAAT(self.vectorized_query, k, type)
        if not old_pos_index:
            print("Results DocumentIds with type of", type, ranked_doc_ids)
        else: 
            print("Results DocumentIds with old postional index", ranked_doc_ids)
        showRankedResult(ranked_doc_ids)

    def vectorize_query(self):
        dict1 = {}
        term_freq = dict(collections.Counter(self.query))
        for term, freq in term_freq.items():
            dict1[term] = 1 + math.log(freq)
        
        # print(dict1)
        return dict1

    def token_extraction(self):
        all_pure_tokens = []
        for token in self.query:
            if token not in self.not_token_extraction() and not str(token).startswith("'") and not str(token).endswith("'") and not token in self.pontu:
                all_pure_tokens.append(token)
        return all_pure_tokens

    def multiWord_extraction(self):
        multi_word = []
        MW_arr = []
        start = False
        for token in self.query:

            if str(token).startswith("'"):
                start = True
                if str(token).removeprefix("'") not in jams and str(token).removesuffix("'") not in jams:
                    multi_word.append(str(token).replace("'", ""))
                continue
            if str(token).endswith("'"):
                start = False
                if str(token).removeprefix("'") not in jams and str(token).removesuffix("'") not in jams:
                    multi_word.append(str(token).replace("'", ""))
                MW_arr.append(multi_word)
                multi_word = []
                continue
            if start:
                if str(token).removeprefix("'") not in jams and str(token).removesuffix("'") not in jams:
                    multi_word.append(str(token).replace("'", ""))
        return MW_arr
        
    def not_token_extraction(self):
        not_tokens = []
        flag = False
        for token in self.query:
            if token == '!':
                flag = True
                continue
            if flag:
                not_tokens.append(token)
                flag = False
        return not_tokens

def similarity_DAAT(query_weight):
    doc_similarity = {} 
    for doc_id in range(N):
        top = 0
        for term, wt in query_weight.items():
            score = 0
            if idInArrDicts(str(doc_id), term, positional_index):
                dict = getDictWithID(positional_index[term][1], doc_id)
                score = dict[str(doc_id)][0]
            if score != 0:
                top += score * wt
        bottom = doc_length()
        doc_similarity[doc_id] = top / bottom

def similarity_TAAT(query_weight, k, type):
    doc_similarity = {} 
    score = 0
    for term, wt in query_weight.items():
        if type == "normal":
            for dict in positional_index[term][1]:
                doc_id = list(dict.keys())[0]
                dict = getDictWithID(positional_index[term][1], doc_id)
                score = dict[str(doc_id)][0]
                if score != 0:
                    if doc_id in doc_similarity:
                        doc_similarity[doc_id] += score * wt
                    else:
                        doc_similarity[doc_id] = score * wt
           
        elif type == "champions_list":
            for posting in champion_list[term]:
                # print(posting)
                doc_id = posting[0]
                score = posting[1][0]
                if score != 0:
                    if doc_id in doc_similarity:
                        doc_similarity[doc_id] += score * wt
                    else:
                        doc_similarity[doc_id] = score * wt

    for doc_id in range(N):
        if doc_id not in doc_similarity:
            doc_similarity[doc_id] = 0
    
    length_arr = doc_length(type)
    for doc_id in range(N):
        doc_similarity[doc_id] /= length_arr[doc_id]

    if type == "normal":
        return extract_doc_ids(sorted(doc_similarity.items(), key=lambda x: x[1], reverse=True)[:k])
    else:
        return list(doc_similarity.keys())[:k]


def doc_length(type = "normal"):

    length_arr = [0 for i in range(N)]
    if type == "normal":
        for term, postings in positional_index.items():
            for dict in positional_index[term][1]:
                doc_id = list(dict.keys())[0]
                posting = dict[doc_id]
                length_arr[int(doc_id)] += (posting[0]) ** 2
    elif type == "champions_list":
        for term, postings_lists in champion_list.items():
            for postings in postings_lists:
                doc_id = postings[0]
                length_arr[int(doc_id)] += (postings[1][0]) ** 2
    
    for i in range(N):
        length_arr[i] = math.sqrt(length_arr[i])
    return length_arr
    
def extract_doc_ids(docId_scores):
    docIds= []
    for doc_id, score in docId_scores:
        docIds.append(doc_id)
    
    return docIds

def multi_word_query(multi_words, id_freq):
    all_results = []
    results_id_freq = []
    for tokens in multi_words:
        idfreq = {}
        pos_index0 = positional_index[tokens[0]]
        pos_index1 = positional_index[tokens[1]]
        docIds_results = biword_processing( pos_index0, pos_index1, idfreq)
        results_id_freq.append(idfreq)
        all_results.append(docIds_results)
    
    for id_freq1 in results_id_freq:
        for key in id_freq1.keys():
            if key in id_freq:
                id_freq[key] += id_freq1[key]
            else:
                id_freq[key] = id_freq1[key]
    
    return all_results

def showRankedResult(docIds):
    print("Results Are Ready!")
    with open('Search Engine Results.txt', 'w', encoding='utf-8') as txt_file:
        if not docIds:
             txt_file.write("\nQuery Not Found!:")
        else:
            for id, docId in enumerate(docIds):
                docId = int(docId)
                txt_file.write("\n" + "Title Number " + str(id) + ":" + all_doc_titles[docId])
                txt_file.write("\n"+ "Content:" + all_docs_contents[docId])
                txt_file.write("URL:" + all_doc_URLs[docId])
                txt_file.write("\n\n\n\n")

def biword_processing(pos_index0, pos_index1, id_freq):
    listOfResults = []
    counter = 0
    id1 = 0
    dict1_counter = 0

    for id0, dict0 in enumerate(pos_index0[1]):
        doc_id0 = int(list(dict0.keys())[0])
        for dict1 in pos_index1[1][counter:]:
            doc_id1 = int(list(dict1.keys())[0])
            if doc_id0 == doc_id1:
                if merge_lists_pos(pos_index0, pos_index1, id0, dict1_counter, doc_id0):
                    listOfResults.append(doc_id1)
                    id_freq[doc_id1] = getDictWithID(pos_index0[1], doc_id0)[str(doc_id0)][0] + getDictWithID(pos_index1[1], doc_id1)[str(doc_id1)][0]
                
            elif doc_id0 < doc_id1:
                counter = id1
                break
            else:
                id1 += 1
                dict1_counter += 1

    return listOfResults

def getDict(pos_index, id):
    dictsOfTerm = pos_index[1]
    idDict = {}
    counter = 0
    for dict in dictsOfTerm:
        if counter == id:
            idDict = dict
        counter += 1
    return idDict

def merge_lists_pos(pos_index0, pos_index1, id0, id1, doc_id):

    dict0 = dict(getDict(pos_index0, id0))
    dict1 = dict(getDict(pos_index1, id1))

    posList0 = dict0[str(doc_id)][1]
    posList1 = dict1[str(doc_id)][1]
    
    position_pointer0 = 0
    position_pointer1 = 0

    while position_pointer0 < len(posList0) and position_pointer1 < len(posList1):
        pos0 = posList0[position_pointer0]
        pos1 = posList1[position_pointer1]

        if pos1-pos0 <= 3 and pos1-pos0 >= 1:
            return True
        elif pos0 < pos1:
            position_pointer0 += 1
        else:
            position_pointer1 += 1
    return False

def notToken_query(resultsIds, notTokens, id_freq):
    not_dictIDs = []
    final_resultIDs = []

    for notToken in notTokens:
        not_pos_index = positional_index[notToken]
        for dict1 in not_pos_index[1]:
            not_dictIDs.append(list(dict1.keys())[0])    

    for result in resultsIds:
        if result not in not_dictIDs or id_freq[str(result)] > 12000:
            final_resultIDs.append(result)

    return final_resultIDs

def convert_to_biword(string):
    s = string.split()
    return zip(s, s[1:])

def toString(arr):
    string = ""
    for el in arr:
        string += " " + el
    return string

def final_processing():
    exQuery = QueryExtraction() 
    all_tokens = exQuery.token_extraction()

    not_tokens = exQuery.not_token_extraction()
    
    multiwords = exQuery.multiWord_extraction()

    id_freq = {}
    if len(all_tokens):
        get_all_results(all_tokens, id_freq)

    multi_id_freq = {}
    if len(multiwords):
        multi_word_query(multiwords, multi_id_freq)

    ranked_resultsID = []
    comb_id_freq = result_ranking(id_freq, multi_id_freq, ranked_resultsID)
    
    if len(not_tokens):
        notResultsId = notToken_query(ranked_resultsID, not_tokens, comb_id_freq)
    else:
        notResultsId = ranked_resultsID
    

    return notResultsId

def combine_two_defFreq(id_freq, comb_id_freq, arg=0):
    for key in id_freq.keys():
        if key in comb_id_freq:
            comb_id_freq[str(key)] += id_freq[(key)] + arg
        else:
            comb_id_freq[str(key)] = id_freq[(key)] + arg

def result_ranking(id_freq,  multi_id_freq, ranked_results):
    comb_id_freq = {}
    if id_freq:
        comb_id_freq = id_freq

    if multi_id_freq:
        combine_two_defFreq(multi_id_freq, comb_id_freq, arg=12000)

    combine_copy = comb_id_freq.copy()
    x = len(combine_copy)
    for dict in range(x):
        our_max = max(combine_copy, key=combine_copy.get)
        ranked_results.append(our_max)
        combine_copy[our_max] = -100
    return comb_id_freq

def getDictWithID(posList, id):
    for dict in posList:
        for key in dict.keys():
            if int(key) == int(id):
                return dict
    
    return None

def getTermDocID(token):
    ids = []
    if not token in positional_index:
        print("Are you sure? \nWe couldn't found ", token)
        exit()
    else:
        dictsOfDocIds = positional_index[token][1]
        for dict in dictsOfDocIds:
            for key in dict.keys():
                ids.append(key)
        return ids

def get_all_results(all_tokens, id_freq):
    resultsIDs = []
    for token in all_tokens:
        resultsIDs.append(getTermDocID(token))
    
    intersection = list(reduce(set.intersection, [set(item) for item in resultsIDs]))

    not_intersection = set()
    for result in resultsIDs:
        for result_id in result:
            if result_id not in intersection:
                not_intersection.add(result_id)
    interleaved_results = []
    for r1 in intersection:
        interleaved_results.append(r1)
    for r2 in not_intersection:
        interleaved_results.append(r2)
    
    for token in all_tokens:
        for resultID in interleaved_results:
            if getDictWithID(positional_index[token][1], resultID) is None: 
                continue
            if resultID not in id_freq:
                id_freq[resultID] = getDictWithID(positional_index[token][1], resultID)[str(resultID)][0]
            else:
            
                id_freq[resultID] += getDictWithID(positional_index[token][1], resultID)[str(resultID)][0]

    return interleaved_results
    

def zipf_law_plot(pos_index):
    pos_index = OrderedDict(sorted(pos_index.items(), key=lambda x: x[1][0], reverse=True))
    word_list = list(pos_index.keys())
    count_multiply_rank = []
    count = []
    for i in range(len(word_list)):
        count_multiply_rank.append(math.log10(pos_index[word_list[i]][0]))
        count.append(pos_index[word_list[i]][0])
    ranks = list(map(lambda x: math.log10(x), range(1, len(word_list)+1)))
    plt.plot(ranks, count_multiply_rank)
    plt.title("Zipf's Law")
    plt.show()

def heap_law_plot():
    k = 50
    b = 0.40
    all_words = set()
    arg = []
    for key in list(positional_index.keys())[:500]:
        all_words.add(key)
        arg.append(k*len(all_words)**b) 
    point = [n for n in range (0, len (arg))]
    plt.plot(point, arg)
    plt.show()


all_docs_contents = []
all_doc_URLs = []
all_doc_titles = []

extract_contents()

N = len(all_docs_contents)
K = 500
k = 10

'''phase 1 posititional inedex:'''
positional_index = dict()
# positional_index = create_inverted_index(all_docs_contents)

# with open('tfidf_positionalIndex.json', 'w') as json_file:
#     json.dump(positional_index, json_file)

with open("positionalIndex_docPreprocess_all.json", 'r', encoding='utf8') as fp:
    positional_index = json.load(fp)

'''pos index with index elimination:'''
weighted_positional_index = dict()
with open("tfidf_positionalIndex.json", 'r', encoding='utf8') as fp:
    weighted_positional_index = json.load(fp)

'''champion list'''
# champion_list = create_champion_list(K)
# with open('champion_list.json', 'w') as json_file:
#     json.dump(champion_list, json_file)

champion_list = dict()
with open("champion_list.json", 'r', encoding='utf8') as fp:
    champion_list = json.load(fp)

'''Processing Query'''
old_pos_index = False
new_pos_index_type = "normal"
# new_pos_index_type = "champions_list"

if old_pos_index:
    resultsDocIDs = final_processing()
    showRankedResult(resultsDocIDs)
else:
    exQuery = QueryExtraction(k, type=new_pos_index_type)

# while(True):
#     resultsDocIDs = final_processing()
#     showResultWithoutRanking(resultsDocIDs)