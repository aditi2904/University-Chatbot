import csv
import spotlight
import pandas as pd
import os

topic_name = []
topic_url = []
course_name = []
topic_left = []


def dbpediaSpotlightAnnotate(text, c_name):
    #print("Entering spotlight", text)
    try:
        annotations = spotlight.annotate('https://api.dbpedia-spotlight.org/en/annotate', text=text, confidence=0.5,
                                         support=20)
        # file_annotations.append(annotations)
        for data in annotations:
            topic_name.append(data['surfaceForm'].strip())
            topic_url.append(data['URI'].strip())
            course_name.append(c_name.strip().split("(")[0].strip())
    except:
        counter = 0
        with open("topic_left.csv", "r", encoding='utf-8') as topic_left_file:
            file_reader = csv.reader(topic_left_file)
            for row in file_reader:
                if c_name in row:
                    counter = counter + 1
            if counter == 0:
                topic_left.append(text)


def dbpediaSpotlightStart():
    with open("Courses.csv", "r", encoding='utf-8') as course_file:
        course_file_reader = csv.reader(course_file, delimiter="|")
        next(course_file_reader)
        for row in course_file_reader:
            #print(row)
            text = row[2].strip()+" "+row[3].strip()
            if text != "":
                if os.stat("topic.csv").st_size == 0:
                    dbpediaSpotlightAnnotate(text, row[2].strip())
                else:
                    count = 0
                    with open("topic.csv", "r", encoding='utf-8') as topic_file:
                        topic_file_reader = csv.reader(topic_file, delimiter="|")
                        for topic_row in topic_file_reader:
                            if row[2].strip().split("(")[0].strip() == topic_row[2].strip():
                                count = count + 1
                        #print(count)
                        if count == 0:
                            dbpediaSpotlightAnnotate(text, row[2].strip())

    topicdf = pd.DataFrame(
        {'topic_name': topic_name,
         'topic_url': topic_url,
         'course_name': course_name
        })

    topicdf_left = pd.DataFrame(
        {
         'course_name': topic_left
        })

    topicdf_no_duplicate = topicdf_left.drop_duplicates()
    topicdf_no_duplicate.to_csv('topic_left.csv',index=False , sep='|', encoding="utf8")
    final_topicdf = topicdf.drop_duplicates()
    if os.stat("topic.csv").st_size == 0:
        final_topicdf.to_csv('topic.csv', index=False, sep='|', encoding="utf8")
    else:
        final_topicdf.to_csv('topic.csv', mode='a', index=False , sep='|', encoding="utf8", header=False)


dbpediaSpotlightStart()
