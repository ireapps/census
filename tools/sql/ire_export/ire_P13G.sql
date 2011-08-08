-- P13G. MEDIAN AGE BY SEX (TWO OR MORE RACES)
-- designed to work with the IRE Census bulk data exports
-- see http://census.ire.org/data/bulkdata.html
CREATE TABLE ire_p13g (
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
	p013g001 FLOAT, 
	p013g001_2000 FLOAT, 
	p013g002 FLOAT, 
	p013g002_2000 FLOAT, 
	p013g003 FLOAT, 
	p013g003_2000 FLOAT, 
	PRIMARY KEY (geoid)
);
