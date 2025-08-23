cdef class ArgumentList(object):

    cdef list __arguments

    cpdef updateConnectedId(self, str previousId, str currentId)
    cpdef addPredicate(self, str predicateId)
    cpdef removePredicate(self)
    cpdef bint containsPredicate(self)
    cpdef bint containsPredicateWithId(self, str predicateId)
    cpdef list getArguments(self)
    cpdef bint containsArgument(self, str argumentType: str, str _id)
