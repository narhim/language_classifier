import re 
class extract_features:
	def __init__(self,path):
		self.path = path
		self.all = self._read_file()
		self.all_cleaned = self._tokenize()

	def _read_file(self):
		'''Reads file and return list of list[text,language_id]'''
		file = open(self.path,"r")
		all_text_lan = []
		for l in file:
			text_language =re.split("\t",l) #Separate text from language id
			clean_text_language = [text_language[0],text_language[1].strip()] #Remove \n from language id
			all_text_lan.append(clean_text_language)
		return all_text_lan	

	def _tokenize(self):
		'''Tokenizes each text. Return list of [list_of_tokens,language_id]'''
		all_cleaned = []
		for text_id in self.all:
			clean_text = [] #List to store stripped and cleaned text. 
			#Separate characters by delimiters defined in regex.
			s = re.split(' |[.] |[.]{2,}|[:]|[;]|[\']|["]|[„]|[‟]|[”]|[<]+|[>]+|[(]|[)]|[\[]|[\]]|[¿]|[?]|[¡]|[!]',text_id[0])
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
						clean_text.append(numbers[0].lower())
						clean_text.append(numbers[1].lower())
				
					#cat-dog
					elif re.search('[a-z]+-[a-z]+',w,flags=re.IGNORECASE):
						clean_text.append(w.lower())

					#45-ben
					elif re.search('\d+-\D+',w):
						numbers = re.split('-',w)
						clean_text.append(numbers[0].lower())
						clean_text.append(numbers[1].lower())
					#-32,9
					elif re.match('-\d+',w):
						clean_text.append(w)
					#alt- (from (alt-)griechisch)
					elif re.search('[a-z]-',w,flags=re.IGNORECASE):
						clean = w.strip('-')
						clean_text.append(clean.lower())
					#-word
					elif re.match('-\w+',w):
						clean = w.strip('-')
						clean_text.append(clean.lower())
					#45-
					elif re.match('\d+-',w):
						clean = w.strip('-')
						clean_text.append(clean.lower())
					#-%45 and -«word
					elif re.match('[-%\d+]|[-«\w+]',w):
						clean = w.strip('[-%]|[-«]')
						clean_text.append(clean.lower())
					#Avoid "-".
					elif re.match('^-$',w):
						continue
				elif (w == '/') or (w=="“"):
					continue
				elif re.search('[a-z]\/',w,flags=re.IGNORECASE):
					splitted = w.split('/')
					clean_text.append(splitted[0].lower())
					clean_text.append(splitted[1].lower())
				elif re.search('\d[.]\d',w):
					clean_text.append(w.lower())
				#avoid the second type of hyphen found in raw text.
				elif re.match('–',w):
						continue
				#If none of the conditions above apply, simply lower and apply.
				else:
					clean_text.append(w.lower())
			all_cleaned.append([clean_text,text_id[1]])
		return all_cleaned
		
	def _build_ngrams(self):
		'''Build 1,2,3,4,5,6-grams and return them to main together in a list.'''
		unigrams = []
		bigrams = []
		trigrams = []
		tetragrams = []
		pentagrams = []
		sextagrams = []
		for text_id in self.all_cleaned:
			for n,word in enumerate(text_id[0]):
				unigrams.append(word)
				if n >0:
					bigrams.append((word,text_id[0][n-1]))
				if n > 1:
					trigrams.append((word,text_id[0][n-1],text_id[0][n-2]))
				if n > 2:
					tetragrams.append((word,text_id[0][n-1],text_id[0][n-2],text_id[0][n-3]))
				if n > 3:
					pentagrams.append((word,text_id[0][n-1],text_id[0][n-2],text_id[0][n-3],text_id[0][n-4]))
				if n > 4:
					sextagrams.append((word,text_id[0][n-1],text_id[0][n-2],text_id[0][n-3],text_id[0][n-4],text_id[0][n-5]))
		ngrams = [unigrams,bigrams,trigrams,tetragrams,pentagrams,sextagrams]
		return ngrams

