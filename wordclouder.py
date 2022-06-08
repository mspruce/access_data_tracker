import matplotlib.pyplot as plt 
import re
from wordcloud import WordCloud


def make_stopwords():
	text_file = open("/Users/ms886/access_data_tracker/streamlit-twitter-stream-master/all_stopwords.txt", "r")
	stopwords_list = text_file.read().split("\n")
	text_file.close()
	return set(stopwords_list)

def preprocess(out):
	text = " ".join(out)
	text = re.sub(pattern=r"http\S+",repl="",string=text.lower())
	text = re.sub(pattern=r"@\S+",repl="",string=text)
	return text

def make_wordcloud(st_words, out):
	text = preprocess(out)
	wordcloud = WordCloud(width=1800, height=1400,stopwords=st_words,
						max_font_size=250, max_words=100, background_color="white",
						colormap='copper', collocations=True).generate(text)  

	fig = plt.figure(figsize=(18,12))
	plt.imshow(wordcloud, interpolation="bilinear")
	plt.axis("off")
	return fig