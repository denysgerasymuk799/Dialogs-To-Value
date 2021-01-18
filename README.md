# Telegram dialogs analysis
### 0. env preparation
0. install Python 3.7.4
1. pip install -r requirements.txt
2. pip install git+https://github.com/Desklop/Uk_Stemmer@master#egg=uk_stemmer

download Cube
it can take time: 50 dialogs with 100 messages = 42 min

## word_frequency_in_dialogs.ipynb

### Preparing
1) In console input: import nltk; nltk.download()

2) Install (or update) NLP-Cube with:
`pip3 install -U nlpcube`

3) Use telegram-data-collection/0_download_dialogs_list.py and 1_download_dialogs_data.py
to get some files to analyse (DO NOT forget to change global variables of paths to dirs at the beginning of the module)


# Dialogs to Value

![](https://img.shields.io/badge/-status:wip-5319e7.svg)
![](https://img.shields.io/github/license/damoklov/nasa.svg)
![](https://img.shields.io/github/languages/code-size/denysgerasymuk799/Dialogs-to-Value.svg)
![](https://img.shields.io/github/last-commit/denysgerasymuk799/Dialogs-to-Value.svg)
    
## Description: :sparkler:

One of the biggest repositories on Github for analyzing of Telegram messenger data and dialogs of Ukrainian and Russian languages
Helps to analyze user’s activity in Telegram:

1.	collect general statistics (online minutes per week, month, year, number of received or sent messages,
 people with whom and when communicate the most for each dialog).
2.	sentiment of messages. 
3.	tracking time and day when you get positive response from special person, so you can better know in what time write for special person to get positive response.
4.	finding the main topics of each subdialog in each chat


**Technologies**: Python, Pandas, Numpy, Plotly.


## Description of structure :pushpin:

- 0_data_preprocessing.py -- script to retrieve and save Telegram data for special USER_ID;

- 1_dialogs_sentiment_analysis.ipynb -- sentiment analysis of USER during special week;

![](sentiment_result.jpg)

- 2_calculate_members_statistics.ipynb -- code which collect general statistics (online minutes per week, month,
year, number of received or sent messages, people with whom and when communicate the most for each dialog);

![](fig_week_received_msgs.png)
![](fig_week_sent_msgs.png)

![](Weekly active minutes in Telegram.png)
![](Monthly active minutes in Telegram.png)

- 3_dialogs_analysis.ipynb -- analysis of each chat of USER and split it on dialogs;

- 4_dialogs_tf_idf.ipynb -- retrieving keywords with TF-IDF algo for each chat;

- 5_dialogs_lda.ipynb -- for each dialog, which we got before, generate topic based on LDA algo


# License:
[MIT](https://choosealicense.com/licenses/mit/)
