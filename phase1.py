import json
from re import I
import re
from turtle import pos
from parsivar import FindStems
from hazm import Normalizer, stopwords_list, word_tokenize
import math
from functools import reduce
from collections import OrderedDict
import matplotlib.pyplot as plt


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
        for key in dict.keys():
            if key == id:
                return True

def create_inverted_index(contents):
    pos_index = {}
    # pre_processed_tokens = pre_process(contents)
    for id, content in enumerate(contents):
        print(id)
        tokens = doc_pre_processing(content)
        for pos, term in enumerate(tokens):
            
            if not term in pos_index:
                pos_index[term] = []
                pos_index[term].append(1)
                pos_index[term].append([])
                
                dict = {}
                dict[id] = []
                dict[id].append(1)
                dict[id].append([])
                dict[id][1] = [pos]  
                pos_index[term][1].append(dict)

            else:     
                if idInArrDicts(id, term, pos_index):
                    dictsOfTerm = pos_index[term][1]
                    idDict = {}
                    for dict in dictsOfTerm:
                        for key in dict.keys():
                            if key == id:
                                idDict = dict
                    idDict[id][0] = idDict[id][0] + 1
                    idDict[id][1].append(pos)
                    pos_index[term][1] = dictsOfTerm

                else:
                    dictsOfTerm = pos_index[term]                    
                    new_dict = {}
                    new_dict[id] = []
                    new_dict[id].append(1)
                    new_dict[id].append([])
                    new_dict[id][1] = [pos]
                    
                    dictsOfTerm[1].append(new_dict)
                    pos_index[term] = dictsOfTerm
                   
                pos_index[term][0] = pos_index[term][0] + 1
        
    return pos_index

class QueryExtraction:
    def __init__(self):
        self.pontu = ["'", "!"]
        print("Please Enter your Query!")
        # query = "تحریم هسته ای' آمریکا ! ایران'"
        # query = "تحریم های آمریکا علیه ایران"
        # query = "تحریم های آمریکا ! ایران"
        # query = "'کنگره ضدتروریست'"
        # query = "صهیونیست ! فلسطین "
        query = "فعالین رمزارز"

        query = doc_pre_processing(query)
        for token in query:
            if token not in positional_index:
                print("Are you sure? \nWe couldn't found ", token)
                exit()
    
        self.query = query

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
            # print(str(token).removeprefix("'"))

            if str(token).startswith("'"):
                start = True
                if str(token).removeprefix("'") not in jams and str(token).removesuffix("'") not in jams:
                    # print(token)
                    multi_word.append(str(token).replace("'", ""))
                continue
            if str(token).endswith("'"):
                start = False
                if str(token).removeprefix("'") not in jams and str(token).removesuffix("'") not in jams:
                    # print(token)
                    multi_word.append(str(token).replace("'", ""))
                MW_arr.append(multi_word)
                multi_word = []
                continue
            if start:
                if str(token).removeprefix("'") not in jams and str(token).removesuffix("'") not in jams:
                    # print(token)
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

def multi_word_query(multi_words, id_freq):
    # tokens = str(multi_word).split(" ")
    # preprocess ro anjam bede baraye query!
    # TODO:
    all_results = []
    results_id_freq = []
    for tokens in multi_words:
        idfreq = {}
        print("Multi Words", tokens)
        pos_index0 = positional_index[tokens[0]]
        pos_index1 = positional_index[tokens[1]]
        docIds_results = biword_processing( pos_index0, pos_index1, idfreq)
        print("Hi", idfreq)
        results_id_freq.append(idfreq)
        all_results.append(docIds_results)
    
    for id_freq1 in results_id_freq:
        for key in id_freq1.keys():
            if key in id_freq:
                id_freq[key] += id_freq1[key]
            else:
                id_freq[key] = id_freq1[key]
    # not_intersection = set()
    # intersection = list(reduce(set.intersection, [set(item) for item in all_results]))
    # for result in all_results:
    #     for result_id in result:
    #         if result_id not in intersection:
    #             not_intersection.add(result_id)
    # ranked_results = []
    # for r1 in intersection:
    #     ranked_results.append(r1)
    # for r2 in not_intersection:
    #     ranked_results.append(r2)
    return all_results

def showResultWithoutRanking(docIds):
    print("Results Are Ready!")
    with open('Search Engine Results.txt', 'w', encoding='utf-8') as txt_file:
        if not docIds:
             txt_file.write("\nQuery Not Found!:")
        else:
            for id, docId in enumerate(docIds):
                docId = int(docId)
                all_docs_contents[docId]
                txt_file.write("\n" + "Title Number " + str(id) + ":" + all_doc_titles[docId])
                txt_file.write("\n"+ "Content:" + all_docs_contents[docId])
                txt_file.write("URL:" + all_doc_URLs[docId])
                txt_file.write("\n\n\n\n")

                print(all_doc_titles[docId])
                print(all_docs_contents[docId])
                print(all_doc_URLs[docId])

def biword_processing(pos_index0, pos_index1, id_freq):
    listOfResults = []

    counter = 0
    id1 = 0
    dict1_counter = 0

    for id0, dict0 in enumerate(pos_index0[1]):
        doc_id0 = int(list(dict0.keys())[0])
        for dict1 in pos_index1[1][counter:]:
            doc_id1 = int(list(dict1.keys())[0])
            # print("doc id0:", doc_id0)
            # print("doc id1:", doc_id1)

            if doc_id0 == doc_id1:
                if merge_lists_pos(pos_index0, pos_index1, id0, dict1_counter, doc_id0):
                    print("helllll")
                    listOfResults.append(doc_id1)
                    # if doc_id0 not in id_freq:
                    # + pos_index1[1][(doc_id1)][0][]
                    id_freq[doc_id1] = getDictWithID(pos_index0[1], doc_id0)[str(doc_id0)][0] + getDictWithID(pos_index1[1], doc_id1)[str(doc_id1)][0]
                    # print(doc_id0)
                    
                    # id_freq[doc_id0] = pos_index0[1][doc_id0][str(doc_id0)][0]
                    # else:
                    #     id_freq[doc_id0] += pos_index0[1][str(doc_id0)][0] + pos_index1[1][str(doc_id1)][0]
                
            elif doc_id0 < doc_id1:
                # print("yes", end="\t")
                counter = id1
                break
            else:
                # print("noo", end="\t")
                id1 += 1
                dict1_counter += 1

    # ranked_results = []
    # num = len(id_freq)
    # for dict in range(num):
    #     ranked_results.append(max(id_freq, key=id_freq.get))
    #     id_freq[str(max(id_freq, key=id_freq.get))] = -1
    return listOfResults

def getDict(pos_index, id):
    dictsOfTerm = pos_index[1]
    # print(dictsOfTerm)
    idDict = {}
    counter = 0
    for dict in dictsOfTerm:
        if counter == id:
            idDict = dict
        counter += 1
    return idDict

def merge_lists_pos(pos_index0, pos_index1, id0, id1, doc_id):
    # print(id0)
    # print(id1)
    dict0 = dict(getDict(pos_index0, id0))
    dict1 = dict(getDict(pos_index1, id1))
    # print(doc_id)
    # print("dict0", dict0)
    # print("dict1", dict1)

    posList0 = dict0[str(doc_id)][1]
    posList1 = dict1[str(doc_id)][1]
    
    position_pointer0 = 0
    position_pointer1 = 0

    while position_pointer0 < len(posList0) and position_pointer1 < len(posList1):
        pos0 = posList0[position_pointer0]
        pos1 = posList1[position_pointer1]

        if pos1-pos0 <= 3 and pos1-pos0 >= 1:
            print("Hiiiiiii")
        # if pos1-pos0 == 1:
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
    # print(not_dictIDs)
    # print("not dicts Id", not_dictIDs)
    # print(resultsIds)
    for result in resultsIds:
        # print(id_freq[str(result)])
        if result not in not_dictIDs or id_freq[str(result)] > 12000:
            final_resultIDs.append(result)

    # print("final results", final_resultIDs)
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
    # print("all", all_tokens)

    not_tokens = exQuery.not_token_extraction()
    print("not", not_tokens)
    
    multiwords = exQuery.multiWord_extraction()
    # print("multi", multiwords)

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
        # print(key)
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

    # ranked_results = []
    combine_copy = comb_id_freq.copy()
    x = len(combine_copy)
    for dict in range(x):
        our_max = max(combine_copy, key=combine_copy.get)
        # print(our_max)
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
    # id_freq = {}
    ids = []
    if not token in positional_index:
        print("Are you sure? \nWe couldn't found ", token)
        exit()
    else:

        dictsOfDocIds = positional_index[token][1]
        for dict in dictsOfDocIds:
            for key in dict.keys():
                ids.append(key)
                # id_freq[key] =  dict[key][0]
                # print(dict[key][0])
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
                # print("posindex:", positional_index[token][1])
                # print(getDictWithID(token, resultID))
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
        # print(key)
        all_words.add(key)
        arg.append(k*len(all_words)**b) 
    point = [n for n in range (0, len (arg))]
    plt.plot(point, arg)
    # plt.title("Heap's Law")
    plt.show()


all_docs_contents = []
all_doc_URLs = []
all_doc_titles = []

extract_contents()

# positional_index2 = create_inverted_index(all_docs_contents)

positional_index = {}
with open("positionalIndex_docPreprocess_all.json", 'r', encoding='utf8') as fp:
    positional_index = json.load(fp)
    
# while(True):
resultsDocIDs = final_processing()
showResultWithoutRanking(resultsDocIDs)


