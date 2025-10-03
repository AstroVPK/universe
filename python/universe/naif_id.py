from pathlib import Path
import pdb

class naif_id(object):
    def __init__(self):
        self.parse_naif_ids()

    def parse_naif_ids(self):
        naif_id = dict()
        cwd = Path.cwd()
        data_path = cwd.parent.parent / 'data'
        naif_codes_file = data_path / 'naif_ids.txt'
        naif_codes_lines = naif_codes_file.read_text().split('\n')
        for line_num, line in enumerate(naif_codes_lines[2:]):
            words = line.split()
            if words:
                naif_id[words[1].rstrip("'").lstrip("'")] = int(words[0])
        self._naif_id = naif_id

    def __getitem__(self, a):
        return self._naif_id[a.upper()]

if __name__ == '__main__':
    id = naif_id()
    print('The NAIF ID of the Earth is %d'%(id['earth']))