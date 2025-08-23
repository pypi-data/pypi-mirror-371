cdef class FramesetArgument(object):

    cdef str __argument_type,__definition, __function, __grammatical_case

    cpdef str getArgumentType(self)
    cpdef str getDefinition(self)
    cpdef str getFunction(self)
    cpdef str getGrammaticalCase(self)
    cpdef setDefinition(self, str definition)
    cpdef setFunction(self, str function)
    cpdef setGrammaticalCase(self, str grammaticalCase)