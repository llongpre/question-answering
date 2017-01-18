
from nltk import word_tokenize, pos_tag
import numpy as np
import re
import os
import csv
import operator


def create_answer_dict(question_num):
    ''' generates a dictionary of {word: [(file number, index), ...]} for each word in the documents in a folder
    '''
    path = "doc_test/{0}".format(question_num)
    acc_dict = {}
    for filename in os.listdir(path):
        with open(path+"/"+filename, 'r') as myfile:
                data=myfile.read().replace('\n', ' ').replace('\r', "")

                try:
                    tokenized = word_tokenize(data)

                    for i in range(len(tokenized)-1):

                        token = tokenized[i]
                        if token in acc_dict:
                            acc_dict[token].append((int(filename),i))

                        else:
                            acc_dict[token] = [(int(filename),i)]
                except:
                    pass
    return acc_dict
                        

def questionProcess():
    ''' output a dictionary of {question number: [content word, content word, ...]}
    '''
    with open('question_test.txt', 'r') as myfile:
        data=myfile.read().replace('\n', '').replace('\r', "").replace("Number: ","").replace("Description:", "")
        data = re.split('<top> |<num> |<desc> |</top>', data)

        clean_data = {}
        remove = ['IN', 'DT', 'VBD', '.', 'WDT', 'MD', 'VBZ', 'TO', 'PRP', 'POS']
        question_words = ['WRB', 'WP']
        for i in range(0,len(data)-2,3):
            # for each question, tokenize it, POS tag it,
            # add the word to clean_data as a value if its POS not in the above lists
            clean_data[data[i+1]] = [n[0] for n in pos_tag(word_tokenize(data[i+2])) if n[1] not in remove+question_words and n[1].isalnum()]
           
    return clean_data


def get_doc_occurrences(qnum, qdict, adict):
    ''' creates dictionary mapping doc number to a list of indices of content word occurrences
        returns {doc: [(index, word), ...]}
    '''
    occ_dict = {}
    for word in qdict[str(qnum)]:
        if word in adict:
            occ_list = adict[word]
            for tup in occ_list:
                if tup[0] in occ_dict:
                    occ_dict[tup[0]].append((tup[1], word))
                else:
                    occ_dict[tup[0]] = [(tup[1], word)]
        else:
            pass
    return occ_dict


def get_init_scores(occ_dict):
    ''' creates dictionary mapping word occurrence to initial score of 0
        returns {( doc number, (index,word) ): score}
    '''
    score_dict = {}
    for doc in occ_dict:
        for tup in occ_dict[doc]:
            score_dict[(doc,tup)] = 0
    return score_dict


def calc_scores(score_dict, occ_dict):
    ''' returns {(doc number, index of word): score}
    '''
    for occ in score_dict:

        #adds to score based on how many occurrences in given document
        doc_occs = occ_dict[occ[0]]
        num_occs = len(doc_occs)
        score_dict[occ] += num_occs

        #adds to score based on how many overlapping occurences with different content word occur
        for tup in doc_occs:
            idx1 = occ[1][0]
            word1 = occ[1][1]
            idx2 = tup[0]
            word2 = tup[1]
            if (abs(idx1-idx2) < 10) & (word1!=word2) :
                score_dict[occ] += 100

    return score_dict


def sort_dict_on_score(score_dict):
    ''' creates highest-first sorted list of occurrence and score maintained as tuples
        returns ( ( doc number, (index, word) ) , score ) list
    '''
    sorted_score = sorted(score_dict.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_score


def generate_guesses(question_num, score_list): 
    ''' returns a list of 5 guesses for a single question
        returns [question number, doc number, string guess] list
    '''
    directory = os.path.join("doc_test/"+str(question_num))
    guesses = []
   
    for x in range(0,5):
        try:
            item = score_list[x]
            doc_num = item[0][0]
            index = item[0][1][0]

            doc = open(directory + '/' + str(doc_num)).read().replace('\n', ' ').replace('\r', "")
            tokenized = word_tokenize(doc)

            if index <= 9:
                sentence = " ".join(tokenized[index:index+10])
            elif index >= len(doc) - 10:
                sentence = " ".join(tokenized[index-10:index])
            else:
                sentence = " ".join(tokenized[index-5:index+5])
            guesses.append([question_num, doc_num, sentence])
        except:
            doc_num = 0
            guesses.append([question_num,doc_num,"nil"])
    return guesses



if __name__ == '__main__':
    guesses_list = []
    question_dict = questionProcess()

    # generate a list of guesses for each question
    for x in range(1,89):
        print x
        answer_dict = create_answer_dict(x)
        occ_dict = get_doc_occurrences(x, question_dict, answer_dict)
        init_score_dict = get_init_scores(occ_dict)
        final_score_dict = calc_scores(init_score_dict, occ_dict)
        sorted_scores = sort_dict_on_score(final_score_dict)
        guesses = generate_guesses(x, sorted_scores)
        guesses_list = guesses_list+guesses

    # generate the output file
    with open("answer_test.txt", "w") as output:
        for x in guesses_list:
            q_num = x[0]
            doc_num = x[1]
            answer = x[2]
            output.write(str(q_num) + " " + str(doc_num) + " " +answer+ "\n")
















