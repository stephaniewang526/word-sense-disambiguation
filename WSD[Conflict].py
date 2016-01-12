#CS4740 Project 2 WSD
#JRL336, QW79
#10/8/2015

import xml.etree.ElementTree as ET

#Preprocessing of dictionary.xml and training-data.xml
tree = ET.parse('Dictionary.xml')
dictionary = tree.getroot()

for lexelt in dictionary:
    item = lexelt.attrib
    word_pos = item.get('item')
    for sense in dictionary.iter('sense'):
        sense_id = sense.get('id')
        synset = sense.get('synset')
        gloss = sense.get('gloss')


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

#
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
            print lst;
            #find position of <head> and </head>
            targetIndex = findIndexHead(lst)
           #endHead = lst.index('</head>')
            
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

for key in sense_dict:
    sennse_dict[key]['unk'] = 1

for lexelt in trainingTree:
    print coOccurenceFeaturesGenerataion(lexelt);

exit()
#God function            
# def trainModel():
#     for lexelt in trainingTree:
        