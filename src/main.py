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
		sentence_tokenized = [c.lower() for c in sentence if not re.match('[.] |[.]{2,}|[:]|[;]|[\']|["]|[„]|[‟]|[”]|[<]+|[>]+|[(]|[)]|[\[]|[\]]|[¿]|[?]|[¡]|[!]',c)]
		'''
		sentence_tokenized = []
		#Separate characters by delimiters defined in regex.
		s = re.split(' |[.] |[.]{2,}|[:]|[;]|[\']|["]|[„]|[‟]|[”]|[<]+|[>]+|[(]|[)]|[\[]|[\]]|[¿]|[?]|[¡]|[!]',sentence)
		#Initialize list in which results from strip will be appended.
		result = []
		for element in s:
		#Remove characters specified in regex from string.
			s_r = element.strip('\n|[.]+|[:]|[,]|[;]|[«]|[»]|["]|[„]|[‟]|[”]|[<]+|[>]+|[\*]|[(]|[)]|[\[]|[\]]|[¿]|[?]|[¡]|[!]')
			result.append(s_r)
		#Loop over results from strip for second clean up.
		for w in result:
			#Avoid empty strings and "===".
			if (w=='') or (re.match('=+',w) != None):
				continue
			#Conditions for string with hyphens. And example for each condition is provided.
			elif re.search('-',w) != None:
				#5-5
				if re.search('\d+-\d+',w):
					numbers = re.split('-',w)
					sentence_tokenized.append(numbers[0].lower())
					sentence_tokenized.append(numbers[1].lower())
			
				#cat-dog
				elif re.search('[a-z]+-[a-z]+',w,flags=re.IGNORECASE):
					sentence_tokenized.append(w.lower())

					#45-ben
				elif re.search('\d+-\D+',w):
					numbers = re.split('-',w)
					sentence_tokenized.append(numbers[0].lower())
					sentence_tokenized.append(numbers[1].lower())
				#-32,9
				elif re.match('-\d+',w):
					sentence_tokenized.append(w)
				#alt- (from (alt-)griechisch)
				elif re.search('[a-z]-',w,flags=re.IGNORECASE):
					clean = w.strip('-')
					sentence_tokenized.append(clean.lower())
				#-word
				elif re.match('-\w+',w):
					clean = w.strip('-')
					sentence_tokenized.append(clean.lower())
				#45-
				elif re.match('\d+-',w):
					clean = w.strip('-')
					sentence_tokenized.append(clean.lower())
				#-%45 and -«word
				elif re.match('[-%\d+]|[-«\w+]',w):
					clean = w.strip('[-%]|[-«]')
					sentence_tokenized.append(clean.lower())
				#Avoid "-".
				elif re.match('^-$',w):
					continue
			elif (w == '/') or (w=="“"):
				continue
			elif re.search('[a-z]\/',w,flags=re.IGNORECASE):
				splitted = w.split('/')
				sentence_tokenized.append(splitted[0].lower())
				sentence_tokenized.append(splitted[1].lower())
			elif re.search('\d[.]\d',w):
				sentence_tokenized.append(w.lower())
			#avoid the second type of hyphen found in raw text.
			elif re.match('–',w):
					continue
			#If none of the conditions above apply, simply lower and apply.
			else:
				sentence_tokenized.append(w.lower())
			'''
		corpus.append(sentence_tokenized)
	return corpus

def build_bigrams(dict_sent_tok):
	dict_big_sent = {lang : [] for lang in languages_list}
	for language,sentences in dict_sent_tok.items():
		for s in sentences:
			for n,word in enumerate(s):
				if n > 0:
					dict_big_sent[language].append((s[n-1],word))
	return dict_big_sent
def build_trigrams(dict_sent_tok):
	dict_trig_sent = {lang : [] for lang in languages_list}
	for language,sentences in dict_sent_tok.items():
		for s in sentences:
			for n,word in enumerate(s):
				#if n > 1:
				dict_trig_sent[language].append(word)
	return dict_trig_sent

def build_tetragrams(dict_sent_tok):
	dict_tetra_sent = {lang : [] for lang in languages_list}
	for language,sentences in dict_sent_tok.items():
		for s in sentences:
			for n,word in enumerate(s):
				if n > 0:
					dict_tetra_sent[language].append((s[n-1],word))
	return dict_tetra_sent

def count_ngrams(dict_ngrams,len_dict,dictmin_ngrams):
	dict_freq_ngram = dict.fromkeys(languages_list)
	num_ngrams = len(dict_ngrams.values())
	for language,ngrams in dict_ngrams.items():
		dict_freq = {}
		for n in ngrams:
			if n in dict_freq:
				dict_freq[n] +=1
			else:
				dict_freq[n] = 1
		#dict_freq = {n:f/len_dict[language] for n,f in dict_freq.items()}
		dict_freq_ngram[language] = dict_freq
	return dict_freq_ngram

def main():
	#Train
	sen_lan_list = read_file("data/train_dev/train.txt") #Extract data
	lang_sens_dict = separate_language(sen_lan_list) #Separate by language
	lang_nsens_dict = {lang:len(sentences) for lang,sentences in lang_sens_dict.items()}
	lang_senstok_dict = {}
	for language,sentences in lang_sens_dict.items():
		corpus_list = tokenize_sentences(sentences)
		lang_senstok_dict[language] = corpus_list
	lang_big_dict = build_bigrams(lang_senstok_dict)#Build bigrams
	lang_tri_dict = build_trigrams(lang_senstok_dict)#Build trigrams
	lang_tetra_dict = build_tetragrams(lang_senstok_dict)#Build tetragrams
	abs_tri_freq_dict = count_ngrams(lang_tri_dict,lang_nsens_dict,lang_big_dict)
	tri_freq_dict = {}
	for language,ngrams in abs_tri_freq_dict.items():
		nsens = lang_nsens_dict[language]
		clean_ngrams = {}
		for n,f in ngrams.items():
			clean_ngrams[n] = f/nsens
		tri_freq_dict[language] = clean_ngrams
	abs_tetra_freq_dict = count_ngrams(lang_tetra_dict,lang_nsens_dict,lang_tri_dict)
	tetra_freq_dict = {}
	for language,ngrams in abs_tetra_freq_dict.items():
		ntetragrams = len(ngrams.keys())
		clean_ngrams = {}
		for n,f in ngrams.items():
			clean_ngrams[n] = f/ntetragrams
		tetra_freq_dict[language] = clean_ngrams
	
	#Dev
	dev_sen_lan_list = read_file("data/train_dev/devel.txt") #Extract data
	gold_labels_list = [pair[1] for n,pair in enumerate(dev_sen_lan_list)]
	id_sentence_dict = {n:pair[0] for n,pair in enumerate(dev_sen_lan_list)}
	dev_sentences_list = [pair[0] for pair in dev_sen_lan_list]
	dev_corpus = tokenize_sentences(dev_sentences_list)
	results = []
	for sentence in dev_corpus:
		trigrams = []
		for n,word in enumerate(sentence):
			#if n > 1:
			trigrams.append(word)
		tetragrams = []
		for n,word in enumerate(sentence):
			if n > 0:
				tetragrams.append((sentence[n-1],word))
		language_probability_dict = {}
		for language,ngrams in tri_freq_dict.items():
			probabilities = []
			try:
				initial_prob = ngrams[trigrams[0]]
				probabilities.append(initial_prob)
			except:
				continue
			for t in tetragrams:
				try:
					transitional_prob = tetra_freq_dict[language][t]
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
			results.append(majority) 
		except:
			results.append("NaN")

	total_sentences = len(dev_corpus)
	nas = 0
	accuracy = 0
	for g,r in zip(gold_labels_list,results):
		if r == "NaN":
			nas += 1
		elif r==g:
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
			trigrams = []
			for n,word in enumerate(sentence):
				if n > 1:
					trigrams.append((sentence[n-2],sentence[n-1],word))
			tetragrams = []
			for n,word in enumerate(sentence):
				if n > 2:
					tetragrams.append((sentence[n-3],sentence[n-2],sentence[n-1],word))
			language_probability_dict = {}
			for language,ngrams in tri_freq_dict.items():
				probabilities = []
				try:
					initial_prob = ngrams[trigrams[0]]
					probabilities.append(initial_prob)
				except:
					continue
				for t in tetragrams:
					try:
						transitional_prob = tetra_freq_dict[language][t]
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