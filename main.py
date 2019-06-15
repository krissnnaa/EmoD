import json
import requests
import datetime
from nltk.corpus import stopwords
import nltk
import re
import os
import csv

stop_words = set(stopwords.words('english'))
login_number = 0
backupJson = {}
dest_path = os.getcwd()


def commentsCollection():
    global login_number
    global backupJson
    output_list = []
    owner_name = 'ipython'
    repo_name = 'ipython'

    with open("authentication.json") as outfile:
        authentication = json.load(outfile)
    url = "https://api.github.com/repos/" + owner_name + "/" + repo_name + "/issues"
    i = 0
    while True:
        print(i)
        url_a = url + '?page={0}'.format(i)
        r = requests.get(url_a,
                         auth=(authentication[login_number]['username'], authentication[login_number]['password']))
        if not r.json():
            break
        else:
            if r.status_code == 200:
                print("Yeah successful")
                issueRequest = r.json()
                for item in range(len(issueRequest)):
                    if issueRequest[item]['closed_at'] == None:
                        issue = issueRequest[item]['comments_url']
                        req = requests.get(issue,
                                           auth=(authentication[login_number]['username'],
                                                 authentication[login_number]['password']))

                        if req.status_code == 403:
                            if login_number < 18:
                                login_number = login_number + 1
                            else:
                                login_number = 0
                            req = requests.get(issue,
                                               auth=(authentication[login_number]['username'],
                                                     authentication[login_number]['password']))
                            output_list.append(req.json())
                            continue
                        output_list.append(req.json())
                i += 1

            else:
                error = r.json()
                print(repo_name + '\t has an error message:\n' + error['message'])

                if r.status_code == 403:
                    print(r.status_code)
                    if login_number < 18:
                        login_number = login_number + 1
                    else:
                        login_number = 0

                    while True:
                        r = requests.get(url_a, auth=(
                            authentication[login_number]['username'], authentication[login_number]['password']))
                        if r.status_code == 200:
                            print("Yeah successful")
                            issueRequest = r.json()
                            for item in range(len(issueRequest)):
                                if issueRequest[item]['closed_at'] == None:
                                    issue = issueRequest[item]['comments_url']
                                    req = requests.get(issue,
                                                       auth=(authentication[login_number]['username'],
                                                             authentication[login_number]['password']))

                                    if req.status_code == 403:
                                        if login_number < 18:
                                            login_number = login_number + 1
                                        else:
                                            login_number = 0
                                        req = requests.get(issue,
                                                           auth=(authentication[login_number]['username'],
                                                                 authentication[login_number]['password']))
                                        output_list.append(req.json())
                                        continue
                                    output_list.append(req.json())

                            i += 1
                            break
                else:
                    break

    output_list = [item for item in output_list if len(item) != 0]
    backupJson['ipython'] = output_list

def processFrom():
    memberComment = {}
    otherComment = {}
    #with open("backup.json") as outfile:
    #   backupJson = json.load(outfile)
    for fileItem in backupJson.values():
        for item in fileItem:
            for index in range(len(item)):
                authorAssociation = item[index]['author_association']
                memberName = item[index]['user']['login']
                commentBody = item[index]['body'] + ' '
                createdDate = item[index]['created_at']
                createDate = re.findall(r'\d{4}-\d{2}-\d{2}', createdDate)
                createDate = ''.join(createDate)
                dateForm = datetime.datetime.strptime(createDate, '%Y-%m-%d')
                finalCreatedDate = (dateForm + datetime.timedelta(1)).date()
                finalCreatedDate=datetime(finalCreatedDate.year,finalCreatedDate.month,finalCreatedDate.day)
                flag = 0
                today = datetime.datetime.today()
                #tillApril10='2019-04-10'
                #tillApril10=datetime.datetime.strptime(tillApril10,'%Y-%m-%d')
                initialComment = []
                if authorAssociation == 'MEMBER' and today==finalCreatedDate: #today > dateForm and tillApril10 < dateForm:
                    for key, value in memberComment.items():
                        if key == memberName:
                            warn = 0
                            previousComment = memberComment[memberName]
                            for values in previousComment:
                                if values[0] == createDate:
                                    comments = values[1] + ' ' + commentBody
                                    previousComment.pop(previousComment.index(values))
                                    commentTuple = (createDate, comments)
                                    previousComment.append(commentTuple)
                                    memberComment[key] = previousComment
                                    warn = 1
                                    break

                            if warn == 0:
                                commentTuple = (createDate, commentBody)
                                previousComment.append(commentTuple)
                                memberComment[key] = previousComment

                            flag = 1
                            break

                    if flag == 0:
                        commentTuple = (createDate, commentBody)
                        initialComment.append(commentTuple)
                        memberComment[memberName] = initialComment

                if authorAssociation != 'MEMBER' and today==finalCreatedDate: #today > dateForm and tillApril10 < dateForm:
                    for key, value in otherComment.items():
                        if key == memberName:
                            warn = 0
                            previousComment = otherComment[memberName]
                            for values in previousComment:
                                if values[0] == createDate:
                                    comments = values[1] + ' ' + commentBody
                                    previousComment.pop(previousComment.index(values))
                                    commentTuple = (createDate, comments)
                                    previousComment.append(commentTuple)
                                    otherComment[key] = previousComment
                                    warn = 1
                                    break

                            if warn == 0:
                                commentTuple = (createDate, commentBody)
                                previousComment.append(commentTuple)
                                otherComment[key] = previousComment

                            flag = 1
                            break

                    if flag == 0:
                        commentTuple = (createDate, commentBody)
                        initialComment.append(commentTuple)
                        otherComment[memberName] = initialComment

    for key, value in memberComment.items():
        idValue = 0
        with open(dest_path + '/' + key + '.csv', 'w', encoding='utf-8', newline='') as csvfile:
            csvObject = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            value = list(set(value))
            csvObject.writerow(['id', 'label', 'text'])
            for eachTuple in value:
                preProcess = re.sub(r'[^\w]', ' ', eachTuple[1])
                preProcess = (re.sub(r'[\r\n]+', '', preProcess)).lower()
                textTokenize = nltk.tokenize.word_tokenize(preProcess)
                afterStopWords = [w for w in textTokenize if not w in stop_words]
                finalData = ' '.join(afterStopWords)
                csvObject.writerow([idValue, 'YES', finalData])
                idValue = idValue + 1

        idValue = 0
        fileRead = open(dest_path + '/' + key + "_data.txt", 'w', encoding="utf-8")
        fileRead.write('ID\t\tCreated Date\t\t\t\tComments\n')
        value = list(set(value))
        for eachTuple in value:
            preProcess = (re.sub(r'[\r\n]+', '', eachTuple[1])).lower()
            fileRead.write('%d\t\t%s\t\t%s\n' % (idValue, eachTuple[0], preProcess))
            idValue = idValue + 1

    for key, value in otherComment.items():
        idValue = 0
        with open(dest_path + '/' + 'other_' + key + '.csv', 'w', encoding='utf-8', newline='') as csvfile:
            csvObject = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            value = list(set(value))
            csvObject.writerow(['id', 'label', 'text'])
            for eachTuple in value:
                preProcess = re.sub(r'[^\w]', ' ', eachTuple[1])
                preProcess = (re.sub(r'[\r\n]+', '', preProcess)).lower()
                textTokenize = nltk.tokenize.word_tokenize(preProcess)
                afterStopWords = [w for w in textTokenize if not w in stop_words]
                finalData = ' '.join(afterStopWords)
                csvObject.writerow([idValue, 'YES', finalData])
                idValue = idValue + 1

        idValue = 0
        fileRead = open(dest_path + '/' + 'other_' + key + "_data.txt", 'w', encoding="utf-8")
        fileRead.write('ID\t\tCreated Date\t\t\t\tComments\n')
        value = list(set(value))
        for eachTuple in value:
            preProcess = (re.sub(r'[\r\n]+', '', eachTuple[1])).lower()
            fileRead.write('%d\t\t%s\t\t%s\n' % (idValue, eachTuple[0], preProcess))
            idValue = idValue + 1


if __name__ == '__main__':
    commentsCollection()
    processFrom()
