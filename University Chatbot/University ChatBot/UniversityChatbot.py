from rdflib import Graph
import re
from KnowledgeBaseAndQuery import sparql_query_5, sparql_query_6

query_graph = Graph()
query_graph.parse("FinalKnowledgeGraph.ttl", format="ttl")

'''Function to fetch the course description of a given course'''
def question1(result):
    course_name = result.groupdict().get("courseName")
    course_name_split = course_name.split(" ")

    query1 = query_graph.query(
        f"""SELECT ?courseTitle ?courseDesc 
            WHERE {{
                ?courseSub a focu:Courses .
                ?courseSub ns1:subject ?courseSubject .
                ?courseSub ns1:identifier '{course_name_split[1]}' .
                ?courseSub ns1:title ?courseTitle .
                ?courseSub ns1:description ?courseDesc .
                FILTER (regex(str(?courseSubject), '{course_name_split[0]}','i'))
            }}""")

    for row in query1:
        print(course_name_split[0].upper(),course_name_split[1],"is %s and the course description is %s" % row)


'''Function to fetch the course details of the courses taken by a particular student'''
def question2(result):
    student_name = result.groupdict().get("studentName")
    if len(student_name.split()) == 2:
        first_name = student_name.split(" ")[0]
        family_name = student_name.split(" ")[1]
    else:
        first_name = student_name
        family_name = None

    query2 = query_graph.query(
        f"""SELECT ?courseSubject ?courseId ?courseName ?grade ?term
            WHERE {{
                ?courseSub a focu:Courses .
                ?courseSub ns1:title ?courseName
                {{
                    SELECT ?courseName ?grade ?term
                    WHERE{{
                        ?transcriptSub a focu:Transcript .
                        ?transcriptSub ns1:identifier ?studentId
                        {{
                            SELECT ?studentId ?grade ?term
                            WHERE{{
                                ?studentSub a focu:Student .
                                ?studentSub foaf:givenName '{first_name}' .
                                Optional {{ ?studentSub foaf:familyName '{family_name}' }} .
                                ?studentSub focu:studentId ?studentId .
                            }}
                        }}
                        ?transcriptSub dbOntology:termPeriod ?term .
                        ?transcriptSub focu:isAwarded ?grade .
                        ?transcriptSub focu:takesCourse ?courseName .   
                    }}
                }}
                ?courseSub ns1:subject ?courseSubject .
                ?courseSub ns1:identifier ?courseId .
            }}""")

    if len(student_name.split()) == 2:
        print(student_name, "took the following courses:")
    else:
        print(first_name,"took the following courses:")
    for row in query2:
        print("%s %s %s scored %s grade in the %s term" % row)


'''Function to fetch the courses which cover the given topic'''
def question3(result):
    topic_name = result.groupdict().get("topicName")

    query3 = query_graph.query(
        f"""SELECT ?courseName 
            WHERE {{
                ?topicSub a focu:Topics .
                ?topicSub ns1:title ?topicName .
                ?topicSub foaf:primaryTopicOf ?courseName .
                FILTER (regex(str(?topicName), '{topic_name}', 'i'))
            }}""")
    print("The following courses cover",topic_name,":")

    for row in query3:
        print("%s" % row)


'''Function to fetch the details of the students who are familiar with the given topic'''
def question4(result):
    topic_name = result.groupdict().get("topicName")
    sparql_query_5(query_graph, topic_name)


'''Function to fetch the topics that are known to a particular student'''
def question5(result):
    student = result.groupdict().get("student")
    if len(student.split(" ")) == 2:
        sparql_query_6(query_graph, student.split(" ")[0], student.split(" ")[1])
    else:
        sparql_query_6(query_graph, student, None)


'''Function which identifies the pattern in a particular question and gives correct answers to the questions asked'''
def university_chatbot():
    print("Hello, I am your smart university agent. How can I help you?")
    while True:
        question = input("Please type your query or type Exit/exit if you do not have any query:")
        if re.search(r'''^[W|w]hat is the (?P<courseName>.*\bw*\b)\?$''', question, flags=re.IGNORECASE):
            result = re.search(r'''[W|w]hat is the (?P<courseName>.*\bw*\b)\?$''', question, flags=re.IGNORECASE)
            question1(result)
        elif re.search(r'''^[W|w]hich courses did (?P<studentName>.*) take\?$''', question, flags=re.IGNORECASE):
            result = re.search(r'''[W|w]hich courses did (?P<studentName>.*) take\?$''', question, flags=re.IGNORECASE)
            question2(result)
        elif re.search(r'''^[W|w]hich courses cover (?P<topicName>.*)\?$''', question, flags=re.IGNORECASE):
            result = re.search(r'''[W|w]hich courses cover (?P<topicName>.*)\?$''', question, flags=re.IGNORECASE)
            question3(result)
        elif re.search(r'''^[W|w]ho is familiar with (?P<topicName>.*)\?$''', question, flags=re.IGNORECASE):
            result = re.search(r'''^[W|w]ho is familiar with (?P<topicName>.*)\?$''', question, flags=re.IGNORECASE)
            question4(result)
        elif re.search(r'''^[W|w]hat does (?P<student>.*) know\?$''', question, flags=re.IGNORECASE):
            result = re.search(r'''^[W|w]hat does (?P<student>.*) know\?$''', question, flags=re.IGNORECASE)
            question5(result)
        elif re.search(r'''[E|e]xit''', question):
            exit()
        result = None
        print()


if __name__ == '__main__':
    university_chatbot()