__author__ = 'Roman'
# -*- coding: UTF-8 -*-

import datetime
import urllib
import time
import json, sys, codecs

from settings import *

class Logger(object):

    def __init__(self):
        self.terminal = sys.stdout
        self.log = codecs.open("logfile.log", "w+", 'utf-8-sig')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

def get_wall_posts(uid = default_id, offset = 0, count = 100):
    # 100 posts max at a time
    # we use offset as a measure of chunks of posts - how many to process
    raw_data = urllib.urlopen(API + 'wall.get?owner_id=%s'
                                    '&filter=owner'
                                    '&offset=%s'
                                    '&count=%s'
                                    '&v=5.27'
                                    '&access_token=%s' % (uid, offset, count, token))
    data = json.load(raw_data)
    time.sleep(sleep)

    if offset != 0: # to get total number of posts in the first time (when offset = 0)
        return data['response']['items']
    else:
        return data['response']['count'], data['response']['items'] # get total number of posts for further processing

def unix_time_convert(unixtime):
    #Converting post time from unix format to normal one
    return datetime.datetime.fromtimestamp(unixtime).strftime('%Y-%m-%d')

def get_time_relevant_posts(posts, time_filter):
    start_date = datetime.date.today() - datetime.timedelta(days=time_filter)

    temp = []
    for i in range(0, len(posts)):
        if datetime.datetime.fromtimestamp(posts[i]["date"]).date() >= start_date:
            temp.append(posts[i])

    return len(temp), temp

#TODO: объединить с get_wall_posts
def get_post_by_id(post_id, uid = default_id):
    # get post data by post_id
    raw_data = urllib.urlopen(API + 'wall.getById?posts=%s_%s'
                                    '&v=5.27'
                                    '&access_token=%s' % (uid, post_id, token))
    data = json.load(raw_data)
    time.sleep(sleep)
    return data['response']

def print_one_post_data(post_tuple, top_id, top_num, flag, uid = default_id):
    post_id, flag_count = post_tuple # decouple the tuple
    post_data = get_post_by_id(post_id, uid)
    if uid[0] == "-":
        print '%s from TOP-%s posts: http://vk.com/wall%s_%s (%s: %s)' % (top_id, top_num, uid, post_id, flag, flag_count)
    else:
        print '%s from TOP-%s posts: http://vk.com/id%s?w=wall%s_%s (%s: %s)' % (top_id, top_num, uid, uid, post_id, flag, flag_count)

def print_top_posts(top_posts_data, flag, top_num, uid = default_id):
    # print 'User: http://vk.com/id%s' % uid
    print '='*20, str(flag).upper(), '='*20
    for i in range(0, top_num):
        if i == len(top_posts_data):
            break
        print_one_post_data(top_posts_data[i], i+1, top_num, flag, uid)
    print '='*20, "END", '='*20

def compute_top_posts(flag, posts, total_posts, uid = default_id):
    top_num = 3
    # get top-5 max posts according to flag
    top_posts = get_max_post(uid, posts, total_posts, flag, top_num)
    if top_posts != []:
        post_id, flag_count = top_posts[0] # if the user ever posted anything we have a non-empty response list
    else:
        flag_count = 0 # otherwise just return 0 value

    print_top_posts(top_posts, flag, top_num, uid)
    return flag_count

def get_max_post(uid, posts_data, total_posts, flag, top_num):
    temp = [] # temp list of posts with max number of flag - likes, comments or reposts
    offset = 100 # number of posts to analyze
    num_iter = (total_posts / offset) #

    temp.extend( get_max_from_100(posts_data, flag) ) #put max from 1st chunk - 100 initial posts

    for i in range(0, num_iter): # number of chunks of 100 posts to analyze
        new_post_data = get_wall_posts(uid, offset)
        temp.extend( get_max_from_100(new_post_data, flag) )
        temp = sort_list_of_tuples(temp)[0:top_num]
        # print str(offset + 100) + ' posts analyzed...'
        offset += 100
        print '.',

    # print flag + ' are being analyzed.'

    return sort_list_of_tuples(temp)[0:top_num]

def get_max_from_100(data_100posts, flag):
    temp = []
    num_iter = len(data_100posts)

    for i in range(0, num_iter):
        temp.append( ( data_100posts[i]['id'], data_100posts[i][flag]['count'] ) ) # (id, count of flag) tuple

    return sort_list_of_tuples(temp)[0:5]

def sort_list_of_tuples(list):

    def getKey(item):
        return item[1]

    list.sort(key = getKey, reverse=True)

    return list

def get_groups(uid = default_id, extended = 0):
    raw_data = urllib.urlopen(API + 'groups.get?user_id=%s'
                                    '&extended=%s'
                                    '&v=5.27'
                                    '&access_token=%s' % (uid, extended, token))
    data = json.load(raw_data)
    time.sleep(sleep)

    return data['response']['items'] # get total number of posts for further processing

def main():

    sys.stdout = Logger()

    groups_list = get_groups(default_id)

    # target_uid = raw_input("Enter VK user ID to analyse (or press ENTER to use default_id=%s): " % default_id)
    #
    # if target_uid == '':
    #     target_uid = default_id
    #
    # print

    default_time_filter = 7 #days
    time_filter = default_time_filter

    # time_filter = raw_input("Enter time period to analyse (number of days) (or press ENTER to use default_time_filter=%s): " % default_time_filter)
    #
    # if time_filter == '':
    #     time_filter = default_time_filter
    #
    # print
    count = 1
    for target_uid in groups_list:

        target_uid = str(-target_uid)
        total_posts, posts = get_wall_posts(target_uid)

    # time_filter = 1 #1 day
    # time_filter = 7 #1 week
    # time_filter = 30 #1 month

        [num_posts, time_filtered_posts] = get_time_relevant_posts( posts, int(time_filter) )

        flag1 = 'likes'
        flag2 = 'comments'
        flag3 = 'reposts'

        print '#'*40
        print count, "of", len(groups_list), ": http://vk.com/public%s, %s posts" % (target_uid, num_posts)
        num_max_likes = compute_top_posts(flag1, time_filtered_posts, num_posts, target_uid)
        num_max_comments = compute_top_posts(flag2, time_filtered_posts, num_posts, target_uid)
        num_max_reposts = compute_top_posts(flag3, time_filtered_posts, num_posts, target_uid)
        print '#'*40
        count += 1

main()