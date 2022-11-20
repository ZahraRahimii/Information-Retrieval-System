# Information Retrieval System
This project is implemented for [ISNA](https://drive.google.com/file/d/1p0sMTj6hAw8G3QxYkFmXXA1Q5eDABgCr/view?usp=sharing) news agency dataset in two phases.

## Brief description
This project consists of two phases; the first phase includes:
* Data preprocessing
* Creating a `positional index`
* Respond to the user

And the second phase consists of the following:
* Representing document in vector space model
* Respond to the user in vector space
* Increasing the speed of query processing by creating `champion list`

## Phase 1: Implement positional index
The most important functions are listed below:
* doc_preprocessing(): tokenizing, removing stopwords, and stemming is done by this function;
* create_inverted_index(): creating the positional index
* Query_extraction class:
  * multiword_extraction(): extracting the biwords
  * not_token_extraction(): extracting the words that mustn't be in the result
* showResultWithoutRanking()

## Phase 2: Efficient query responding by modeling in vector space and champion list
The most important functions are listed below:
* create_inverted_index(): Improve positional index by adding tf-idf element
* vectorize_query(): modeling query in vector space
* similarity_DAAT(): Document at a time similarity algorithm which is not efficient
* similarity_TAAT(): Text at a time similarity algorithm which extremely decrease the time complexity by using index elimination technique
* create_champion_list()
* showRankedResult()
