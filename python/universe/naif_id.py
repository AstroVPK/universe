from pathlib import Path
import re
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
            num, expr = self._extract_number_and_text(line)
            if num:
                naif_id[expr] = int(num)
        self._naif_id = naif_id

    def __getitem__(self, a):
        id = self._naif_id[a.upper()]
        return id

    def _extract_number_and_text(self, expression):
        """
        Extracts the number and the text within single quotes from a string.

        Args:
            expression (str): The input string (e.g., "     0            'SOLAR_SYSTEM BARYCENTER'")

        Returns:
            tuple or None: A tuple (number_string, quoted_text) if a match is found, 
                        otherwise None. The number is returned as a string.
        """
        # Regex explanation:
        # r"" - Raw string for regex
        # \s* - Matches zero or more whitespace characters (for leading spaces)
        # (\d+) - Group 1: Matches one or more digits (the number).
        # \s* - Matches zero or more whitespace characters (between number and quote)
        # ' - Matches the opening single quote
        # ([^']+?) - Group 2: Matches one or more characters that are NOT a single quote (the text).
        #             The '?' makes it non-greedy, stopping at the first closing quote.
        # ' - Matches the closing single quote
        pattern = r"\s*(\d+)\s*'([^']+?)'"
        
        match = re.search(pattern, expression)
        
        if match:
            # match.group(1) is the number (Group 1)
            # match.group(2) is the text inside single quotes (Group 2)
            return (match.group(1), match.group(2))
        else:
            return None


if __name__ == '__main__':
    id = naif_id()
    print('The NAIF ID of the Earth is %d'%(id['earth']))
    print('The NAIF ID of Mars is %d'%(id['Mars']))