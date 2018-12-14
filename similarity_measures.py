import csv
from math import *
import json
from pprint import pprint
import itertools
from itertools import combinations
import unicodedata

# x and y are lists
def jaccard_similarity(x, y):
    #intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
    #union_cardinality = len(set.union(*[set(x), set(y)]))
    #return intersection_cardinality / float(union_cardinality)
    intersection = len(list(set(x) & set(y)))
    union = 10 - intersection
    return float(intersection)/union

def new_jaccard(list1, list2):
    inter = 0
    union = 0
    for x in list1:
        if x in list1:
            inter+=1
    s = {}
    for x in list1:
        if x not in s:
            s[x] = 1
            union+=1
    for x in list2:
        if x not in s:
            s[x] = 1
            union+=1
    return float(inter)/float(union)

# the set of elements which are in either of the sets and not in their intersection
# x and y are lists
def symmetric_difference(x, y):
    intersection_set = set(set(x) & set(y))
    #intersection_set = x.intersection(y)
    symmetric_diff_sz = len(set(x).union(set(y))) - len(intersection_set)    
    return symmetric_diff_sz

# x and y are lists, i is the length of the list
def permute_top_k(x,y,k):
    list1, lisrt2 = x[:k], y[:k]
    return symmetric_difference(list1, lisrt2)

def permute_list(l1):
    return list(itertools.permutations(l1))

def combination(l1):
    return list(combinations(l1, 5))

def calc_rbo(l1, l2, p):
    sl, ll = sorted([(len(l1), l1), (len(l2), l2)])
    s, S = sl
    l, L = ll

    # Calculate the overlaps at ranks 1 through l
    # (the longer of the two lists)
    ss = set([])
    ls = set([])
    overs = {}
    for i in range(l):
        ls.add(L[i])
        if i < s:
            ss.add(S[i])
        X_d = len(ss.intersection(ls))
        d = i + 1
        overs[d] = float(X_d)

    # (1) \sum_{d=1}^l (X_d / d) * p^d
    sum1 = 0
    for i in range(l):
        d = i + 1
        sum1 += overs[d] / d * pow(p, d)
    X_s = overs[s]
    X_l = overs[l]

    # (2) \sum_{d=s+1}^l [(X_s (d - s)) / (sd)] * p^d
    sum2 = 0
    for i in range(s, l):
        d = i + 1
        sum2 += (X_s * (d - s) / (s * d)) * pow(p, d)

    # (3) [(X_l - X_s) / l + X_s / s] * p^l
    sum3 = ((X_l - X_s) / l + X_s / s) * pow(p, l)

    # Equation 32.
    rbo_ext = (1 - p) / p * (sum1 + sum2) + sum3
    return rbo_ext


if __name__ == "__main__":
    # take in file
    searchengines = [("duckduckgo", "google"), ("duckduckgo", "baidu"), ("duckduckgo", "bing"), ("google", "bing"), ("google", "baidu"), ("bing", "baidu")]
    #searchengines = [("bing", "baidu")]
    topics = ["science", "religion", "history", "generic", "ideas", "current"]
    #topics = ["current"]
    for SE in searchengines:
        vals = []
        filename = SE[0] + "_" + SE[1] + "_symdiff.csv"
        for topic in topics:
            datafile = "./data/" +SE[0]+ "_"+topic+".json"
            datafile2 = "./data/" + SE[1]+"_"+topic+".json"
            with open(datafile) as f1:
                first_data = json.load(f1)
            with open(datafile2) as f2:
                second_data = json.load(f2)
            masterlist1 = {}
            for query in first_data:
                querystring = unicodedata.normalize('NFKD', query).encode('ascii','ignore')
                list1 = first_data[query]
                for dicts in list1:
                    url = unicodedata.normalize('NFKD', dicts["url"]).encode('ascii', 'ignore')
                    if querystring not in masterlist1:
                        masterlist1[querystring] = [url]
                    else:
                        masterlist1[querystring].append(url)
    
            masterlist2 = {}
            for query in second_data:
                querystring = unicodedata.normalize('NFKD', query).encode('ascii','ignore')
                list2 = second_data[query]
                for dicts in list2:
                    url = unicodedata.normalize('NFKD', dicts["url"]).encode('ascii', 'ignore')
                    if querystring not in masterlist2:
                        masterlist2[querystring] = [url]
                    else:
                        masterlist2[querystring].append(url)

            #filename = SE[0] + "_" + SE[1] + "_" + topic + "_jaccard.csv"
     
            #calculate jaccard  
            #vals = []
            for query in masterlist1:
                js = jaccard_similarity(masterlist1[query], masterlist2[query])
                d = [query, js]
                vals.append(d)
            #filename = SE[0] + "_" + SE[1] + "_" + topic + "_jaccard.csv"
            with open(filename, "wb") as csv_file:
                writer = csv.writer(csv_file, delimiter=",")
                for line in vals:
                    writer.writerow(line)

            # calculate rank bias overlap 
            #vals = []
            for query in masterlist1:
                rbo = calc_rbo(masterlist1[query], masterlist2[query], 0.98)
                d = [query, rbo]
                vals.append(d)
            #filename = SE[0] + "_" + SE[1] + "_" + topic + "_RBO.csv"
            with open(filename, "wb") as csv_file:
                writer = csv.writer(csv_file, delimiter=",")
                for line in vals:
                    writer.writerow(line)

            #calculate top k symmetric difference
            #vals = []
            for query in masterlist1:
                total = 0
                for k in range(1, 6):
                    total += 1 - (float(permute_top_k(masterlist1[query], masterlist2[query], k))/(k*2)) #distance metric
                total = float(total)/5
                d = [query, total]
                vals.append(d)
            
            #filename = SE[0] + "_" + SE[1] + "_" + topic + "_symdiff.csv"
            with open(filename, "wb") as csv_file:
                writer = csv.writer(csv_file, delimiter=",")
                for line in vals:
                    writer.writerow(line)

            #O(n!) consensus ranking jaccard
            #vals = []
            for query in masterlist1:
                setofall = set(masterlist1[query] + masterlist2[query])
                listofcombos = combination(list(setofall))
                maxval = 0
                maxA = 0
                maxB = 0
                for combo in listofcombos:
                    listofpermutes = permute_list(combo)
                    for permute in listofpermutes:
                        valA = jaccard_similarity(permute, masterlist1[query])
                        valB = jaccard_similarity(permute, masterlist2[query])
                        if (((float(valA+valB))/2.0)-(valB-valA)**2) > maxval:
                            maxval = (float(valA+valB))/2.0 - (valB-valA)**2
                            maxA = valA
                            maxB = valB
                if(maxA!=0 and maxB!=0):
                    d = [query, maxA, maxB]
                    vals.append(d)
            #filename = SE[0] + "_" + SE[1] + "_" + topic + "_consensusrank_jaccard_improved.csv"
           
            with open(filename, "w") as f:
                for line in vals:
                    f.write("\"%s\", %s, %s\n" % (line[0], str(line[1]), str(line[2])))

            #O(n!) consensus ranking RBO
            for query in masterlist1:
                setofall = set(masterlist1[query] + masterlist2[query])
                listofcombos = combination(list(setofall))
                maxval = 0
                maxA = 0
                maxB = 0
                for combo in listofcombos:
                    listofpermutes = permute_list(combo)
                    for permute in listofpermutes:
                        valA = calc_rbo(permute, masterlist1[query], 0.98)
                        valB = calc_rbo(permute, masterlist2[query], 0.98)
                        if (((float(valA+valB))/2.0)-(valB-valA)**2) > maxval:
                            maxval = (float(valA+valB))/2.0 - (valB-valA)**2
                            maxA = valA
                            maxB = valB
                if(maxA!=0 and maxB!=0):
                    d = [query, maxA, maxB]
                    vals.append(d)
            #filename = SE[0] + "_" + SE[1] + "_" + topic + "_consensusrank_RBO_improved.csv"
            with open(filename, "wb") as csv_file:
                writer = csv.writer(csv_file, delimiter=",")
                for line in vals:
                    writer.writerow(line)
