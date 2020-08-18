import re
import math
import datetime as dat
from word2number import w2n


def url_to_domain(word: str, check=False):
    """
    Extracts domain from url.
    :param word: str
    :param check: bool - used to check if given
    string contains url.
    :return: str
    """
    url_extract = re.compile(r'(?:[-a-zA-Z0-9@:%_\+.~#?&//=]*)?(?:https?:\/\/)'
                             r'(?:[^@\n]+@)?(?:www\.)?([^:\/\n?]+)(?:[-a-zA-Z0'
                             r'-9@:%_\+.~#?&//=]*)?')
    if check:
        return url_extract.match(word)
    return url_extract.findall(word)[0]


def word_to_num(word: str) -> str:
    """
    Tries to convert word to number
    works only with English words
    :param word: str
    :return: str
    """
    try:
        num = str(w2n.word_to_num(word))
    except ValueError:
        # logging.debug('Cannot convert word to number.')
        return word
    return num


def delete_special_characters(msg: str) -> str:
    """
    Substitutes symbols with spaces.
    :param msg: str
    :return: str
    """
    symbols = re.compile(r"[-!$%^&*()_+|~=`{}\[\]:';<>?,ʼ\/]|[^\w]")
    return re.sub(symbols, ' ', msg)


def delete_apostrophes(msg: str) -> str:
    """
    Deletes apostrophes, curly quotes, quotes
    :param msg: str
    :return: str
    """
    out_msg = re.sub(r"`'ʼ", '', msg)
    return re.sub(r'"', '', out_msg)


def prepare_message(msg: str) -> str:
    """
    Makes preparation for the given message.
    :param msg: str
    :return: str
    """
    out_msg = []
    for word in str(msg).split():
        if url_to_domain(word, check=True):
            out_msg.append(url_to_domain(word))
        else:
            word = word_to_num(word)
            out_msg.append(delete_special_characters(word))
    return re.sub(r'\s\s+', ' ', ' '.join(out_msg))


def convert(date_info: str):
    """
    Converts string with symbols to datetime obj.
    :param date_info: str
    :return: dat.datetime()
    """
    date = date_info[:10].split('-') + date_info[11:19].split(':')
    return dat.datetime(*[int(x) for x in date])


def round_to_decimal(num):
    """
    Rounds given value to be divisible by 10
    :param num:
    :return:
    """
    return int(math.ceil(num / 100.0)) * 100


def add_reply_time(data):
    """
    Adds reply time between two users column @ given DataFrame (data)
    :param data: DataFrame
    :return: DataFrame
    """
    data['reply_time'] = 0
    i = k = data['id'].count() - 1
    msg_counter = 0
    while i > 0 and k > 0:
        sender = data['from_id'][i]
        j = i
        while sender == data['from_id'][j]:
            j -= 1
        if j <= 1:
            break
        recipient = data['from_id'][j]
        time_diff = (convert(data['date'][j]) - convert(data['date'][i])).total_seconds()
        data['reply_time'][i] += time_diff
        k = j
        msg_counter += 1
        while recipient == data['from_id'][k]:
            k -= 1
        i = k + 1
    return data


def get_reply_frequency(data):
    """
    Counts number of messages with ~same reply_time
    :param data: DataFrame
    :return: DataFrame
    """
    reply_frequency = {}
    for i in data.index:
        reply_time = round_to_decimal(int(data['reply_time'][i]))
        if not reply_frequency.get(reply_time):
            reply_frequency.setdefault(reply_time, 1)
        else:
            reply_frequency[reply_time] += 1
    return reply_frequency


def add_subdialogs_ids(data):
    """
    Adds subdialog id column @ given DataFrame (data),
    based on calculated time between subdialogs:
    (( length of list of reply times rounded to be divisible by 10 sorted
    and reversed) / 100) * 40, which is the index of minimum subdialog time.
    Note: in DataFrame reply_time column should be.
    :param data: DataFrame
    :return: DataFrame
    """
    subdialog_count = 1
    data['subdialog_id'] = ''
    reply_frequency = get_reply_frequency(data)
    min_delay = sorted(list(reply_frequency.keys()))[-(round((len(reply_frequency) / 100) * 40))]
    for i in data.index:
        reply_time = data['reply_time'][i]
        if reply_time > min_delay and reply_time:
            subdialog_count += 1
        data['subdialog_id'][i] = subdialog_count
    return data
