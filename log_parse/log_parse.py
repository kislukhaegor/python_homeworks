# -*- encoding: utf-8 -*-
from urllib.parse import urlparse, urlunparse, ParseResult
from datetime import datetime
import re

class LogLineParseException(ValueError):
    def __init__(self, line):
        self.line = line
        self.message = 'Cant parse line: {0}'.format(self.line)
        ValueError.__init__(self, self.message)


class LogLine:
    """
        This class store parsed line
    """

    compile_parser = re.compile(r'\[(.+)\] \"(.+) (.+) (.+)\" (\d+) (\d+)')

    def __init__(self, line, ignore_www=False):
        self._line = line.strip()
        match_obj = LogLine.compile_parser.match(self._line)
        if not match_obj:
            raise LogLineParseException(self._line)

        self._line_components = {
            'request_date': datetime.strptime(match_obj.group(1), '%d/%b/%Y %X'),
            'request_type': match_obj.group(2),
            'protocol': match_obj.group(4),
            'response_code' : int(match_obj.group(5)),
            'response_time' : int(match_obj.group(6))
        }
        if ignore_www:
            self._line_components['request'] = LogLine._cut_www(match_obj.group(3))
        else:
            self._line_components['request'] = match_obj.group(3)

    def __getitem__(self, key):
        return self._line_components[key]

    @classmethod
    def _cut_www(cls, line):
        url = urlparse(line)
        netloc = url.netloc
        if 'www' in netloc:
            netloc = netloc[4:]
        new_url = ParseResult(url.scheme, netloc, url.path, url.params, url.query, url.fragment)
        return urlunparse(new_url)

    def get_url(self):
        url = urlparse(self['request'])
        return url.netloc + url.path

    def get_path(self):
        return urlparse(self['request']).path

    def __str__(self):
        return self.get_url()

    def __repr__(self):
        return self.get_url()

    def __hash__(self):
        return hash(self.get_url())

    def __eq__(self, other):
        return hash(self) == hash(other)


class LogLineHandler:
    """
        This class handle lines and store them
    """

    def __init__(self, **params):
        self.params = params
        if self.params['start_at']:
            self.params['start_at'] = datetime.strptime(self.params['start_at'], '%d/%b/%Y %X')

        if self.params['stop_at']:
            self.params['stop_at'] = datetime.strptime(self.params['stop_at'], '%d/%b/%Y %X')

        self.logs = dict()

    def add_log(self, line):
        if self.check_line(line):
            if line in self.logs:
                self.logs[line][0] += 1
                self.logs[line][1] += line['response_time']
            else:
                self.logs[line] = [1, line['response_time']]

    def check_line(self, line):
        if self.params['ignore_files']:
            # try to find extension in path
            if re.search(r'.+\.\w+', line.get_path()):
                return False

        if self.params['ignore_urls']:
            for ignore_url in self.params['ignore_urls']:
                if ignore_url in line:
                    return False

        if self.params['start_at']:
            if line['request_date'] < self.params['start_at']:
                return False

        if self.params['stop_at']:
            if line['request_date'] > self.params['stop_at']:
                return False

        if self.params['request_type']:
            if line['request_type'] != self.params['request_type']:
                return False

        return True

    def get_top(self, count=5, slow_queries=False):
        if slow_queries:
            key = lambda x: x[1][1]
        else:
            key = lambda x: x[1][0]

        sorted_logs = sorted(self.logs.items(), key=key, reverse=True)
        count = min(len(sorted_logs), count)
        if slow_queries:
            return sorted([sorted_logs[i][1][1] // sorted_logs[i][1][0] \
                           for i in range(count)], reverse=True)
        return [sorted_logs[i][1][0] for i in range(count)]


def parse(
        ignore_files=False,
        ignore_urls=[],
        start_at=None,
        stop_at=None,
        request_type=None,
        ignore_www=False,
        slow_queries=False
):
    line_handler = LogLineHandler(
        ignore_files=ignore_files,
        ignore_urls=ignore_urls,
        start_at=start_at,
        stop_at=stop_at,
        request_type=request_type,
    )
    with open('log.log', 'r') as log_file:
        for line in log_file:
            try:
                log_line = LogLine(line, ignore_www)
                line_handler.add_log(log_line)
            except LogLineParseException:
                pass

    return line_handler.get_top(slow_queries=slow_queries)
