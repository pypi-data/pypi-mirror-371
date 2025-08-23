cdef class Argument(object):

    cdef str __argument_type
    cdef str __id

    cpdef constructor1(self, str argument)
    cpdef constructor2(self, str argumentType, str _id)
    cpdef str getArgumentType(self)
    cpdef str getId(self)
    cpdef setId(self, str _id)
