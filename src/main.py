import re 
import math

def read_file(path):
	'''Reads file and return list of list[text,language_id]'''
	file = open(path,"r",encoding="utf-8")
	all_text_lan = []
	for l in file:
		try:
			text_language =re.split("\t",l) #Separate text from language id
			clean_text_language = [text_language[0],text_language[1].strip()] #Remove \n from language id
			all_text_lan.append(clean_text_language)
		except:
			all_text_lan.append(l.strip())
	return all_text_lan	

def separate_language(list_of_lists):
	global languages_list
	languages_list = [pair[1] for pair in list_of_lists]
	dict_sentences = {lang : [] for lang in languages_list}
	for pair in list_of_lists:
		try:
			dict_sentences[pair[1]].append(pair[0])
		except:
			print(pair)
	return dict_sentences

def tokenize_sentences(list_sentences):
	corpus = []
	for sentence in list_sentences:
		sentence_tokenized = [c.lower() for c in sentence if not re.match('[.]|[:]|[;]|[,||[(]|[)]|[\[]|[\]]',c)]
		corpus.append(sentence_tokenized)
	return corpus

def build_unigrams(dict_sent_tok):
	dict_unig_sent = {lang : [] for lang in languages_list}
	for language,sentences in dict_sent_tok.items():
		for s in sentences:
			for n,word in enumerate(s):
				dict_unig_sent[language].append(word)
	return dict_unig_sent

def build_bigrams(dict_sent_tok):
	dict_bi_sent = {lang : [] for lang in languages_list}
	for language,sentences in dict_sent_tok.items():
		for s in sentences:
			for n,word in enumerate(s):
				if n > 0:
					dict_bi_sent[language].append((s[n-1],word))
	return dict_bi_sent

def count_ngrams(dict_ngrams,len_dict):
	dict_freq_ngram = dict.fromkeys(languages_list)
	num_ngrams = len(dict_ngrams.values())
	for language,ngrams in dict_ngrams.items():
		dict_freq = {}
		for n in ngrams:
			if n in dict_freq:
				dict_freq[n] +=1
			else:
				dict_freq[n] = 1
		dict_freq_ngram[language] = dict_freq
	return dict_freq_ngram

def compute_prob(corpus):
	results = []
	for sentence in corpus:
		unigrams = []
		for n,word in enumerate(sentence):
			unigrams.append(word)
		bigrams = []
		for n,word in enumerate(sentence):
			if n > 0:
				bigrams.append((sentence[n-1],word))
		language_probability_dict = {}
		for language,ngrams in uni_freq_dict.items():
			probabilities = []
			try:
				initial_prob = ngrams[unigrams[0]]
				probabilities.append(initial_prob)
			except:
				initial_prob = uni_except_dict[language]
				probabilities.append(initial_prob)
			for t in bigrams:
				try:
					transitional_prob = bi_freq_dict[language][t]
					probabilities.append(transitional_prob)
				except:
					transitional_prob = bi_except_dict[language]
					probabilities.append(transitional_prob)
			prob = math.prod(probabilities)
			language_probability_dict[language] = prob
		majority = list(language_probability_dict.keys())[0]
		probability = list(language_probability_dict.values())[0]
		for lang,prob in language_probability_dict.items():
			if prob > probability:
				majority = lang
				probability = prob
		results.append(majority) 
	return results
def write_corpus(name,list_tuples):
	'''Function that takes a string and a list and writes the list in a file with the string as a name.'''
	with open(name,"w",encoding = "utf-8") as file:
		for pair in list_tuples:
			for n,element in enumerate(pair):
				if (n+1) < len(pair):
					file.write(str(element)+"\t")
				else:
					file.write(str(element) + '\n')

def main():
	#Train
	sen_lan_list = read_file("data/train_dev/train.txt") #Extract data [[sentence,language]]
	lang_sens_dict = separate_language(sen_lan_list) #Separate by language {language:[s1,s2]}
	lang_nsens_dict = {lang:len(sentences) for lang,sentences in lang_sens_dict.items()} #Compute number of sentences per language {language:#sentences}
	lang_senstok_dict = {}#Tokenize by letters {language:[[l,e,t, ,t,e,r,s],[l,e,t, ,t,e,r,s]]}
	for language,sentences in lang_sens_dict.items():
		corpus_list = tokenize_sentences(sentences)
		lang_senstok_dict[language] = corpus_list
	lang_uni_dict = build_unigrams(lang_senstok_dict)#Build unigrams {lang:[ngram,ngram]}
	lang_bi_dict = build_bigrams(lang_senstok_dict)#Build bigrams {lang:[ngram,ngram]}
	global uni_except_dict
	uni_except_dict = {} #Smoothing values for initial states {language:1/#sentences}
	abs_uni_freq_dict = count_ngrams(lang_uni_dict,lang_nsens_dict) #Compute abs frequencies{lang:[{ngram:freq},{ngram:freq}]}
	global uni_freq_dict
	uni_freq_dict = {}#Transform into initial state frequencies {lang:[{ngram:freq},{ngram:freq}]}
	for language,ngrams in abs_uni_freq_dict.items():
		nsens = lang_nsens_dict[language]
		vocabulary= len(ngrams.keys())
		uni_except_dict[language] = 1/(nsens+vocabulary)
		clean_ngrams = {}
		for n,f in ngrams.items():
			clean_ngrams[n] = (f+1)/(nsens+vocabulary)
		uni_freq_dict[language] = clean_ngrams
	abs_bi_freq_dict = count_ngrams(lang_bi_dict,lang_nsens_dict)#Compute abs frequencies{lang:[{ngram:freq},{ngram:freq}]}
	number_of_transitions = {lang:{} for lang in languages_list}
	for lang,ngrams in abs_uni_freq_dict.items():
		for unigram,frequency in ngrams.items():
			transition = 0
			for b,f in abs_bi_freq_dict[lang].items():
				if unigram==b[0]:
					transition += 1
			number_of_transitions[lang][unigram] = transition
	global bi_freq_dict
	bi_freq_dict = {}#Transform into initial state frequencies {lang:[{ngram:freq},{ngram:freq}]}
	for language,ngrams in abs_bi_freq_dict.items():
		vocabulary = len(abs_uni_freq_dict[language].keys())
		clean_ngrams = {}
		for n,f in ngrams.items():
			try:
				transitions = number_of_transitions[lang][n[0]]
			except:
				transitions = 0
			clean_ngrams[n] = (f+1)/(transitions + vocabulary)
		bi_freq_dict[language] = clean_ngrams
	global bi_except_dict
	bi_except_dict = {lang:(1/(len(v))) for lang,v in abs_bi_freq_dict.items()}
	
	#Dev
	dev_sen_lan_list = read_file("data/train_dev/devel.txt") #Extract data
	gold_labels_list = [pair[1] for n,pair in enumerate(dev_sen_lan_list)]
	id_sentence_dict = {n:pair[0] for n,pair in enumerate(dev_sen_lan_list)}
	dev_sentences_list = [pair[0] for pair in dev_sen_lan_list]
	dev_corpus = tokenize_sentences(dev_sentences_list)
	dev_results = compute_prob(dev_corpus)
	total_sentences = len(dev_corpus)
	total_true_dict = {language:0 for language in languages_list}
	for g in gold_labels_list:
		total_true_dict[g] += 1
	true_dict = {language:0 for language in languages_list}
	accuracy = 0
	for g,r in zip(gold_labels_list,dev_results):
		if r==g:
			accuracy += 1
			true_dict[r] += 1 
	accuracy = accuracy/total_sentences
	print("Accuracy for the development set is:" + str(accuracy))
	
	predicted_dict = {language:0 for language in languages_list}
	for language in dev_results:
		predicted_dict[language]+=1

	precision_list = []
	for lang,true in true_dict.items():
		try:
			precision_list.append((lang,(true/predicted_dict[lang])))
		except:
			precision_list.append((lang,"NaN")) 
	precision_list.append(("ACCURACY",accuracy))
	recall_list = []
	for lang,true in true_dict.items():
		try:
			recall_list.append((lang,(true/total_true_dict[lang])))
		except:
			recall_list.append((lang,"NaN"))
	f1_list = []
	for p,r in zip(precision_list,recall_list):
		try:
			f1_list.append((lang,(2*(p*r)/(p+r))))
		except:
			f1_list.append((lang,"NaN"))
	write_corpus("results/dev_precision_accuracy.tsv",precision_list)
	write_corpus("results/dev_recall.tsv",recall_list)
	write_corpus("results/dev_f1_score.tsv",f1_list)
	
	dev_to_write_list = [("SENTENCE","GOLD","PREDICTED")]
	for s,g,p in zip(dev_sentences_list,gold_labels_list,dev_results):
		dev_to_write_list.append((s,g,p))
	write_corpus("results/dev.tsv",dev_to_write_list)
	#Test
	test_sen_list = read_file("data/test/test.txt") #Extract data
	test_corpus = tokenize_sentences(test_sen_list) #Tokenize sentences
	test_results = compute_prob(test_corpus)
	test_to_write_list = [("SENTENCE","PREDICTED")]
	for s,p in zip(test_sen_list,test_results):
		test_to_write_list.append((s,p))
	write_corpus("results/test.tsv",test_to_write_list)

	test_none_sen_list = read_file("data/test/test-none.txt") #Extract data
	test_none_corpus = tokenize_sentences(test_none_sen_list) #Tokenize sentences
	test_none_results = compute_prob(test_none_corpus)
	test_none_to_write_list = [("SENTENCE","PREDICTED")]
	for s,p in zip(test_none_sen_list,test_none_results):
		test_none_to_write_list.append((s,p))
	write_corpus("results/test_none.tsv",test_none_to_write_list)
	
if __name__=='__main__':
	main()