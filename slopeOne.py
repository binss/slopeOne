# coding=utf-8
#
# slopeOne.py
# forecast the rating of movie based on Slope One and UBCF
# Created by bin on 14/11/17.
# Copyright (c) 2014年 bin. All rights reserved.
#
import re
import math

# 对从文本读出每行记录进行正则匹配
def data_filter(data):
    re1 = '(\\d+)'    # Integer Number 1
    re2 = '.*?'   # Non-greedy match on filler
    re3 = '(\\d+)'    # Integer Number 2
    re4 = '.*?'   # Non-greedy match on filler
    re5 = '(\\d+)'    # Integer Number 3

    rg = re.compile(re1+re2+re3+re4+re5, re.IGNORECASE|re.DOTALL)
    m = rg.search(data)
    if m:
        user = int(m.group(1))
        movie = int(m.group(2))
        rating = int(m.group(3))
        return {"user":user, "movie":movie, "rating":rating}

# 计算用户的平均rating
def cal_avg(user_vector):
    user_sum = 0.0
    for i in user_vector:
        user_sum += user_vector[i]
    avg = user_sum / len(user_vector)
    return avg


# 生成矩阵(其实是二维字典)
def formMatrix():
    matrix = {}
    f = open("80train.txt", "r")
    lines = f.readlines()
    for line in lines:
        data = data_filter(line)
        if data["user"] in matrix:
            matrix[data["user"]][data["movie"]] = data["rating"]
        else:
            matrix[data["user"]] = {data["movie"]:data["rating"]}
    f.close()
    return matrix

# 预测分数
def cal_slopeOne(matrix, test_user, test_movie):
    suppose_list = []
    movie_list_of_test_user = matrix[test_user]
    # 对于每一部电影，都计算它和test_movie的差值(b)，最终算出相对于它的test_movie的rating
    for movie in movie_list_of_test_user:
        diff_sum = 0.0
        user_num = 0
        for user in matrix:
            user_movie = matrix[user]
            # 如果该user同时看过这两部，则采纳他的评分
            if test_movie in user_movie and movie in user_movie:
                diff_sum += user_movie[test_movie] - user_movie[movie]
                user_num += 1
        if user_num:
            diff_avg = diff_sum / user_num
            suppose_rate = movie_list_of_test_user[movie] + diff_avg
            suppose_list.append((suppose_rate, user_num))

    # 如果没人看过，取这个人的平均分
    if not suppose_list:
        # return 3
        avg = cal_avg(movie_list_of_test_user)
        # print avg
        return avg

    # 否则算出它的rating
    molecusar = 0.0
    denominator = 0.0
    for suppose in suppose_list:
        molecusar += suppose[0] * suppose[1]
        denominator += suppose[1]
    # return int(round(molecusar / denominator))
    return molecusar / denominator

def userbased_cal_matrix(matrix, test_user, test_movie):
    # STEP 1 计算test_user的均值
    test_user_vector = matrix[test_user]
    test_user_avg = cal_avg(test_user_vector)
    # print test_user_vector
    # print test_user_avg

    # 只选为该电影打过分的user
    sim_list = []
    for user in matrix:
        if test_movie in matrix[user]:
            user_vector = matrix[user]
            user_avg = cal_avg(user_vector)
            molecusar = 0.0
            denominatorA = 0.0
            denominatorB = 0.0
            for key in test_user_vector:
                if key in user_vector:
                    a = test_user_vector[key] - test_user_avg
                    b = user_vector[key] - user_avg
                    molecusar += a * b
                    denominatorA += a * a
                    denominatorB += b * b
            if denominatorA and denominatorB and molecusar:
                sim = molecusar / math.sqrt(denominatorA) / math.sqrt(denominatorB)
                sim_list.append((user, user_avg, user_vector[test_movie], sim))

    # print sim_list

    molecusar = 0.0
    denominator = 0.0
    if sim_list:
        for data in sim_list:
            molecusar += data[3] * ( data[2] - data[1] )
            denominator += abs(data[3])
        pearson_rating = test_user_avg + molecusar / denominator
    else:
        # 如果没有相似集（本质上是因为没人看过这电影），取自己打分的平均值
        pearson_rating = test_user_avg
    return pearson_rating


def creatOutput():
    mae_sum = 0
    rmae_sum = 0
    number = 0

    matrix = formMatrix()
    f = open("test.txt", "r")
    wf = open("output.txt", 'w')
    lines = f.readlines()
    for line in lines:
        data = data_filter(line)
        rating1 = cal_slopeOne(matrix, data["user"], data["movie"])
        rating2 = userbased_cal_matrix(matrix, data["user"], data["movie"])
        rating = int(round((rating1 + rating2)/ 2))
        string = str(data["user"]) + "\t" + str(data["movie"]) + "\t" + str(rating) + "\t" + str(data["rating"]) + "\n"
        wf.write(string)
        t = rating - data['rating']
        mae_sum += abs(t)
        rmae_sum += t * t
        number += 1
        print number
    wf.close()
    print "MAE: " + str(mae_sum * 1.0 / number)
    print "RMAE: " + str(math.sqrt(rmae_sum * 1.0 /number))


creatOutput()

# slope one, 取平均分
# MAE: 0.6998
# RMAE: 0.984174781225

# 混合
# MAE: 0.6992
# RMAE: 0.976729235766
