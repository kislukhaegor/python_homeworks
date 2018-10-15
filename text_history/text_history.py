from abc import ABCMeta, abstractmethod

class TextHistory:
    def __init__(self):
        self._text = ''
        self._version = 0
        self._actions = []

    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def insert(self, text, pos=None):
        if pos is None:
            pos = len(self.text)

        action = InsertAction(pos, text, self.version, self.version + 1)
        return self.action(action)

    def replace(self, text, pos=None):
        if pos is None:
            pos = len(self.text)

        action = ReplaceAction(pos, text, self.version, self.version + 1)
        return self.action(action)

    def delete(self, pos, length):
        action = DeleteAction(pos, length, self.version, self.version + 1)
        return self.action(action)

    def action(self, action):
        self._text = action.apply(self.text, self.version)
        self._version = action.to_version
        self._actions.append(action)
        return self._version

    def get_actions(self, from_version=0, to_version=None):
        if to_version is None:
            to_version = self.version

        if to_version > self._version:
            raise ValueError()

        if from_version < 0 or from_version > to_version:
            raise ValueError()

        if from_version == to_version == 0:
            return []

        start_pos = self._find_version_index(from_version)
        end_pos = self._find_version_index(to_version)
        return self._optimyze(self._actions[start_pos:end_pos])

    def _find_version_index(self, version):
        for index, action in enumerate(self._actions):
            if action.from_version == version:
                return index
            elif action.to_version == version:
                return index + 1
        raise ValueError()

    @staticmethod
    def _optymize_delete(action_list, action):
        if type(action_list[-1]) != type(action) or type(action) != DeleteAction:
            return None

        if action.pos == action_list[-1].pos:
            new_action = DeleteAction(action.pos,
                                      action.length + action_list[-1].length,
                                      action_list[-1].from_version,
                                      action.to_version)
            del action_list[-1]
            action_list.append(new_action)

    @staticmethod
    def _optimyze_insert(action_list, action):
        if type(action_list[-1]) != type(action) or type(action) != InsertAction:
            return None

        if action.pos == action_list[-1].pos:
            new_action = InsertAction(action.pos,
                                      action.text,
                                      action_list[-1].from_version,
                                      action.to_version)
            del action_list[-1]
            action_list.append(new_action)

        elif action.pos - (action_list[-1].pos + len(action_list[-1].text)) == 0:
            new_action = InsertAction(action_list[-1].pos,
                                      action_list[-1].text + action.text,
                                      action_list[-1].from_version,
                                      action.to_version)
            del action_list[-1]
            action_list.append(new_action)

    @staticmethod
    def _optimyze(actions):
        new_list = []
        for action in actions:
            if not new_list:
                new_list.append(action)
            elif type(action) == type(new_list[-1]):
                if type(action) == DeleteAction:
                    TextHistory._optymize_delete(new_list, action)
                elif type(action) == InsertAction:
                    TextHistory._optimyze_insert(new_list, action)
                else:
                    new_list.append(action)
            else:
                new_list.append(action)
        return new_list



class Action(metaclass=ABCMeta):
    def __init__(self, from_version, to_version):
        self._from_version = from_version
        self._to_version = to_version

    @property
    def from_version(self):
        return self._from_version
    @property
    def to_version(self):
        return self._to_version

    @abstractmethod
    def apply(self, text, version):
        pass

    def _check_version(self, version):
        if version != self.from_version:
            return False

        if self.to_version - self.from_version < 1:
            return False

        return True


class InsertAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        super().__init__(from_version, to_version)
        self._text = text
        self._pos = pos

    @property
    def text(self):
        return self._text

    @property
    def pos(self):
        return self._pos

    def apply(self, text, version):
        if not self._check_version(version):
            raise ValueError()

        return self._insert(text, self._pos, self._text)

    @staticmethod
    def _insert(old_str, pos, ins_str):
        if pos > len(old_str) or pos < 0:
            raise ValueError()

        return ins_str.join([old_str[:pos], old_str[pos:]])


class ReplaceAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        super().__init__(from_version, to_version)
        self._pos = pos
        self._text = text

    @property
    def text(self):
        return self._text

    @property
    def pos(self):
        return self._pos

    def apply(self, text, version):
        if not self._check_version(version):
            raise ValueError()

        return self._replace(text, self._pos, self._text)

    @staticmethod
    def _replace(old_str, pos, ins_str):
        if pos > len(old_str) or pos < 0:
            raise ValueError()

        if pos + len(ins_str) >= len(old_str):
            return old_str[:pos] + ins_str
        else:
            return old_str[:pos] + ins_str + old_str[pos + len(ins_str):]

class DeleteAction(Action):
    def __init__(self, pos, length, from_version, to_version):
        super().__init__(from_version, to_version)
        self._pos = pos
        self._length = length

    @property
    def pos(self):
        return self._pos

    @property
    def length(self):
        return self._length

    def apply(self, text, version):
        if not self._check_version(version):
            raise ValueError()

        return self._delete(text, self._pos, self._length)

    @staticmethod
    def _delete(text, pos, length):
        if pos > len(text) or pos < 0:
            raise ValueError()

        if pos + length > len(text):
            raise ValueError()

        return text[:pos] + text[pos + length:]
