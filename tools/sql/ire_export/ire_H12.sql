-- H12. AVERAGE HOUSEHOLD SIZE OF OCCUPIED HOUSING UNITS BY TENURE
-- designed to work with the IRE Census bulk data exports
-- see http://census.ire.org/data/bulkdata.html
CREATE TABLE ire_h12 (
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
	h012001 FLOAT, 
	h012001_2000 FLOAT, 
	h012002 FLOAT, 
	h012002_2000 FLOAT, 
	h012003 FLOAT, 
	h012003_2000 FLOAT, 
	PRIMARY KEY (geoid)
);
