from rdflib.namespace import RDFS, RDF, FOAF, DC, OWL
from rdflib import Graph, Namespace, Literal
import rdflib
import csv

dbOntology =rdflib.Namespace('http://dbpedia.org/ontology/')
graph = Graph()
graph.parse("Classes.rdf", format="application/rdf+xml")
graph.bind("dbOntology", dbOntology)

'''Function to generate triples for the university'''
def universityTripleGenerator(university_class):
    university_ns = Namespace("http://example.org/university/")
    university_list = ["Concordia_University"]
    university = university_ns[university_list[0]]
    graph.add((university, RDF.type, university_class))
    graph.add((university, FOAF.name, Literal("Concordia University")))
    graph.add((university, RDFS.seeAlso, Literal("http://dbpedia.org/resource/Concordia_University")))
    graph.serialize(format='turtle')
    return university


'''Function to generate triples for the courses offered'''
def courseTripleGenerator(course_class, is_offered_by, university):
    course_ns = Namespace("http://example.org/course/")
    with open("Courses.csv", 'r', encoding='utf-8') as csv_file:
        file_reader = csv.reader(csv_file, delimiter="|")
        next(file_reader)
        for course_list in file_reader:
            course = course_ns[course_list[1]+"_"+course_list[0]]
            graph.add((course, RDF.type, course_class))
            graph.add((course, DC.identifier, Literal(course_list[0])))
            graph.add((course, DC.title, Literal(course_list[2].strip().split("(")[0].strip())))
            graph.add((course, DC.subject, Literal(course_list[1])))
            graph.add((course, DC.description, Literal(course_list[3])))
            graph.add((course, is_offered_by, Literal(university)))
            graph.add((course, RDFS.seeAlso, Literal(course_list[4])))

    graph.serialize(format='turtle')


'''Function to generate triples for the topics'''
def topicsTripleGenerator(topic_class):
    topic_ns = Namespace("http://example.org/topics/")
    with open("topic.csv", 'r', encoding='utf-8') as csv_file:
        file_reader = csv.reader(csv_file, delimiter="|")
        next(file_reader)
        for topic_list in file_reader:
            if " " in topic_list[0]:
                topic_name = topic_list[0].split(" ")[0] + "_" + topic_list[0].split(" ")[1]
            else:
                topic_name = topic_list[0]
            topic = topic_ns[topic_name]
            graph.add((topic, RDF.type, topic_class))
            graph.add((topic, DC.title, Literal(topic_list[0])))
            graph.add((topic, OWL.sameAs, Literal(topic_list[1])))
            graph.add((topic, FOAF.primaryTopicOf, Literal(topic_list[2])))

    graph.serialize(format='turtle')


'''Function to generate triples for the students'''
def studentTripleGenerator(student_class, student_Id, enrolled_property, takes_course_property, is_awarded, university, has_transcript, transcript_class):
    student_ns = Namespace("http://example.org/people/")
    with open("StudentsRecord.csv", 'r') as csv_file:
        file_reader = csv.reader(csv_file, delimiter="|")
        next(file_reader)
        for student_list in file_reader:
            student = student_ns[student_list[0]]
            graph.add((student, RDF.type, student_class))
            graph.add((student, student_Id, Literal(student_list[0])))
            graph.add((student, FOAF.givenName, Literal(student_list[1])))
            graph.add((student, FOAF.familyName, Literal(student_list[2])))
            graph.add((student, FOAF.mbox, Literal(student_list[3])))
            graph.add((student, enrolled_property, university))
            row_length = len(student_list)
            counter = 1
            for i in range(4,row_length):
                transcript_identifier = "T" + str(counter) + "S" + student_list[0]
                transcript_record = transcriptTripleGenerator(transcript_identifier, student_list[i], student_list[0], takes_course_property, is_awarded, transcript_class)
                graph.add((student, has_transcript, transcript_record))
                counter = counter + 1

    graph.serialize(destination='FinalKnowledgeGraph.ttl', format='turtle')


'''Function to generate triples for the transcripts of the students'''
def transcriptTripleGenerator(transcript_identifier, student_subject_list, student_id, takes_course_property, is_awarded, transcript_class):
    transcript_ns = Namespace("http://example.org/transcript/")
    split_subject_list = student_subject_list.split("-",3)
    transcript = transcript_ns[transcript_identifier]
    graph.add((transcript, RDF.type, transcript_class))
    graph.add((transcript, DC.identifier, Literal(student_id)))
    graph.add((transcript, takes_course_property, Literal(split_subject_list[0])))
    graph.add((transcript, is_awarded, Literal(split_subject_list[1])))
    graph.add((transcript, dbOntology.termPeriod, Literal(split_subject_list[2])))

    graph.serialize(format='turtle')
    return transcript


'''Function to fetch the total count of triples present in the knowledge base graph'''
def sparql_query_1(query_graph):

    query1 = query_graph.query(
        """SELECT (count(*) AS ?Triples) 
        WHERE{
            ?sub ?p ?o .
    }"""
    )

    for row in query1:
        print("Total number of Triples:%s" % row)


'''Function to fetch the total count of students, courses and topics'''
def sparql_query_2(query_graph):
    query2 = query_graph.query(
        """SELECT ?studentCount ?courseCount ?topicCount {
         {
            SELECT (count(DISTINCT ?studentId) AS ?studentCount) 
                WHERE{
                    ?studentSub a focu:Student .
                    ?studentSub focu:studentId ?studentId.}
         }
         {
            SELECT (count(?courseTitle) AS ?courseCount)
                WHERE{   
                    ?courseSub a focu:Courses .
                    ?courseSub ns1:title ?courseTitle .}
         }
         {
            SELECT (count(?topicTitle) AS ?topicCount)
                WHERE{   
                    ?topicSub a focu:Topics .
                    ?topicSub ns1:title ?topicTitle .}
         }
        }"""
    )

    for row in query2:
        print("Total number of students:%s, total number of courses:%s and total number of topics:%s" % row)


'''Function to fetch the topics of a particular course'''
def sparql_query_3(query_graph, courseName):
    query3 = query_graph.query(
                f"""SELECT ?topicTitle ?topicUri 
                    WHERE {{ 
                        ?topicSub foaf:primaryTopicOf '{courseName}' . 
                        ?topicSub ns1:title ?topicTitle . 
                        ?topicSub ns2:sameAs ?topicUri
                }}""")

    if len(query3) == 0:
        print(courseName, "does not have any topics related to it in the knowledge base graph.")
    else:
        print("The following topics are part of the course {}:".format(courseName))
        for row in query3:
            print("Topic title:%s and Topic URI:%s" % row)


''''Function to fetch the courses cleared by a particular student'''
def sparql_query_4(query_graph, studentName):
    if len(studentName.split(" ")) == 2:
        student_first_name = studentName.split(" ")[0]
        student_last_name = studentName.split(" ")[1]
    else:
        student_first_name = studentName.split(" ")[0]
        student_last_name = " "

    query4 = query_graph.query(
        f"""SELECT ?courseName ?grade ?semester
            WHERE {{ 
                ?transcriptSub a focu:Transcript . 
                ?transcriptSub ns1:identifier ?studentId . 
                {{
                    SELECT ?studentId 
                    WHERE {{ 
                        ?studentSub foaf:givenName '{student_first_name}' . 
                        Optional {{ ?studentSub foaf:familyName '{student_last_name}'}} .
                        ?studentSub focu:studentId ?studentId .
                    }} 
                }} . 
                ?transcriptSub focu:takesCourse ?courseName . 
                ?transcriptSub focu:isAwarded ?grade .
                ?transcriptSub dbOntology:termPeriod ?semester .
        }}""")

    if len(query4) == 0:
        print(studentName, "is not enrolled in the University!")
    else:
        for row in query4:
            print(studentName, "has completed the Course %s with the Grade:%s in the term %s" % row)


'''Function to fetch the list of students fsmiliar with the particular topic'''
def sparql_query_5(query_graph, topicName):
    query5 = query_graph.query(
        f"""SELECT ?studentId ?firstName ?lastName
            WHERE {{
                ?studentSub a focu:Student .
                ?studentSub focu:studentId ?studentId .
                {{
                SELECT ?studentId
                    WHERE {{ 
                        ?transcriptSub a focu:Transcript . 
                        ?transcriptSub focu:takesCourse ?courseName . 
                        {{
                            SELECT ?courseName 
                            WHERE{{ 
                                ?topicSub ns1:title ?topicName . 
                                ?topicSub foaf:primaryTopicOf ?courseName .
                                FILTER (regex(str(?topicName), '{topicName}', 'i'))
                            }}
                        }} . 
                        ?transcriptSub ns1:identifier ?studentId .
                        FILTER NOT EXISTS {{ ?transcriptSub focu:isAwarded "F"}} .
                    }}
                }} .
                ?studentSub foaf:givenName ?firstName .
                ?studentSub foaf:familyName ?lastName .
        }}""" )

    if len(query5) == 0:
        print("Student/Students did not enroll for the course containing the topic", topicName)
    else:
        print("Below is the list students familiar with the topic {}:".format(topicName))
        for row in query5:
            print("Student id:%s and the Student Name:%s %s" % row)


'''Function to fetch the list of topics that a student is familiar with'''
def sparql_query_6(query_graph, student_first_name, student_last_name):
    query6 = query_graph.query(
        f"""SELECT DISTINCT ?topicName
            WHERE {{
                ?topicSub a focu:Topics .
                ?topicSub foaf:primaryTopicOf ?courseName .
                {{
                    SELECT ?courseName
                        WHERE {{ 
                            ?transcriptSub a focu:Transcript . 
                            ?transcriptSub ns1:identifier ?studentId . 
                            {{
                                SELECT ?studentId 
                                WHERE{{ 
                                    ?studentSub a focu:Student .
                                    ?studentSub foaf:givenName '{student_first_name}' . 
                                    Optional {{ ?studentSub foaf:familyName '{student_last_name}'}}.
                                    ?studentSub focu:studentId ?studentId .  
                                }}
                            }} . 
                            ?transcriptSub focu:takesCourse ?courseName .
                            FILTER NOT EXISTS {{ ?transcriptSub focu:isAwarded "F"}} .
                        }}
                }} .
                ?topicSub ns1:title ?topicName .
        }}""" )
    if len(query6) == 0:
        print("The student",student_first_name,student_last_name, "is not enrolled in the university!")
    else:
        if student_last_name:
            print("The student",student_first_name,student_last_name, "is familiar with the following topics:")
        else:
            print("The student", student_first_name, "is familiar with the following topics:")
        for row in query6:
            print("Topic Name:%s" % row)


def customizedQuery(query_graph, query_input):
    query7 = query_graph.query(query_input)

    for row in query7:
        if len(row) == 1:
            print("%s" % row)
        elif len(row) == 2:
            print("%s, %s" % row)
        elif len(row) == 3:
            print("%s, %s, %s" % row)


def main():
    subject = list(graph.subjects(RDF.type, RDFS.Class))
    for row in subject:
        if "#Courses" in row:
            course_class = row
        elif "#University" in row:
            university_class = row
        elif "#Student" in row:
            student_class = row
        elif "#Topics" in row:
            topic_class = row
        elif "#Transcript" in row:
            transcript_class = row

    properties = list(graph.subjects(RDF.type, RDF.Property))
    for row in properties:
        if "#studentId" in row:
            student_Id = row
        elif "#isEnrolledAt" in row:
            enrolled_property = row
        elif "#takesCourse" in row:
            takes_course_property = row
        elif "#isAwarded" in row:
            is_awarded = row
        elif "#isofferedBy" in row:
            is_offered_by = row
        elif "#hasTranscript" in row:
            has_transcript = row

    university = universityTripleGenerator(university_class)
    courseTripleGenerator(course_class, is_offered_by, university)
    topicsTripleGenerator(topic_class)
    studentTripleGenerator(student_class, student_Id,enrolled_property, takes_course_property, is_awarded, university, has_transcript, transcript_class)
    query_graph = Graph()
    query_graph.parse("FinalKnowledgeGraph.ttl", format="ttl")

    print("Hello, I am your smart university agent. Please choose one of the options mentioned below")

    while True:
        choice = input("\n1. Query 1\n2. Query 2\n3. Query 3\n4. Query 4\n5. Query 5\n6. Query 6\n7. Customize Query\n8. Exit\n")
        if choice not in ('1', '2', '3', '4', '5', '6', '7', '8'):
            print("Not an appropriate choice. Please enter a valid one")
        else:
            if choice == "1":
                sparql_query_1(query_graph)
            elif choice == "2":
                sparql_query_2(query_graph)
            elif choice == "3":
                while True:
                    counter = 0
                    courseName = input("Enter the course name:")
                    with open("Courses.csv", 'r', encoding='utf-8') as course_file:
                        file_reader = csv.reader(course_file, delimiter="|")
                        for row in file_reader:
                            if courseName == row[2].strip().split("(")[0].strip():
                                counter = counter + 1
                        if counter == 0:
                            print("Enter a valid course name")
                        else:
                            sparql_query_3(query_graph, courseName)
                            break
            elif choice == "4":
                studentName = input("Enter the name of the student:")
                sparql_query_4(query_graph, studentName)
            elif choice == "5":
                topicName = input("Enter the topic:")
                sparql_query_5(query_graph, topicName)
            elif choice == "6":
                while True:
                    studentId = input("Enter the student name:")
                    '''if studentId.isdigit():
                        if (len(studentId) < 8) or (len(studentId) > 8):
                            print("Please enter a valid student id")
                        else:
                            sparql_query_6(query_graph, studentId, None, None)
                            break
                    else:'''
                    if len(studentId.split(" ")) == 2:
                        sparql_query_6(query_graph, studentId.split(" ")[0], studentId.split(" ")[1])
                    else:
                        sparql_query_6(query_graph, studentId, None)
                    break

            elif choice == "7":
                query = input("Enter the full query:")
                #query without quotes
                customizedQuery(query_graph, query)
            elif choice == "8":
                exit()


if __name__ == "__main__":
    main()

