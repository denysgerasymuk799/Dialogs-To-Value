import pandas as pd


def get_old_ua_tonality_dict(dict_path="dicts/tone-dict-uk.tsv") :
    """
    Read dictionary of ukrainian words tonality and
    return is a a python dict
    """
    tonality_data_ua_old = pd.read_csv(dict_path, sep="\t")
    tonality_dict_ua_old = dict(zip(tonality_data_ua_old.iloc[:, 0], tonality_data_ua_old.iloc[:, 1] / 2))

    return tonality_dict_ua_old


def get_ua_tonality_dict(dict_path="dicts/tone-dict-ua.csv") :
    """
    Read dictionary of ukrainian words tonality and
    return is a a python dict
    """
    sentiment_data = pd.read_csv(dict_path)
    sentiment_dict = dict(zip(sentiment_data.iloc[:, 1], sentiment_data.iloc[:, 3]))

    return sentiment_dict


def get_ua_tonality_dict_combined(dict_path="dicts/tone-dict-uk-full.csv"):
    """
    Get combined ua tone dictionary
    :param dict_path:
    :return:
    """
    sentiment_data = pd.read_csv(dict_path)
    sentiment_dict = dict(zip(sentiment_data.iloc[:, 0], sentiment_data.iloc[:, 1]))

    return sentiment_dict


def get_ru_tonality_dict(dict_path="dicts/tone-dict-ru.csv") :
    """
    Read dictionary of russian words tonality and
    return is a a python dict
    """
    sentiment_data = pd.read_csv(dict_path, sep=";")
    sentiment_dict = dict(zip(sentiment_data.iloc[:, 0], sentiment_data.iloc[:, 2]))

    return sentiment_dict


def get_dict_intersection(dict1, dict2) :
    """
    Get intersection of words of two distinct dictionaries.
    Create a dataframe  *word* :  *word_sentiment_difference*
    Save it to a file
    """
    dict1_keys = set(dict1.keys())
    dict2_keys = set(dict2.keys())
    intersected_set = dict1_keys.intersection(dict2_keys)

    intesected_dataframe = pd.DataFrame(columns=['word', 'sentiment_difference'])

    while intersected_set :
        word = intersected_set.pop()
        sent_diff = abs(dict1[word] - dict2[word])
        intesected_dataframe = intesected_dataframe.append({'word' : word,
                                                            'sentiment_difference' : sent_diff},
                                                           ignore_index=True)

    intesected_dataframe.to_csv("dicts/ukr-tone-dict-intersection", index=False)


def combine_dict(dict_primary, dict_secondary, save_path="dicts/tone-dict-uk-full.csv") :
    """
    Combine two dictionaries.
    If words intersect, word of a primary dict replace the one of a
    secondary
    """
    dict_secondary.update(dict_primary)
    data = pd.DataFrame({'word' : list(dict_secondary.keys()),
                         'sentiment' : list(dict_secondary.values())})

    data.to_csv(save_path, index=False)

# new = get_ua_tonality_dict("../dicts/tone-dict-ua.csv")
# old = get_old_ua_tonality_dict("../dicts/tone-dict-uk.tsv")
# combine_dict(new, old, "../dicts/tone-dict-uk-full.csv")
