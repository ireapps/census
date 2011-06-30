function table_comparator (table) {
    parts = table.match(/([A-Z]+)(\d+)([A-Z]+)?/);

    key = parts[1];
    num = parts[2];

    if (key[0] == 'P') {
        key = "A" + key; // sort P tables first as Census does
    }   
    while (num.length < 3) {
        num = '0' + num;
    }

    key += num;

    if (!_.isUndefined(parts[3])) {
        key += parts[3];
    }

    return key; 
}
    