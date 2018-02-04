def name(_xpath):  # 1
    return "name(%s)" % (_xpath)
#-------------------------------------------------------------------------


def nodes(_xpath):  # 2
    return "%s/*" % (_xpath)
#-------------------------------------------------------------------------


def node(_xpath, _i):  # 3
    return "%s/*[%i]" % (_xpath, _i)
#-------------------------------------------------------------------------


def text(_xpath):  # 4
    return "%s/text()" % (_xpath)
#-------------------------------------------------------------------------


def arguments(_xpath):  # 5
    return "%s/@*" % (_xpath)
#-------------------------------------------------------------------------


def argument(_xpath, _i):  # 6
    return "%s/@*[%i]" % (_xpath, _i)
#-------------------------------------------------------------------------


def comments(_xpath):  # 7
    return "%s/comment()" % (_xpath)
#-------------------------------------------------------------------------


def comment(_xpath, _i):  # 8
    return "%s/comment()[%i]" % (_xpath, _i)
#-------------------------------------------------------------------------


def namespace_uri(_xpath):  # 9
    return "%s/namespase-uri()" % (_xpath)
#-------------------------------------------------------------------------


def processing_instructions(_xpath):  # 10
    return "%s/processing-instruction()" % (_xpath)
#-------------------------------------------------------------------------


def processing_instruction(_xpath, _i):  # 11
    return "%s/processing-instruction()[%i]" % (_xpath, _i)
#-------------------------------------------------------------------------


class NODE:  # 12

    def S(self, _xpath):
        return nodes(_xpath)

    def E(self, _xpath, _i):
        return node(_xpath, _i)
#-------------------------------------------------------------------------


class ARG:  # 13

    def S(self, _xpath):
        return arguments(_xpath)

    def E(self, _xpath, _i):
        return argument(_xpath, _i)
#-------------------------------------------------------------------------


class COMM:  # 14

    def S(self, _xpath):
        return comments(_xpath)

    def E(self, _xpath, _i):
        return comment(_xpath, _i)
#-------------------------------------------------------------------------


class PRIN:  # 15

    def S(self, _xpath):
        return processing_instructions(_xpath)

    def E(self, _xpath, _i):
        return processing_instruction(_xpath, _i)
#-------------------------------------------------------------------------
