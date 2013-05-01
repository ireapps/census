#!/usr/bin/env ruby

TESTS = [
  [ 'P3',     1,  'P0030001' ],
  [ 'P1',     1,  'P001001', true], # original algorithm test
  [ 'P7',     1,  'P0070001' ],
  [ 'P38G',   19, 'P038G019' ],
  [ 'PCT20A', 4,  'PCT020A004' ],
  [ 'PCO1',   33, 'PCO0010033' ]
]

def data_dictionary_reference_name(table, cell_number, original_algorithm = false)
  first_int = table.index(/\d/)
  prefix, rest = table[0..first_int-1], table[first_int..-1]

  suffix = rest.to_i.to_s.rjust(3, '0')

  unless original_algorithm
    # Append a '0' unless the last char was a letter (in which case, append it back)
    if rest[-1] =~ /\d/
      suffix += '0'
    else
      suffix += rest[-1]
    end
  end

  sprintf("%s%s%03i", prefix, suffix, cell_number).upcase
end

# run the tests
TESTS.each do |table, i, result, original_algorithm|
  real_result = data_dictionary_reference_name(table, i, original_algorithm || false)
  raise "failed on #{table} + #{i} = #{result} (got #{real_result})" unless result == real_result
end

# Group the lines by segment (aka file)
segments = {}
for line in File.readlines("ak2010.sf1.prd.packinglist.txt")
  if /^(.+)\|(\d+):(\d+)\|$/.match(line)
    table, segment, number_of_cells = $1, $2, $3
    segment = segment.to_s.rjust(2, '0')
    segments[segment] ||= []
    segments[segment] << [table, number_of_cells]
  end
end

creates = File.open('all_sf1_files.sql', 'w')
rename = File.open('rename_columns.sql', 'w')

# For each segment (aka file) produce a CREATE TABLE statement
segments.keys.sort.each do |segment|
  creates.write """CREATE TABLE sf1_#{segment} (
\tFILEID VARCHAR(6) NOT NULL,
\tSTUSAB VARCHAR(2) NOT NULL,
\tCHARITER VARCHAR(3) NOT NULL,
\tCIFSN VARCHAR(3) NOT NULL,
\tLOGRECNO VARCHAR(7) NOT NULL PRIMARY KEY,\n"""

  columns = []
  segments[segment].each do |table, number_of_cells|
    number_of_cells.to_i.times do |i|
      proper_name = data_dictionary_reference_name(table, i + 1)
      original_name = data_dictionary_reference_name(table, i + 1, true)

      columns << "\t#{proper_name} INTEGER NOT NULL"
      rename.write "ALTER TABLE sf1_#{segment} RENAME COLUMN #{original_name} TO #{proper_name};\n"
    end
  end
  creates.write columns.join(",\n") + "\n"
  creates.write ");\n\n"
end

creates.close
rename.close
