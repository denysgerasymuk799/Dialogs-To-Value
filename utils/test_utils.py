import unittest
import pandas as pd

from utils.dialog_manipulation import add_reply_time, add_subdialogs_ids, get_avg_subdialog_reply_time


class DialogManipulationTesting(unittest.TestCase):

    def test_get_avg_reply_time(self):
        """
        Testing of calculating average minimum reply time value
        for dividing for subdialogs.
        """
        reply_times = {1: [1, 2, 3, 4, 5],
                       2: list(range(10)),
                       3: [],
                       4: [1],
                       5: [1, 2],
                       6: [0, 0],
                       7: [-1, -1, -1]}

        self.assertEqual(get_avg_subdialog_reply_time(pd.DataFrame(reply_times[1], columns=['reply_btw_sender_time'])),
                         3, 'Basic  average diff sender reply time test.')
        self.assertEqual(get_avg_subdialog_reply_time(pd.DataFrame(reply_times[2], columns=['reply_btw_sender_time'])),
                         5, 'Basic  average diff sender reply time test.')

        # Should log ERROR: here
        with self.assertRaises(IndexError):
            get_avg_subdialog_reply_time(pd.DataFrame(reply_times[3], columns=['reply_btw_sender_time']))

        self.assertEqual(get_avg_subdialog_reply_time(pd.DataFrame(reply_times[4], columns=['reply_btw_sender_time'])),
                         1, '1 reply time test.')
        self.assertEqual(get_avg_subdialog_reply_time(pd.DataFrame(reply_times[5], columns=['reply_btw_sender_time'])),
                         2, '2 reply times test.')
        self.assertEqual(get_avg_subdialog_reply_time(pd.DataFrame(reply_times[6], columns=['reply_btw_sender_time'])),
                         0, 'Basic  average diff sender reply time test.')
        self.assertEqual(get_avg_subdialog_reply_time(pd.DataFrame(reply_times[7], columns=['reply_btw_sender_time'])),
                         -1, 'Basic  average diff sender reply time test.')

    def test_add_reply_time(self):
        """
        Tests addition of reply between own and different
        sender messages time values.
        """
        dates = {1: ['2020-02-20 00:00:30+00:00',
                     '2020-02-20 00:00:25+00:00',
                     '2020-02-20 00:00:20+00:00',
                     '2020-02-20 00:00:15+00:00',
                     '2020-02-20 00:00:10+00:00',
                     '2020-02-20 00:00:05+00:00',
                     '2020-02-20 00:00:00+00:00', ],

                 2: ['2020-02-20 00:00:45+00:00',
                     '2020-02-20 00:00:35+00:00',
                     '2020-02-20 00:00:30+00:00',
                     '2020-02-20 00:00:25+00:00',
                     '2020-02-20 00:00:15+00:00',
                     '2020-02-20 00:00:10+00:00',
                     '2020-02-20 00:00:00+00:00', ],

                 3: ['2020-02-20 00:00:45+00:00',
                     '2020-02-20 00:00:35+00:00',
                     '2020-02-20 00:00:30+00:00',
                     '2020-02-20 00:00:25+00:00',
                     '2020-02-20 00:00:15+00:00',
                     '2020-02-20 00:00:10+00:00',
                     '2020-02-20 00:00:00+00:00', ],

                 4: []
                 }
        from_ids = {1: ['1', '1', '1', '1', '1', '1', '1', ],
                    2: ['1', '2', '2', '2', '1', '1', '2'],
                    3: ['1', '3', '2', '2', '3', '1', '2'],
                    4: []
                    }

        df = pd.DataFrame(list(zip(from_ids[1], dates[1])), columns=['from_id', 'date'])
        add_reply_time(df)
        # print(df[['date','from_id', 'reply_btw_own_time', 'reply_btw_sender_time']])
        self.assertEqual(list(df['reply_btw_own_time']), [5, 5, 5, 5, 5, 5, 0], 'Testing equal 5 sec btw own msgs.')
        self.assertEqual(list(df['reply_btw_sender_time']), [0, 0, 0, 0, 0, 0, 0],
                         'Testing basic 5 sec btw diff sender msgs.')

        df = pd.DataFrame(list(zip(from_ids[2], dates[2])), columns=['from_id', 'date'])
        add_reply_time(df)
        # print(df[['date','from_id', 'reply_btw_own_time', 'reply_btw_sender_time']])
        self.assertEqual(list(df['reply_btw_own_time']), [0, 5, 5, 0, 5, 0, 0], 'Testing diff 5 sec btw own msgs')
        self.assertEqual(list(df['reply_btw_sender_time']), [10, 0, 0, 10, 0, 10, 0],
                         'Testing diff 5 sec btw diff sender msgs')

        df = pd.DataFrame(list(zip(from_ids[3], dates[3])), columns=['from_id', 'date'])
        add_reply_time(df)
        # print(df[['date', 'from_id', 'reply_btw_own_time', 'reply_btw_sender_time']])
        self.assertEqual(list(df['reply_btw_own_time']), [0, 0, 5, 0, 0, 0, 0],
                         'Testing diff 5 sec btw own msgs (3 users)')
        self.assertEqual(list(df['reply_btw_sender_time']), [10, 5, 0, 10, 5, 10, 0],
                         'Testing diff 5 sec btw diff sender msgs (3 users)')

        df = pd.DataFrame(list(zip(from_ids[4], dates[4])), columns=['from_id', 'date'])
        add_reply_time(df)
        # print(df[['date', 'from_id', 'reply_btw_own_time', 'reply_btw_sender_time']])
        self.assertEqual(list(df['reply_btw_own_time']), [],
                         'Testing diff 5 sec btw own msgs (0 users)')
        self.assertEqual(list(df['reply_btw_sender_time']), [],
                         'Testing diff 5 sec btw diff sender msgs (0 users)')

    def add_subdialogs_ids(self):
        """
        Testing addition of subdialog ids.
        """
        dates = {1: ['2020-02-20 00:00:09+00:00',
                     '2020-02-20 00:00:08+00:00',
                     '2020-02-20 00:00:07+00:00',
                     '2020-02-20 00:00:06+00:00',
                     '2020-02-20 00:00:05+00:00',
                     '2020-02-20 00:00:04+00:00',
                     '2020-02-20 00:00:03+00:00',
                     '2020-02-20 00:00:02+00:00',
                     '2020-02-20 00:00:01+00:00',
                     '2020-02-20 00:00:00+00:00', ],
                 #
                 # 2: ['2020-02-20 00:00:45+00:00',
                 #     '2020-02-20 00:00:35+00:00',
                 #     '2020-02-20 00:00:30+00:00',
                 #     '2020-02-20 00:00:25+00:00',
                 #     '2020-02-20 00:00:15+00:00',
                 #     '2020-02-20 00:00:10+00:00',
                 #     '2020-02-20 00:00:00+00:00', ],
                 #
                 # 3: ['2020-02-20 00:00:45+00:00',
                 #     '2020-02-20 00:00:35+00:00',
                 #     '2020-02-20 00:00:30+00:00',
                 #     '2020-02-20 00:00:25+00:00',
                 #     '2020-02-20 00:00:15+00:00',
                 #     '2020-02-20 00:00:10+00:00',
                 #     '2020-02-20 00:00:00+00:00', ],
                 #
                 # 4: []
                 }

        from_ids = {1: ['1', '2', '1', '2', '1', '2', '1', '2', '1', '2']}
        df = pd.DataFrame(list(zip(from_ids[1], dates[1])), columns=['from_id', 'date'])
        add_reply_time(df)
        add_subdialogs_ids(df)
        print(df)
