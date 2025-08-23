cdef class Frame:

    def __init__(self, name: str):
        """
        Constructor of Frame class which takes inputStream as input and reads the frame
        :param name: Name of the frame
        """
        self.__lexical_units = []
        self.__frame_elements = []
        self.__name = name

    cpdef addLexicalUnit(self, str lexicalUnit):
        """
        Adds a new lexical unit to the current frame
        :param lexicalUnit: lexicalUnit Lexical unit to be added
        """
        self.__lexical_units.append(lexicalUnit)

    cpdef addFrameElement(self, str frameElement):
        """
        Adds a new frame element to the current frame
        :param frameElement: Frame element to be added
        """
        self.__frame_elements.append(frameElement)

    cpdef bint lexicalUnitExists(self, str synSetId):
        """
        Checks if the given lexical unit exists in the current frame
        :param synSetId: Lexical unit to be searched.
        :return: True if the lexical unit exists, false otherwise.
        """
        return synSetId in self.__lexical_units

    cpdef str getLexicalUnit(self, int index):
        """
        Accessor for a given index in the lexicalUnit array.
        :param index: Index of the lexical unit
        :return: The lexical unit at position index in the lexicalUnit array
        """
        return self.__lexical_units[index]

    cpdef str getFrameElement(self, int index):
        """
        Accessor for a given index in the frameElements array.
        :param index: Index of the frame element
        :return: The frame element at position index in the frameElements array
        """
        return self.__frame_elements[index]

    cpdef int lexicalUnitSize(self):
        """
        Returns number of lexical units in the current frame
        :return: Number of lexical units in the current frame
        """
        return len(self.__lexical_units)

    cpdef int frameElementSize(self):
        """
        Returns number of frame elements in the current frame
        :return: Number of frame elements in the current frame
        """
        return len(self.__frame_elements)

    cpdef str getName(self):
        """
        Accessor for the name of the frame
        :return: Name of the frame
        """
        return self.__name

    def __repr__(self):
        return f"{self.__name} {self.__lexical_units} {self.__frame_elements}"
