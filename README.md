# Information Retrieval System
This project is implemented for ISNA news agency dataset in two phases.

# Brief description
This project consists of two phases; the first phase includes:
* Data preprocessing
* Creating a `positional index`
* Respond to the user

and the second phase consists of:
* Representing document in vector space model
* Respond to the user in vector space
* Increasing the speed of query processing by creating `champion list`

# Phase 1: Implement positional index
The most important functions are listed below:
* doc_preprocessing(): tokenizing, removing stopwords and stemming are done by this function;
* create_inverted_index(): creating the positional index
* Query_extraction class:
  * multiword_extraction(): extracting the biwords
  * not_token_extraction(): extracting the words that mustn't be in the result
* showResultWithoutRanking()

# Phase 2: Efficient query responding by modeling in vector space and chmampion list
The most important functions are listed below:
* create_inverted_index(): Improve positonal index by adding tf-idf element
* vectorize_query(): modeling query in vector space
* similarity_DAAT(): Document at a time similarty algorithm which is not efficiant
* similarity_TAAT(): Text at a time similarty algorithm which extremly decrease the time complexity by using index elimination technique
* create_champion_list()
* showRankedResult()
