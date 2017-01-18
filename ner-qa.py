
''' 
    Steps:
    1. turn question document into dictionary of {question number: content words}
        -this involves POS tagging to find verbs and past tense, VB / VRB and VBD
        -find the named entity within the question
    2. Go through documents to find the N (=5) documents that have the highest co-occurrence of the content words
    3. For these documents, break into sentences, find the ones that have the highest occurrence and co-occurrence
        of the content words, check to make sure that the returned answer
        has a named entity of the same type as the question
'''


from nltk import word_tokenize, pos_tag, ne_chunk, sent_tokenize
import numpy as np
import re
import os
import csv
import operator


def remove_function_words(sent_as_tokens):
    ''' takes in a list of strings and removes function words'''
    remove = ['IN', 'DT', '.', 'WDT', 'MD', 'VBZ', 'TO', 'PRP', 'POS']
    question_words = ['WRB', 'WP']
    cleaned = [n[0] for n in pos_tag(sent_as_tokens) if n[1] not in remove+question_words and n[1].isalnum()]
    return cleaned


def questionProcess(doc):
    ''' output a dictionary of {question number: [content word, content word, ...]}
        and a dictionary of {question number: ner type that answer must have}
        1. record what the question type is and what corresponding answer NER should be
            if first word == 'Who', answer ne = 'PERSON'
            'Where' == 'LOCATION' or 'GPE'
            'When' == 'TIME'
        2. Reduce each question to content words
    '''
    with open(doc, 'r') as myfile:
        data=myfile.read().replace('\n', '').replace('\r', "").replace("Number: ","").replace("Description:", "")
        data = re.split('<top> |<num> |<desc> |</top>', data)

        clean_data = {}
        ner_type = {}
        ners = {'Where': ['LOCATION','GPE'], 'When': ['TIME'], 'Who': ['PERSON'], 'Whom': ['PERSON']}
        
        for i in range(0,len(data)-2,3):
            # for each question, tokenize it, POS tag it,
            # add the word to clean_data as a value if its POS not in the above lists
            q_num = int(data[i+1])
            sent = data[i+2]
            tokens = word_tokenize(sent)
            ner_type[q_num] = ners[tokens[0]]
            clean_data[q_num] = remove_function_words(tokens)
           
    return clean_data, ner_type


def create_doc_score_dict(path, q_num, content_words):
    ''' Go through documents in a folder, assign score for each one
        based on occurrence and overlap of content words
        return dictionary of {document number: score}
    '''
    path += str(q_num)
    score_dict = {}
    for filename in os.listdir(path):
        with open(path+"/"+filename, 'r') as myfile:
            data=myfile.read().replace('\n', ' ').replace('\r', "")
            try:
                tokens = word_tokenize(data)
                last_occ = (0, "nil")
                score_dict[filename] = 0
                for index in range(len(tokens)):
                    if tokens[index] in content_words:
                        if (abs(index-last_occ[0])<10) & (tokens[index]!=last_occ[1]):
                            score_dict[filename] += 10
                        last_occ = (index, tokens[index])
                        score_dict[filename] += 1
            except:
                pass
                
    return score_dict


def filter_sentences(path, q_num, score_dict, ne_type):
    ''' Take in dictionary of {document number: score} and NE type for answer (as a list of strings)
        NER tag all sentences in the corpus, only return ones that contain proper NE type
        Return a dictionary of {doc number: [sentence, ...]}
    '''
    path += str(q_num)
    # sort the score dictionary by value, return top 5 keys, where key = document number
    docs = dict(sorted(score_dict.iteritems(), key=operator.itemgetter(1), reverse=True)[:5]).keys()
    ne_sent_dict = {}
    
    for doc in docs:
        with open(path + '/' + doc, 'r') as docfile:
            data = docfile.read().replace('\n', ' ').replace('\r', "")
            sents = sent_tokenize(data)
            ne_sent_dict[doc] = []
            for sent in sents:
                tokens = word_tokenize(sent)
                parse_tree = ne_chunk(pos_tag(tokens), binary=False)
                
                for subtree in parse_tree.subtrees():
                    if subtree.label() in ne_type:
                        ne_sent_dict[doc].append(sent)

    return ne_sent_dict
    

def create_sentence_score(doc_sentences, content_words):
    ''' takes in dictionary of sentences, {doc number: [sentence, ...]}
        takes in list of content words
        scores sentences to return as dictionary, {(doc number, sentence): score}
    '''
    score_dict = {}
    for doc in doc_sentences:
        if doc_sentences[doc] == []:
            score_dict[(0, "nil")] = 0
        else:
            for sentence in doc_sentences[doc]:
                last_occ = (0, "nil")
                score_dict[(doc, sentence)] = 0
                sen = word_tokenize(sentence)
                for index in range(len(sen)):
                    if sen[index] in content_words:
                        if (abs(index-last_occ[0])<len(sen)) & (sen[index]!=last_occ[1]) & (last_occ[1]!="nil"):
                            score_dict[(doc, sentence)] += 10
                        last_occ = (index, sen[index])
                        score_dict[(doc, sentence)] += 1

    return score_dict


def get_top_sents(N, sent_scores, ne_type, content_words):
    ''' Get the top N scoring sentences, shorten them to 10 words or less
        ne_chunk the sentences, return only the appropriate type named entities
    '''
    sents = dict(sorted(sent_scores.iteritems(), key=operator.itemgetter(1), reverse=True)[:N]).keys()

    cleaned = []
    for tup in sents:
        doc_num = tup[0]
        sent_tokens = word_tokenize(tup[1])
        kept_words = []
        
        parse_tree = ne_chunk(pos_tag(sent_tokens), binary=False)
                
        for subtree in parse_tree.subtrees():
            if subtree.label() in ne_type:
                [kept_words.append(leaf[0]) for leaf in subtree.leaves() if leaf[0] not in content_words]
                
        if len(kept_words) == 0:
            kept_words = ["nil"]
        kept_words = set(kept_words[:10])
            
        cleaned.append((doc_num, " ".join(kept_words)))
            
    return cleaned

    
        
            
if __name__ == '__main__':
    doc_folder = 'doc_test/'
    input_doc = 'question_test.txt'
    output_doc = 'answer_test.txt'
    questions, ner_dict = questionProcess(input_doc)

    with open(output_doc, "w") as output:
        for i in range(1,89):
            print i
            question_number = i
            content_ws = questions[question_number]
            ne_types = ner_dict[question_number]
            doc_score_dict = create_doc_score_dict(doc_folder, question_number, content_ws)
            filtered_sents = filter_sentences(doc_folder, question_number, doc_score_dict, ne_types)
            sent_scores = create_sentence_score(filtered_sents, content_ws)

            if len(sent_scores) == 1:
                top_sents = [(0, "nil")] * 5
            else:
                top_sents = get_top_sents(5, sent_scores, ne_types, content_ws)
            
            for x in top_sents:
                doc_num = x[0]
                answer = x[1]
                output.write(str(i) + " " + str(doc_num) + " " + answer + "\n")



