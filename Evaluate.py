import os
import re


def main():
    # get the current working directory
    cwd = os.getcwd()
    path = os.path.join(cwd, "output")
    # get all the folders in the output folder
    output_folders = [x[0] for x in os.walk(path)]
    # remove the base directory
    output_folders.pop(0)
    # get the path to the gold standard tagged files
    gold_folder_path = os.path.join(cwd, "data")
    gold_folder_path = os.path.join(gold_folder_path, "test_tagged")
    precision_sum = 0
    recall_sum = 0
    f_measure_sum = 0
    for folder in output_folders:
        files = os.listdir(folder)
        for file in files:
            file_path = os.path.join(folder, file)
            text = ""
            # read in the text in the file I tagged
            with open(file_path) as f:
                line = f.readline()
                while line:
                    text += line
                    line = f.readline()
            stimes = get_tagged_start_times(text)
            etimes = get_tagged_end_times(text)
            speakers = get_tagged_speakers(text)
            locations = get_tagged_locations(text)
            sentences = get_tagged_sentences(text)
            paragraphs = get_tagged_paragraphs(text)

            gold_file_path = os.path.join(gold_folder_path, file)
            gold_text = ""
            # read in the text in the file of the gold standard tagging
            with open(gold_file_path) as f:
                line = f.readline()
                while line:
                    gold_text += line
                    line = f.readline()
            gold_stimes = get_tagged_start_times(gold_text)
            gold_etimes = get_tagged_end_times(gold_text)
            gold_speakers = get_tagged_speakers(gold_text)
            gold_locations = get_tagged_locations(gold_text)
            gold_sentences = get_tagged_sentences(gold_text)
            gold_paragraphs = get_tagged_paragraphs(gold_text)

            precision = calc_precision(stimes, gold_stimes)\
                        + calc_precision(etimes, gold_etimes)\
                        + calc_precision(speakers, gold_speakers)\
                        + calc_precision(locations, gold_locations)\
                        + calc_precision(sentences, gold_sentences)\
                        + calc_precision(paragraphs, gold_paragraphs)
            precision = precision / 6

            recall = calc_recall(stimes, gold_stimes) \
                        + calc_recall(etimes, gold_etimes) \
                        + calc_recall(speakers, gold_speakers) \
                        + calc_recall(locations, gold_locations) \
                        + calc_recall(sentences, gold_sentences) \
                        + calc_recall(paragraphs, gold_paragraphs)
            recall = recall / 6

            f_measure = calc_f_measure(precision, recall)

            precision_sum += precision
            recall_sum += recall
            f_measure_sum += f_measure

    final_precision = precision_sum / 184
    final_recall = recall_sum / 184
    final_f_measure = f_measure_sum / 184

    print("Precision: " + str(final_precision))
    print("Recall: " + str(final_recall))
    print("F measure: " + str(final_f_measure))


# get the tagged times
def get_tagged_start_times(text):
    start_times = re.findall(r'(?<=<stime>).*(?=<\/stime>)', text)
    return start_times


# get the tagged ends
def get_tagged_end_times(text):
    end_times = re.findall(r'(?<=<etime>).*(?=<\/etime>)', text)
    return end_times


# get the tagged speakers
def get_tagged_speakers(text):
    speakers = re.findall(r'(?<=<speaker>).*(?=<\/speaker>)', text)
    return speakers


# get the tagged locations
def get_tagged_locations(text):
    locations = re.findall(r'(?<=<location>).*(?=<\/location>)', text)
    return locations


# get the tagged sentences
def get_tagged_sentences(text):
    #text = text.replace("\n", "")
    sentences = re.findall(r'(?<=<sentence>).*?(?=<\/sentence>)', text, re.DOTALL)
    formatted_sentences = []
    for s in sentences:
        s = s.replace("<stime>", "")
        s = s.replace("</stime>", "")
        s = s.replace("<etime>", "")
        s = s.replace("</etime>", "")
        s = s.replace("<speaker>", "")
        s = s.replace("</speaker>", "")
        s = s.replace("<location>", "")
        s = s.replace("</location>", "")
        formatted_sentences.append(s)
    return formatted_sentences


# get the tagged paragraphs
def get_tagged_paragraphs(text):
    paragraphs = re.findall(r'(?<=<paragraph>).*?(?=<\/paragraph>)', text, re.DOTALL)
    formatted_paragraphs = []
    for s in paragraphs:
        s = s.replace("<stime>", "")
        s = s.replace("</stime>", "")
        s = s.replace("<etime>", "")
        s = s.replace("</etime>", "")
        s = s.replace("<speaker>", "")
        s = s.replace("</speaker>", "")
        s = s.replace("<location>", "")
        s = s.replace("</location>", "")
        s = s.replace("<sentence>", "")
        s = s.replace("</sentence>", "")
        formatted_paragraphs.append(s)
    return formatted_paragraphs


# calculate the precision
# precision = #TPclassified / #classified
def calc_precision(list, gold_list):
    numerator = 0
    denominator = len(list)
    for item in list:
        if item in gold_list:
            numerator += 1
    if denominator == 0:
        return 1
    result = numerator / denominator
    return result


# calculate the recall
# recall = #TPclassified / #TP_in_corpus
def calc_recall(list, gold_list):
    numerator = 0
    denominator = len(gold_list)
    for item in list:
        if item in gold_list:
            numerator += 1
    if numerator == 0 and denominator == 0:
        return 1
    if denominator == 0:
        return 0
    result = numerator / denominator
    return result


# calculate the f measure
# f measure = 2 * (precision * recall) / (precision + recall))
def calc_f_measure(precision, recall):
    numerator = precision * recall
    denominator = precision + recall
    result = 2 * (numerator / denominator)
    return result


main()
