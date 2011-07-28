-- H4. TENURE
-- designed to work with the IRE Census bulk data exports
-- see http://census.ire.org/data/bulkdata.html
CREATE TABLE ire_h4 (
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
	h004001 INTEGER, 
	h004001_2000 INTEGER, 
	h004002 INTEGER, 
	h004002_2000 INTEGER, 
	h004003 INTEGER, 
	h004003_2000 INTEGER, 
	h004004 INTEGER, 
	h004004_2000 INTEGER, 
	PRIMARY KEY (geoid)
);
