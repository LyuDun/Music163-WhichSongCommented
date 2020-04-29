import requests
import json
import time


class Music163_Spider(object):

    def __init__(self):
        self.headers = {
            'host': 'music.163.com',
            'Referer': 'http://music.163.com/search/',
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36')
        
        }
        self.cookies = {'appver': '1.5.2'}

    def get_playlist_detail(self, playlist_id):
        url = 'http://music.163.com/api/playlist/detail'
        payload = {'id': playlist_id}

        r = requests.get(url, params=payload, headers=self.headers,
                         cookies=self.cookies)

        playlist_detail = r.json()['result']['tracks']
        user_id = r.json()['result']['creator']['userId']

        return playlist_detail, user_id

    def from_playlist_get_song_list(self, playlist_id):
        playlist_detail, user_id = self.get_playlist_detail(playlist_id)
        songlist = []
        for song_detail in playlist_detail:
            song = {}
            song['id'] = song_detail['id']
            song['name'] = song_detail['name']
            artists_detail = []
            for artist in song_detail['artists']:
                artist_detail = {}
                artist_detail['name'] = artist['name']
                artist_detail['id'] = artist['id']
                artists_detail.append(artist_detail)
            song['artists'] = artists_detail
            songlist.append(song)

        return songlist, user_id

    def get_song_comments(self, song_id, offset=0, total='false', limit=100):
        url = ('http://music.163.com/api/v1/resource/comments/R_SO_4_{}/'
               ''.format(song_id))
        payload = {
            'rid': 'R_SO_4_{}'.format(song_id),
            'offset': offset,
            'total': total,
            'limit': limit
        }

        r = requests.get(url, params=payload, headers=self.headers,
                         cookies=self.cookies)

        return r.json()

    def get_total_comments(self, song_id, user_id):
        try:
            comments = self.get_song_comments(song_id)['comments']
        except:
            print('遭到网易云反扒虫系统，建议过段时间再试')
            return False

        comments_list = []
        offset = 0
        while comments:
            for comment in comments:
                comment_detail = {}
                '''
                comment_detail['user_name'] = comment['user']['nickname']
                comment_detail['user_id'] = comment['user']['userId']
                comment_detail['content'] = comment['content']
                comment_detail['time'] = comment['time']
                comments_list.append(comment_detail)
                '''
                if user_id == comment['user']['userId']:
                    comment_detail['user_name'] = comment['user']['nickname']
                    comment_detail['user_id'] = comment['user']['userId']
                    comment_detail['content'] = comment['content']
                    comment_detail['time'] = comment['time']
                    comments_list.append(comment_detail)
                    print(comment_detail['content'])
            time.sleep(0.5)
            offset = offset + 100
            comments = self.get_song_comments(song_id,
                                              offset=offset)['comments']

        return comments_list


if __name__ == '__main__':

    spider = Music163_Spider()

    songlist_id = input("请输入歌单ID:")
    songlist, user_id = spider.from_playlist_get_song_list(songlist_id)

    songcomments = []
    for song in songlist:
        song_id = song['id']
        songcomments = spider.get_total_comments(song_id, user_id)
        if songcomments is False:
            break
        elif len(songcomments):
            for comment in songcomments:
                print('{} ta在歌曲:<{}> 下评论了{}'.format(
                    comment['time'], comment['content']))
        else:
            print('ta在歌曲<{}> 下没有评论'.format(song['name']))
