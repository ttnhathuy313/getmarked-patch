from bs4 import BeautifulSoup, NavigableString
import json

data_json = ""
with open('usecase.html', 'r') as f:
    soup = BeautifulSoup(''.join(f.read().split('\n')), 'html.parser')

def get_pandoc_content_iter(tag):
    if (isinstance(tag, NavigableString)):
        with open('content.txt', 'a') as f:
            if (tag.string == '\n'):
                return
            f.write(tag.string)
            f.write('\n')
    else:
        for child in tag.contents:
            get_pandoc_content_iter(child)

def get_pandoc_content():
    with open('content.txt', 'w') as f:
        pass
    get_pandoc_content_iter(soup)

def get_header_from_html(tag):
    if (isinstance(tag, NavigableString)):
        parse_question = open('content.txt', 'r').read()
        #remove trailing spaces
        if (parse_question.count(tag.string.strip()) == 1):
            return tag.string.strip()
        else: return -1
    else:
        for child in tag.contents:
            v = get_header_from_html(child)
            if (v != -1):
                return v
    return -1

question_index = 0
question_header = ""
prev_question_header = ""
multiple_choices = ['A', 'B', 'C', 'D']
choice_tags_list = []
choice_contents = []

def find_lca(tag_list):
    common_ancestor = tag_list[0].parent
    ok = True
    for i in range(1, len(tag_list)):
        if (tag_list[i].parent != common_ancestor):
            ok = False
    if (not ok): 
        return find_lca([tag.parent for tag in tag_list])
    else: return common_ancestor


def filter_choice_from_lca(lca, depth = 0):
    global choice_contents
    choice_in_subtree = ''
    children_result = []
    for child in lca.contents:
        if (isinstance(child, NavigableString)):
            if (child.string in ['A', 'B', 'C', 'D']):
                choice_contents.append([child.string, []])
                return child.string
        else:
            avail = filter_choice_from_lca(child, depth + 1)
            children_result.append((avail, child))
            if (avail != None):
                choice_in_subtree = avail
    latest_choice = None
    for choice, child in children_result:
        if (choice != None):
            latest_choice = choice
        if (choice == None and choice_in_subtree and latest_choice != None):
            for i in range(len(choice_contents)):
                if (choice_contents[i][0] == latest_choice):
                    choice_contents[i][1].append(child)
                    break


    if (depth == 0):
        return choice_contents
    else: 
        if (choice_in_subtree != ''):
            return choice_in_subtree
        else: return None

def fix_image_in_choicse(tag, depth = 0):
    global question_index
    global question_header
    global multiple_choices
    global choice_tags_list
    global prev_question_header
    global choice_contents

    if (question_header == "" and question_index < len(data_json['questions'])):
        question_prompt = data_json['questions'][question_index]['prompt']
        question_prompt_soup = BeautifulSoup(question_prompt, 'html.parser')
        question_header = get_header_from_html(question_prompt_soup)
    if (isinstance(tag, NavigableString)):
        if (question_header in tag.string) and (question_header != ""):
            if (len(multiple_choices) <= 1):
                cur_type = data_json['questions'][question_index]['category']
                if (cur_type == 'OEQ'):
                    min_depth = 0
                    for choice_tag in choice_tags_list:
                        if (choice_tag[0] > min_depth):
                            min_depth = choice_tag[0]
                    for i in range(len(choice_tags_list)):
                        while (choice_tags_list[i][0] > min_depth):
                            choice_tags_list[i][0] -= 1
                            choice_tags_list[i][1] = choice_tags_list[i][1].parent
                    #climb to the common ancestors from all choice tag
                    common_ancestor = find_lca([choice_tag[1] for choice_tag in choice_tags_list])
                    choice_contents = []
                    # print(filter_choice_from_lca(common_ancestor))
                    data_json['questions'][question_index - 1]['category'] = 'MCQ'
                    data_json['questions'][question_index - 1]['choices'] = [{
                        'id': choice[0],
                        'content': ''.join([str(child) for child in choice[1]])
                    } for choice in choice_contents]

            prev_question_header = question_header
            multiple_choices = ['A', 'B', 'C', 'D']
            choice_tags_list = []
            question_index += 1
            question_header = ""
        else:
            if (tag.string in multiple_choices):
                #erase tag.string from multiple_choices
                multiple_choices.remove(tag.string)
                choice_tags_list.append((depth, tag))


    else:
        for child in tag.contents:
            fix_image_in_choicse(child, depth + 1)

def fix(path_to_getmarked_output, path_to_save_output):
    global data_json
    global soup
    get_pandoc_content()
    data_json = json.load(open(path_to_getmarked_output, 'r'))
    fix_image_in_choicse(soup)
    json.dump(data_json, open(path_to_save_output, 'w'), indent=2)
