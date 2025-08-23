cdef class Argument(object):

    cpdef constructor1(self, str argument):
        """
        A constructor of Argument class which takes argument string which is in the form of argumentType$id
        and parses this string into argumentType and id. If the argument string does not contain '$' then the
        constructor return a NONE type argument.

        PARAMETERS
        ----------
        argument : str
            Argument string containing the argumentType and id
        """
        if "$" in argument:
            self.__argument_type = argument[0:argument.index("$")]
            self.__id = argument[argument.index("$") + 1:]
        else:
            self.__argument_type = "NONE"

    cpdef constructor2(self, str argumentType, str _id):
        """
        Another constructor of Argument class which takes argumentType and id as inputs and initializes corresponding
        attributes

        PARAMETERS
        ----------
        argumentType : str
            Type of the argument
        _id : str
            Id of the argument
        """
        self.__argument_type = argumentType
        self.__id = _id

    def __init__(self, argumentOrType: str, _id: str = None):
        if _id is None:
            self.constructor1(argumentOrType)
        else:
            self.constructor2(argumentOrType, _id)

    cpdef str getArgumentType(self):
        """
        Accessor for argumentType.

        RETURNS
        -------
        str
            argumentType.
        """
        return self.__argument_type

    cpdef str getId(self):
        """
        Accessor for id.

        RETURNS
        -------
        str
            id.
        """
        return self.__id

    cpdef setId(self, str _id):
        """
        Setter for id.
        :param _id: New id
        """
        self.__id = _id


    def __str__(self) -> str:
        """
        __str__ converts an Argument to a string. If the argumentType is "NONE" returns only "NONE", otherwise
        it returns argument string which is in the form of argumentType$id

        RETURNS
        -------
        str
            string form of argument
        """
        if self.__argument_type == "NONE":
            return self.__argument_type
        else:
            return self.__argument_type + "$" + self.__id
