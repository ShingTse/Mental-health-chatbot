
import numpy as np
import nltk
import pickle
from neo4jrestclient.client import GraphDatabase
gdb = GraphDatabase("http://localhost:7474/db/data/",username="1234", password="1234")
#Password can be set in Neo4j client interface
from nltk.stem import PorterStemmer
from textblob import TextBlob
from nltk.parse.generate import generate, demo_grammar
from nltk import CFG
from nltk import word_tokenize, pos_tag, ne_chunk,conlltags2tree, tree2conlltags
from nltk.tree import Tree
from nltk.corpus import wordnet
from pycorenlp import StanfordCoreNLP
from nltk.sentiment.vader import SentimentIntensityAnalyzer
nlp = StanfordCoreNLP('http://localhost:9000')
sen=SentimentIntensityAnalyzer()

#Global variables for initialization
chatlog=[]
State=0
state=0
state1=0
state2=0
state3=1
state4=0
class FSM(object):
    def __init__(self):
        self.state = state
        self.state1=state1
        self.state2=state2
        self.state3=state3
        self.state4=state4
    def speak(self):
        respond=input("Your response:")
        chatlog.append(respond)
        return respond
    def response(self):
        return chatlog[-1]    
chatbot=FSM()
'Query from graph database and return node id and its properties for inference'
from neo4jrestclient import client
def query_id(x):
    q="MATCH (ee:Person) WHERE ee.who='{}' RETURN ee".format(x)
    result = gdb.query(q, returns=( lambda x:x['metadata']))
    return result[0][0]['id']
def query_who(x):
    q="MATCH (ee:Person) WHERE ee.name='{}' RETURN ee.who".format(x)
    result = gdb.query(q, returns=( lambda x:x))
    return result[0][0]
def Query_id(x):
    q="MATCH (ee:Person) WHERE ee.name='{}' RETURN ee".format(x)
    result = gdb.query(q, returns=( lambda x:x['metadata']))
    return result[0][0]['id']
def query_info_id():
    q="MATCH (ee:data) return ee"
    result = gdb.query(q, returns=( lambda x:x['metadata']))
    return result[0][0]['id']
def query_sentiment():
    q="MATCH (ee:data) return ee.sentiment"
    result=gdb.query(q,returns=( lambda x:x))
    return result[0][0]
def query_stored_id():
    c=[]
    q="MATCH (u:Person)-[r:Knows]->(c) where u.who='user' return c"
    result=gdb.query(q,returns=lambda x:x['metadata'])
    for i in range(len(result[:])):
        c.append(result[i][0]['id'])
    return c
def query_stored_name():
    c=[]
    for i in query_stored_id():
        c.append(gdb.nodes[i]['name'])
    return c
def query_stored_who():
    c=[]
    for i in query_stored_id():
        c.append(gdb.nodes[i]['who'])
    return c
#######################
def welcome_back():
    return "Welcome back {}! Nice to see you again. How're you doing today?".format(gdb.nodes[query_id('user')]['name'])
def store_feeling(respond,Type):
    try:
        query_id('user')
        get_event(respond)
        gdb.nodes[query_id('user')].set(Type,get_event(respond))
    except:
        a=gdb.nodes.create()
        a.labels.add("Person")
        a.set('who','user')
        get_event(respond)
        gdb.nodes[query_id('user')].set(Type,get_event(respond))
def retrieve_stored_feeling():
    return gdb.nodes[query_id('user')][Type]
def classify(respond):
    file = open('f1.obj','rb')
    cl = pickle.load(file)
    return cl.classify(respond)
def loop():
    while State==1:
        error1()
        clarify_topic(chatlog[-1])
        continue_topic()
        continue_topic1() 
        chatbot.speak()
def extract_name(sentence):
    try:
        query_id('user')
        c=[]
        text = (sentence)
        output = nlp.annotate(text, properties={
         'annotators': 'tokenize,ssplit,pos,depparse,parse',
         'outputFormat': 'json'
          })
        a=output['sentences'][0]['parse']
        tree=nltk.Tree.fromstring(a)
        for t in tree.subtrees():
            if t.label() == 'NNP':
                    b=t.leaves()
                    c.append(b[0])
                    print("Nice to meet you {} ! Could you tell me more about yourself or your family?".format(c[0]))
    except:
        c=[]
        text = (sentence)
        output = nlp.annotate(text, properties={
         'annotators': 'tokenize,ssplit,pos,depparse,parse',
         'outputFormat': 'json'
          })
        a=output['sentences'][0]['parse']
        tree=nltk.Tree.fromstring(a)
        for t in tree.subtrees():
            if t.label() == 'NNP':
                    chatbot.state1='ok'
                    b=t.leaves()
                    c.append(b[0])
                    a=gdb.nodes.create()
                    a.set('name',c[0])
                    a.labels.add("Person")
                    a.set('who','user')
                    print("Nice to meet you {} ! Could you tell me more about yourself or your family?".format(c[0]))
def get_name(respond):
    d=[]
    j=[]
    n=gdb.nodes.create()
    n.labels.add("Person")
    gdb.nodes[query_id('user')].relationships.create("Knows", n)
    text = (
    respond)
    output = nlp.annotate(text, properties={
        'annotators': 'tokenize,ssplit,pos,depparse,parse',
       'outputFormat': 'json'
    })
    a=output['sentences'][0]['parse']
    tree=nltk.Tree.fromstring(a)
    for t in tree.subtrees():
        if t.label()=='NN':
                c=t.leaves()
                d.append(c[0])
                n.set('who',d[0])
        if t.label() == 'NNP':
                b=t.leaves()
                j.append(b)
                n.set('name',j[0])  
def Get_name(respond):
    text = (
    respond)
    output = nlp.annotate(text, properties={
        'annotators': 'tokenize,ssplit,pos,depparse,parse',
       'outputFormat': 'json'
    })
    a=output['sentences'][0]['parse']
    tree=nltk.Tree.fromstring(a)
    for t in tree.subtrees():
        if t.label() == 'NNP':
                b=t.leaves()
    return b
def get_who(respond):
    j=[]
    text = (
    respond)
    output = nlp.annotate(text, properties={
        'annotators': 'tokenize,ssplit,pos,depparse,parse',
       'outputFormat': 'json'
    })
    a=output['sentences'][0]['parse']
    tree=nltk.Tree.fromstring(a)
    for t in tree.subtrees():
        if t.label() == 'NN':
                b=t.leaves()
                j.append(b)
    return j[0]
def location(respond):
    if chatbot.state2=='pass2':
        pass
    else:
        c=[]
        a=[]
        parsed=ne_chunk(pos_tag(word_tokenize(respond)))
        for t in parsed.subtrees():
            if t.label()=='GPE':
                for i in range(len(t)):
                    c.append(t[i][0])
                    d=' '.join(c)
                    a.append(d)
        try: 
            try:
                for b in gdb.nodes[query_id('user')]['life_event']:
                    if a[0] in b:
                        chatbot.state2='pass2'
                        print("I remembered that you used to live in {}.".format(a[0]))
                        chatbot.speak()
                        print("I see. Can you tell me anything about this place?")
                        chatbot.speak()
                        if sentiment(chatlog[-1])=='negative':
                            print("I see. Please don't feel obliged. Anyway Let's get back to what we were talking about.")
                            print("Can you tell me your other memories or the one you previously mentioned.")
                            chatbot.speak()
                        else:
                            print("That's good to know. I'm glad to know that. I hope you could have good memories with {}.".format(a[0]))
                            print("Do you also have any special memory about this place?")
                            chatbot.speak()
                        chatbot.state4==2
            except:
                for b in gdb.nodes[query_id('user')]['memories']:
                    if a[0] in b:
                        chatbot.state2='pass2'
                        print("I recalled that you mentioned {} when you told me about your memorable events.".format(a[0]))
                        chatbot.speak()
                        print("Can you tell me more indepth about it?")
                        chatbot.speak()
                        chatbot.state4==2
        except:
            chatbot.state2='pass2'
            print("What do you think about {}, do you like this place?".format(a[0]))
            chatbot.speak()
            if sentiment(chatlog[-1])=='positive':
                print("That's good to know. What makes you like about this place?")
                chatbot.speak()
                print("I'm glad it reminds you about your good memories. It's always good to refresh our memories")
                print("Can you also tell me your other memories?")
                chatbot.speak()
                chatbot.state4==2
            if sentiment(chatlog[-1])=='negative':
                print("What makes you dislike this place?")
                chatbot.speak()
                extract_memories(chatlog[-1])
                print("I see your point. I'm sorry if this is something you don't want to talk about. Let's get back to we previously talked about.")
                chatbot.speak()
                chatbot.state4==2
def extract_work(respond):
    c=[]
    text = (
       respond)
    output = nlp.annotate(text, properties={
      'annotators': 'tokenize,ssplit,pos,depparse,parse',
       'outputFormat': 'json'
        })
    a=output['sentences'][0]['parse']
    tree=nltk.Tree.fromstring(a)
    for t in tree.subtrees():
        if t.label() == 'NN':
            b=t.leaves()
            c.append(b[0])
    try : 
        query_id(c[0])
        n = gdb.nodes[query_id(c[0])]
        n.set('work',get_VP(respond))
    except:
        n=gdb.nodes.create()
        gdb.nodes[query_id('user')].relationships.create("Knows", n)
        n.labels.add("Person")
        n.set('who',c[0])
        n.set('work',get_VP(respond))
        print("Thanks. Can you tell me his/her name?".format(c[0]))
        chatbot.speak()
        text = (
        chatlog[-1])
        output = nlp.annotate(text, properties={
        'annotators': 'tokenize,ssplit,pos,depparse,parse',
       'outputFormat': 'json'
        })
        a=output['sentences'][0]['parse']
        tree=nltk.Tree.fromstring(a)
        for t in tree.subtrees():
            if t.label() == 'NP':
                b=t.leaves()
        n.set('name',b[-1])
        print("Can you tell me more about him/her?")
def record_states_passed(i,x):
    n=gdb.nodes[query_info_id()]
    try:
        n['rec_previous_states{}']
        a=[n['rec_previous_states']]
        a.append(x)
        n.set('rec_previous_states',a)
    except:
        n.set('rec_previous_states',a)
def set_prev_states(x):
    n=gdb.nodes[query_info_id()]
    n.set('previous_states',n['rec_previous_states'])
def extract_life_event(respond):
    c=[]
    text = (
       respond)
    output = nlp.annotate(text, properties={
      'annotators': 'tokenize,ssplit,pos,depparse,parse',
       'outputFormat': 'json'
        })
    a=output['sentences'][0]['parse']
    tree=nltk.Tree.fromstring(a)
    for t in tree.subtrees():
        if t.label() == 'NN':
            b=t.leaves()
            c.append(b[0])
    try : 
        query_id(c[0])
        n = gdb.nodes[query_id(c[0])]
        try:
            n['life_event']
            a=[n['life_event']]
            a.append(get_event(respond))
            n.set('life_event',a)
        except:
            n.set('life_event',[get_event(respond)])
    except:
        n=gdb.nodes.create()
        gdb.nodes[query_id('user')].relationships.create("Knows", n)
        n.labels.add("Person")
        n.set('who',c[0])
        n.set('life_event',get_event(respond))
        print("Thanks. Can you tell me his/her name?".format(c[0]))
        chatbot.speak()
        text = (
        chatlog[-1])
        output = nlp.annotate(text, properties={
        'annotators': 'tokenize,ssplit,pos,depparse,parse',
       'outputFormat': 'json'
        })
        a=output['sentences'][0]['parse']
        tree=nltk.Tree.fromstring(a)
        for t in tree.subtrees():
            if t.label() == 'NP':
                b=t.leaves()
        n.set('name',b[-1])
        print("Can you tell me more about him/her?")
def extract_self_life_event(respond):
    n=gdb.nodes[query_id('user')]
    try:
        n['life_event']
        a=[n['life_event']]
        a.append(get_event(respond))
        n.set('life_event',a)
    except:
        n.set('life_event',[get_event(respond)])
def extract_memories(respond):
    n=gdb.nodes[query_id('user')]
    try:
        n['memories']
        a=n['memories']
        a.append(get_event(respond))
        n.set('memories',a)
    except:
        n.set('memories',[get_event(respond)])
def extract_hobbies(respond):
    ps=PorterStemmer()
    d=[]
    j=[]
    text = (
    respond)
    output = nlp.annotate(text, properties={
    'annotators': 'tokenize,ssplit,pos,depparse,parse',
    'outputFormat': 'json'
    })
    a=output['sentences'][0]['parse']
    tree=nltk.Tree.fromstring(a)
    for t in tree.subtrees():
        if t.label() == 'NN':
            b=t.leaves()
            b
        if t.label() == 'VP':
            bb=t.leaves()
            d.append(bb)
            e=ps.stem(d[-1][0])
            d[-1].remove(d[-1][0])
            d[-1].insert(0,e)
            c=','.join(d[-1]).replace(',',' ')  
            s=ps.stem(c)
            j.append(s)
    try : 
        n = gdb.nodes[query_id(b[0])]
        try:
            n['hobby']
            a=[n['hobby']]
            a.append(j[-1])
            n.set('hobby',a)
        except:
            n.set('hobby',[j[-1]])
            print("I believe that's interesting hobby! Could you tell me more about your {}".format(b[0]))
    except:
        n=gdb.nodes.create()
        n.labels.add("Person")
        gdb.nodes[query_id('user')].relationships.create("Knows", n)
        n.set('who',b[0])
        n.set('hobby',j[-1])
        print("Thanks and what's your {}'s name".format(b[0]))
        chatbot.speak()
        parsed=ne_chunk(pos_tag(word_tokenize(chatlog[-1])))
        for t in parsed.subtrees():
            if t.label()=='PERSON':
                 t[0][0]
        n.set('name',t[0][0])
        print("Can you tell me more about him/her?")  
def get_stemmed_VP(respond):
    d=[]
    ps=PorterStemmer()
    text = (
    respond)
    output = nlp.annotate(text, properties={
    'annotators': 'tokenize,ssplit,pos,depparse,parse',
    'outputFormat': 'json'
    })
    a=output['sentences'][0]['parse']
    tree=nltk.Tree.fromstring(a)
    for t in tree.subtrees():
         if t.label() == 'VP':
            bb=t.leaves()
            d.append(bb)
            e=ps.stem(d[-1][0])
            d[-1].remove(d[-1][0])
            d[-1].insert(0,e)
            c=','.join(d[-1]).replace(',',' ')  
            s=ps.stem(c)
            j.append(s)
    return j[-1]
def extract_persona(respond):
    c=[]
    text = (
       respond)
    output = nlp.annotate(text, properties={
      'annotators': 'tokenize,ssplit,pos,depparse,parse',
       'outputFormat': 'json'
        })
    a=output['sentences'][0]['parse']
    tree=nltk.Tree.fromstring(a)
    for t in tree.subtrees():
        if t.label() == 'NN':
            b=t.leaves()
            c.append(b[0])
    try : 
        query_id(c[0])
        n = gdb.nodes[query_id(c[0])]
        n.set('personality',get_VP(respond))
        print("Thanks. Could you tell me more about your {}?".format(c[0]))
    except:
        n=gdb.nodes.create()
        gdb.nodes[query_id('user')].relationships.create("Knows", n)
        n.labels.add("Person")
        n.set('who',c[0])
        n.set('personality',get_VP(respond))
        print("Thanks. Can you tell me his/her name?".format(c[0]))
        chatbot.speak()
        text = (
        chatlog[-1])
        output = nlp.annotate(text, properties={
        'annotators': 'tokenize,ssplit,pos,depparse,parse',
       'outputFormat': 'json'
        })
        a=output['sentences'][0]['parse']
        tree=nltk.Tree.fromstring(a)
        for t in tree.subtrees():
            if t.label() == 'NP':
                b=t.leaves()
        n.set('name',b[-1])
        print("Can you tell me more about him/her?")
def extract_self_hobbies(respond):
    ps=PorterStemmer()
    d=[]
    j=[]
    text = (
    respond)
    output = nlp.annotate(text, properties={
    'annotators': 'tokenize,ssplit,pos,depparse,parse',
    'outputFormat': 'json'
    })
    a=output['sentences'][0]['parse']
    tree=nltk.Tree.fromstring(a)
    for t in tree.subtrees():
        if t.label() == 'VP':
            bb=t.leaves()
            d.append(bb)
            e=ps.stem(d[-1][0])
            d[-1].remove(d[-1][0])
            d[-1].insert(0,e)
            c=','.join(d[-1]).replace(',',' ')  
            s=ps.stem(c)
            j.append(s)
    n=gdb.nodes[query_id('user')]
    try:
        n['hobby']
        a=[n['hobby']]
        a.append(j[-1])
        n.set('hobby',a)
    except:
        n.set('hobby',[j[-1]])
def extract_self_persona(respond):
        n = gdb.nodes[query_id('user')]
        try:
            n['personality']
            a=[n['personality']]
            a.append(get_VP(respond))
            n.set('personality',a)
        except:
            n.set('personality',get_VP(respond))
def error1():
            State=1
            print("Could you also tell me if you want to talk about yourself , family or other events?")
            chatbot.speak()
            if sen.polarity_scores(chatlog[-1])['neg'] > 0:
                confirm2()
            #for word in word_tokenize(chatlog[-1]):
                #if word in ["other","others"]:
                    #free_loop()
            else:
                confirm()
def confirm():
        for word in word_tokenize(chatlog[-1]):
                if word.lower() in ["family","son","daughter","wife","husband"]:
                    chatbot.state1='family'
                    print("Thanks. Please tell me more about your family members.")
                    chatbot.speak()
                if word.lower() in ["myself","me","mine"]:
                    chatbot.state1='yourself'
                    print("Thanks. Please tell me more about yourself.")
                    chatbot.speak()
                if word.lower() in["other","others"]:
                    chatbot.state1='other'
                    print("Thanks. Please tell me more about it.")
                    chatbot.speak()
def clarify_topic(respond):
        if chatbot.state1=='yourself':
                if classify(respond) == 'hobby':
                        gdb.nodes[query_info_id()].set('state','your hobbies')
                        chatbot.state2='self hobby'
                        extract_self_hobbies(respond)
                        print("What makes you develope this hobby?")
                        chatbot.speak()
                if classify(respond) == 'personality':
                        gdb.nodes[query_info_id()].set('state','your personality')
                        chatbot.state2='personality'
                        extract_self_persona(respond)
                        print("Thanks for letting me know , could you tell me more about yourself?")
                        chatbot.speak()
                if classify(respond) =='work':
                        gdb.nodes[query_info_id()].set('state','work')
                        chatbot.state2='event'
                if classify(respond) =='memory':
                        gdb.nodes[query_info_id()].set('state','memories')
                        chatbot.state2='event'
                        extract_memories(respond)
                if classify(respond)=='life event':
                        gdb.nodes[query_info_id()].set('state','life event')
                        chatbot.state2='event'
                        extract_self_life_event(respond)
                if classify(respond)=='marriage':
                        gdb.nodes[query_info_id()].set('state','marriage')
                        chatbot.state2='event'
                        try:
                            try:
                                query_id('wife')
                            except:
                                query_id('husband')
                        except:
                                print("Can you also tell me the name of your wife/husband?")
                                chatbot.speak()
                                get_name(chatlog[-1])
                                
        if chatbot.state1=='family':
                   # parsed=ne_chunk(pos_tag(word_tokenize(respond)))
                    #for t in parsed.subtrees():
                    #    if t.label()=='PERSON':
                    #        extract_family(respond)
                   # else:
                        if classify(respond) == 'hobby':
                            gdb.nodes[query_info_id()].set('state','family hobbies')
                            chatbot.state2='family hobby'
                            try:
                                extract_hobbies(respond)
                            except:
                                pass
                            chatbot.speak()
                        if classify(respond) == 'personality':
                            gdb.nodes[query_info_id()].set('state','family personality')
                            chatbot.state2='family personality'
                            try:
                                extract_persona(chatlog[-1])
                            except:
                                pass
                            chatbot.speak()
                        if classify(respond) =='work':
                            gdb.nodes[query_info_id()].set('state','work')
                            try:
                                extract_work(respond)
                            except:
                                pass
                            chatbot.state2='event'
        if chatbot.state1 == 'other':
                        chatbot.state2='other'
                        print("I'm not sure if I get you correctly but free feel to tell me more about it.")
                        chatbot.speak()
def continue_topic():
    if chatbot.state2=='family personality':
        state=1
        gdb.nodes[query_info_id()].set('state','family personality')
        if sentiment(chatlog[-1])=='negative':
            print("They might have some bad qualities but mutual understanding is the key to problem.")
            chatbot.speak()
            print("I see your point, maybe your family members are impatient sometimes.")
            chatbot.speak()
            print("I understand your viewpoint, are there any moments that make you particularly angry?")
            chatbot.speak()
            for word in word_tokenize(chatlog[-1]):
                if word.lower() in ["no","don't","dont","not"]:
                    print("That's a good thing. I'm glad you could control your temper. ")
                    chatbot.speak()
                    print("I believe everyone has their bad sides in personality and good sides as well.")
                    chatbot.speak()
                    print("I hope you are feeling better now. Could you tell me other things?")
                    state=0
                    gdb.nodes[query_info_id()].set('sentiment','bad')
            if state!=0:
                    print("I see, can you tell me what's that moment?")
                    chatbot.speak()
                    store_feeling(chatlog[-1],'previous_neg')
                    print("It's hard to deal with but try to communicate with them. You never know what they think without asking.")
                    chatbot.speak()
                    print("I hope you are feeling better now, do you wish to talk about other things?")
                    gdb.nodes[query_info_id()].set('sentiment','bad')
        else:
            print("It's always good to possess virtue or good habits.Im glad he/she is positive.")
            chatbot.speak()
            print("I see your point, are there any good moments that you have with your family?")
            chatbot.speak()
            if sentiment(chatlog[-1])=='negative':
                print("I bet everyone has memorable moments in life, you may just forgot about it.")
                chatbot.speak()
                print("I think it's also a good practise to try remembering things. Can you also tell me about your family?")
                gdb.nodes[query_info_id()].set('sentiment','good')
            else:
                print("Can you tell me what's that moment?")
                chatbot.speak()
                store_feeling(chatlog[-1],'family')
                store_feeling(chatlog[-1],'previous_pos')
                print("It's nice to know about it. Im glad you have such enjoyable moments.")
                chatbot.speak()
                print("I think this is what keep people to move on with their lifes.")
                chatbot.speak()
                print("I hope you are feeling better now, do you wish to talk about other things?")
                gdb.nodes[query_info_id()].set('sentiment','good')
    if chatbot.state2=='personality':
        gdb.nodes[query_info_id()].set('state','your personality')
        if sentiment1(chatlog[-1])=='negative':
            print("I see your point. I hope you could stay positive and try to change bad habits.")
            chatbot.speak()
            print("It always take time to change bad habits so try progress slowly.")
            chatbot.speak()
            print("Maybe you should also try to think positively and I hope that you could be happier.")
            chatbot.speak()
            print("I hope you are feeling better now, do you wish to talk about other things?")
            gdb.nodes[query_info_id()].set('sentiment','bad')
        else:
            print("That's good to know. It is good to maintain positive attitudes.")
            chatbot.speak()
            print("I hope that you could keep up with this good attitude.")
            chatbot.speak()
            print("Could you also tell me more about yourself or other things?")
            gdb.nodes[query_info_id()].set('sentiment','good')
    if chatbot.state2=='self hobby':
        gdb.nodes[query_info_id()].set('state','your hobbies')
        print("I think that should be a good habit and motivation for you.")
        chatbot.speak()
        if sentiment(chatlog[-1])=='negative':
            print("I see your point, it always takes time to change bad habits.")
            chatbot.speak()
            print("Maybe you could also try to develope new hobbies.")
            chatbot.speak()
            print("I hope you are feeling better, Do you wish to talk about other things?")
            gdb.nodes[query_info_id()].set('sentiment','bad')
        else:
            print("That's good to know. It's always nice to have something to focus on.")
            chatbot.speak()
            print("I also think developing hobbies do give us a healthier mind as well.")
            chatbot.speak()
            print("Could you also tell me more about yourself?")
            gdb.nodes[query_info_id()].set('sentiment','good')
    if chatbot.state2=='family hobby':
        gdb.nodes[query_info_id()].set('state','family hobbies')
        print("I think that's a fascinating hobby. What makes him/her develope this hobby?")
        chatbot.speak()
        print("That's a good motivation.")
        chatbot.speak()
        print("That's good to know, it's always nice to develope more hobbies.")
        print("Could you also tell me more about your other family members?")
    if chatbot.state2=='event':
        if classify(chatlog[-1])=='work':
            if chatbot.state1=='yourself':
                gdb.nodes[query_info_id()].set('state','work')
                gdb.nodes[query_id('user')].set('work',get_VP(chatlog[-1]))
                print("Did you like your job?")
                chatbot.speak()
            if chatbot.state1=='family':
                gdb.nodes[query_info_id()].set('state','work')
                extract_work()
                print("Did he/she like their job?") 
                chatbot.speak()
            if sen.polarity_scores(chatlog[-1])['neg']>0 or sen.polarity_scores(chatlog[-1])['neu']==1.0:
                    gdb.nodes[query_info_id()].set('sentiment','bad')
                    print("I guess no job is simple and there must be hardship involved in every job.")
                    chatbot.speak()
                    print("Have you retired? If not, maybe it's a good time to reconsider your job.")
                    chatbot.speak()
                    for word in word_tokenize(chatlog[-1]):
                        if word.lower() in ["no","dont","not"]:
                            print(random_positive_suggestion())
                            chatbot.speak()
                            print("I hope you are feeling better now, maybe you want to talk about other things?")
                    if chatbot.state1=='yourself':
                        gdb.nodes[query_id('user')].set('previous_neg','dislike your job')
                        gdb.nodes[query_id('user')].set('previous_work','dislike your job')
                        print("I get your feeling. Sometimes we might feelt fatiqued at things we used to. Maybe you want to talk about other things?")
                    if chatbot.state1 =='family':
                        gdb.nodes[query_id('user')].set('previous_neg','your family member dislike their job')
                        gdb.nodes[query_id('user')].set('previous_work','your family member dislike their job')
                        print("I get your feeling. Sometimes we might feelt fatiqued at things we used to. Maybe you want to talk about other things?")
            else:   
                gdb.nodes[query_info_id()].set('sentiment','good')
                if chatbot.state1=='yourself':
                    gdb.nodes[query_id('user')].set('previous_pos','like your job')
                    gdb.nodes[query_id('user')].set('previous_work','like your job')
                    print("I guess you enjoyed your job. What makes you like about this job?")
                    chatbot.speak()
                    print("I see your point, it's good to love your job or else it would be hard to work.")
                    chatbot.speak()
                    print("I'm glad you enjoyed your job. Can you also tell me about other things?")
                if chatbot.state1 =='family':
                    gdb.nodes[query_id('user')].set('previous_pos','your family member like their job')
                    gdb.nodes[query_id('user')].set('previous_work','your family member like their job')
                    print("I guess they enjoyed their job. What makes them like about this job?")
                    chatbot.speak()
                    print("I see your point, it's good to love your job or else it would be hard to work.")
                    chatbot.speak()
                    print("I think their job is quite interesting")
                    chatbot.speak()
                    print("Can you also tell me about other things?")
        if classify(chatlog[-1])=='marriage':
                gdb.nodes[query_info_id()].set('state','marriage')
                print("Thanks and what do you think about your marriage?")
                chatbot.speak()
                store_feeling(chatlog[-1],'marriage')
                if sentiment(chatlog[-1])=='negative':
                    gdb.nodes[query_info_id()].set('sentiment','bad')
                    print("What makes you think about this?")
                    chatbot.speak()
                    store_feeling(chatlog[-1],'previous_neg')
                    print("I see your point. I think communication is important in every marriage.")
                    chatbot.speak()
                    marriage_suggestion()
                    print("I hope you are feeling better now. Do you want to talk about other things?")
                if sentiment(chatlog[-1])=='positive':
                    gdb.nodes[query_info_id()].set('sentiment','good')
                    print("Im glad to know about that. Can you tell me more about your marriage?")
                    chatbot.speak()
                    store_feeling(chatlog[-1],'previous_pos')
                    print("I see. Having a positive relationship is crucial.")
                    chatbot.speak()
                    print("I hope you could keep up with the good relationship, can you tell me about your family or other things?")
        if classify(chatlog[-1])=='memory':
            state5=0
            gdb.nodes[query_info_id()].set('state','memory')
            print("I guess you are talking about your memory. Please tell me more about it.")
            chatbot.speak()
            if  sen.polarity_scores(chatlog[-1])['neg'] > 0: 
                    gdb.nodes[query_info_id()].set('sentiment','bad')
                    print("I understand your feeling. There are things that we can't control in life.")
                    chatbot.speak()
                    print("Maybe it is a bad memory, but I hope you could cherish the positive moments in life.")
                    chatbot.speak()
                    print("I hope you are feeling better now. Are there any particular moments that you feel bad about because of this ?")
                    chatbot.speak()
                    for word in word_tokenize(chatlog[-1]): 
                        if word.lower() in ["yes","right","yea","certainly","yup"]:
                                print("Please tell me about it.")
                                chatbot.speak()
                                store_feeling(chatlog[-1],'previous_neg')
                                print("I get your feeling. I think there are things that we cant control sometimes.")
                                chatbot.speak()
                                print("I hope you are getting better now. Do you wish to talk about other things?")
                                state5=1
                        if word.lower() in ["no","not","don't","dont"]:
                            print("There's always things we cant control and I hope you could stay positive.")
                            chatbot.speak()
                            print("I hope you are getting better now. Do you wish to talk about other things?")   
                            state5=1
                    if state5 !=1:
                        print("Please tell me about it.")
                        chatbot.speak()
                        store_feeling(chatlog[-1],'previous_neg')
                        print("I get your feeling. I think there are things that we cant control sometimes.")
                        chatbot.speak()
                        print("I hope you are getting better now. Do you wish to talk about other things?")
            else:
                print("Thanks for letting me know. Is this a good memory to you?")
                chatbot.speak()
                if  sen.polarity_scores(chatlog[-1])['neg'] > 0:
                    gdb.nodes[query_info_id()].set('sentiment','bad')
                    print("I see your point. I hope you didn't feel too bad but these memories do keep us stronger.")
                    chatbot.speak()
                    r=["I think you might develope some hobbies just to distract yourself from these feelings.",
                    "I believe that sometimes we can't control things despite our effort.",
                    "One of the solution is to forget. We should always move forward.",
                    "Since we couldn't control it, it might be better for us to look forward."]
                    print(np.random.choice(r))
                    chatbot.speak()
                    print("I hope this would help and do you want to chat about other things?")
                else:    
                    gdb.nodes[query_info_id()].set('sentiment','good')
                    print("I'm glad to hear that. Please tell me more about it.")
                    chatbot.speak()
                    store_feeling(chatlog[-1],'previous_pos')
                    print("I see your point, it is always important to be optimistic .")
                    chatbot.speak()
                    print("I'm glad that you had such experiences to motivate you. Do you also wish to talk about other things?")
        if classify(chatlog[-1])=='life event':
            if chatbot.state1=='family':
                gdb.nodes[query_info_id()].set('state','family history')
                extract_life_event(chatlog[-1])
                print("Thanks for letting me know. It's good to remind about events that we might have forgotten about.")
                chatbot.speak()
                print("I hope these events could keep you stay positive as well.")
                chatbot.speak()
                print("Can you also tell me about yourself or family?")
            if chatbot.state1=='yourself':
                gdb.nodes[query_info_id()].set('state','your history')
                print("Thanks for letting me know. It's good to remind about events that we might have forgotten about.")
                chatbot.speak()
                print("I also believe that these memories could remind who we are and what we cherished for.")
                chatbot.speak()
                print("Do you want to talk about other things?")
def continue_topic1():
    if chatbot.state1=='other':
        gdb.nodes[query_info_id()].set('state','other')
        if  sen.polarity_scores(chatlog[-1])['neg'] > 0: 
            print("Is this something that you feel bad about?")
            chatbot.speak()
            for word in word_tokenize(chatlog[-1]): 
                if word.lower() in ["yes","right","yea","certainly","yup"]:
                    store_feeling(chatlog[-2],'previous')
                    store_feeling(chatlog[-2],'previous_neg')
                    print("I get you. I think there are things that we cant control sometimes.")
                    chatbot.speak()
                    print(random_positive_motivation())
                    chatbot.speak()
                    print("I'm sorry if I can't give you good advice on this problem.")
                    print("Are there any other things you want to talk about?")
                if word.lower() in ["no","not"]:
                    print("Can you tell me more about it?")
                    chatbot.speak()
                    print("I see. There's always things we cant control and I'm glad you are fine with it.")
                    chatbot.speak()
                    print("I hope you get better now. Are there other things that you want to talk about?")
        else:
            print("I see your point. I think that's interesting to know.")
            store_feeling(chatlog[-1],'previous')
            store_feeling(chatlog[-1],'previous_pos')
            chatbot.speak()
            print(random_positive_motivation())
            chatbot.speak()
            print("I'm sorry if I can't give you good advice on this problem.")
            print("Are there any other things you want to talk about?")
def confirm2():
        sen=SentimentIntensityAnalyzer()
        print("Sorry if I have misunderstood, do you want to take some rest or continue?")
        chatbot.speak()
        if sentiment(chatlog[-1])=='negative':
            State=0
            print("I see, please take a rest and see you next time.")
        for word in word_tokenize(chatlog[-1]):
            if word.lower() in ["rest","stop","sleep","quit","exit","dont","don't"]:
                print("I see, please take a rest and see you next time.")
                State=0
        if State!=0:
            print("I see, could you also tell me if you are talking about family, yourself or other things?")
            chatbot.speak()
            confirm()
def greeting():
    return "Welcome and nice to meet you , how are you doing today? "
def starting_respond(sentence):
    RESPONSES=["What makes you feel bad?","Why are you unhappy?"]
    if sentiment1(sentence)=='negative':
            chatbot.state='bad'
            return np.random.choice(RESPONSES)
    if sentiment1(sentence)=='positive':
            chatbot.state='good'
            return "Im glad you are feeling fine, Can i have your name?"
def bad_respond(sentence):
    DEMENTIA=("memory","dementia","forget","mindless","remember","remembering")
    FAMILY=("family","son","daughter","wife","husband")
    DONT=("don't","dont","know","myself","self","bad","personal","depressed","no")
    SICK=("sick","illness","unwell","fever")
    for word in word_tokenize(sentence):
        if word.lower() in DEMENTIA:
            chatbot.state1='dementia'
            return "How's memory lost affecting you?"
        if word.lower() in FAMILY:
            chatbot.state1='family'
            return "How does your family treat you?"
        if word.lower() in DONT:
            chatbot.state1='self'
            return "Bad emotions do hit us unexpectedly. What do you think about yourself? "
        if word.lower() in SICK:
            chatbot.state1='sick'
            return "Are feeling unwell? Please tell me more about it."
    else:
        chatbot.state1='other'
        return "Bad emotions do hit us unexpectedly. But please tell me more about it"
def catagories_bad1(sentence):
    DAILY=("daily","lifes","shopping","shop","wake","waking","life","live","lives")
    RELATIONSHIP=("relationship","family","friends","friend","son","daughter","wife","husband")
    COMMUNICATION=("communicate","communication","talk","speak","chat","negotiate")
    if chatbot.state1=='sick':
        print("Try to have some rest for now but if you're are feelnig very bad. Please see a doctor immediately.")
        chatbot.speak()
        print("I hope you will get better soon. Can i get your name?")
    if chatbot.state1 =='self':
        print("What makes you think about this?")
        chatbot.speak()
        if sentiment1(chatlog[-1])=='negative':
            print("I understand that others' impression might affect us but What important is who we truly are.")
        else:
            print("Im glad that you have good impression on yourself.")
        chatbot.speak()        
        print("I also think it is important to know that the only thing we could control is to improve ourselves.")
        chatbot.speak()
        try:
            query_id('user')
            print("Are you feeling better?")
        except:
            print("I hope you are feeling better now. Could you tell me your name?")
    if chatbot.state1 =='dementia':
        print(suggestion_remem())
        chatbot.speak()
        print("I think it takes effort to handle memory problem but don't force yourself too hard.")
        chatbot.speak()
        print("Do you also have anything that you want me to remind you about? Please feel free to let me know.")
        chatbot.speak()
        if sen.polarity_scores(chatlog[-1])['neg'] > 0:
            try:
                query_id('user')
                print("Don't worry about it. ")
            except:
                print("I see. Don't worry about it. Could you tell me your name by the way.")
        if sen.polarity_scores(chatlog[-1])['pos'] > 0:
            store_feeling(chatlog[-1],'remember')
            try:
                query_id('user')
                print("I hope this is helpful for you. ")
            except:
                print("I hope this is helpful for you. Could you also tell me your name?")
    if chatbot.state1 =='family':
            print("What makes you think about this?")
            chatbot.speak()
            print("I'm sorry to hear about that. If violence is involved please inform people you know. ")
            chatbot.speak()
            bad=["Maybe there are some misunderstanding. Try to communicate with them.",
            "That might be something you can't control, dont blame yourself too much.",
            "Everyone has emotional times, try not to overthink about it."
            ,"I believe seeking mutual understanding is the key to solving problem."]
            print(np.random.choice(bad))
            chatbot.speak()
            try:
                query_id('user')
                print("I hope you are feeling better now.")
            except:
                print("I hope you are feeling better now. Could you first tell me your name?") 
        #if sentiment1(sentence) == 'positive':
        #    print("Im glad to hear that.")
        #    print("Could you tell me more about your family?")
    if chatbot.state1=='other':      
        for word in word_tokenize(sentence):
            if word.lower() in DAILY:
                chatbot.state2='daily'
            if word.lower() in COMMUNICATION:
                chatbot.state2='comm'
            else:
                chatbot.state2='other'
        if chatbot.state2=='daily':
            print(random_positive_suggestion())
            try:
                query_id('user')
                print("I hope you are feeling better now. Please free feel to talk about anything.")
            except:
                print("I hope you are feeling better now. Could you tell me your name?")
        if chatbot.state2=='comm':
            print(suggestestion_comm())
            try:
                query_id('user')
                print("I hope you are feeling better now. Please free feel to talk about anything.")
            except:
                print("I hope you are feeling better now. Could you tell me your name?")
        if chatbot.state2=='other':
            print("What makes you think about that?")
            chatbot.speak()
            print(random_positive_motivation())
            chatbot.speak()
            try:
                query_id('user')
                print("I hope you are feeling better now. Please free feel to talk about anything.")
            except:
                print("I hope you are feeling better now. Could you tell me your name?")

#Loop responses
def marriage_suggestion():
    marriage=["There are always problems in marriage that makes it valuable.","Communication is the key. Try talking to your\
    partner slowly.","Patience and understanding are important in marriage.",
    "I believe your partner still cares about you, everyone has their irrational moment.",
    "I think that argument is inevitable in marriage and that makes relationship improve."]
    return np.random.choice(marriage)
def random_positive_motivation():
    positive=["I found it helpful when we think in another perspective.",
              "Stay positive and be motivated",
              "I know it's hard but we could ignore negative feelings by ourselves as there are produced by our mind",
             "It always take time to adapt to new changes and difficulties , stay calm and be motivated."]
    return np.random.choice(positive)
def random_positive_suggestion():
    pos=["Try to make little progress every day. Everything's achievable by breaking down into smaller tasks."
         ,"Take a deep breath and workout slowly.","I believe staying positive could help you cope with difficulties."
        ,"It always take time to adapt to new changes and difficulties , stay calm and be motivated.",]
    return np.random.choice(pos)
def suggestestion_comm():
    comm=["Take a breath and talk slowly.It could help expressing yourself.","Take time to speak words clearly. That could help\
    expressing feelings.","I think you could practise speaking slowly. There's nothing shameful about it!"]
    return np.random.choice(comm)
def suggestion_remem():
    remem=["I think you could record things in notebook ,that would certain helps!","I think its  great to read the time constantly\
    to keep track on current time.","Do try to go for a walk whenever there's stress, fresh air always keep our mind refreshed!"]
    return np.random.choice(remem)
def get_VP(sentence):
    d=[]
    text = (
    sentence)
    output = nlp.annotate(text, properties={
    'annotators': 'tokenize,ssplit,pos,depparse,parse',
    'outputFormat': 'json'
    })
    a=output['sentences'][0]['parse']
    tree=nltk.Tree.fromstring(a)
    for t in tree.subtrees():
        if t.label() == 'VP':
            b=t.leaves()
            d.append(b)
            d[0]
            for word in d[0]:
                if word=='me':
                    d[0][d[0].index('me')]='you'
                if word=='our':
                    d[0][d[0].index('our')]='your'
                if word=='my':
                    d[0][d[0].index('my')]='your'
                if word=='I':
                    d[0][d[0].index('I')]='you'
                if word=='myself':
                    d[0][d[0].index('myself')]='yourself'
                if word=='am':
                    d[0][d[0].index('am')]='are'
            c=','.join(d[0]).replace(',',' ')  
            return c
def get_event(sentence):
    d=[]
    text = (
    sentence)
    output = nlp.annotate(text, properties={
    'annotators': 'tokenize,ssplit,pos,depparse,parse',
    'outputFormat': 'json'
    })
    a=output['sentences'][0]['parse']
    tree=nltk.Tree.fromstring(a)
    for t in tree.subtrees():
        if t.label() == 'S':
            b=t.leaves()
            d.append(b)
            d[0]
            for word in d[0]:
                if word=='me':
                    d[0][d[0].index('me')]='you'
                if word=='our':
                    d[0][d[0].index('our')]='your'
                if word=='my':
                    d[0][d[0].index('my')]='your'
                if word=='My':
                    d[0][d[0].index('My')]='Your'
                if word=='I':
                    d[0][d[0].index('I')]='You'
                if word=='myself':
                    d[0][d[0].index('myself')]='yourself'
                if word=='We':
                    d[0][d[0].index('We')]='You'
                if word=='we':
                    d[0][d[0].index('we')]='you'
                if word=='Im':
                    d[0][d[0].index('Im')]='you'
                if word=='am':
                    d[0][d[0].index('am')]='are'
            c=','.join(d[0]).replace(',',' ')  
            return c
def rephrase(sentence):
    sen="What makes you think they {}?".format(get_VP(sentence))
    return sen
def change_topic():
    return "I hope you are feeling better now. Can you talk about yourself or family?"
def sentiment(respond):
    sen = SentimentIntensityAnalyzer()
    if  sen.polarity_scores(respond)['neg'] > 0:
        return 'negative'
    if  sen.polarity_scores(respond)['pos'] >0:
        return 'positive'
def sentiment1(respond):
    sen = SentimentIntensityAnalyzer()
    if  sen.polarity_scores(respond)['neg'] > 0:
        return 'negative'
    if  sen.polarity_scores(respond)['pos'] >0.5:
        return 'positive'
    if  sen.polarity_scores(respond)['pos'] <0.5:
        return 'negative'
def error():
    while chatbot.state1 !='ok':
        print('Sorry I didnt get you. Could you repeat again?')
        chatbot.speak()
        parsed=ne_chunk(pos_tag(word_tokenize(chatlog[-1])))
        for t in parsed.subtrees():
            if t.label()=='PERSON':
                chatbot.state1='ok'
        if chatbot.state1 =='ok':
             extract_name(chatlog[-1])
def Error():
    if chatbot.state3==1:
        text = (
        chatlog[-1])
        output = nlp.annotate(text, properties={
        'annotators': 'tokenize,ssplit,pos,depparse,parse',
        'outputFormat': 'json'
        })
        a=output['sentences'][0]['parse']
        tree=nltk.Tree.fromstring(a)
        for t in tree.subtrees():
            if t.label() == 'NNP':
                chatbot.state3 ='ok'
            if t.label() =='NN':
                chatbot.state3 ='ok'
    while chatbot.state3 !='ok':
        print('Sorry I didnt get you. Could you repeat again?')
        chatbot.speak()
        text = (
        chatlog[-1])
        output = nlp.annotate(text, properties={
        'annotators': 'tokenize,ssplit,pos,depparse,parse',
        'outputFormat': 'json'
        })
        a=output['sentences'][0]['parse']
        tree=nltk.Tree.fromstring(a)
        for t in tree.subtrees():
            if t.label() == 'NNP':
                chatbot.state3 ='ok'
            if t.label() =='NN':
                chatbot.state3 ='ok'
        if chatbot.state3 =='ok':
             pass
    
def loop_bad():
    print("Would you mind telling me more?")
    chatbot.speak()
    print("Sometimes we could not control everything. Stay positive.")
    chatbot.speak()
    print(random_positive_suggestion())
    sentiment1(chatlog[-1])
def loop_bad1():
    loop_bad()
    good_loop_bad()
def good_loop_bad():
    print("Im glad you are feeling better now")
    if sentiment1(chatlog[-1]) == 'positive':
        chatbot.speak()
        sentiment1(chatlog[-1])
        random_positive_motivation()
        print("Do you want to talk about yourself?")
        chatbot.speak()
        for word in word_tokenize(chatlog[-1]):
            if word.lower() in ["yes","would","like"]:
                 state='next'
    if sentiment1(chatlog[-1]) == 'negative':
        return loop_bad1()
    if state=='next':
        print("next conversation")

#Second+ time conversation:
def generate_persona(sentence):
    if chatbot.state2=='pass':
        pass
    else:
        c=[]
        text = (
        sentence)
        output = nlp.annotate(text, properties={
        'annotators': 'tokenize,ssplit,pos,depparse,parse',
        'outputFormat': 'json'
        })
        a=output['sentences'][0]['parse']
        tree=nltk.Tree.fromstring(a)
        for t in tree.subtrees():
            if t.label() == 'NNP':
                c.append(t[0])
            if t.label() =='NN':
                c.append(t[0])
        try:
            if c[0] in query_stored_name():
                chatbot.state2=='pass'
                x=gdb.nodes[query_id(c[0])]['personality']
                b=' '.join([c[0],x[-1]])
            if c[0] in query_stored_who():
                chatbot.state2=='pass'
                x=gdb.nodes[query_id(c[0])]['personality']
                b=' '.join(['your',c[0],x[-1]])
            if sen.polarity_scores(b)['neg']>0:
                print("I recall you've mentioned {}, I guess everyone has their good/bad sides.".format(b))
                chatbot.speak()
            if sen.polarity_scores(b)['pos']>0:
                if sen.polarity_scores(sentence)['neg']>0:
                    print("I heard {}. Maybe there are some misunderstanding".format(b))
                    chatbot.speak()
                else:
                    print("I think {} and hope he/she could keep going on with the virtue.".format(b))
                    chatbot.speak
        except:
            pass
def generate_hobbies(sentence):
    if chatbot.state2=='pass':
        pass
    else:
        c=[]
        text = (
        sentence)
        output = nlp.annotate(text, properties={
        'annotators': 'tokenize,ssplit,pos,depparse,parse',
        'outputFormat': 'json'
        })
        a=output['sentences'][0]['parse']
        tree=nltk.Tree.fromstring(a)
        for t in tree.subtrees():
            if t.label() == 'NNP':
                c.append(t[0])
            if t.label() =='NN':
                c.append(t[0])
        try:
            if c[0] in query_stored_name():
                chatbot.state2=='pass'
                n=gdb.nodes[Query_id(c[0])]['hobby']
                n[-1]
                b=' '.join([c[0],'loves to',n[-1]])
            if c[0] in query_stored_who():
                chatbot.state2=='pass'
                n=gdb.nodes[Query_id(c[0])]['hobby']
                x=np.random.choice(n[-1])
                b=' '.join(['your',c[0],'loves to',x])
                print("I also remembered that {}".format(b))
        except:
            pass
def generate_memories(sentence):
    if chatbot.state2=='pass1':
        pass
    else:
        try:
            gdb.nodes[query_id('user')]['memories']
            j=[]
            c=[]
            text = (
            sentence)
            output = nlp.annotate(text, properties={
            'annotators': 'tokenize,ssplit,pos,depparse,parse',
            'outputFormat': 'json'
            })
            a=output['sentences'][0]['parse']
            tree=nltk.Tree.fromstring(a)
            for t in tree.subtrees():
                if t.label() == 'NNP':
                    c.append(t[0])
                if t.label() =='NN':
                    c.append(t[0])
            for x in [gdb.nodes[query_id('user')]['memories']]:
                if c[0] in x:
                    chatbot.state2='pass1'
                    j.append(x)
                try:
                    gdb.nodes[query_id(c[0])]['name']
                    if gdb.nodes[query_id(c[0])]['name'] in x:
                        chatbot.state2='pass1'
                        j.append(x)
                except:
                    if query_who(c[0]) in x:
                        chatbot.state2='pass1'
                        j.append(x)      
            if sentiment(j[0])=='negative':
                print(' '.join(["You once mentioned {}.".format(j[0]),"Does this created conflict between you and {}".format(c[0])]))
                chatbot.speak()
            else:
                print("I remembered that you also said that {}.".format(j[0]))
                chatbot.speak()
        except:
            pass
def random_hobbies():
    try:
        z=np.random.choice(query_stored_id())
        gdb.nodes[z]['hobby']
        b=' '.join([gdb.nodes[z]['name'],'also loves to',gdb.nodes[z]['hobby']])
        print("I remembered that {}. What do you think about his/her hobby?".format(b))
    except:
        print("What do you think about the hobbies of your other family members?")
def random_persona():
    try:    
        z=np.random.choice(query_stored_id())
        b=' '.join([gdb.nodes[z]['name'],gdb.nodes[z]['personality']])
        return b
    except:
        pass
def generate_family():
    try:
        gdb.nodes[query_id('user')]['family']
        n=gdb.nodes[query_id('user')]['family']
        if sentiment(n)=='negative':
            print("I remembered you mentioned {} a while ago. What do you think about it".format(n[-1]))
        if sentiment(n)=='positive':
            print("I remembered you mentioned {} a while ago.".format(n[-1]))
    except:
        print("Can you tell me more about your family personalities?")
def generate_marriage(sentence):
    if chatbot.state2=='pass':
        pass
    else:
        s=0
        c=[]
        text = (
        sentence)
        output = nlp.annotate(text, properties={
        'annotators': 'tokenize,ssplit,pos,depparse,parse',
        'outputFormat': 'json'
        })
        a=output['sentences'][0]['parse']
        tree=nltk.Tree.fromstring(a)
        for t in tree.subtrees():
            if t.label() == 'NNP':
                c.append(t[0])
            if t.label() =='NN':
                c.append(t[0])
        try:        
            if c[0] in query_stored_name():
                try:
                    gdb.nodes[Query_id(c[0])]['personality'] 
                    chatbot.state2='pass'
                    b=' '.join([gdb.nodes[Query_id(c[0])]['name'],gdb.nodes[Query_id(c[0])]['personality']])
                    s=1
                except:
                    pass
                
            if c[0] in ['wife','husband']:
                try:
                    gdb.nodes[query_id(c[0])]['personality']
                    chatbot.state2='pass'
                    b=' '.join(['your',c[0],gdb.nodes[query_id(c[0])]['personality']])
                    s=1
                except:
                    pass
            if s==1:
                if sen.polarity_scores(b)['neg']>0:
                    chatbot.state2='pass'
                    print("I recall you've mentioned {}, I guess conflicts between couples are inevitable.".format(b))
                    chatbot.speak()
                if sen.polarity_scores(b)['pos']>0:
                    if sen.polarity_scores(sentence)['neg']>0:
                        chatbot.state2='pass'
                        print("I heard {}. Maybe there are some misunderstanding between you two?".format(b))
                        chatbot.speak()
                    else:
                        chatbot.state2='pass'
                        print("I heard {} and hope he/she gets along well with you.".format(b))
                        chatbot.speak()
        except:
            pass
def inference():
    if gdb.nodes[query_info_id()]['state']=='marriage':
        print("Can you tell me more about your marriage?")
        chatbot.speak()
        generate_marriage(chatlog[-1])
        n=gdb.nodes[query_id('user')]['marriage']
        if sentiment(n)=='negative':
            r=["I remembered that your viewpoint on marriage is pessimistic.",
               "I think I remembered that you felt bad about marriage.",
               "I recalled that you don't have much confidence in marriage."]
            print(np.random.choice(r))
            chatbot.speak()
            generate_marriage(chatlog[-1])
            print(marriage_suggestion())
            chatbot.speak()
            generate_marriage(chatlog[-1])
            print("I really think that you should talk with him/her. Communication is important in marriage.")
            chatbot.speak()
            generate_memories(chatlog[-1])
            print("I hope you are feeling better now. Please feel free to tell me anything.")
            chatbot.speak()
            error1()
            clarify_topic(chatlog[-1])
            continue_topic()
            continue_topic1()
        if sentiment(n)=='positive':
            r=["I remembered that your viewpoint on marriage is quite optimistic.",
               "I remembered you are quite confidence in marriage",
               "I recalled that you are quite optimistic about marriage."]
            print(np.random.choice(r))
            chatbot.speak()
            generate_marriage(chatlog[-1])
            print("I'm glad you are fine with your marriage. It's always hard to maintain relationship.")
            chatbot.speak()
            generate_marriage(chatlog[-1])
            print("How do you get along with your wife/husband?")
            chatbot.speak()
            if sentiment(chatlog[-1])=='negative':
                print("Are there incidents that lead to such thought?")
                chatbot.speak()
                generate_marriage(chatlog[-1])
                print("I see. Can you tell me more about him/her?")
                chatbot.speak()
                if classify(chatlog[-1])=='personality':
                    chatbot.state2='family personality'
                    extract_persona(chatlog[-1])
                    print("Thanks for letting me know. Can you tell me more about it.")
                    continue_topic()
                if classify(chatlog[-1])=='hobby':
                    chatbot.state2='family hobbies'
                    extract_hobbies(chatlog[-1])
                    print("Thanks for letting me know. Can you tell me more about it.")
                    continue_topic()
                for word in word_tokenize(chatlog[-1]):
                    if word in ["no","don't","dont","not"]:
                        chatbot.state1=='other'
                        continue_topic1()
                else:
                    chatbot.state2='event'
                    continue_topic()
                    
            else:
                print("That's good to know. Can you tell me more about him/her?")
                chatbot.speak()
                for word in word_tokenize(chatlog[-1]):
                    if word in ["no","don't","dont","not"]:
                        chatbot.state1=='other'
                        continue_topic1()
                if classify(chatlog[-1])=='personality':
                    chatbot.state2='family personality'
                    extract_persona(chatlog[-1])
                    continue_topic()
                if classify(chatlog[-1])=='hobby':
                    chatbot.state2='family hobby'
                    extract_hobbies(chatlog[-1])
                    continue_topic()
                else:
                    chatbot.state2='event'
                    continue_topic()
    if gdb.nodes[query_info_id()]['state']=='family hobbies':
        chatbot.state1='family'
        print("Can you tell me more about hobbies/habits of your family members?")
        chatbot.speak()
        generate_hobbies(chatlog[-1])
        if sentiment(chatlog[-1])=='negative':
                print("I see your point. Why is it so?")
                chatbot.speak()
                print("I think it always takes time to change bad habits. Maybe just give them some time.")
                generate_hobbies(chatlog[-1])
                chatbot.speak()
                generate_hobbies(chatlog[-1])
                random_hobbies()
                chatbot.speak()
                if sentiment(chatlog[-1])=='negative':
                    print("I guess everyone has their virtue and bad habbits. Maybe it's better if we try looking at the good side.")
                    chatbot.speak()
                    print("I hope you are feeling better. Please feel free to tell me anything.")
                    chatbot.speak()
                    if sentiment(chatlog[-1])=='negative':
                        print("Are you still feeling bad? Please tell me more about it.")
                        chatbot.speak()
                        print(bad_respond(chatlog[-1]))
                        chatbot.speak()
                        catagories_bad1(chatlog[-1])
                    else:
                        error2()
                        chatbot.speak()
                        clarify_topic(chatlog[-1])
                        continue_topic()
                        continue_topic1()
                if sentiment(chatlog[-1])=='positive':
                    print("That's good to know. I hope they could keep up with good habits.")
                    chatbot.speak()
                    print("I hope you are feeling better. Please feel free to talk about anything.")
                    if sentiment(chatlog[-1])=='negative':
                        print("Are you still feeling bad? Please tell me more.")
                        chatbot.speak()
                        print(bad_respond(chatlog[-1]))
                        chatbot.speak()
                        catagories_bad1(chatlog[-1])
                    else:
                        error2()
                        chatbot.speak()
                        clarify_topic(chatlog[-1]) 
        if sentiment(chatlog[-1])=='positive':
                print("I think that's great. These interests could help us stay both mentally and physically healthy.")
                chatbot.speak()
                generate_hobbies(chatlog[-1])
                print(random_positive_suggestion())
                chatbot.speak()
                generate_hobbies(chatlog[-1])
                random_hobbies()
                chatbot.speak()
                if sentiment(chatlog[-1])=='negative':
                    print("I guess everyone has their virtue and bad habbits. Maybe it's better if we try looking at the good side.")
                    chatbot.speak()
                    print("I hope you are feeling better. Please feel free to tell me anything.")
                    chatbot.speak()
                    if sentiment(chatlog[-1])=='negative':
                        print("Are you still feeling bad? Please tell me more about it.")
                        chatbot.speak()
                        print(bad_respond(chatlog[-1]))
                        chatbot.speak()
                        catagories_bad1(chatlog[-1])
                    else:
                        error1()
                        chatbot.speak()
                        clarify_topic(chatlog[-1])
                        continue_topic()
                        continue_topic1()
                if sentiment(chatlog[-1])=='positive':
                    print("That's good to know. I hope they could keep up with good habits.")
                    chatbot.speak()
                    print("I hope you are feeling better. Please feel free to talk about anything.")
                    chatbot.speak()
                    if sentiment(chatlog[-1])=='negative':
                        print("Are you still feeling bad? Please tell me more.")
                        chatbot.speak()
                        print(bad_respond(chatlog[-1]))
                        chatbot.speak()
                        catagories_bad1(chatlog[-1])
                    else:
                        error1()
                        chatbot.speak()
                        clarify_topic(chatlog[-1])
                        continue_topic()
                        continue_topic1()
    if gdb.nodes[query_info_id()]['state']=='your hobbies':
        print("Please tell me more about yourself.")
        chatbot.speak()
        print("I remembered that you like to {}. Do you also have other hobbies?".format(gdb.nodes[query_id('user')]['hobby'][-1]))
        chatbot.speak()
        if sentiment(chatlog[-1])=='negative':
            print("It's ok. Not all people have time to develop multiple hobbies.")
            print("Do you want to talk about other things?")
            error1()
            clarify_topic(chatlog[-1])
            continue_topic()
            continue_topic1()
        if sentiment(chatlog[-1])=='positive':
            print("What do you think about your habits/hobbies?")
            chatbot.speak()
            print("That's great. Can you tell me your other habits/hobbies?")
            chatbot.speak()
            extract_hobbies(chatlog[-1])
            chatbot.state1='yourself'
            chatbot.state2='self hobby'
            continue_topic()
    if gdb.nodes[query_info_id()]['state']=='your personality':
        chatbot.state1='yourself'
        S=1
        try:
            n=b.nodes[query_info_id()]['personality_info']
            S=0
            print("I remembered that you mentioned {}, do you think the same about yourself now?".format(n))
            chatbot.speak()
            if sentiment(chatlog[-1])=='negative':
                print("I see. Why you still think so?")
                chatbot.speak()
                print(random_positive_suggestion())
                chatbot.speak()
                print("I hope you could keep up with your progress and achieve yourself.")
                chatbot.speak()
                print("Do you still wish to talk about your personality?")
                chatbot.speak()
                for word in word_tokenize(chatlog[-1]):
                    if word.lower() in ["no","other","not","nope"] or sentiment(chatlog[-1])=='negative':
                        print("I see, please feel free to tell me other things.")
                        chatbot.speak()
                        error1()
                        clarify_topic(chatlog[-1])
                        continue_topic()
                        continue_topic1()
                if sentiment(chatlog[-1])=='positive':
                    S=1
            gdb.nodes[query_info_id()].delete('personality_info')
        except:
            pass
        if S==1:
            print("Maybe you can talk more about your personality.")
            chatbot.speak()
            if sentiment(chatlog[-1])=='negative':
                store_feeling(chatlog[-1],'previous_neg')
                r=["I see your point, what makes you think so?","What makes you lead to such thought?","Could you tell me why you think about that?"]
                print(np.random.choice(r))
                chatbot.speak()
                print("Can you tell me why you dislike about your personality?")
                chatbot.speak()
                store_feeling(chatlog[-1],'personality_info')
                store_feeling(chatlog[-1],'previous_neg')
                print("I see your point. I guess everyone have their own weaknesses in personalities. It's important for us to keep improving.")
                chatbot.speak()
                random_positive_suggestion()
                print("I hope you can try to appreiciate yourself more, It's often easy for people to neglect themselves.")
                print("Do you want to talk about the same topic or others?")
                error1()
                clarify_topic(chatlog[-1])
                continue_topic()
                continue_topic1()
            if sentiment(chatlog[-1])=='positive':
                print("I'm glad to hear that. Hope you can keep up with the good traits.")
                chatbot.speak()
                print("I guess it's important appreciate ourselves. Can you tell me anything that you appreciate yourself?")
                chatbot.speak()
                if sentiment(chatlog[-1])=='negative':
                    print("Don't worry about it. It's often easy for people to neglect themselves.")
                    chatbot.speak()
                    print("But I believe that you must have something worth appreciate for.")
                    chatbot.speak()
                    print("I hope you would try to appreciate yourself more. Please feel free to tell me anything.")
                if sentiment(chatlog[-1])=='positive':
                    store_feeling(chatlog[-1],'personality_info')
                    store_feeling(chatlog[-1],'previous_pos')
                    print("That's good. I'm happy that you understand well about yourself.It's often easy for us to neglect ourselves.")
                    chatbot.speak()
                    print("I hope you can keep up with this thought. Please feel free to tell me anything.")
                    error1()
                    clarify_topic(chatlog[-1])
                    continue_topic()
                    continue_topic1()
    if gdb.nodes[query_info_id()]['state']=='family personality': 
            chatbot.state1='family'
            generate_family()
            chatbot.speak()
            generate_persona(chatlog[-1])
            if sentiment(chatlog[-1])=='negative':
                r=["I see your point, what makes you think so?","What makes you lead to such thought?","Could you tell me why you think about that?"]
                print(np.random.choice(r))
                chatbot.speak()
                generate_persona(chatlog[-1])
                print("I think that every person has their own drawbacks but I hope they didn't affect you much.")
                chatbot.speak()
                generate_persona(chatlog[-1])
                print("Can you tell me the things that you dislike about your family members?")
                chatbot.speak()
                state=0
                for word in word_tokenize(chatlog[-1]):
                    if word.lower() in["no","refuse"]:
                        state=1
                        print("I see. Please feel free to tell me other things.")
                        error1()
                        clarify_topic(chatlog[-1])
                        continue_topic()
                        continue_topic1()
                if state==0:
                    store_feeling(chatlog[-1],'family')
                    store_feeling(chatlog[-1],'previous_neg')
                    r=["I believe understanding is important in a family.","I see your point. I guess you can try to communicate with them.",
                       "Maybe you could try approaching him/her. It helps when we try to be nice."]
                    print(np.random.choice(r))
                    chatbot.speak()
                    print(random_positive_suggestion())
                    print("I hope you could get along well with them, could you also tell me about your other family members?")
                    chatbot.speak()
                    if sentiment(chatlog[-1])=='negative':
                        print("I see. Please feel free to tell me anything.")
                        chatbot.speak()
                        error1()
                        chatbot.speak()
                        clarify_topic(chatlog[-1])
                    if sentiment(chatlog[-1])=='positive':
                        chatbot.state1=='family'
                        print("I see. Please tell me anything about them.")
                        chatbot.speak()
                        clarify_topic(chatlog[-1])
                        continue_topic()
                        continue_topic1()
                        chatbot.speak()
            if sentiment(chatlog[-1])=='positive':
                print("I see your point. I hope he/she could keep up with the good personality. ")
                chatbot.speak()
                r=["I believe that understanding is important in family.","It seems your family get along well.","I think that mutual respect is important in a family."]
                print(np.random.choice(r))
                print("I also remembered that {}, are there any family members that are like him/her?".format(random_persona()))
                chatbot.speak()
                if sentiment(chatlog[-1])=='negative':
                    print("I see. Please feel free to tell me other things.")
                    error1()
                    clarify_topic(chatlog[-1])
                    continue_topic()
                    continue_topic1()
                if sentiment(chatlog[-1])=='positive':
                    print("Can you tell me more about him/her?")
                    chatbot.state1=='family'
                    chatbot.speak()
                    clarify_topic(chatlog[-1])
                    continue_topic()
                    continue_topic1()
                    chatbot.speak()
    if gdb.nodes[query_info_id()]['state']=='memory':
        chatbot.state1='yourself'
        print("Maybe you can tell me more indepth about your memories/memorable events that you told me.")
        chatbot.speak()
        z=chatlog[-1]
        generate_persona(chatlog[-1])
        unextracted_family(chatlog[-1])
        location(chatlog[-1])
        if sentiment(z)=='negative':
            print("How does the memory negatively affect you ?")
            chatbot.speak()
            generate_memories(chatlog[-1])
            print("Maybe it's a bad memory. But there must be things you gained from it. ")
            chatbot.speak()
            print("I see your point.I do understand sometimes it's hard not to care about the bad memories.")
            chatbot.speak()
            generate_persona(chatlog[-1])
            r=["I think you might develope some hobbies in order to distract yourself from these feelings.",
               "I believe that sometimes we can't control things despite our best effort.",
               "One of the solution is to forget. We should always move forward.",
               "Since we couldn't control it, it might be better for us to look forward."]
            print(np.random.choice(r,replace=True))
            chatbot.speak()
            generate_memories(chatlog[-1])
            print("I hope you are feeling better now. Please feel free to tell me anything.")
            chatbot.speak()
            error1()
            clarify_topic(chatlog[-1])
            continue_topic()
            continue_topic1()
        if sentiment(z)=='positive':
            chatbot.state1='yourself'
            generate_persona(chatlog[-1])
            print("I'm glad to know more about it. It's always good to recall memories.")
            chatbot.speak()
            generate_memories(chatlog[-1])
            print("I'm also glad you have such experiences, What do you think about these memories?")
            chatbot.speak()
            if sentiment(chatlog[-1])=='negative':
                print("I see. Maybe it's not really a good moment to you but I believe that memories keep us alive.")
                chatbot.speak()
                generate_persona(chatlog[-1])
                generate_memories(chatlog[-1])
                print("I hope you could try to remember more about your good memories. try to give yourself a complement sometimes.")
                chatbot.speak()
                print("I hope you are feeling fine right now. Do you want to talk about other things?")
                chatbot.speak()
                error1()
                clarify_topic(chatlog[-1])
                continue_topic()
                continue_topic1()
            if sentiment(chatlog[-1])=='positive':
                print("That's great to know. It seems that these memories did help you to become more positive.")
                chatbot.speak()
                print("I think memories are what keep us mentally alive as well. One can not live without memories.")
                chatbot.speak()
                generate_memories(chatlog[-1])
                print("I hope you are feeling good right now. Do you want to talk about other things?")
                chatbot.speak()
                error1()
                clarify_topic(chatlog[-1])
                continue_topic()
                continue_topic1()
    if gdb.nodes[query_info_id()]['state'] in ['life event','family history','your history']:
            chatbot.state1='yourself'
            j=gdb.nodes[query_id('user')]['life_event'][-1]
            print("I remembered that you mentioned that {} before. Do you remember anything related to this?".format(j))
            chatbot.speak()
            unextracted_family(chatlog[-1])
            try:
                location(chatlog[-1])
            except:
                pass
            if sentiment(chatlog[-1])=='negative':
                print("Don't worry about it. Sometimes we forget thing unexpectedly.")
                chatbot.speak()
                print(suggestion_remem())
                chatbot.speak()
                print("I hope you are feeling better. Please free feel to talk about anything.")
                chatbot.speak()
                try:
                    try:
                        unextracted_family(chatlog[-1])
                    except:
                        generate_hobbies(chatlog[-1])
                except:
                    location(chatlog[-1])
                error1()
                clarify_topic(chatlog[-1])
                continue_topic()
                continue_topic1()
            else:
                print("Thanks for talking about it. Can you also tell me more about your life event?")
                chatbot.speak()
                extract_self_life_event(chatlog[-1])
                try:
                    try:
                        unextracted_family(chatlog[-1])
                        print("So back to the topic, What do you feel about the event you mentioned? ")
                    except:
                        location(chatlog[-1])
                        print("So back to the topic, What do you feel about the event you mentioned? ")
                except:
                    generate_persona(chatlog[-1])
                    print("So back to the topic, What do you feel about the event you mentioned? ")
                if sentiment(chatlog[-1])=='negative':
                    print("I hope this doesn't make you feel too bad. Sometimes things are out of our reach.")
                    chatbot.speak()
                    unextracted_family(chatlog[-1])
                    print("But I think that staying positive and moving forward is the right thing to do.")
                    chatbot.speak()
                    
                    print("I hope you are feeling better. Can you tell me about yourself or other things?")
                    error1()
                    clarify_topic(chatlog[-1])
                    continue_topic()
                    continue_topic1()
                if sentiment(chatlog[-1])=='positive':
                    print("Im glad this has created a good impact on you. ")
                    chatbot.speak()
                    generate_persona(chatlog[-1])
                    try:
                        location(chatlog[-1])
                    except:
                        pass
                    print("I hope this could keep you cheerful everytime you feel bad. Can you also tell me more about yourself or other things?")
                    error1()
                    clarify_topic(chatlog[-1])
                    continue_topic()
                    continue_topic1()
    if gdb.nodes[query_info_id()]['state']=='other':
          first_conversation()
    if gdb.nodes[query_info_id()]['state']=='work':
        print("I think you mentioned that you/they {}. Can you tell me more about it? ".format(gdb.nodes[query_id('user')]['previous_work'])) 
        chatbot.speak()
        if sentiment(chatlog[-1])=='negative':
            try:
                gdb.nodes[query_id('user')]['work_info']
                print("I see. I also recalled that you mentioned {} .".format(gdb.nodes[query_id('user')]['work_info']))
                chatbot.speak()
                r=["Do you still think the same way now?","How do you feel about it now?","Are you feeling the same?"]
                print(np.random.choice(r))
                chatbot.speak()
                b=["I see your point. Maybe you need to think carefully about the job",
                   "If you found the job too stressful, maybe it's time to reconsider about it.",
                   "I guess not all jobs are suitable to every person."]
                print(np.random.choice(b))
                chatbot.speak()
            except:
                print("I guess this is why you/they dislike about the job.")
                chatbot.speak()
                store_feeling(chatlog[-2],'work_info')
                print("I see your point. I hope it doesnt affect you much.")
                chatbot.speak()
            print("I hope you are feeling better now. Do you wish to talk about other topics?")
            chatbot.speak()
            for word in word_tokenize(chatlog[-1]):
                if word.lower() in ["no","not","dont"]:
                        print("I see. Please tell me more about your job.")
                        chatbot.speak()
                        store_feeling(chatlog[-2],'work_info')
                        print("What makes you think about that?")
                        chatbot.speak()
                        print("I see your point. I believe you need to be clear about your job.")
                        chatbot.speak()
                        print(random_positive_suggestion())
                        chatbot.speak()
                        print("I hope you are feeling better now. Do you wish to talk about other topics?")
            chatbot.speak()
            error1()
            clarify_topic(chatlog[-1])
            continue_topic()
            continue_topic1()
        if sentiment(chatlog[-1])=='positive':
            try:
                gdb.nodes[query_id('user')]['work_info']
                print("I'm glad you/they like the job.")
                print("I remembered you told me {} before. What do you think now?".format(gdb.nodes[query_id('user')]['work_info']))
                chatbot.speak()
                if sentiment(chatlog[-1])=='negative':
                        print("I see your point. I think the important thing is to make sure about what we want to do.")
                        chatbot.speak()
                        print("I also hope that you could keep up with your goal.")
                        chatbot.speak()
                else:
                        print("I'm glad you felt decisive or clear about what you want.")
                        chatbot.speak()
                        print("I also hope that you could keep up with your goal.")
                        chatbot.speak()
            except:    
                print("I'm glad you/they like the job. Can you tell me why you/they enjoy the work?")
                chatbot.speak()
                store_feeling(chatlog[-2],'work_info')
                print("It seems that you/they have found joy in work. I believe that's the most important thing in working.")
                chatbot.speak()
                print("We could not live with only money as our goal. It would be as bad as working without passion.")
                chatbot.speak()
            print("I hope you are feeling fine right now. Maybe you wish to talk about other topics?")
            chatbot.speak()
            error1()
            clarify_topic(chatlog[-1])
            continue_topic()
            continue_topic1()

                
def error2():
    print("Could you tell me if it's about yourself, family or others?")
    chatbot.speak()
    chatbot.state='wait'
    while chatbot.state !='ok':
        for word in word_tokenize(chatlog[-1]):
            if word.lower() in ["family","son","daughter","wife","husband","myself","my","mine","other","others"]:
                    chatbot.state='ok'
        if chatbot.state!='ok':
            print("Sorry I didn't get you , could you repeat again?")
            chatbot.speak()
        if chatbot.state=='ok':
             confirm()                  
def Clarify_topic(respond):
        if chatbot.state1=='yourself':
                if classify(respond) == 'hobby':
                        gdb.nodes[query_info_id()].set('state','your hobbies')
                if classify(respond) == 'personality':
                        gdb.nodes[query_info_id()].set('state','your personality')
                if classify(respond) =='work':
                        gdb.nodes[query_info_id()].set('state','work')
                if classify(respond) =='memory':
                        gdb.nodes[query_info_id()].set('state','memories')
                if classify(respond)=='life event':
                        gdb.nodes[query_info_id()].set('state','life event')
                if classify(respond)=='marriage':
                        gdb.nodes[query_info_id()].set('state','marriage')
                if classify(respond) == 'other':
                        gdb.nodes[query_info_id()].set('state','other')
        if chatbot.state1=='family':
                        if classify(respond) == 'hobby':
                            gdb.nodes[query_info_id()].set('state','family hobbies')
                        if classify(respond) == 'personality':
                            gdb.nodes[query_info_id()].set('state','family personality')
                        if classify(respond) == 'other':
                            chatbot.state2='other'
def Second_conversation():
    print(welcome_back())
    chatbot.speak()
    response() 
def response():
    if sentiment(chatlog[-1])=='negative':       
            if query_sentiment()=='bad':
                    print("I remembered that last time you felt bad about {}.".format(gdb.nodes[query_info_id()]['state']))
                    chatbot.speak()
                    try:
                        try:
                            gdb.nodes[query_id('user')]['previous_neg']
                            print("I recalled that you mentioned {} that makes you feel bad.".format(gdb.nodes[query_id('user')]['previous_neg']))
                            chatbot.speak()
                        except:
                            gdb.nodes[query_id('user')]['previous_neg']
                            print("I also recalled that you mentioned {} which you felt pleasant.".format(gdb.nodes[query_id('user')]['previous_pos']))
                            chatbot.speak()
                    except:
                        pass
                    print("Do you wish to talk more about it?")
                    chatbot.speak()
                    if sen.polarity_scores(chatlog[-1])['neg'] >0:
                        print("I get your feeling. What makes you feel bad today?")
                        chatbot.speak()
                        print(bad_respond(chatlog[-1]))
                        chatbot.speak()
                        catagories_bad1(chatlog[-1])
                        chatbot.speak()
                        print("I hope you are feeling better, please feel free to talk about anything.")
                        chatbot.speak()
                        error2()
                        clarify_topic(chatlog[-1])
                        continue_topic()
                        continue_topic1()
                        loop()
                    else:
                        inference()
                        loop()
            if query_sentiment()=='good':
                print("What makes you feel bad today? I remembered that you were good last time.")
                chatbot.speak()
                print(bad_respond(chatlog[-1]))
                chatbot.speak()
                catagories_bad1(chatlog[-1])
                chatbot.speak()
                n=gdb.nodes[query_info_id()]['state']
                try:
                    x=gdb.nodes[query_id('user')]['previous_pos']
                    print("I hope you are feeling better now. I recalled that {}.".format(x))
                    chatbot.speak()
                    print("I also remembered that you talked about {} last time. Do you want to continue on this topic today?".format(n))
                except:
                    print("I also remembered that you talked about {} last time. Do you want to continue on this topic today?".format(n))
                chatbot.speak()
                if sentiment(chatlog[-1])=='negative':
                    print("Please don't felt obliged and feel free to talk about anything.")
                    chatbot.speak()
                    error2()
                    clarify_topic(chatlog[-1])
                    continue_topic()
                    continue_topic1()
                    loop()
                else:
                    print("I'm glad you would like to chat today. It's always better to ")
                    inference()
                    loop()
    if sentiment(chatlog[-1])=='positive':
            if query_sentiment()=='good':
                print("I'm glad as you are also feeling well today like last time.")
                chatbot.speak()
                try:
                    gdb.nodes[query_id('user')]['previous_pos']
                    print("I love to think of good memories. It keeps us motivated.")
                    chatbot.speak()
                    print("I remembered you've mentioned that {} which makes you feel pleasant. Do you wish to continue on the topic?".format(gdb.nodes[query_id('user')]['previous_pos']))
                except:
                    print("I think it's good to think about good memories. It does keep us motivated.")
                    chatbot.speak()
                    print("It seems that you have talked about {}, do you wish to continue on it?".format(gdb.nodes[query_info_id()]['state']))               
                chatbot.speak()
                for word in word_tokenize(chatlog[-1]):
                    if word.lower() in ["no","other","others","alternative"]:
                        print("I see. Please feel free to tell me about anything.")
                        error2()
                        clarify_topic(chatlog[-1])
                        continue_topic()
                        continue_topic1()    
                        loop()
                if sen.polarity_scores(chatlog[-1])['neg']>0:
                    print("I see. Please feel free to tell me about anything.")
                    error2()
                    chatbot.speak()
                    clarify_topic(chatlog[-1])
                    continue_topic()
                    continue_topic1()
                    loop()
                else:
                    inference()
                    loop()
            if query_sentiment()=='bad':
                j=["I'm glad to hear that as you were feeling bad last time.","That's great. You were a bit down last time",
                "There's a good sign, it seems that you're getting better and better."]
                print(np.random.choice(j))
                chatbot.speak()
                print(random_positive_suggestion())
                chatbot.speak()
                try:
                    n=gdb.nodes[query_id('user')]['previous_pos']
                    print("Although you felt bad last time but I remembered you mentioned {} ,which cheered you up.".format(n))
                    chatbot.speak()
                    print("I also remembered you talked about {}, do you want to continue on it?".format(gdb.nodes[query_info_id()]['state']))
                except:    
                    print("I remembered you mentioned {} last time, maybe you still want to talk about it?".format(gdb.nodes[query_info_id()]['state']))
                chatbot.speak()
                for word in word_tokenize(chatlog[-1]):
                    if word.lower() in ["no","other","others","alternative"]:
                        print("I see. Please feel free to tell me about anything.")
                        chatbot.speak()
                        error2()
                        clarify_topic(chatlog[-1])
                        continue_topic()
                        continue_topic1() 
                        loop()
                    if sen.polarity_scores(chatlog[-1])['neg']>0:
                        print("I see. Please feel free to tell me about anything.")
                        chatbot.speak()
                        error2()
                        clarify_topic(chatlog[-1])
                        continue_topic()
                        continue_topic1()
                        loop()
                    else:
                        inference()
                        loop()
def unextracted_family(sentence):
    x=0
    c=[]
    j=[]
    y=0
    text = (sentence)
    output = nlp.annotate(text, properties={
        'annotators': 'tokenize,ssplit,pos,depparse,parse',
        'outputFormat': 'json'
         })
    a=output['sentences'][0]['parse']
    tree=nltk.Tree.fromstring(a)
    parsed=ne_chunk(pos_tag(word_tokenize(sentence)))
    for t in parsed.subtrees():
        if t.label()=='GPE':
             y=1
    try:
        if y!=1:
            for t in tree.subtrees():
                 if t.label() == 'NNP':
                    b=t.leaves()
                    if b[0] not in query_stored_name():
                        c.append(b[0])
            print("Can your tell me more about {}? ".format(c[0]))
            chatbot.speak()
            if classify(chatlog[-1])=='hobby':
                    z=gdb.nodes.create()
                    z.labels.add('Person')
                    z.set('name',c[0])
                    z.set('hobby',get_stemmed_VP(chatlog[-1]))
                    gdb.nodes[query_id('user')].relationships.create("Knows", z)
                    print("I hope they could develop good habits as well.")
                    chatbot.speak()
                    print("Can you also tell me who this person is to you?")
                    chatbot.speak()
                    Error()
                    p=chatlog[-1]
                    z.set('who',get_who(chatlog[-1])[0])
                    if get_who(p)[0] in ['wife','husband']:
                        gdb.nodes[query_info_id()].set('state','marriage')
                        print("What do you think about your marriage?")
                        chatbot.speak()
                        gdb.nodes[query_id('user')].set('marriage',chatlog[-1])
                    if get_who(p)[0] in ['son','daughter']:
                        gdb.nodes[query_info_id()].set('state','family hobbies')
                    print("Thanks. It's good to know more about {}.".format(c[0]))
                    chatbot.speak()
                    print("I hope this could also help you in reminding things. Let's get back to what we've previous chatted about.")
                    x=1
                    chatbot.state3=1
                    chatbot.state4=1
            if classify(chatlog[-1])=='personality':
                    z=gdb.nodes.create()
                    z.labels.add('Person')
                    z.set('name',c[0])
                    z.set('personality',get_VP(chatlog[-1]))
                    gdb.nodes[query_id('user')].relationships.create("Knows", z)
                    print("That's interesting to know. I hope he/she could maintain their good qualities.")
                    chatbot.speak()
                    print("Can you also tell me who this person is to you?")
                    chatbot.speak()
                    Error()
                    p=chatlog[-1]
                    z.set('who',get_who(chatlog[-1])[0])
                    if get_who(p)[0] in ['wife','husband']:
                        gdb.nodes[query_info_id()].set('state','marriage')
                        print("What do you think about your marriage?")
                        chatbot.speak()
                        gdb.nodes[query_id('user')].set('marriage',chatlog[-1])
                    if get_who(p)[0] in ['son','daughter']:
                        gdb.nodes[query_info_id()].set('state','family personality')
                    print("Thanks. It's interesting to know more about {}.".format(c[0]))
                    chatbot.speak()
                    print("I hope this could also help you in remembering things.Let's get back to what we've previous chatted about.")
                    x=1
                    chatbot.state3=1
                    chatbot.state4=1
            if x!=1:
                if sentiment(chatlog[-1])=='negative':
                    z=gdb.nodes.create()
                    z.labels.add('Person')
                    z.set('name',c[0])
                    gdb.nodes[query_id('user')].relationships.create("Knows", z)
                    print("I hope you didn't feel too bad about this. There's something we couldn't control.")
                    chatbot.speak()
                    print("How is he/she as a person?")
                    chatbot.speak()
                    print("I see. Sometimes we could not change someone despite our wish.")
                    chatbot.speak()
                    print(random_positive_motivation())
                    chatbot.speak()
                    print("Can you also tell me who this person is to you?")
                    chatbot.speak()
                    Error()
                    p=chatlog[-1]
                    if get_who(p)[0] in ['wife','husband']:
                        gdb.nodes[query_info_id()].set('state','marriage')
                        print("What do you think about your marriage?")
                        chatbot.speak()
                        gdb.nodes[query_id('user')].set('marriage',chatlog[-1])
                    if get_who(p)[0] in ['son','daughter']:
                        gdb.nodes[query_info_id()].set('state','family personality')
                    z.set('who',get_who(chatlog[-1])[0])
                    print("Thanks. It's good to know more about {}.".format(c[0]))
                    print("I hope you are feeling better now. Let's get back to our previous talk.")
                    chatbot.state3=1
                    chatbot.state4=1
                else:
                    z=gdb.nodes.create()
                    z.labels.add('Person')
                    z.set('name',c[0])
                    gdb.nodes[query_id('user')].relationships.create("Knows", z)
                    print("I see your point. How is he/she as a person?")
                    chatbot.speak()
                    print("I get you point. Sometimes we might not be able to influence others despite our wish.")
                    chatbot.speak()
                    print("Can you also tell me who this person is to you?")
                    chatbot.speak()
                    Error()
                    p=chatlog[-1]
                    if get_who(p)[0] in ['wife','husband']:
                        gdb.nodes[query_info_id()].set('state','marriage')
                    if get_who(p)[0] in ['son','daughter']:
                        gdb.nodes[query_info_id()].set('state','family personality')
                    z.set('who',get_who(chatlog[-1])[0])
                    print("Thanks it is nice to know more about him/her.")
                    print("I hope this could also help you in reminding things as well. Let's get back to our previous topic.")
                    chatbot.state3=1
                    chatbot.state4=1
    except:
        if y!=1:
            j=[]
            for word in word_tokenize(sentence):
                if word.lower() in ["son","daughter","wife","husband"]:
                    j.append(word)
                    if j[0] not in query_stored_who():
                            print("Can your tell me more about your {}? ".format(j[0]))
                            chatbot.speak()
                    if classify(chatlog[-1])=='hobby':
                        z=gdb.nodes.create()
                        z.labels.add('Person')
                        if j[0] in ['wife','husband']:
                            gdb.nodes[query_info_id()].set('state','marriage')
                            print("What do you think about your marriage?")
                            chatbot.speak()
                            gdb.nodes[query_id('user')].set('marriage',chatlog[-1])
                        if j[0] in ['son','daughter']:
                            gdb.nodes[query_info_id()].set('state','family hobbies')
                        z.set('who',j[0])
                        gdb.nodes[query_id('user')].relationships.create("Knows", z)
                        z.set('hobby',get_stemmed_VP(chatlog[-1]))
                        print("I hope they could develop a good habit as well.")
                        chatbot.speak()
                        print(random_positive_motivation())
                        chatbot.speak()
                        print("Can you also tell me his/her name?")
                        chatbot.speak()
                        Error()
                        z.set('name',Get_name(chatlog[-1])[0])
                        print("Thanks. It's good to know more about your {}.".format(j[0]))
                        chatbot.speak()
                        print("I hope this could also help you in reminding things. Let's get back to what we've previous chatted about.")
                        x=1
                        chatbot.state3=1
                        chatbot.state4=1
                    if classify(chatlog[-1])=='personality':
                        z=gdb.nodes.create()
                        z.labels.add('Person')
                        if j[0] in ['wife','husband']:
                            gdb.nodes[query_info_id()].set('state','marriage')
                            print("What do you think about your marriage?")
                            chatbot.speak()
                            gdb.nodes[query_id('user')].set('marriage',chatlog[-1])
                        if j[0] in ['son','daughter']:
                            gdb.nodes[query_info_id()].set('state','family personality')
                        z.set('who',j[0])
                        gdb.nodes[query_id('user')].relationships.create("Knows", z)
                        z.set('personality',get_VP(chatlog[-1]))
                        print("I see. I hope he/she could continue with the good qualities . ")
                        chatbot.speak()
                        print("Can you also tell me his/her name?")
                        chatbot.speak()
                        Error()
                        z.set('name',Get_name(chatlog[-1])[0])
                        print("Thanks. It's interesting to know more about your {}.".format(j[0]))
                        chatbot.speak()
                        print("I hope you are feeling better now. Shall we get back to our previous topic?")
                        x=1
                        chatbot.state3=1
                        chatbot.state4=1
                    if x!=1:
                        if sentiment(chatlog[-1])=='negative':
                            z=gdb.nodes.create()
                            z.labels.add('Person')
                            if j[0] in ['wife','husband']:
                                gdb.nodes[query_info_id()].set('state','marriage')
                                print("What do you think about your marriage?")
                                chatbot.speak()
                                gdb.nodes[query_id('user')].set('marriage',chatlog[-1])
                            if j[0] in ['son','daughter']:
                                gdb.nodes[query_info_id()].set('state','family personality')
                            z.set('who',j[0])
                            gdb.nodes[query_id('user')].relationships.create("Knows", z)
                            print("I see your point. I think there's something we couldn't control despite our effort.")
                            chatbot.speak()
                            print(random_positive_motivation())
                            print("Can you also tell me his/her name?")
                            chatbot.speak()
                            Error()
                            z.set('name',Get_name(chatlog[-1])[0])
                            print("Thanks. It's good to know more about your{}.".format(j[0]))
                            chatbot.speak()
                            print("I hope you are feeling better now. Shall we get back to our previous topic?")
                            chatbot.state3=1
                            chatbot.state4=1
                        else:
                            z=gdb.nodes.create()
                            z.labels.add('Person')
                            if j[0] in ['wife','husband']:
                                gdb.nodes[query_info_id()].set('state','marriage')
                                print("What do you think about your marriage?")
                                chatbot.speak()
                                gdb.nodes[query_id('user')].set('marriage',chatlog[-1])
                            if j[0] in ['son','daughter']:
                                gdb.nodes[query_info_id()].set('state','family personality')
                            z.set('who',j[0])
                            gdb.nodes[query_id('user')].relationships.create("Knows", z)
                            print("I'm glad to know about that. I hope he/she could continue to improve.")
                            chatbot.speak()
                            print("Can you also tell me his/her name?")
                            chatbot.speak()
                            Error()
                            z.set('name',Get_name(chatlog[-1])[0])
                            print("Thanks. It's nice to know more about your {} .".format(j[0]))
                            chatbot.speak()
                            print("I hope this could also help you in reminding things as well. Let's get back to our previous topic.")
                            chatbot.state3=1
                            chatbot.state4=1
def start():
    print(greeting())
    chatbot.speak()
    print(starting_respond(chatlog[-1]))
def first_conversation():
    if chatbot.state =='bad':
        n=gdb.nodes.create()
        n.labels.add("data")
        n.set('sentiment','bad')
        chatbot.speak()
        print(bad_respond(chatlog[-1]))
        chatbot.speak()
        catagories_bad1(chatlog[-1])
        chatbot.speak()
        extract_name(chatlog[-1])
        error()
        chatbot.speak()
        error1()
        clarify_topic(chatlog[-1])
        continue_topic()
        continue_topic1()
        chatbot.speak()
        loop()
    if chatbot.state =='good':
        n=gdb.nodes.create()
        n.labels.add("data")
        n.set('sentiment','good')
        chatbot.speak()
        extract_name(chatlog[-1])
        error()
        chatbot.speak()
        error1()
        clarify_topic(chatlog[-1])
        continue_topic()
        continue_topic1()
        chatbot.speak()
        loop()
#Using The chatbot:
try: 
    query_id('user') 
    Second_conversation()
except:
    start()
    first_conversation()
