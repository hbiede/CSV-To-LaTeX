#!/bin/env python3
import random
import string
import re
from typing import List, Tuple, Literal, Iterable, Union
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
('rating_with_reasoning', X, Y) where X and Y are single column indices. This
  will create a pie chart of the values in X, and a list of responses in Y,
  where each response is prepended with its associated rating. The section
  header will be the column header of column X.
('rating_with_response_no_rating', X, Y) - Same as rating_with_reasoning, but
  without concatenation of the rating and response.
('combo', X, Y) where X and Y are single column indices. This will print all
  responses as a list, with X and Y concatenated with a hyphen.
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
"""
OneArgType = Tuple[Literal['normal', 'rating'], int]
TwoArgType = Tuple[Literal['rating_with_reasoning', 'combo'], int, int]
SectionalType = Tuple[Literal['section'], List[Iterable['Section']]]
NameType = Tuple[Literal['name'], bool]
Section = Union[OneArgType, TwoArgType, SectionalType, NameType]

column_styles: List[Section] = [
    ('normal', 0),
    ('rating', 1),
    ('normal', 2),
    ('normal', 3),
    ('normal', 4),
    ('normal', 5),
    ('rating', 6),
    ('rating_with_reasoning', 7, 8),
    ('rating', 9),
    ('normal', 10),
    ('rating', 11),
    ('normal', 12),
    ('normal', 13),
    ('text', '\n\\pagebreak\n'),
    ('section', [
        ('name', 14, False),
        ('normal', 15),
        ('rating', 16),
    ]),
    ('section', [
        ('name', 17, False),
        ('rating', 20),
        ('normal', 18),
        ('normal', 19),
    ]),
    ('normal', 21),
    ('rating_with_reasoning', 23, 22),
    ('rating_with_reasoning', 25, 24),
    ('normal', 26),
    ('rating', 27),
    ('normal', 28),
    ('normal', 29),
    ('normal', 30)
]


def arg_check() -> None:
    if sys.argv[1] is None:
        print("Usage: %s [data_file.csv]" % sys.argv[0], file=sys.stderr)


def read_csv() -> List[List[str]]:
    with open(sys.argv[1], newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        return_val = []
        for line in reader:
            return_val.append(line)
        return return_val


def parse_normal(eval_data: List[List[str]], index: int) -> str:
    return_val = "\\begin{itemize}\n"
    for i in range(1, len(eval_data)):
        line = eval_data[i][index].strip()
        if len(line) > 0:
            return_val += "\\item %s\n" % line
    return return_val + "\\end{itemize}\n"


def random_name(length: int) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


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
    fig1, ax1 = plt.subplots()
    ax1.pie(rating_data.values(), labels=rating_data.keys(), autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')

    output_file = "./figures/%s.png" % random_name(6)
    open(output_file, "w").close()  # create the file if it doesn't exist
    plt.savefig(output_file)
    plt.close()
    return (("\\begin{figure}[H]\n" +
             "\\centering\n" +
             "\\includegraphics[width=0.8\\textwidth]{%s}\n" +
             "\\centering\n" +
             "\\end{figure}\n") % output_file)


def parse_combined_columns(eval_data: List[List[str]], index_a: int, index_b: int, delimiter: str = '-') -> str:
    return_val = "\\begin{itemize}\n"
    for i in range(1, len(eval_data)):
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
                                should_combine=True) -> str:
    return "%s\n%s" % (
        parse_rating(eval_data, index_rating),
        parse_combined_columns(eval_data, index_rating, index_reasoning) if should_combine else parse_normal(eval_data,
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


def parse_section(eval_data: List[List[str]], sections: List[Section], section_depth: int = 0) -> str:
    return_val = section_header(eval_data[0][sections[0][1]], section_depth)
    section_categories = list(set(eval_data[i][sections[0][1]] for i in range(1, len(eval_data))))
    section_categories.sort()
    for section_category in section_categories:
        section_category_trimmed = section_category.strip()
        if len(section_category_trimmed) > 0:
            section_data = list(filter(lambda row: row[sections[0][1]] == section_category_trimmed, eval_data))
            if len(section_data) > 0:
                section_data.insert(0, eval_data[0])
                if sections[0][2]:
                    return_val += "\\pagebreak\n"
                return_val += section_header(section_category_trimmed, section_depth + 1)
                return_val += parse_evals(section_data, sections[1:], section_depth + 2)
    return return_val


def parse_evals(eval_data: List[List[str]], sections: List[Section], section_depth: int = 0) -> str:
    if section_depth < 0 or section_depth > 2:
        return ""
    return_val = ""
    for section in sections:
        if isinstance(section[1], int):
            return_val += section_header(eval_data[0][section[1]], section_depth)
        if section[0] == 'normal':
            return_val += parse_normal(eval_data, section[1])
        elif section[0] == 'rating':
            return_val += parse_rating(eval_data, section[1])
        elif section[0] == 'rating_with_reasoning':
            return_val += parse_rating_with_reasoning(eval_data, section[1], section[2], True)
        elif section[0] == 'rating_with_response_no_rating':
            return_val += parse_rating_with_reasoning(eval_data, section[1], section[2], False)
        elif section[0] == 'combo':
            return_val += parse_combined_columns(eval_data, section[1], section[2])
        elif section[0] == 'section':
            return_val += parse_section(eval_data, section[1], section_depth)
        elif section[0] == 'text':
            return_val += section[1]
        return_val += "\n"
    return return_val


if __name__ == '__main__':
    import os

    if not os.path.exists('./figures'):
        os.mkdir('./figures')
    arg_check()
    latex = parse_evals(read_csv(), column_styles).replace('#', '\\#').replace('&', '\\&').replace('$', '\\$') \
        .replace('_', '\\_')
    with open('template.tex', 'r') as output:
        open('output.tex', 'w').write(output.read().strip().replace('DATA_LATEX_OUTPUT', latex))
