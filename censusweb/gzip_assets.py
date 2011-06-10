#!/usr/bin/env python

import os
import gzip
import shutil

class FakeTime:
    def time(self):
        return 1261130520.0

# Hack to override gzip's time implementation
# See: http://stackoverflow.com/questions/264224/setting-the-gzip-timestamp-from-python
gzip.time = FakeTime()

shutil.rmtree('gzip_media', ignore_errors=True)
shutil.copytree('media', 'gzip_media')

for path, dirs, files in os.walk('gzip_media'):
    for filename in files:
        if filename[-3:] not in ['js', 'css', 'txt', 'html']:
            continue
    
        file_path = os.path.join(path, filename)

        f_in = open(file_path, 'rb')
        contents = f_in.read()
        f_in.close()
        f_out = gzip.open(file_path, 'wb')
        f_out.write(contents)
        f_out.close();

