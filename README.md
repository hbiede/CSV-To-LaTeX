# CSV to LaTeX
Takes a CSV file and converts the data in its columns into a LaTeX file based on a section
definition at the top of `csv-latex.py`. `compile.sh` has also been provided to easily
compile all LaTeX files in the PWD (except `template.tex`).

## Setup
### Initial Setup
To setup the environment to run this script, first you must run
`pip install -r requirements.txt` to install the Python packages necessary for the script.

### LaTeX setup
You will need a manner to compile LaTeX scripts. 

#### Mac Setup
Run the following to install LaTeX:
`brew install basictex`

This should make the `lualatex` and `latexmk` commands available to you.
You can then pass a LaTeX file to either to compile it into a PDF.

#### Windows Setup
* Option 1: Figure out how to compile LaTeX on Windows, I've never done it before.
* Option 2: Upload them all to Overleaf and compile there
* Option 3: Buy a Mac and see above

### Document Setup
#### Python Side
##### Sections
You will need to create a list of section definitions for your document in the Python
file. The outputted LaTeX file will follow the order and formatting assigned in these
sections.

The format of these sections is an array of tuples, each defining a section.
The tuples must follow the following formats:

`('normal', X)` where X is a single column index. This will print all responses
  as a list
`('rating', X)` where X is a single column index. This will print all responses
  as a pie chart. This column will also split on columns to count multiple
  values
`('rating_with_reasoning', X, Y, C)` where X and Y are single column indices.
  This will create a pie chart of the values in X, and a list of responses
  in Y, where each response is prepended with its associated rating. The section
  header will be the column header of column X. C will be the character used to
  separate the rating from the response. A hyphen will be used if no C is
  provided.
`('rating_with_response_no_rating', X, Y)` - Same as `rating_with_reasoning`, but
  without concatenation of the rating and response.
`('combo', X, Y, C)` where X and Y are single column indices. This will print all
  responses as a list, with X and Y concatenated with character C (if no
  character is provided, a hyphen will be used as default).
`('section', A)` where A is an array. This array should contain more nested
  arrays describing how the associated columns should be printed (think another
  document inside this one). Data in a section will be split by the values in
  'name'. Thus, the first array in a 'section' format array must always be a 
  'name' format to permit splitting. Nesting 'section's is limited to 4 in
  depth.
`('name', X, B)` where X is a single column index. This will create a (sub)section
  header and B is a boolean (True or False) denoting if the section should
  appear on a new page.
`('text', X)` where X is a string to be printed, as-is.
`('title', X)` where X is the column from which the first value should be printed
  as a (sub)section header

**Note: Column indices are 0 indexed!**

##### Split Data by Columns
You can also use the `multiple_files_column` to split the data based on the contents of a
given column. If the value of this variable is less than 0, all data will be output to a
single `output.tex` file, but if this variable is 0 or greater, multiple files will be
created. The resulting files will be created as if the data was grouped by the contents of
the given column, compiled, and stored to `[X].tex`, where `[X]` is the contents of the
given column. This is useful if you form is asking for evaluations of individuals. In this
case, you could set `multiple_files_column` to the column with the name of the individual
being evaluated. If you had evaluations for three people named Derek, Jessica, and Alex,
you would get back three files named `Derek.tex`, `Jessica.tex`, and `Alex.tex`.

This contents of the column `multiple_files_column` will also be used to replace all
occurrences of `NAMEPLACEHOLDER` in the template file.

**Note: This column index is 0 indexed!**

##### Date Replacement

The following terms will be replaced with the date of LaTeX generation according to the
following table:
| Replacement Phrase | Example Output |
| ------------------ | -------------- |
| REPLACEMENTDATE | August 2021 |
| REPLACEMENTFULLDATE | August 29, 2021 |
| REPLACEMENTISODATE | 2021-08-29 |
| REPLACEMENTMONTH | August |
| REPLACEMENTYEAR | 2021 |

#### LaTeX Side
The LaTeX can be formatted however you wish. The important notes are as follows:
* Any occurrences of the phrase `DATA_LATEX_OUTPUT` will be replaced with the output
  of your sections
* Any occurrences of the phrase `NAMEPLACEHOLDER` will be replaced with the contents of
  the column marked as the `multiple_files_column`.
