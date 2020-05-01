import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

#Web Scraping of Software Engineering and Computer Science Course page
def compWebPageScraping(comp_grad_page):
    page = requests.get(comp_grad_page)
    soup = BeautifulSoup(page.content, "html.parser")
    #print(soap)
    section = soup.find(id="content-main")
    course_details = section.find_all(class_="wysiwyg parbase section")
    courses = course_details[2].find_all("p")
    course_name_list = course_details[0].find_all(class_="large-text")
    #print(course_name_list)

    course_name = []
    course_subject = []
    course_number = []
    course_desc = []
    course_link = []
    for i in range(2, len(courses)):
        courses_split = courses[i].find(class_="large-text").getText(strip=True).replace(u"\xa0", u" ").split(")", 1)
        print (courses_split)
        cname_split = courses_split[0].split("(")[0]
        courses_split.pop(0)
        #print(courses_split)
        if len(courses_split)>1:
          x=courses_split[1]
        else:
          x=courses_split[0]
        course_desc.append(x)
        course_subject.append(cname_split.strip().split(" ", 2)[0])
        course_number.append(cname_split.strip().split(" ", 2)[1])
        course_name.append(cname_split.strip().split(" ", 2)[2])
        course_link.append(comp_grad_page)

    courses_list = []
    for j in range(1, len(course_name_list), 2):
        courses = course_name_list[j].find_all("b")
        #print(courses)
        for k in courses:
            data = k.getText().replace(u"\xa0", u" ").strip()
            if "\n" in data:
                data_split = data.split("\n")
                for l in data_split:
                    courses_list.append(l)
            else:
                courses_list.append(data)

    #print(courses_list)
    for items in courses_list:
        if "(" in items:
            item_spl = items.split("(", 1)
        else:
            item_spl = items.split("\n",1)
        items_split = item_spl[0].strip().split(" ", 2)
        #print(items_split[2])
        if items_split[2] in course_name:
            #print("yes")
            continue
        else:
            course_desc.append("")
            course_subject.append(items_split[0])
            course_number.append(items_split[1])
            course_name.append(items_split[2])
            course_link.append(comp_grad_page)

    '''print(course_subject)
    print(course_number)
    print(course_name)
    print(course_desc)'''

    df = pd.DataFrame(
        {'course_number': course_number,
         'course_subject': course_subject,
         'course_name': course_name,
         'course_desc': course_desc,
         'course_link': course_link
        })
    df.to_csv('Courses.csv', index=False, sep='|')


def course_name_extract(courses, course_number, course_subject, course_name, course_desc, course_link, grad_page):
    #print(courses)
    reg_pattern = re.compile(r'[A-Z]\d\d -')
    for i in courses[1:]:
        #print(i.find_all("b"))
        data = i.getText().replace(u"\xa0", u" ")
        #print(data)
        if "Note:" in data:
            continue
        if reg_pattern.search(data):
            continue
        else:
            #print(data)
            if "\n" in data:
                data_split = data.split("\n")
                #print(data_split)
                for l in data_split:
                    split_data = l.split("(",1)[0]
                    course_subject.append(split_data.strip().split(" ", 2)[0])
                    course_number.append(split_data.strip().split(" ", 2)[1])
                    course_name.append(split_data.strip().split(" ", 2)[2])
                    course_desc.append("")
                    course_link.append(grad_page)
            else:
                split_dt = data.split("(",1)[0]
                course_subject.append(split_dt.strip().split(" ", 2)[0])
                course_number.append(split_dt.strip().split(" ", 2)[1])
                course_name.append(split_dt.strip().split(" ", 2)[2])
                course_desc.append("")
                course_link.append(grad_page)


def courses_with_desc(courses, course_number, course_subject, course_name, course_desc, course_link, grad_page):
    for item in courses:
        item_clean = item.getText().replace(u"\xa0", u" ")
        #print(item_clean)

        if "ENCS 8501 Comprehensive Examination (No credit value)" in item_clean:
            continue

        if "ENGR 791 Topics in Engineering II" in item_clean:
            item_split = item_clean.strip().split("\n", 2)

        if "(***)" in item_clean:
            item_split = item_clean.strip().split(")", 2)
        #elif "(****)" in item_clean:
        #    item_split = item_clean.split("redits)", 2)
        elif "credits" in item_clean or "Credits" in item_clean:
            item_split = item_clean.strip().split("redits)", 2)
        elif "credit" in item_clean or "Credit" in item_clean:
            item_split = item_clean.strip().split("redit)", 2)
        elif "credtis" in item_clean:
            item_split = item_clean.strip().split("redtis)", 2)

        #print(item_split)
        if item_split[0] == '(4 c':
            name_split = 'INDU 6211 Production Systems and Inventory Control'
        else:
            name_split = item_split[0].split("(",1)[0]
        #print(name_split)
        #print()
        if len(item_split) == 1:
            continue
        else:
            desc = item_split[1]
            if name_split.strip().split(" ",2)[2] in course_name:
                #print(name_split.strip().split(" ",2)[2])
                index1 = course_name.index(name_split.strip().split(" ",2)[2])
                course_desc[index1] = desc.strip()
            else:
                course_subject.append(name_split.strip().split(" ", 2)[0])
                course_number.append(name_split.strip().split(" ", 2)[1])
                course_name.append(name_split.strip().split(" ", 2)[2])
                course_desc.append(desc.strip())
                course_link.append(grad_page)

def engWebPageScraping(grad_page):
    course_name = []
    course_subject = []
    course_number = []
    course_desc = []
    course_link = []
    page = requests.get(grad_page)
    soup = BeautifulSoup(page.content, "html.parser")
    #print(soap)
    section = soup.find(id="content-main")
    course_details = section.find_all(class_="wysiwyg parbase section")
    #course_details = course_details.find_all(class_="large-text")
    for i in range(3, 46):
        courses = course_details[i].find_all(class_="large-text")
        course_name_extract(courses, course_number, course_subject, course_name, course_desc, course_link, grad_page)

    for i in range(51, 58):
        courses = course_details[i].find_all(class_="large-text")
        #print(courses)
        courses_with_desc(courses, course_number, course_subject, course_name, course_desc, course_link, grad_page)

    '''print(course_number)
    print(course_subject)
    print(course_name)
    print(course_desc)'''

    df = pd.DataFrame(
        {'course_number': course_number,
         'course_subject': course_subject,
         'course_name': course_name,
         'course_desc': course_desc,
         'course_link' : course_link
         })
    df.to_csv('Courses.csv', mode='a', index=False, sep='|', header=False)


comp_grad_page = "https://www.concordia.ca/academics/graduate/calendar/current/encs/computer-science-courses.html#course-descriptions"
compWebPageScraping(comp_grad_page)
#grad_page = "https://www.concordia.ca/academics/graduate/calendar/current/encs/engineering-courses.html#topicsinengineering"
#engWebPageScraping(grad_page)