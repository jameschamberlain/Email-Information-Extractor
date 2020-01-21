import os
from nltk.tokenize import sent_tokenize
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from collections import Counter
from nltk.corpus import wordnet as wn


def main():
    # load in the files
    male_names = get_names("male")
    female_names = get_names("female")
    family_names = get_names("family")
    path_to_files = load_files()
    for file in os.listdir(path_to_files):
        path = os.path.join(path_to_files, file)
        # tag the sentences and paragraphs
        result = tag(path)
        category = get_category(path, male_names, female_names, family_names)
        output_files(result, file, category)


# get a list of male names
def get_names(version):
    file_name = "names." + version + ".txt"
    path = os.getcwd()
    path = os.path.join(path, 'data')
    path = os.path.join(path, file_name)
    names = []
    file = open(path, "r")
    for line in file:
        name = line.rstrip()
        names += [name.lower()]
    file.close()
    return names


# load in the files
def load_files():
    path = os.getcwd()
    path = os.path.join(path, 'data', 'test_untagged')
    return path


# output the files
def output_files(text, file_name, folder):
    output_path = os.getcwd()
    output_path = os.path.join(output_path, 'output')
    output_path = os.path.join(output_path, folder)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    output_path = os.path.join(output_path, file_name)
    output_file = open(output_path, "w")
    output_file.write(text)
    output_file.close()


# tag paragraphs and sentences
def tag(file):
    start_time = ""
    end_time = ""
    speaker = ""
    location = ""
    lines = []

    with open(file) as f:
        line = f.readline()
        while line:
            text = line
            line = f.readline()
            # while the line is not empty and is a line add it to the string text
            while not line.isspace() and line:
                text += line
                line = f.readline()
                # if the header contains the time, tag it
                if "Time:     " in line:
                    line = tag_time_in_head(line)
                    if "<stime>" in line:
                        if len(start_time) == 0:
                            start_time = get_start_time(line)
                    if "<etime>" in line:
                        if len(end_time) == 0:
                            end_time = get_end_time(line)
                # if the header contains the speaker, tag it
                if "Who:      " in line:
                    line = tag_speaker_in_head(line)
                    if "<speaker>" in line:
                        speaker = get_speaker(line)
                # if the header contains the location, tag it
                if "Place:    " in line:
                    line = tag_location_in_head(line)
                    if "<location>" in line:
                        location = get_location(line)

            # detach newline characters from strings
            first2 = text[:1]
            last2 = text[-1:]
            if first2 == "\n" and last2 == "\n":
                lines.append("\n")
                lines.append(text[1:-1])
                lines.append("\n")
            elif first2 == "\n":
                lines.append("\n")
                lines.append(text[1:])
            elif last2 == "\n":
                lines.append(text[:-1])
                lines.append("\n")
            else:
                lines.append(text)
    # loop through the lines array while keeping track
    # of the element and its index
    lines = tag_sents_para(lines)
    tagged_text = ""
    for line in lines:
        tagged_text += line
    # modify current formatting to more closely resemble the input
    tagged_text = tagged_text.replace(".</sentence>", "</sentence>.")
    tagged_text = tagged_text.replace(".<sentence>", ".  <sentence>")
    tagged_text = tagged_text.replace("!</sentence>", "</sentence>!")
    tagged_text = tagged_text.replace("!<sentence>", "!  <sentence>")
    tagged_text = tagged_text.replace("?</sentence>", "</sentence>?")
    tagged_text = tagged_text.replace("?<sentence>", "?  <sentence>")
    # split the email into the head and body
    split_email = tagged_text.split('Abstract:')
    # tag instances of the speaker in the body
    if len(speaker) > 0:
        split_email[1] = split_email[1].replace(speaker, '<speaker>' + speaker + '</speaker>')
        # remove double tags
        split_email[1] = split_email[1].replace("<speaker><speaker>", "<speaker>")
        split_email[1] = split_email[1].replace("</speaker></speaker>", "</speaker>")
    # tag instances of the location in the body
    if len(location) > 0:
        split_email[1] = split_email[1].replace(location, '<location>' + location + '</location>')
        # remove double tags
        split_email[1] = split_email[1].replace("<location><location>", "<location>")
        split_email[1] = split_email[1].replace("</location></location>", "</location>")
    # tag instances of the start time in the body
    if len(start_time) > 0:
        split_email[1] = tag_time_in_body(start_time, split_email[1], True)
        # remove double tags
        split_email[1] = split_email[1].replace("<stime><stime>", "<stime>")
        split_email[1] = split_email[1].replace("</stime></stime>", "</stime>")
    # tag instances of the end time in the body
    if len(end_time) > 0:
        split_email[1] = tag_time_in_body(end_time, split_email[1], False)
        # remove double tags
        split_email[1] = split_email[1].replace("<etime><etime>", "<etime>")
        split_email[1] = split_email[1].replace("</etime></etime>", "</etime>")
    tagged_text = str(split_email[0]) + "Abstract:" + str(split_email[1])
    return tagged_text


# tags sentences and paragraphs
def tag_sents_para(text):
    for i, s in enumerate(text):
        # if the string contains three words then a sentence end then it is likely a paragraph,
        # tag it as a paragraph and tag each sentence
        if re.search('([A-Za-z]+\s){3,}\w*[.?!]', s):
            sents = sent_tokenize(s)
            new_str = "<paragraph>"
            for sent in sents:
                new_str += "<sentence>"
                new_str += sent
                new_str += "</sentence>"
            new_str += "</paragraph>"
            text[i] = new_str
    return text


# tag the start and end time in the head if available
def tag_time_in_head(text):
    text = text[:-1]
    text = re.sub(r'(?<=Time:\s{5})([0-9]{1,2})(\s?)(?:((?=[:])([:])((\s?)'
                  r'([0-9]{1,2}))|(([a](\.?)[m])(\.?)|([p](\.?)[m](\.?))'
                  r'|([A](\.?)[M](\.?))|([P](\.?)[M](\.?))))(\s?))(([a](\.?)[m](\.?))'
                  r'|([p](\.?)[m](\.?))|([A](\.?)[M](\.?))|([P](\.?)[M](\.?)))?',
                  r'<stime>\1\2\3\13\14</stime>', text)
    text = re.sub(r'(?<=[-]\s)([0-9]{1,2})(\s?)(?:((?=[:])([:])((\s?)'
                  r'([0-9]{1,2}))|(([a](\.?)[m](\.?))|([p](\.?)[m](\.?))'
                  r'|([A](\.?)[M](\.?))|([P](\.?)[M](\.?))))(\s?))(([a]'
                  r'(\.?)[m](\.?))|([p](\.?)[m](\.?))|([A](\.?)[M](\.?))|([P](\.?)[M](\.?)))?',
                  r'<etime>\1\2\3\13\14</etime>', text)
    return text + "\n"


# get the start time
def get_start_time(text):
    match = re.search(r'(?<=<stime>).*(?=<\/stime>)', text)
    return match.group(0)


# get the start time
def get_end_time(text):
    match = re.search(r'(?<=<etime>).*(?=<\/etime>)', text)
    return match.group(0)


# tag the speaker in the head if available
def tag_speaker_in_head(text):
    text = re.sub(r'(?<=Who:\s{6})([A-Z])(\w+)(\s([A-Z])\w+)?',
                  r'<speaker>\1\2\3</speaker>', text)
    return text


# get the speaker
def get_speaker(text):
    match = re.search(r'(?<=<speaker>).*(?=<\/speaker>)', text)
    return match.group(0)


# tag instances of the selected time in the body
def tag_time_in_body(base_time, text, start):
    times = re.findall(r'(([0-9]{1,2})(\s?)(?:((?=[:])([:])((\s?)([0-9]{1,2}))'
                      r'|(([a](\.?)[m](\.?))|([p](\.?)[m](\.?))|([A](\.?)[M](\.?))'
                       r'|([P](\.?)[M](\.?))))(\s?))(([a](\.?)[m](\.?))|([p](\.?)'
                       r'[m](\.?))|([A](\.?)[M](\.?))|([P](\.?)[M](\.?)))?)', text)
    before_colon = re.search(r'\d{1,2}(?=:)', base_time)
    before_colon = before_colon.group(0)
    after_colon = re.search(r'(?<=:)\d{1,2}',base_time)
    after_colon = after_colon.group(0)
    base_num = before_colon + "." + after_colon
    base_num = float(base_num)
    for time in times:
        if ":" in time:
            before_colon = re.search(r'\d{1,2}(?=:)', time[0])
            before_colon = before_colon.group(0)
            after_colon = re.search(r'(?<=:)\d{1,2}', time[0])
            after_colon = after_colon.group(0)
        else:
            before_colon = re.search(r'\d{1,2}', time[0])
            before_colon = before_colon.group(0)
            after_colon = "0"
        num = before_colon + "." + after_colon
        num = float(num)
        if num == base_num and start:
            text = text.replace(time[0], "<stime>" + time[0] + "</stime>")
        elif num == base_num and not start:
            text = text.replace(time[0], "<etime>" + time[0] + "</etime>")
    return text


# tag the location in the head if available
def tag_location_in_head(text):
    text = re.sub(r'(?<=Place:\s{4})(.*)?',
                  r'<location>\1</location>', text)
    return text


# get the location
def get_location(text):
    match = re.search(r'(?<=<location>).*(?=<\/location>)', text)
    return match.group(0)


# get the category
def get_category(file, male_names, female_names, family_names):
    text = ""
    with open(file) as f:
        line = f.readline()
        while line:
            text += line
            line = f.readline()
    text = text.lower()
    text = word_tokenize(text)
    wnl = WordNetLemmatizer()
    lemmed = []
    result = []
    for i in text:
        if ("." not in i) and (len(i) > 4):
            lemmed.append(wnl.lemmatize(i))
    text = nltk.pos_tag(lemmed)
    for i in text:
        # check if the word is a noun or plural noun
        if i[1] == 'NN' or i[1] == 'NNS':
            if (re.match(r"([A-Za-z])+$", i[0])) is not None:
                is_noun = True
                if len(wn.synsets(i[0], pos=wn.VERB)) > 0:
                    is_noun = False
                if len(wn.synsets(i[0], pos=wn.ADJ)) > 0:
                    is_noun = False
                if len(wn.synsets(i[0], pos=wn.ADV)) > 0:
                    is_noun = False
                if is_noun:
                    # check if the word is a name
                    if (i[0] not in male_names) and (i[0] not in female_names) and (i[0] not in family_names) and \
                            (not i[0] == "seminar"):
                        result.append(i[0])
    category = Counter(result).most_common(1)
    if len(category) == 0:
        category = "no category"
    else:
        category = category[0][0]
        category = category.lower()
    return category


# run the main function
main()
