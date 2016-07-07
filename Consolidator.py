import csv
import pprint
import operator
import re


contribFilePath = 'contribs_bottom_99.csv'
crosswalkFilePath = 'zip_to_zcta.csv'
demoFilePath = 'selected_demos_percwhite.csv'


def strip_alpha(input):
    nums_only = re.compile(r'[A-Z]+[5].')
    return nums_only.sub('', input)

# Read Contributor Information into Array

contribFile = open(contribFilePath, 'rU')
contribFile_r = csv.reader(contribFile)

contribs = []  # contributors array

for row in contribFile_r:
        contribs.append(row)


# Read crosswalk file into dictionary
crosswalkFile = open(crosswalkFilePath, 'rU')
crosswalkFile_r = csv.reader(crosswalkFile)

crosswalk = {}  # Crosswalk dictionary
st_and_name = {}  # State and name dictionary

for row in crosswalkFile_r:
        crosswalk[row[0]] = row[4]
        st_and_name[row[0]] = [row[1], row[2]]

# Convert USPS Zip codes into ZCTA codes

for i in contribs:
    if crosswalk.has_key(i[0]):
        i[0] = crosswalk[i[0]]
    else:
        i[0] = 'drop'

# Sort by zip code, convert $ amounts to numbers

contribs = sorted(contribs, key=operator.itemgetter(0))
for i in contribs:
    for j in xrange(1, len(i)):
        i[j] = float(i[j])


# Consolidate matches

for i in xrange(0, len(contribs) - 1):
    if contribs[i][0] == contribs[i+1][0] and contribs[i][0] != 'drop':
            for j in xrange(1, len(contribs[i])):
                contribs[i+1][j] = contribs[i+1][j] + contribs[i][j]
            contribs[i][0] = 'drop'

# Drop non-convertible zip codes and matches then sort by zip code, convert $ amounts to numbers

contribs = [item for item in contribs if item[0] != 'drop']
# Convert contribs to dictionary for faster search
contribs_dict = {}

for i in xrange(0, len(contribs)):
    key = contribs[i][0]
    contribs[i].pop(0)
    contribs_dict[key] = contribs[i]

# Load in Demographics Data, stripping non decimal characters from zipcode and converting pop info to numbers

demoFile = open(demoFilePath, 'rU')
demoFile_r = csv.reader(demoFile)

next(demoFile_r, None)

demos = []  # Demographics Array

for row in demoFile_r:
    row[0] = strip_alpha(row[0])
    for i in xrange(1, len(row)):
        row[i] = float(row[i])
    demos.append(row)

# Add Contribs into demographics data

for i in demos:
    if contribs_dict.has_key(i[0]):
        i.extend(contribs_dict[i[0]])
        i.extend(st_and_name[i[0]])
    else:
        i.extend([0, 0, 0, 0])
        i.extend(st_and_name[i[0]])

pprint.pprint(demos)
# Write combined data to outfile

outFile = open('output_demos.csv', 'wb')
writer = csv.writer(outFile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
writer.writerow(['ZCTA', 'Total', 'White', 'Black', 'AmInd or Alaskan Native',
                 'Asian', 'PacIslander or HI Native', 'Other Race', 'Mixed', 'Hispanic',
                 'Total Contribs', 'Number Contribs', 'To Dems', 'To Repubs', 'Pct To Dems', 'Pct to Repubs',
                 'Per Capita', 'Name', 'State'])
for row in demos:
    writer.writerow(row)

# Close Files

outFile.close()
contribFile.close()
crosswalkFile.close()
demoFile.close()