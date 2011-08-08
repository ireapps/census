-- P17F. AVERAGE HOUSEHOLD SIZE BY AGE (SOME OTHER RACE ALONE HOUSEHOLDER)
-- designed to work with the IRE Census bulk data exports
-- see http://census.ire.org/data/bulkdata.html
CREATE TABLE ire_p17f (
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
	p017f001 FLOAT, 
	p017f001_2000 FLOAT, 
	p017f002 FLOAT, 
	p017f002_2000 FLOAT, 
	p017f003 FLOAT, 
	p017f003_2000 FLOAT, 
	PRIMARY KEY (geoid)
);
