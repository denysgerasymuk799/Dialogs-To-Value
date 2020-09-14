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


# (TODO) structure
0. short description and images
1. how to install dependency, and prepare env
2. instructions how to use our tool: download data, prep it and short one sentence description for each module
3. team and contributors