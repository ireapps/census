#!/usr/bin/python

# Script to convert Table names from SAS files into tsv file

import re

def get_indent_level(s):
	"""Return number of indents based on length of spaces in string"""
	num_spaces = len(s)

	if num_spaces == 1:
		return 0
	elif num_spaces == 7:
		return 1
	elif num_spaces == 9:
		return 2
	elif num_spaces == 11:
		return 3
	elif num_spaces == 13:
		return 4
	elif num_spaces == 15:
		return 5
	elif num_spaces == 17:
		return 6
	else:
		return -1	

def create_column_id(alpha_id,table_id,line_id):
	"""Return column ID in format 'P002003' based on parts of ID:
	Initial alpha identifier 'P',
	Table id '2',
	and line id, '3'"""
	table_id = '{0:0>3}'.format(str(table_id))
	line_id = '{0:0>3}'.format(str(line_id))
	return alpha_id + table_id + line_id
	

source_files = ['./phlabs.sas.txt','./pctlabs.sas.txt']
output_file = open('./table_index.tsv','w')

indent_content = {}		# dictionary used to keep track of current indentation level

output_file.write("2000 ID\tIs count\tTable name\n")	# headers for output table

for f in source_files:
	input_file = open(f,'rb')

	for line in input_file.readlines():
		# Search for Table name
		table_name_search = re.search('Table [A-Z]+\d+\.  ([A-Z0-9 ,]+)\[', line)

		# Search for column ID at beginning of line
		column_id_search = re.search('^([A-Z]+)(\d+)i(\d+)=\'(\s+)(.*?):?\'', line)

		# If line is a table name, set the table name
		if table_name_search:
			table_name = table_name_search.group(1)

			# if table name contains "median" or "average" we can't do crosswalk math
			if table_name.find('MEDIAN') > -1 or table_name.find('AVERAGE') > -1:
				is_count = "False"
			else:
				is_count = "True"

		# if line starts with a column ID
		if column_id_search:
			# Collect the three parts of the column ID
			table_alpha = column_id_search.group(1)
			table_number = column_id_search.group(2)
			line_number = column_id_search.group(3)

			# create column ID from parts 
			column_id = create_column_id(table_alpha,table_number,line_number)

			# Determine indentation level by checking number of spaces
			spaces = column_id_search.group(4)
			indent_level = get_indent_level(spaces)

			# insert column label into indent dictionary using indentation level as key
			column_label = column_id_search.group(5)
			indent_content[indent_level] = column_label
		
			# Set first part of output row
			output_row = "\t".join([column_id,is_count,table_name])
	
			# Add human readable labels at each indentation level relevant for current row 
			for i in range(indent_level):
				output_row += ("\t" + indent_content[i+1])

			output_file.write(output_row + '\n')
	
	input_file.close()