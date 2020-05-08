import json

words = {'nouns': [], 'verbs': []}

with open('nouns.txt') as f:
    for word in f:
        word = word.replace('\n', '')
        w = {'word': word, 'length': len(word)}
        words['nouns'].append(w)
    
words['nouns'] = sorted(words['nouns'], key=lambda k: k['length']) 
        
with open('verbs.txt') as f:
    for word in f:
        word = word.replace('\n', '')
        w = {'word': word, 'length': len(word)}
        words['verbs'].append(w)

words['verbs'] = sorted(words['verbs'], key=lambda k: k['length']) 
    
with open('words.json', 'w') as f:
    json.dump(words, f, indent=4)