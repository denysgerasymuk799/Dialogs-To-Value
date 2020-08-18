import re
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


def prepare_messages(data):
    """
    Makes preparation for the given message.
    :param data: DataFrame
    :return: None
    """
    for i in data.index:
        out_msg = []
        for word in str(data.loc[i, 'message']).split():
            if url_to_domain(word, check=True):
                out_msg.append(url_to_domain(word))
            else:
                word = word_to_num(word)
                out_msg.append(delete_special_characters(word))
        data.loc[i, 'message'] = re.sub(r'\s\s+', ' ', ' '.join(out_msg))
