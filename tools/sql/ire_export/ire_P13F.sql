-- P13F. MEDIAN AGE BY SEX (SOME OTHER RACE ALONE)
-- designed to work with the IRE Census bulk data exports
-- see http://census.ire.org/data/bulkdata.html
CREATE TABLE ire_p13f (
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
	p013f001 FLOAT, 
	p013f001_2000 FLOAT, 
	p013f002 FLOAT, 
	p013f002_2000 FLOAT, 
	p013f003 FLOAT, 
	p013f003_2000 FLOAT, 
	PRIMARY KEY (geoid)
);
