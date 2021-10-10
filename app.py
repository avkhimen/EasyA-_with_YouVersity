from flask import Flask
from flask import request
from flask import render_template
from youtube_transcript_api import YouTubeTranscriptApi
from pprint import pprint
import json
import nltk
from pprint import pprint
from nltk.tokenize import word_tokenize
import os
import yake
from time import strftime
from time import gmtime

def get_keywords(video_id):

	unprocessed_text = YouTubeTranscriptApi.get_transcript(video_id)

	total_time = unprocessed_text[-1]['start'] + unprocessed_text[-1]['duration']

	numOfKeywords = 10

	os.remove("sample.txt")
	for item in unprocessed_text:
	    list_of_words = word_tokenize(item['text'])
	    new_string=' '.join(str(i) for i in list_of_words)
	    
	    file_object = open('sample.txt', 'a')
	    file_object.write(new_string)
	    file_object.close()       
	file = open("sample.txt")
	line = file.read().replace("\n", " ")
	file.close()

	incr = int(len(line)/numOfKeywords)

	keywords = []
	for i in [*range(numOfKeywords)]:
		text = line[i*incr : (i+1)*incr]

		text = (f'"{text}"')

		deduplication_thresold = 0.5
		max_ngram_size=1

		custom_kw_extractor = yake.KeywordExtractor(n=max_ngram_size, dedupLim=deduplication_thresold, top=1, features=None)
		keywords_from_section = custom_kw_extractor.extract_keywords(text)
		mins = str(strftime("%M:%S", gmtime(int((int(((i)*incr/len(line))*total_time))))))
		keywords_from_section_with_time = (keywords_from_section[0][0], mins, 'https://www.youtube.com/watch?v=' + str(video_id) + '&t=' + str(int(((i)*incr/len(line))*total_time)) + 's')
		keywords.append(keywords_from_section_with_time)

	#print(keywords)

	keywords = keywords[1:]
	keywords = keywords[:-1]

	return keywords

app = Flask(__name__, template_folder="templates")

def reverse(text):
    rev = ''
    for i in range(len(text), 0, -1):
        rev += text[i-1]
    return rev

@app.route("/")
def index():
    url_of_webpage = request.args.get("url_of_webpage", "")
    if url_of_webpage:
        topics = get_topics(url_of_webpage)
        return render_template('display_topics.html', topics=topics)
    else:
    	return render_template('home.html')
    
def get_topics(url_of_webpage):
	"""Function that does something"""
	video_id = ''
	for letter in reversed(url_of_webpage):
		if letter != '=':
			video_id += letter
		else:
			break
	video_id = reverse(video_id)
	keywords = get_keywords(video_id)
	return keywords

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)