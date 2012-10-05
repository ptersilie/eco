class StateSet(object):

    def __init__(self, elements=None):
        if elements:
            self.elements = elements
        else:
            self.elements = []

    def __getitem__(self, i):
        return self.elements[i]

    def add(self, element):
        if False:#isinstance(element, LR1Element):
            # merge LR1 elements if they differ only in their lookahead
            merged = False
            for e in self.elements:
                if e.d == element.d and e.p == element.p:
                    e.lookahead |= element.lookahead
                    merged = True
            if not merged:
                self.elements.append(element)
            return

        if element not in self.elements:
            self.elements.append(element)

    def merge(self):
        # merge states that only differ in their lookahead
        # XXX this is slow
        for a in self.elements:
            for b in self.elements:
                if a is not b and a.d == b.d and a.p == b.p:
                    a.lookahead |= b.lookahead
                    self.elements.remove(b)

    def __contains__(self, element):
        return element in self.elements

    def is_empty(self):
        return self.elements == []

    def get_next_symbols(self):
        symbols = set()
        for state in self.elements:
            symbol = state.next_symbol()
            if symbol:
                symbols.add(symbol)
        return symbols


    def __eq__(self, other):
        if not isinstance(other, StateSet):
            return False
        for e in self.elements:
            if e not in other:
                return False
        return True

    def __str__(self):
        return str(self.elements)

class State(object):

    # backpointer only necessary for earley parser
    # lookahead only necessary for normal earley parser
    def __init__(self, production, pos, backpointer=None, lookaheadsymbol=None):
        self.p = production
        self.d = pos
        self.b = backpointer
        self.k = lookaheadsymbol

    def next_symbol(self):
        try:
            return self.p.right[self.d]
        except IndexError:
            return None

    def remaining_symbols(self):
        return self.p.right[self.d+1:]

    def isfinal(self):
        return len(self.p.right) == self.d

    def get_left(self):
        return self.p.left

    def get_lookahead(self):
        if self.d+1 >= len(self.p.right):
            return self.k
        return self.p.right[self.d+1].name

    def get_backpointer(self):
        return self.b

    def get_lookahead_raw(self):
        return self.get_lookahead().strip("\"")

    def clone(self):
        return State(self.p, self.d, self.b, self.k)

    def __repr__(self):
        return "State(%s, %s, %s, %s)" % (self.p, self.d, self.b, self.k)

    def __str__(self):
        """Displays the state in readable form as used in the Earley paper"""
        if not self.p.left:
            left = "None"
        else:
            left = self.p.left.name
        right = [x.name for x in self.p.right]
        right.insert(self.d, ".")
        right = "".join(right)
        #s = "%s ::= %s %s %s" % (left, right, self.k, self.b)
        s = "%s ::= %s" % (left, right)
        return s

    def equals_str(self, s):
        return self.__str__() == s

    def __eq__(self, other):
        return self.p == other.p and self.d == other.d and self.b == other.b and self.k == other.k

class LR0Element(State):

    def __init__(self, production, pos):
        State.__init__(self, production, pos, None, None)

class LR1Element(State):

    def __init__(self, production, pos, lookahead):
        State.__init__(self, production, pos, None, None)
        self.lookahead = lookahead

    def clone(self):
        return LR1Element(self.p, self.d, self.lookahead)

    def __eq__(self, other):
        return State.__eq__(self, other) and self.lookahead == other.lookahead

    def __str__(self):
        s = State.__str__(self)
        s += " " + str(self.lookahead)
        return s

    def __repr__(self):
        return "LR1Element(%s, %s, %s)" % (self.p, self.d, self.lookahead)
