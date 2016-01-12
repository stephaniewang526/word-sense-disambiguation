#CS4740 Project 2 WSD
#JRL336, QW79
#10/8/2015

from __future__ import division
import xml.etree.ElementTree as ET
import random

#Preprocessing of training-data.xml
tree2 = ET.parse('training-data.xml')
trainingTree = tree2.getroot()

#Make a hashtable to store context and senseid
sense_context = dict()
for lexelt in trainingTree:
    item = lexelt.attrib
    word_pos = item.get('item')
    #print word_pos
    for instance in lexelt.iter('instance'):
        for answer in instance.iter('answer'):
            sense_id = answer.get('senseid')
        for context in instance.iter('context'):
            context = context.text
            #print context

#Calculate prior probability of each sense for given lexelt
def calcAllPriors(lexelt):
    numSenses = 0
    sense_counts = dict()
    for instance in lexelt.iter('instance'):
        for answer in instance.iter('answer'):
            numSenses = numSenses+1
            sense_id = answer.get('senseid')
            if sense_id in sense_counts:
                sense_counts[sense_id] += 1
            else:
                sense_counts[sense_id] = 1        
    for key,val in sense_counts:
        sense_counts[key] = val / numSenses
    return sense_counts


#Get total number of each sense
def calcAllSenseCounts(lexelt):
    numSenses = 0
    sense_counts = dict()
    for instance in lexelt.iter('instance'):
        for answer in instance.iter('answer'):
            numSenses = numSenses+1
            sense_id = answer.get('senseid')
            if sense_id in sense_counts:
                sense_counts[sense_id] += 1
            else:
                sense_counts[sense_id] = 1
    return sense_counts

def calcPriorProbs(lexelt):
    sense_counts = calcAllSenseCounts(lexelt)
    sum = 0
    for ele in sense_counts:
        sum+= sense_counts[ele]
    for ele in sense_counts:
        sense_counts[ele] = sense_counts[ele]/sum
    return sense_counts

def findIndexHead(lst):
    for i in range(0, len(lst)):
        if lst[i].startswith('*head*'):
            return i
                           
#Co-occurence counting
def coOccurenceFeaturesGenerataion(lexelt):
    sense_dict = dict() #list of senses and their hashtable of co-occurent counts
    for instance in lexelt.iter('instance'):
        sense_list = []
        #add senseID to sense_dict
        for answer in instance.iter('answer'):
            currentSenseID = answer.get('senseid')
            sense_list.append(currentSenseID)
            #new senseID
            if not currentSenseID in sense_dict:
               sense_dict[currentSenseID] = dict() 
            
        #add hashtable of features and counts
        for context in instance.iter('context'):
            txt = context.text
            lst = txt.split()
            #find position of <head> and </head>
            targetIndex = findIndexHead(lst)
            
            #find co-occurrence features
            if (targetIndex - 10) < 0:
                prior = lst[:targetIndex]
            else:
                prior = lst[targetIndex-10:targetIndex]
            
            if (targetIndex + 11) > len(lst):
                post = lst[targetIndex+1:]
            else:
                post = lst[targetIndex+1 : targetIndex+11]
            
            for word in prior:
                for sense in sense_list:
                    #count (fj, si)
                    if sense_dict[sense].has_key(word):
                        #increment fj count by 1
                        sense_dict[sense][word] = sense_dict[sense][word] + 1
                    else:
                        sense_dict[sense][word] = 1
            
            for word in post:
                for sense in sense_list:
                    #count (fj, si)
                    if sense_dict[sense].has_key(word):
                        #increment fj count by 1
                        sense_dict[sense][word] = sense_dict[sense][word] + 1
                    else:
                        sense_dict[sense][word] = 1  
    return sense_dict;

def extractFeatures(context):
    txt = context.text
    lst = txt.split()
    #find position of <head> and </head>
    targetIndex = findIndexHead(lst)
    
    #find co-occurrence features
    if (targetIndex - 10) < 0:
        prior = lst[:targetIndex]
    else:
        prior = lst[targetIndex-10:targetIndex]
    
    if (targetIndex + 11) > len(lst):
        post = lst[targetIndex+1:]
    else:
        post = lst[targetIndex+1 : targetIndex+11]
    return prior + post

#Add 'unk' in to smooth sense hash table
def addUnktoFeatures(hash_features):
    hash_features['UNK'] = 1
    return hash_features

# Calculate Naive Bayes for each senseid 
def trainModel():
    model_hash = dict()
    for lexelt in trainingTree:
        priorTable = calcPriorProbs(lexelt) #figure out way to pass this to runModel
        hash_senseCounts = calcAllSenseCounts(lexelt)
        hash_featureCounts = coOccurenceFeaturesGenerataion(lexelt)
        for key in hash_senseCounts:
            hash_smoothed = addUnktoFeatures(hash_featureCounts[key])
            for feature in hash_smoothed:
                hash_smoothed[feature] = hash_smoothed[feature] / hash_senseCounts[key]
            hash_smoothed['UNK'] = 0.0000001
            hash_smoothed['PP'] = priorTable[key]
            hash_featureCounts[key] = hash_smoothed
        model_hash[lexelt.attrib.get('item')] = hash_featureCounts
    return model_hash
trainModel()

def findMax(lst):
    m = 0
    for a,b in lst:
        if b > m:
            m = b
            sense = a
    return sense

#Run training model on test data
def runTest():
    tree = ET.parse('test-data.xml')
    dictionary = tree.getroot()
    train_model = trainModel()
    #sense associated with its probability
    prob_lst = []
    text_file = open('output.txt', "w")
    for lexelt in dictionary:
        sense_dict = train_model[lexelt.attrib.get('item')]
        for instance in lexelt.iter('instance'):
            prob_lst = []
            instance_id = instance.get('id')
            for context in instance.iter('context'):
                window = extractFeatures(context)
            for s in sense_dict:
                prob = sense_dict[s]['PP']
                for w in window:
                    #if w is in the feature set
                    if w in sense_dict[s]:
                        prob = prob * sense_dict[s][w]
                    #w is not in the feature set
                    else:
                        prob = prob * sense_dict[s]['UNK']
                #print (prob)
                prob_lst.append((s, prob))
            best_sense = findMax(prob_lst) #used to be indented one tab over
            text_file.write(instance_id + ',' + best_sense + '\n')
    text_file.close()

runTest()