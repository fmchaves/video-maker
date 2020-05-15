def get_search_term_content(search_term: str, search_lang: str, credentials: dict) -> dict:

	# Import Algorithmia package
	try:
		import Algorithmia
	except ImportError as err:
		raise err
	
	# Creates a dictionary with the search information for Algorithmia API
	input_search = {"articleName": search_term, "lang": search_lang}

	# Search Wikipedia
	try:
		client = Algorithmia.client(credentials['api_key'])
		algo = client.algo(credentials['url'])
		algo.set_options(timeout=300)
		response = algo.pipe(input_search).result
	except:
		print('Consider the following problems:')
		print(' 1) There is a problem with Algorithmia credentials')
		print(' 2) For some unknown reason, the search could not be done')        
		response = {}       
	finally:
		return response

def divide_into_sentences(text: str, lang: str) -> list:	  

    # Divide text into sentences
	try:
		import pysbd
		seg = pysbd.Segmenter(language=lang, clean=False)
		sentences = seg.segment(text)
	except:
		print('It was not possible to divide the text into sentences.')
		sentences = []
	finally:
		return sentences

def get_keywords(sentence: str, lang: str, credentials: dict) -> list:  
    
	# Import IBM WATSON modules
	try:		
		from ibm_watson import NaturalLanguageUnderstandingV1
		from ibm_cloud_sdk_core.authenticators import IAMAuthenticator    
		from ibm_watson.natural_language_understanding_v1 import Features, KeywordsOptions	
	except ImportError as err:
		raise err

    # Authenticating the service
	authenticator = IAMAuthenticator(credentials['api_key'])
	natural_language_understanding = NaturalLanguageUnderstandingV1(
		version='2019-07-12',
		authenticator=authenticator
	)

	# Sets url for the service
	natural_language_understanding.set_service_url(credentials['url'])

	try:
		response = natural_language_understanding.analyze(text=sentence, language=lang, features=Features(keywords=KeywordsOptions(limit=3))).get_result()
	except Exception as e:
		print(e)
		response = []
	else:
		response = [keyword_dict.get('text') for keyword_dict in response.get('keywords')]
	finally:    
		return response

    

def run(filename: str):
	
	import os, json	
	from robots.rw_robot.robot import read_file, write_file

	# Import search content
	try:
		search_content = read_file(filename=filename)
	except Exception as e:
		raise e

	# Load credentials.json
	file_path = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'credentials.json')
	credentials = read_file(filename=file_path)

	# Search Wikipedia
	must_have = (
		search_content.get('search_term'),
		search_content.get('search_lang')
	)
	if all(must_have):
		print(f'Searching {search_content["search_term"]} on Wikipedia...')
		response = get_search_term_content(
			search_term=search_content['search_term'],
			search_lang=search_content['search_lang'],
			credentials=credentials['algorithmia']
			)
		
		if response :
			search_content['summary'] = response.get('summary')
			search_content['title'] = response.get('title')
			search_content['url'] = response.get('url')
			search_content['last_proccess'] = 'The content was searched on wikipedia.'

			# Save data structure
			write_file(
				filename=filename, 
				content=search_content
			)

	# Divide text into sentences
	must_have = (
		search_content.get('summary'),
		search_content.get('search_lang')
	)
	if all(must_have):
		response = divide_into_sentences(
			text=search_content['summary'],
			lang=search_content['search_lang']
		)

		if response:
			search_content['sentences'] = response
			search_content['last_proccess'] = 'The summary was divided into sentences.'
		
			# Save data structure
			write_file(
				filename=filename, 
				content=search_content
			)

	# Get keywords for each sentence
	must_have = (
		search_content.get('sentences'),		
		search_content.get('search_lang')
	)
	if all(must_have):
		sentences_keywords = []
		for sentence in search_content['sentences']:
			response = get_keywords(
				sentence=sentence,
				lang=search_content['search_lang'],
				credentials=credentials['ibm-watson']
			)			
		
			sentences_keywords.append({'sentence': sentence, 'keywords': response})

		search_content['items'] = sentences_keywords
		del search_content['sentences']
		search_content['last_proccess'] = 'Keywords were extracted for each sentence.'		
		# Save data structure
		write_file(
			filename=filename,
			content=search_content		
		)