import json

class JSONFile():
    def __init__(self, filename, location, on_error = {}, encoding='utf-16-le'):
        self.filename = location + filename
        self.on_error = on_error
        self.encoding = encoding
        pass

    def read(self):
        try:
            with open(self.filename, encoding=self.encoding) as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.write(self.on_error)
            return self.on_error

    def write(self, object):
        with open(self.filename, 'w', encoding=self.encoding) as f:
            return json.dump(object, f, ensure_ascii=False, indent=4)

    def get(self, attribute, on_error = []):
        file = self.read()
        if attribute in file: return file[attribute]
        self.set(attribute, on_error)
        return on_error

    def set(self, attribute, value):
        file = self.read()
        file[attribute] = value
        self.write(file)
