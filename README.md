# Mental health chatbot/companion-bot 

Reminiscence chatbot designed to counsel patients with mild cognitive impairment  constructed using machine learning and NLP methods(e.g. POS tagging, named entity recognition, sentiment analysis). The chatbot is a prototype and still subject to unseen errors.
# Installation guide:
Neo4j installation guide:\
Install Neo4j using window or MAC option (https://www.quackit.com/neo4j/tutorial/neo4j_installation.cfm)\
set user name to 1234 in Neo4j user interface\
set password to 1234 

Stanford-corenlp guide:\
Install stanford-corenlp-full-2015-12-09 version

In first terminal:\
sudo service neo4j start\
cd stanford-corenlp-full-2015-12-09/\
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer

In second terminal:\
pip install nltk\
pip install stanfordcorenlp\
pip install textblob\
pip install neo4jrestclient\
python Chatbot.py\
make sure everything is in the folder