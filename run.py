import sys, os, pickle
import threading, time
import instapy
from socket import *

TBL_USE_ACCOUNT = 0
TBL_ID = 1
TBL_PW = 2
TBL_USE_LIKE = 3
TBL_USE_FOLLOW = 4
TBL_USE_COMMENT = 5
TBL_USE_FILTER = 6
TBL_HASHTAGS = 7
TBL_COMMENTS = 8
TBL_FILTERS = 9
TBL_REPEAT_CNT = 10
TBL_TAG_SHIFT = 11
TBL_SPEED = 12
TBL_MAX = 13

MODE_TAGRUN = 0
MODE_IDRUN = 1
MODE_UNFOLLOW1 = 2
MODE_UNFOLLOW2 = 3

PORT = 8081
CLIENT_SOCKET = socket(AF_INET, SOCK_STREAM)

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, func, args):
        super(StoppableThread, self).__init__()
        self._stop_event = threading.Event()
        self.func = func
        self.args = args

    def run(self):
        self.func(*self.args)

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

def receive(sock):
    while True:
        recvData = sock.recv(1024)
        command = recvData.decode('utf-8')
        if command.find("Terminate") != -1:
            break
        s = "[Server] %s" % command
        print(s)
    sock.close()
    # import subprocess
    # CREATE_NO_WINDOW = 0x08000000
    # subprocess.call('taskkill /F /IM chromedriver.exe', creationflags=CREATE_NO_WINDOW)
    sys.exit()

# run InstaPy function..
def startActivity(row=0,
                  accounts=None,
                  hashtags=None,
                  comments=None,
                  filters=None,
                  bHeadless=False):
    id = str(accounts[row][TBL_ID])
    pwd = str(accounts[row][TBL_PW])
    session = instapy.InstaPy(username=id, password=pwd, headless_browser=bHeadless,
                              show_logs=True)
    session.login()
    try:
        speed = int(accounts[row][TBL_SPEED])
        session.set_quota_supervisor(enabled=True,
                                     sleep_after=["likes", "comments", "follows", "unfollows",
                                                  "server_calls_h"], sleepyhead=True, stochastic_flow=True,
                                     notify_me=True,
                                     peak_likes=(42 + 8 * speed, 500 + 100 * speed),
                                     peak_comments=(13 + 2 * speed, 150 + 50 * speed),
                                     peak_follows=(13 + 2 * speed, 150 + 50 * speed),
                                     peak_unfollows=(13 + 2 * speed, 150 + 50 * speed),
                                     peak_server_calls=(None, 4700))

        session.set_skip_users(skip_private=True, private_percentage=100)

        # dont comment, unfollowing my follower list
        CLIENT_SOCKET.send("팔로워 목록 확인".encode('utf-8'))
        my_follwers = session.grab_followers(username=id, amount="full", live_match=True, store_locally=True)
        session.set_dont_include(my_follwers)

        if accounts[row][TBL_USE_COMMENT] and comments:
            valComments = []
            for col in range(1, 11):
                comment = comments[int(accounts[row][TBL_COMMENTS])][col]
                if not comment == 'None':
                    valComments.append(comment)
            if valComments:
                session.set_do_comment(enabled=True, percentage=40)
                session.set_comments(valComments)

        if accounts[row][TBL_USE_FILTER] and filters:
            valFilters = []
            for col in range(1, 11):
                filter = filters[int(accounts[row][TBL_FILTERS])][col]
                # print(hashtag)
                if not filter == 'None':
                    valFilters.append(filter)
            if valFilters:
                session.set_dont_like(tags=valFilters)

        if accounts[row][TBL_USE_LIKE] or \
                accounts[row][TBL_USE_FOLLOW]:
            valHashtags = []
            for col in range(1, 11):
                hashtag = hashtags[int(accounts[row][TBL_HASHTAGS])][col]
                # print(hashtag)
                if not hashtag == 'None':
                    valHashtags.append(hashtag)
            if valHashtags and accounts[row][TBL_USE_LIKE]:
                if accounts[row][TBL_USE_FOLLOW]:
                    session.set_do_follow(enabled=True, percentage=40)
                    CLIENT_SOCKET.send("좋아요/댓글/팔로우 실행".encode('utf-8'))
                for cnt in range(0, int(accounts[row][TBL_REPEAT_CNT])):
                    session.like_by_tags(tags=valHashtags, amount=int(accounts[row][TBL_TAG_SHIFT]),
                                         use_smart_hashtags=False)
                    CLIENT_SOCKET.send("좋아요/댓글/팔로우 완료".encode('utf-8'))
                    s = "좋아요: %d개, 댓글: %d개, 팔로우: %d개\n" % (session.liked_img,
                                                         session.commented, session.followed)
                    CLIENT_SOCKET.send(s.encode('utf-8'))
            else:
                CLIENT_SOCKET.send("좋아요/댓글/팔로우 실행".encode('utf-8'))
                for cnt in range(0, int(accounts[row][TBL_REPEAT_CNT])):
                    session.follow_by_tags(tags=valHashtags, amount=int(accounts[row][TBL_TAG_SHIFT]),
                                           use_smart_hashtags=False)
                    CLIENT_SOCKET.send("좋아요/댓글/팔로우 완료".encode('utf-8'))
                    s = "좋아요: %d개, 댓글: %d개, 팔로우: %d개\n" % (session.liked_img,
                                                         session.commented, session.followed)
                    CLIENT_SOCKET.send(s.encode('utf-8'))
        else:
                CLIENT_SOCKET.send("좋아요 사용에 체크해주세요.".encode('utf-8'))

        instapy.InstaPy.end_sub(session)
    except:
        raise(CLIENT_SOCKET.send("세선 실행 에러 발생".encode('utf-8')))

# unfollow1 InstaPy function..
def unfollowActivity1(row=0,
                  accounts=None,
                  bHeadless=False):
    id = str(accounts[row][TBL_ID])
    pwd = str(accounts[row][TBL_PW])
    session = instapy.InstaPy(username=id, password=pwd, headless_browser=bHeadless,
                              show_logs=True)
    session.login()
    try:
        # unfollow if not follow me
        CLIENT_SOCKET.send("팔로워 정리 실행".encode('utf-8'))
        session.unfollow_users(amount=120, nonFollowers=True, style="RANDOM",
                               unfollow_after=1 * 60 * 60, sleep_delay=100)
        s = "언팔로우: %d개\n" % (session.unfollowed)
        CLIENT_SOCKET.send(s.encode('utf-8'))
        CLIENT_SOCKET.send("팔로워 정리 완료".encode('utf-8'))

        instapy.InstaPy.end_sub(session)

    except:
        raise(CLIENT_SOCKET.send("세션 실행 에러 발생".encode('utf-8')))

# unfollow1 InstaPy function..
def unfollowActivity2(row=0,
                  accounts=None,
                  bHeadless=False):
    id = str(accounts[row][TBL_ID])
    pwd = str(accounts[row][TBL_PW])
    session = instapy.InstaPy(username=id, password=pwd, headless_browser=bHeadless,
                              show_logs=True)
    session.login()
    try:
        # unfollow if not follow me
        CLIENT_SOCKET.send("팔로워 정리 실행".encode('utf-8'))
        session.unfollow_users(amount=120, allFollowing=True, style="RANDOM",
                               unfollow_after=1 * 60 * 60, sleep_delay=100)
        s = "언팔로우: %d개\n" % (session.unfollowed)
        CLIENT_SOCKET.send(s.encode('utf-8'))
        CLIENT_SOCKET.send("팔로워 정리 완료".encode('utf-8'))

        instapy.InstaPy.end_sub(session)

    except:
        raise(CLIENT_SOCKET.send("세션 실행 에러 발생".encode('utf-8')))


def followerActivity(row=0,
                  accounts=None,
                  hashtags=None,
                  comments=None,
                  filters=None,
                  bHeadless=False):
    id = str(accounts[row][TBL_ID])
    pwd = str(accounts[row][TBL_PW])
    session = instapy.InstaPy(username=id, password=pwd, headless_browser=bHeadless,
                              show_logs=True)
    session.login()
    try:
        speed = int(accounts[row][TBL_SPEED])
        session.set_quota_supervisor(enabled=True,
                                     sleep_after=["likes", "comments", "follows", "unfollows",
                                                  "server_calls_h"], sleepyhead=True, stochastic_flow=True,
                                     notify_me=True,
                                     peak_likes=(42 + 8 * speed, 500 + 100 * speed),
                                     peak_comments=(13 + 2 * speed, 150 + 50 * speed),
                                     peak_follows=(13 + 2 * speed, 150 + 50 * speed),
                                     peak_unfollows=(13 + 2 * speed, 150 + 50 * speed),
                                     peak_server_calls=(None, 4700))

        session.set_skip_users(skip_private=True, private_percentage=100)

        # dont comment, unfollowing my follower list
        CLIENT_SOCKET.send("팔로워 목록 확인".encode('utf-8'))
        # my_follwers = session.grab_followers(username=id, amount="full", live_match=True, store_locally=True)

        session.set_user_interact(amount=5, randomize=True, percentage=50, media='Photo')

        if accounts[row][TBL_USE_COMMENT] and comments:
            valComments = []
            for col in range(1, 11):
                comment = comments[int(accounts[row][TBL_COMMENTS])][col]
                if not comment == 'None':
                    valComments.append(comment)
            if valComments:
                session.set_do_comment(enabled=True, percentage=75)
                session.set_comments(valComments)

        if accounts[row][TBL_USE_FILTER] and filters:
            valFilters = []
            for col in range(1, 11):
                filter = filters[int(accounts[row][TBL_FILTERS])][col]
                # print(hashtag)
                if not filter == 'None':
                    valFilters.append(filter)
            if valFilters:
                session.set_dont_like(tags=valFilters)

        if accounts[row][TBL_USE_LIKE] or \
                accounts[row][TBL_USE_FOLLOW]:
            valHashtags = []
            for col in range(1, 11):
                hashtag = hashtags[int(accounts[row][TBL_HASHTAGS])][col]
                # print(hashtag)
                if not hashtag == 'None':
                    valHashtags.append(hashtag)
            if valHashtags and accounts[row][TBL_USE_LIKE]:
                session.set_do_like(enabled=True, percentage=100)
                if accounts[row][TBL_USE_FOLLOW]:
                    session.set_do_follow(enabled=True, percentage=75)
                    CLIENT_SOCKET.send("좋아요/댓글/팔로우 실행".encode('utf-8'))
                for cnt in range(0, int(accounts[row][TBL_REPEAT_CNT])):
                    session.interact_user_followers(valHashtags, amount=int(accounts[row][TBL_TAG_SHIFT]),
                                                    randomize=True)
                    CLIENT_SOCKET.send("좋아요/댓글/팔로우 완료".encode('utf-8'))
                    s = "좋아요: %d개, 댓글: %d개, 팔로우: %d개\n" % (session.liked_img, session.commented, session.followed)
                    CLIENT_SOCKET.send(s.encode('utf-8'))
            else:
                session.set_do_follow(enabled=True, percentage=75)
                CLIENT_SOCKET.send("좋아요/댓글/팔로우 실행".encode('utf-8'))
                for cnt in range(0, int(accounts[row][TBL_REPEAT_CNT])):
                    session.interact_user_followers(valHashtags, amount=int(accounts[row][TBL_TAG_SHIFT]),
                                                    randomize=True)
                    CLIENT_SOCKET.send("좋아요/댓글/팔로우 완료".encode('utf-8'))
                    s = "좋아요: %d개, 댓글: %d개, 팔로우: %d개\n" % (session.liked_img, session.commented, session.followed)
                    CLIENT_SOCKET.send(s.encode('utf-8'))
        else:
                CLIENT_SOCKET.send("좋아요 사용에 체크해주세요.".encode('utf-8'))

        instapy.InstaPy.end_sub(session)
    except:
        raise(CLIENT_SOCKET.send("세선 실행 에러 발생".encode('utf-8')))

def getAccountData():
    if os.path.isfile('db/tbA.p'):
        with open('db/tbA.p', 'rb') as file:
            accounts = pickle.load(file)
    else:
        accounts = None

    return accounts

def getHashtagData():
    if os.path.isfile('db/tbH.p'):
        with open('db/tbH.p', 'rb') as file:
            hashtags = pickle.load(file)
    else:
        hashtags = None

    return hashtags

def getCommentData():
    if os.path.isfile('db/tbC.p'):
        with open('db/tbC.p', 'rb') as file:
            comments = pickle.load(file)
    else:
        comments = None

    return comments

def getFilterData():
    if os.path.isfile('db/tbF.p'):
        with open('db/tbF.p', 'rb') as file:
            filters = pickle.load(file)
    else:
        filters = None

    return filters

def getUnfollowData():
    if os.path.isfile('db/tbU.p'):
        with open('db/tbU.p', 'rb') as file:
            mode = pickle.load(file)
    else:
        mode = 0

    return mode

if __name__ == "__main__":
    CLIENT_SOCKET.connect(('127.0.0.1', PORT))
    CLIENT_SOCKET.send("접속 완료".encode('utf-8'))
    print('[Client] 접속 완료')

    accounts = getAccountData()
    hashtags = getHashtagData()
    comments = getCommentData()
    filters = getFilterData()
    rxData = CLIENT_SOCKET.recv(1024).decode('utf-8')
    bHeadless = False
    if rxData.find('True') != -1:
        bHeadless = True

    threads = []
    for row in range(0, len(accounts)):
        if accounts[row][TBL_USE_ACCOUNT]:
            mode = getUnfollowData()
            if mode == MODE_TAGRUN:
                t = StoppableThread(startActivity, (row, accounts, hashtags, comments, filters, bHeadless,))
            elif mode == MODE_IDRUN:
                t = StoppableThread(followerActivity, (row, accounts, hashtags, comments, filters, bHeadless,))
            elif mode == MODE_UNFOLLOW1:
                t = StoppableThread(unfollowActivity1, (row, accounts, bHeadless,))
            elif mode == MODE_UNFOLLOW2:
                t = StoppableThread(unfollowActivity2, (row, accounts, bHeadless,))

            threads.append(t)

    for t in threads:
        t.daemon = True
        t.start()

    while True:
        receive(CLIENT_SOCKET)
