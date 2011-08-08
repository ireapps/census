-- PCT20D. GROUP QUARTERS POPULATION BY GROUP QUARTERS TYPE (ASIAN ALONE)
-- designed to work with the IRE Census bulk data exports
-- see http://census.ire.org/data/bulkdata.html
CREATE TABLE ire_pct20d (
	geoid VARCHAR(11) NOT NULL, 
	sumlev VARCHAR(3) NOT NULL, 
	state VARCHAR(2) NOT NULL, 
	county VARCHAR(3), 
	cbsa VARCHAR(5), 
	csa VARCHAR(3), 
	necta VARCHAR(5), 
	cnecta VARCHAR(3), 
	name VARCHAR(90) NOT NULL, 
	pop100 INTEGER NOT NULL, 
	hu100 INTEGER NOT NULL, 
	pop100_2000 INTEGER, 
	hu100_2000 INTEGER, 
	pct020d001 INTEGER, 
	pct020d001_2000 INTEGER, 
	pct020d002 INTEGER, 
	pct020d002_2000 INTEGER, 
	pct020d003 INTEGER, 
	pct020d003_2000 INTEGER, 
	pct020d004 INTEGER, 
	pct020d004_2000 INTEGER, 
	pct020d005 INTEGER, 
	pct020d005_2000 INTEGER, 
	pct020d006 INTEGER, 
	pct020d006_2000 INTEGER, 
	pct020d007 INTEGER, 
	pct020d007_2000 INTEGER, 
	pct020d008 INTEGER, 
	pct020d008_2000 INTEGER, 
	pct020d009 INTEGER, 
	pct020d009_2000 INTEGER, 
	pct020d010 INTEGER, 
	pct020d010_2000 INTEGER, 
	pct020d011 INTEGER, 
	pct020d011_2000 INTEGER, 
	pct020d012 INTEGER, 
	pct020d012_2000 INTEGER, 
	pct020d013 INTEGER, 
	pct020d013_2000 INTEGER, 
	pct020d014 INTEGER, 
	pct020d014_2000 INTEGER, 
	pct020d015 INTEGER, 
	pct020d015_2000 INTEGER, 
	pct020d016 INTEGER, 
	pct020d016_2000 INTEGER, 
	pct020d017 INTEGER, 
	pct020d017_2000 INTEGER, 
	pct020d018 INTEGER, 
	pct020d018_2000 INTEGER, 
	pct020d019 INTEGER, 
	pct020d019_2000 INTEGER, 
	pct020d020 INTEGER, 
	pct020d020_2000 INTEGER, 
	pct020d021 INTEGER, 
	pct020d021_2000 INTEGER, 
	pct020d022 INTEGER, 
	pct020d022_2000 INTEGER, 
	pct020d023 INTEGER, 
	pct020d023_2000 INTEGER, 
	pct020d024 INTEGER, 
	pct020d024_2000 INTEGER, 
	pct020d025 INTEGER, 
	pct020d025_2000 INTEGER, 
	pct020d026 INTEGER, 
	pct020d026_2000 INTEGER, 
	pct020d027 INTEGER, 
	pct020d027_2000 INTEGER, 
	pct020d028 INTEGER, 
	pct020d028_2000 INTEGER, 
	pct020d029 INTEGER, 
	pct020d029_2000 INTEGER, 
	pct020d030 INTEGER, 
	pct020d030_2000 INTEGER, 
	pct020d031 INTEGER, 
	pct020d031_2000 INTEGER, 
	pct020d032 INTEGER, 
	pct020d032_2000 INTEGER, 
	PRIMARY KEY (geoid)
);