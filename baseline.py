
from nltk import word_tokenize
import numpy as np
import re
import os
import csv


def questionProcess():
    ''' reduce each question to a single "content" word, as defined by being the longest non-function word in a sentence
        create a dictionary of {question number: content word} for each question
    '''
    
    with open('question.txt', 'r') as myfile:
        data=myfile.read().replace('\n', '').replace('\r', "").replace("Number: ","").replace("Description:", "")
        function_words = [' Who ', ' Where ', ' When ', ' the ', ' a ', ' and ', ' or ', ' is ', ' did ',
                          'does', ' was ', '?', ' of ', ' from ', ' do ', ' can ', ' come ', ' you ', ' in ', ' most ']
        for word in function_words:
            data = data.replace(word," ")
        data = re.split('<top> |<num> |<desc> |</top>', data)
        clean_data = {}
        for i in range(0,len(data)-2,3):
            clean_data[data[i+1]] = data[i+2]
        for key in clean_data:
            clean_data[key] = max(word_tokenize(clean_data[key]), key=len)
        
    return clean_data


def generate_output_file(dictionary):
    ''' Now, for each key in the dictionary, iterate through all files in corresponding folder
        Stop at document with first occurrence of dict[key]
        Tokenize that document
        Find index of word
        Record the 5 moving windows of 10 words around the question word
        Write each guess to an output file
    '''
    
    with open("answer.txt", "w") as output:
        #output = csv.writer(output, delimiter=" ")
        for key in dictionary: # for each question, open corresponding folder
            directory = os.path.join("doc_dev/"+str(key))
            word = dictionary[key]

            for root,dirs,files in os.walk(directory): # opens each file in the folder
                for file in files:
                    doc = open(directory + '/' + file).read()
                    doc = word_tokenize(doc)
                    if word in doc:
                        index = doc.index(word)
                        answers = []
                        if index >= 9 and index <= len(doc) - 10:
                            answers.append(doc[index-10:index])
                            answers.append(doc[index-8:index+2])
                            answers.append(doc[index-6:index+4])
                            answers.append(doc[index-4:index+6])
                            answers.append(doc[index-2:index+8])
                        else:
                            answers.append("nil")
                            answers.append("nil")
                            answers.append("nil")
                            answers.append("nil")
                            answers.append("nil")
                        for answer in answers:
                            output.write(key + " " + file + " " + " ".join(answer) + "\n")
                        break
                    else:
                        answers = []
                        answers.append("nil")
                        answers.append("nil")
                        answers.append("nil")
                        answers.append("nil")
                        answers.append("nil")
                    for answer in answers:
                        output.write(key + " " + file + " " + " ".join(answer) + "\n")
                    break

                    
if __name__ == '__main__':
    question_dict = questionProcess()
    generate_output_file(question_dict)




