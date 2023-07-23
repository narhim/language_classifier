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
		#sentence_tokenized = [c.lower() for c in sentence if not re.match('[.] |[.]{2,}|[:]|[;]|[\']|["]|[„]|[‟]|[”]|[<]+|[>]+|[(]|[)]|[\[]|[\]]|[¿]|[?]|[¡]|[!]',c)]
		sentence_tokenized = [c.lower() for c in sentence]
		corpus.append(sentence_tokenized)
	return corpus

def build_unigrams(dict_sent_tok):
	dict_unig_sent = {lang : [] for lang in languages_list}
	for language,sentences in dict_sent_tok.items():
		for s in sentences:
			for n,word in enumerate(s):
				#if n > 1:
				dict_unig_sent[language].append(word)
	return dict_unig_sent

def build_trigrams(dict_sent_tok):
	dict_tri_sent = {lang : [] for lang in languages_list}
	for language,sentences in dict_sent_tok.items():
		for s in sentences:
			for n,word in enumerate(s):
				if n > 0:
					dict_tri_sent[language].append((s[n-1],word))
	return dict_tri_sent

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

def main():
	#Train
	sen_lan_list = read_file("data/train_dev/train.txt") #Extract data [[sentence,language]]
	lang_sens_dict = separate_language(sen_lan_list) #Separate by language {language:[s1,s2]}
	lang_nsens_dict = {lang:len(sentences) for lang,sentences in lang_sens_dict.items()} #Compute number of sentences per language {language:#sentences}
	uni_except_dict = {language:(1/n) for language,n in lang_nsens_dict.items()} #Smoothing values for initial states {language:1/#sentences}
	lang_senstok_dict = {}#Tokenize by letters {language:[[l,e,t, ,t,e,r,s],[l,e,t, ,t,e,r,s]]}
	for language,sentences in lang_sens_dict.items():
		corpus_list = tokenize_sentences(sentences)
		lang_senstok_dict[language] = corpus_list
	lang_uni_dict = build_unigrams(lang_senstok_dict)#Build unigrams {lang:[ngram,ngram]}
	lang_tri_dict = build_trigrams(lang_senstok_dict)#Build trigrams {lang:[ngram,ngram]}
	abs_uni_freq_dict = count_ngrams(lang_uni_dict,lang_nsens_dict) #Compute abs frequencies{lang:[{ngram:freq},{ngram:freq}]}
	uni_freq_dict = {}#Transform into initial state frequencies {lang:[{ngram:freq},{ngram:freq}]}
	for language,ngrams in abs_uni_freq_dict.items():
		nsens = lang_nsens_dict[language]
		clean_ngrams = {}
		for n,f in ngrams.items():
			clean_ngrams[n] = (f+1)/nsens
		uni_freq_dict[language] = clean_ngrams
	
	abs_tri_freq_dict = count_ngrams(lang_tri_dict,lang_nsens_dict)#Compute abs frequencies{lang:[{ngram:freq},{ngram:freq}]}
	tri_freq_dict = {}#Transform into initial state frequencies {lang:[{ngram:freq},{ngram:freq}]}
	for language,ngrams in abs_tri_freq_dict.items():
		ntrigrams = len(ngrams.keys())
		clean_ngrams = {}
		for n,f in ngrams.items():
			clean_ngrams[n] = (f+1)/ntrigrams
		tri_freq_dict[language] = clean_ngrams
	tri_except_dict = {lang:(1/len(v)) for lang,v in abs_tri_freq_dict.items()}

	#Dev
	dev_sen_lan_list = read_file("data/train_dev/devel.txt") #Extract data
	gold_labels_list = [pair[1] for n,pair in enumerate(dev_sen_lan_list)]
	id_sentence_dict = {n:pair[0] for n,pair in enumerate(dev_sen_lan_list)}
	dev_sentences_list = [pair[0] for pair in dev_sen_lan_list]
	dev_corpus = tokenize_sentences(dev_sentences_list)
	results = []
	for sentence in dev_corpus:
		unigrams = []
		for n,word in enumerate(sentence):
			#if n > 1:
			unigrams.append(word)
		trigrams = []
		for n,word in enumerate(sentence):
			if n > 0:
				trigrams.append((sentence[n-1],word))
		language_probability_dict = {}
		for language,ngrams in uni_freq_dict.items():
			probabilities = []
			try:
				initial_prob = ngrams[unigrams[0]]
				probabilities.append(initial_prob)
			except:
				initial_prob = uni_except_dict[language]
				probabilities.append(initial_prob)
			for t in trigrams:
				try:
					transitional_prob = tri_freq_dict[language][t]
					probabilities.append(transitional_prob)
				except:
					transitional_prob = tri_except_dict[language]
					probabilities.append(transitional_prob)
			prob = math.prod(probabilities)
			language_probability_dict[language] = prob
		#try:
		majority = list(language_probability_dict.keys())[0]
		probability = list(language_probability_dict.values())[0]
		for lang,prob in language_probability_dict.items():
			if prob > probability:
				majority = lang
				probability = prob
		results.append(majority) 
		#except:
		#	results.append("NaN")

	total_sentences = len(dev_corpus)
	nas = 0
	accuracy = 0
	for g,r in zip(gold_labels_list,results):
		#if r == "NaN":
		#	nas += 1
		if r==g:
			accuracy += 1 
	nas = nas*100/total_sentences
	print(nas)
	accuracy = accuracy*100/total_sentences
	print(accuracy)


	'''
#Test
	test_sen_lan_list = read_file("data/test/test.txt") #Extract data
	
	test_lang_senstok_dict = tokenize_sentences(test_lang_sens_dict) #Tokenize sentences
	language_sen_maj = {language:[] for language in languages_list}
	for l,sentences in test_lang_senstok_dict.items():
		for sentence in sentences:
			unigrams = []
			for n,word in enumerate(sentence):
				if n > 1:
					unigrams.append((sentence[n-2],sentence[n-1],word))
			trigrams = []
			for n,word in enumerate(sentence):
				if n > 2:
					trigrams.append((sentence[n-3],sentence[n-2],sentence[n-1],word))
			language_probability_dict = {}
			for language,ngrams in uni_freq_dict.items():
				probabilities = []
				try:
					initial_prob = ngrams[unigrams[0]]
					probabilities.append(initial_prob)
				except:
					continue
				for t in trigrams:
					try:
						transitional_prob = tri_freq_dict[language][t]
						probabilities.append(transitional_prob)
					except:
						continue
				prob = math.prod(probabilities)
				language_probability_dict[language] = prob
			try:
				majority = list(language_probability_dict.keys())[0]
				probability = list(language_probability_dict.values())[0]
				for lang,prob in language_probability_dict.items():
					if prob > probability:
						majority = lang
						probability = prob
				language_sen_maj[l].append(majority) 
			except:
				language_sen_maj[l].append("NaN")
	print(language_sen_maj["es-ES"])
	'''
if __name__=='__main__':
	main()