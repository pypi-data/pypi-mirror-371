from PropBank.Argument cimport Argument


cdef class ArgumentList:

    def __init__(self, argumentList: str):
        """
        Constructor of argument list from a string. The arguments for a word is a concatenated list of arguments
        separated via '#' character.
        :param argumentList: String consisting of arguments separated with '#' character.
        """
        self.__arguments = []
        items = argumentList.split('#')
        for item in items:
            self.__arguments.append(Argument(item))

    def __str__(self) -> str:
        """
        Overloaded toString method to convert an argument list to a string. Concatenates the string forms of all
        arguments with '#' character.
        :return: String form of the argument list.
        """
        if len(self.__arguments) == 0:
            return "NONE"
        else:
            result = self.__arguments[0].__str__()
            for i in range(1, len(self.__arguments)):
                result += "#" + self.__arguments[i].__str__()
            return result

    cpdef updateConnectedId(self, str previousId, str currentId):
        """
        Replaces id's of predicates, which have previousId as synset id, with currentId.
        :param previousId: Previous id of the synset.
        :param currentId: Replacement id.
        """
        cdef Argument argument
        for argument in self.__arguments:
            if argument.getId() == previousId:
                argument.setId(currentId)

    cpdef addPredicate(self, str predicateId):
        """
        Adds a predicate argument to the argument list of this word.
        :param predicateId: Synset id of this predicate.
        """
        if len(self.__arguments) != 0 and self.__arguments[0].getArgumentType() == "NONE":
            self.__arguments.pop(0)
        self.__arguments.append(Argument("PREDICATE", predicateId))

    cpdef removePredicate(self):
        """
        Removes the predicate with the given predicate id.
        """
        cdef Argument argument
        for argument in self.__arguments:
            if argument.getArgumentType() == "PREDICATE":
                self.__arguments.remove(argument)
                break

    cpdef bint containsPredicate(self):
        """
        Checks if one of the arguments is a predicate.
        :return: True, if one of the arguments is predicate; false otherwise.
        """
        cdef Argument argument
        for argument in self.__arguments:
            if argument.getArgumentType() == "PREDICATE":
                return True
        return False

    cpdef bint containsPredicateWithId(self, str predicateId):
        """
        Checks if one of the arguments is a predicate with the given id.
        :param predicateId: Synset id to check.
        :return: True, if one of the arguments is predicate; false otherwise.
        """
        cdef Argument argument
        for argument in self.__arguments:
            if argument.getArgumentType() == "PREDICATE" and argument.getId() == predicateId:
                return True
        return False

    cpdef list getArguments(self):
        """
        Returns the arguments as an array list of strings.
        :return: Arguments as an array list of strings.
        """
        cdef Argument argument
        cdef list result = []
        for argument in self.__arguments:
            result.append(argument.__str__())
        return result

    cpdef bint containsArgument(self, str argumentType, str _id):
        """
        Checks if the given argument with the given type and id exists or not.
        :param argumentType: Type of the argument to search for.
        :param _id: Id of the argument to search for.
        :return: True if the argument exists, false otherwise.
        """
        cdef Argument argument
        for argument in self.__arguments:
            if argument.getArgumentType() == argumentType and argument.getId() == _id:
                return True
        return False
