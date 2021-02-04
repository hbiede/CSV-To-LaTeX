#!/bin/env python3
# Created by Hundter Biede
import random
import string
import re
from typing import List, Tuple, Literal, Union, Optional
import matplotlib.pylab as plt
import csv
import sys

"""
The manner in which the eval will be parsed is listed below. The outputted
LaTeX file will follow the order and formatting assigned below.

The format of this styling is an array of tuples. The tuples must follow the
following formats:

('normal', X) where X is a single column index. This will print all responses
  as a list
('rating', X) where X is a single column index. This will print all responses
  as a pie chart. This column will also split on columns to count multiple
  values
('rating_with_reasoning', X, Y, C) where X and Y are single column indices.
  This will create a pie chart of the values in X, and a list of responses
  in Y, where each response is prepended with its associated rating. The section
  header will be the column header of column X. C will be the character used to
  separate the rating from the response. A hyphen will be used if no C is
  provided.
('rating_with_response_no_rating', X, Y) - Same as rating_with_reasoning, but
  without concatenation of the rating and response.
('combo', X, Y, C) where X and Y are single column indices. This will print all
  responses as a list, with X and Y concatenated with character C (if no
  character is provided, a hyphen will be used as default).
('section', A) where A is an array. This array should contain more nested
  arrays describing how the associated columns should be printed (think another
  document inside this one). Data in a section will be split by the values in
  'name'. Thus, the first array in a 'section' format array must always be a 
  'name' format to permit splitting. Nesting 'section's is limited to 4 in
  depth.
('name', X, B) where X is a single column index. This will create a (sub)section
  header and B is a boolean (True or False) denoting if the section should
  appear on a new page.
('text', X) where X is a string to be printed, as-is.
('title', X) where X is the column from which the first value should be printed
  as a (sub)section header
"""
OneArgType = Tuple[Literal['normal', 'rating'], int]
TextArgType = Tuple[Literal['text'], str]
TwoArgType = Tuple[Literal['rating_with_response_no_rating'], int, int]
ThreeArgType = Tuple[Literal['rating_with_reasoning', 'combo'], int, int, Optional[str]]
NameType = Tuple[Literal['name'], bool]
Section = Union[OneArgType, TextArgType, TwoArgType, ThreeArgType, NameType]
"""
multiple_files_column, if greater than or equal to 0, splits the results into
separate files grouped by common values from the given column.
"""
multiple_files_column = 1
column_styles: List[Section] = [
    ('rating', 2),
    ('rating', 3),
    ('normal', 4),
    ('normal', 5),
    ('rating', 6),
    ('rating', 7),
    ('normal', 8),
    ('normal', 9),
    ('normal', 10),
    ('normal', 11),
    ('normal', 12),
    ('rating', 13),
    ('rating', 14),
    ('rating', 15),
]

figure_storage = './figures'
figure_file_extension = 'png'


def arg_check() -> None:
    if sys.argv.count('--help') > 0 or sys.argv.count('-h') > 0:
        print("Usage: %s [data file csv]" % sys.argv[0])
        sys.exit(0)
    if len(sys.argv) < 2 or sys.argv[1] is None:
        print("Usage: %s [data file csv]" % sys.argv[0], file=sys.stderr)
        sys.exit(1)


def read_csv() -> List[List[str]]:
    with open(sys.argv[1], newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        return_val = []
        for line in reader:
            return_val.append(line)
        return return_val


def parse_normal(eval_data: List[List[str]], index: int) -> str:
    if len(eval_data) <= 1:
        return ''
    return_val = "\\begin{itemize}\n"
    for i in range(1, len(eval_data)):
        line = eval_data[i][index].strip()
        if len(line) > 0:
            return_val += "\\item %s\n" % line
    return return_val + "\\end{itemize}\n"


def random_name(length: int) -> str:
    rand_name = ''
    while rand_name == '' or os.path.exists('%s/%s.%s' % (figure_storage, rand_name, figure_file_extension)):
        letters = string.ascii_lowercase
        rand_name = ''.join(random.choice(letters) for _ in range(length))
    return rand_name


def parse_rating(eval_data: List[List[str]], index: int) -> str:
    rating_data = {}
    for i in range(1, len(eval_data)):
        value = eval_data[i][index].strip()
        if len(value) > 0:
            split_values = value.split(',')
            for split_value in split_values:
                split_value_trimmed = re.sub('[!.?]$', '', split_value.strip().lower())
                rating_data[split_value_trimmed] = \
                    rating_data[split_value_trimmed] + 1 if split_value_trimmed in rating_data else 1
    if len(rating_data.values()) == 0:
        return ''
    fig1, ax1 = plt.subplots()
    ax1.pie(rating_data.values(), labels=rating_data.keys(), autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')

    output_file = "./%s/%s.%s" % (figure_storage, random_name(6), figure_file_extension)
    open(output_file, "w").close()  # create the file if it doesn't exist
    plt.savefig(output_file)
    plt.close()
    return (("\\begin{figure}[H]\n" +
             "\\centering\n" +
             "\\includegraphics[width=0.8\\textwidth]{%s}\n" +
             "\\centering\n" +
             "\\end{figure}\n") % output_file)


def parse_combined_columns(eval_data: List[List[str]], index_a: int, index_b: int, delimiter: str = '-') -> str:
    if len(eval_data) <= 1:
        return ''
    return_val = "\\begin{itemize}\n"
    for i in range(0, len(eval_data)):
        item_a = eval_data[i][index_a].strip()
        item_b = eval_data[i][index_b].strip()
        if len(item_a) > 0 and len(item_b) > 0:
            return_val += "\\item %s %s %s\n" % (item_a, delimiter, item_b)
        elif len(item_a) > 0:
            return_val += "\\item %s\n" % item_a
        elif len(item_b) > 0:
            return_val += "\\item %s\n" % item_b
    return return_val + "\\end{itemize}\n"


def parse_rating_with_reasoning(eval_data: List[List[str]], index_rating: int, index_reasoning: int,
                                should_combine=True, delimiter: str = '-') -> str:
    return "%s\n%s" % (
        parse_rating(eval_data, index_rating),
        parse_combined_columns(eval_data, index_rating, index_reasoning, delimiter) if should_combine else parse_normal(
            eval_data,
            index_reasoning))


def section_header(column_name: str, section_depth: int = 0) -> str:
    if section_depth < 0 or section_depth > 3:
        return column_name

    if section_depth == 0:
        return "\\section{%s}\n" % column_name
    elif section_depth == 1:
        return "\\subsection{%s}\n" % column_name
    elif section_depth == 2:
        return "\\subsubsection{%s}\n" % column_name
    elif section_depth == 3:
        return "\\paragraph{%s}\n" % column_name


def parse_section(eval_data: List[List[str]], sections, section_depth: int = 0) -> str:
    if sections[0][0] != 'name':
        return r'\LARGE{error is section formatting. Must include a name}'
    return_val = section_header(eval_data[0][sections[0][1]], section_depth)
    section_categories = list(set(eval_data[i][sections[0][1]] for i in range(1, len(eval_data))))
    section_categories.sort()
    for section_category in section_categories:
        section_category_trimmed = section_category.strip()
        if len(section_category_trimmed) > 0:
            section_data = list(filter(lambda row: row[sections[0][1]] == section_category_trimmed, eval_data))
            if len(section_data) > 0:
                section_data.insert(0, eval_data[0])
                section_contents = parse_evals(section_data, sections[1:], section_depth + 2)
                if 'itemize' in section_contents and r'\item' in section_contents:
                    if sections[0][2]:
                        return_val += "\\pagebreak\n"
                    return_val += section_header(section_category_trimmed, section_depth + 1)
                    return_val += section_contents
    return return_val


def parse_evals(eval_data: List[List[str]], sections: List[Section], section_depth: int = 0) -> str:
    if section_depth < 0 or section_depth > 2:
        return ""
    return_val = ""
    for section in sections:
        if isinstance(section[1], int) and section[0] != 'title':
            return_val += section_header(eval_data[0][section[1]], section_depth)
        elif section[0] == 'title':
            return_val += section_header(eval_data[1][section[1]], section_depth)

        if section[0] == 'normal':
            contents = parse_normal([eval_data[0]] + random.sample(eval_data[1:], len(eval_data) - 1), section[1])
            if 'itemize' in contents and r'\item' in contents:
                return_val += contents
        elif section[0] == 'rating':
            return_val += parse_rating([eval_data[0]] + random.sample(eval_data[1:], len(eval_data) - 1), section[1])
        elif section[0] == 'rating_with_reasoning':
            return_val += parse_rating_with_reasoning([eval_data[0]] + random.sample(eval_data[1:], len(eval_data) - 1),
                                                      section[1], section[2], True,
                                                      section[3] if len(section) == 4 else '-')
        elif section[0] == 'rating_with_response_no_rating':
            return_val += parse_rating_with_reasoning([eval_data[0]] + random.sample(eval_data[1:], len(eval_data) - 1),
                                                      section[1], section[2], False)
        elif section[0] == 'combo':
            contents = parse_combined_columns([eval_data[0]] + random.sample(eval_data[1:], len(eval_data) - 1),
                                              section[1], section[2],
                                              section[3] if len(section) == 4 else '-')
            if 'itemize' in contents and r'\item' in contents:
                return_val += contents
        elif section[0] == 'section':
            return_val += parse_section(eval_data, section[1], section_depth)
        elif section[0] == 'text':
            return_val += section[1]
        return_val += "\n"
    return return_val


def split_and_parse_sections(eval_data: List[List[str]], sections: List[Section], group_by_column) -> [str]:
    section_categories = list(set(eval_data[i][group_by_column] for i in range(1, len(eval_data))))
    section_categories.sort()
    return_val = {}
    for section_category in section_categories:
        section_category_trimmed = section_category.strip()
        if len(section_category_trimmed) > 0:
            section_data = list(filter(lambda row: row[group_by_column] == section_category_trimmed, eval_data))
            if len(section_data) > 0:
                section_data.insert(0, eval_data[0])
                return_val[section_category_trimmed] = parse_evals(section_data, sections)
    return return_val


if __name__ == '__main__':
    import os

    if not os.path.exists(figure_storage):
        os.mkdir(figure_storage)
    arg_check()
    csv_data = read_csv()
    if multiple_files_column < 0:
        latex = parse_evals(csv_data, column_styles).replace('#', r'\#').replace('&', r'\&').replace('$', r'\$') \
            .replace('_', r'\_')
        with open('template.tex', 'r') as output:
            open('output.tex', 'w').write(output.read().strip().replace('DATA_LATEX_OUTPUT', latex))
    else:
        latex_array = split_and_parse_sections(csv_data, column_styles, multiple_files_column)
        with open('template.tex', 'r') as output:
            output_text = output.read().strip()
            for name in latex_array:
                file_name = name.replace(' ', '')
                open('%s.tex' % file_name, 'w').write(output_text.replace('NAMEPLACEHOLDER', name) \
                                                      .replace('DATA_LATEX_OUTPUT', latex_array[name]))
