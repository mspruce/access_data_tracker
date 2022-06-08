import streamlit as st
import pandas as pd
#from sqlalchemy import create_engine
#from config import DBConfig
import datetime
import altair as alt
from wordcloud import WordCloud
from wordclouder import *
import streamlit.components.v1 as components
import requests
from streamlit_plotly_events import plotly_events

#@st.experimental_memo
#@st.cache(allow_output_mutation=True, show_spinner=False)
#def get_con():
    #return create_engine('mysql+pymysql://{}:{}@{}/twitter_sqlalc'.format(DBConfig.USER, DBConfig.PWORD, DBConfig.HOST),
                         #convert_unicode=True)

#@st.experimental_memo(show_spinner=True)
#@st.cache(allow_output_mutation=True, show_spinner=True, ttl=5*60)
#def get_data():
    #timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #df = pd.read_sql_table('tweets', get_con())
    #df = df[~df['body'].str.startswith('RT')]
    #df = df.rename(columns={'body': 'Tweet', 'tweet_date': 'Timestamp',
                            #'followers': 'Followers', 'sentiment': 'Sentiment',
                            #'keyword': 'Subject'})
    #df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    #df = df.sort_values(by='Timestamp')
    #return df, timestamp

#@st.experimental_memo(show_spinner=True)
#@st.cache(allow_output_mutation=True, show_spinner=True, ttl=5*60)
#def get_data_RT():
    #timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #df = pd.read_sql_table('tweets', get_con())
    #df = df.rename(columns={'body': 'Tweet', 'tweet_date': 'Timestamp',
                            #'followers': 'Followers', 'sentiment': 'Sentiment',
                            #'keyword': 'Subject'})
    #return df, timestamp
    
@st.experimental_memo(show_spinner=True)
#@st.cache(allow_output_mutation=True, show_spinner=True, ttl=5*60)
def get_data_csv(csv_file):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    df = pd.read_csv(csv_file, sep = ';', lineterminator='\r', encoding = 'utf-8')
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df = df.sort_values(by='Timestamp')
    return df, timestamp


@st.cache(show_spinner=True)
def filter_by_date(df, start_date, end_date):
    df_filtered = df.loc[(df.Timestamp.dt.date >= start_date) & (df.Timestamp.dt.date <= end_date)]
    return df_filtered


@st.cache(show_spinner=True)
def filter_by_subject(df, subjects):
    return df[df.Subject.isin(subjects)]
    
@st.cache(show_spinner=True)
def filter_by_keyword(df, keyword):    
	df_filtered = df[df['Tweet'].str.contains(keyword)]
	return df_filtered


@st.cache(show_spinner=True)
def count_plot_data(df, freq):
    #plot_df = df.set_index('Timestamp').groupby('Subject').resample(freq).id.count().unstack(level=0, fill_value=0)
    plot_df = df.set_index('Timestamp').resample(freq).id.count()
    plot_df.index.rename('Date', inplace=True)
    #plot_df = plot_df.rename_axis(None, axis='columns')
    return plot_df


@st.cache(show_spinner=True)
def sentiment_plot_data(df, freq):
    #plot_df = df.set_index('Timestamp').groupby('Subject').resample(freq).Sentiment.mean().unstack(level=0, fill_value=0)
    plot_df = df.set_index('Timestamp').resample(freq).Sentiment.mean()
    plot_df.index.rename('Date', inplace=True)
    #plot_df = plot_df.rename_axis(None, axis='columns')
    return plot_df
		
@st.cache(show_spinner=True)
def get_hashtags(df):
	df_hashtags = df.Tweet.str.extractall(r'(\#\w+)')[0].value_counts().rename_axis('hashtag').reset_index(name='tweet count')
	return df_hashtags
	
@st.cache(show_spinner=True)
def top_daily_tweets(df):
	df = df.sort_values(['Followers'], ascending=False).head(10)
	return df

@st.cache(show_spinner=True)
class Tweet(object):
	def __init__(self, tid, embed_str=False):
		if not embed_str:
			try:
				# Use Twitter's oEmbed API
				# https://dev.twitter.com/web/embedded-tweets
				api = 'https://publish.twitter.com/oembed?url=https://twitter.com/XXX/status/'+str(tid)
				response = requests.get(api)
				self.text = response.json()["html"]
			except:
				return "<blockquote class='missing'>This tweet is no longer available.</blockquote>"
		else:
			self.text = tid

	def _repr_html_(self):
		return self.text

	def component(self):
		return components.html(self.text, height=600)

@st.cache(show_spinner=True)
def get_embed_codes(tid):
	try:
		result = requests.get('https://publish.twitter.com/oembed?url=https://twitter.com/XXX/status/'+tid)
		return result.json()["html"]
	except:
		return "<blockquote class='missing'>This tweet is no longer available.</blockquote>";

st.set_page_config(layout="wide", page_title='Climate Change Tweets')
col1, mid, col2 = st.columns([3,1,3])
col1.image("/Users/ms886/access_data_tracker/images/ACCESS22.png")
mid.write(" ")
col2.image("/Users/ms886/access_data_tracker/images/ESRC_logo.png")
st.write(
    """Welcome to the [ACCESS project](https://greenfutures.exeter.ac.uk/access/) social media tracker, 
     which provides a visualisation of social media discussion on environmental issues, such as climate change and net zero.
    """)
st.write(
	"""Below is a summary of tweets containing the term **climate change** or **climatechange**.
	""")

#retweets_option = st.sidebar.checkbox('Include retweets')

#if retweets_option:
	#data, timestamp = get_data_RT()
#else:
	#data, timestamp = get_data()
	
#data, timestamp = get_data()

csv_file = 'climatechange_AprMay22.csv'
data, timestamp = get_data_csv(csv_file)

date_options = data.Timestamp.dt.date.unique()
#start_date_option = st.sidebar.selectbox('Select Start Date', date_options, index=0)
#end_date_option = st.sidebar.selectbox('Select End Date', date_options, index=len(date_options)-1)
start_date_option, end_date_option = st.sidebar.date_input('Select Dates', min_value=date_options.min(), max_value=date_options.max(), value=(date_options.max()-datetime.timedelta(days=30),date_options.max()))
#date_selection = pd.to_datetime(date_selection)
#start_date_option = date_selection[0]
#end_date_option = date_selection[1]

#keywords = data.Subject.unique()
#keyword_options = st.sidebar.multiselect(label='Subjects to Include:', options=keywords.tolist(), default=keywords.tolist())

keyword_options = st.sidebar.text_input(label='Keyword search:', key='keyword').lower()


data_daily = filter_by_date(data, start_date_option, end_date_option)

#data_subjects = data[data.Subject.isin(keyword_options)]
data_subjects = filter_by_keyword(data_daily, keyword_options)

st.header('Climate change on Twitter')
c = st.container()
st.write('Keyword(s) searched: {}'.format(keyword_options))
c.write('Total tweet count: {}'.format(data_subjects.shape[0]))
c.write('Data last loaded {}'.format(timestamp))

plot_freq_options = {
    'Daily': 'D',
    'Four Hourly': '4H',
    'Hourly': 'H'
}
plot_freq_keys = list(plot_freq_options.keys())
plot_freq_values = list(plot_freq_options.values())
if (end_date_option - start_date_option).days <= 1:
	plot_freq_box = st.sidebar.selectbox(label='Plot Frequency:', options=plot_freq_keys, index=2)
	plot_freq = plot_freq_options[plot_freq_box]
else:
	plot_freq_box = st.sidebar.selectbox(label='Plot Frequency:', options=plot_freq_keys, index=0)
	plot_freq = plot_freq_options[plot_freq_box]

csv = data_subjects.to_csv().encode('utf-8')
st.download_button("Download data as CSV", data=csv, file_name='tracker_data.csv', mime='text/csv')

with st.expander("Tweet Volumes", expanded=True):
	heading1 = plot_freq_keys[plot_freq_values.index(plot_freq)] + " Tweet Volumes"
	st.subheader(heading1)
	plotdata = count_plot_data(data_subjects, plot_freq)
	st.line_chart(plotdata)

with st.expander("More info on Tweet Volumes plot"):
	st.write("""
		The chart above shows the number of tweets containing the term **climate change** or
		**climatechange** for the dates specified.
		
		Use the *Plot Frequency* dropdown in the sidebar to change the view to show the number
		of tweets daily, 4-hourly or hourly.
	""")

with st.expander("Sentiment", expanded=True):
	heading2 = plot_freq_keys[plot_freq_values.index(plot_freq)] + " Tweet Sentiment"
	st.subheader(heading2)
	plotdata2 = sentiment_plot_data(data_subjects, plot_freq)
	st.line_chart(plotdata2)

with st.expander("More info on Sentiment plot"):
	st.write("""
		The chart above shows the average sentiment of tweets containing the term **climate change** or
		**climatechange** for the dates specified.
		
		Sentiment is shown on a scale -1 to 1 where -1 is most negative and 1 is most positive.
		It is calculated using the Vader Sentiment python package (<https://pypi.org/project/vaderSentiment/>)
		which is a lexicon and rule-based sentiment analysis tool that is specifically attuned to sentiments
		expressed in social media.
		
		Use the *Plot Frequency* dropdown in the sidebar to change the view to show the number
		of tweets daily, 4-hourly or hourly.
	""")

#col1, col2 = st.columns(2)

with st.expander("Trending Hashtags", expanded=True):
	top_hashtags = get_hashtags(data_subjects).head(10)
	st.subheader("Most used hashtags")
	st.write("During the dates selected, these are the most used hashtags in climate change tweets")
	#st.dataframe(top_hashtags)
	bar_chart = alt.Chart(top_hashtags).mark_bar().encode(
		x='tweet count:Q',
		y=alt.Y('hashtag:O', sort='-x')
	)
	st.altair_chart(bar_chart)

with st.expander("Create Wordcloud"):
	st.subheader('Wordcloud of Tweets')
	if st.checkbox('Generate wordcloud - may take a few minutes'):
		# display loading sign whie making the wordcould
		st.spinner()
		with st.spinner(text='We\'re building the wordcloud. One moment...'):
			#figure = make_wordcloud(st.session_state.all_stopwords, data['Tweet'])
			#st.pyplot(figure)
			wordcloud = make_wordcloud(make_stopwords(), data_subjects['Tweet'])
		st.pyplot(wordcloud)

#with st.expander("Influential Tweets"):
	#st.subheader('Influential Tweets')
	#st.table(top_daily_tweets[['Tweet', 'Timestamp', 'Followers']].reset_index(drop=True))

#with st.expander("Recent Tweets"):          
	#st.subheader('Recent Tweets')
	#st.table(data_subjects[['Tweet', 'Timestamp']].sort_values(['Timestamp'], ascending=False).
               #reset_index(drop=True).head(10))

top_daily_tweets = top_daily_tweets(data_subjects)

#st.write(top_daily_tweets.iloc[0]['tweet_id'])

with st.expander("Twitter feed", expanded=True):             
	st.subheader("Most influential tweets")
	st.write("Tweets from users with the most followers during the dates selected")
	for i in range(len(top_daily_tweets)):
		#tweet_res = get_embed_codes(top_daily_tweets.iloc[i]['tweet_id'])
		#st.write(components.html(,height=700, scrolling=True))
		t = Tweet(top_daily_tweets.iloc[i]['tweet_id']).component()

#locations = pd.DataFrame(pd.eval(data_daily[data_daily['location'].notnull()].location), columns=['lon', 'lat'])
#st.map(locations)
