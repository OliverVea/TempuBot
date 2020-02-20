import json

from defs import timestamp, dir_path

from threading import Lock

lock = Lock()

class JSONFile(object):
    filename = ''
    encoding = 'utf-16-le'

    def __init__(self, filename, location = dir_path + '/json/', encoding='utf-16-le'):
        self.filename = location + filename
        self.encoding = encoding

    def read(self):
        with lock:
            try:
                with open(self.filename, encoding=self.encoding) as f:
                    content = json.load(f)
                return content
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(timestamp(), 'tried to load file:', self.filename, 'raised error', e)
        self.write({})
        return {}    

    def write(self, content):
        with lock:
            with open(self.filename, 'w', encoding=self.encoding) as f:
                json.dump(content, f, ensure_ascii=False, indent=4)

    def get(self, attribute, on_error):
        file = self.read()
        if attribute in file: return file[attribute]
        self.set(attribute, on_error)
        return on_error

    def set(self, attribute, value):
        file = self.read()
        file[attribute] = value
        self.write(file)
