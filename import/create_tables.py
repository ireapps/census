import csv

file = csv.reader(open('data/Mississippi.tsv'), delimiter='\t')

first_line = file.next()

def tablize(q):
    return q.replace(" ", "_") + ' VARCHAR(255)'

fields = map(tablize, first_line)

line = "create table tract_data (" + ", ".join(fields) + ")"

print line
