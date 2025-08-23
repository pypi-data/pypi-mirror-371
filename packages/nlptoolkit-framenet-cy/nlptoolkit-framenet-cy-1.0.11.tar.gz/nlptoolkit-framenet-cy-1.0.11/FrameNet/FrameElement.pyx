cdef class FrameElement(object):

    cpdef constructor1(self, str frameElement):
        """
        A constructor of FrameElement class which takes frameElement string which is in the form of frameElementType$id
        and parses this string into frameElementType and id. If the frameElement string does not contain '$' then the
        constructor return a NONE type frameElement.

        PARAMETERS
        ----------
        frameElement : str
            Argument string containing the argumentType and id
        """
        if "$" in frameElement:
            self.__frame_element_type = frameElement[0:frameElement.index("$")]
            self.__frame = frameElement[frameElement.index("$") + 1:frameElement.rindex("$")]
            self.__id = frameElement[frameElement.rindex("$") + 1:]
        else:
            self.__frame_element_type = "NONE"

    cpdef constructor2(self,
                   str frameElementType,
                   str frame,
                   str _id):
        """
        Another constructor of FrameElement class which takes frameElementType and id as inputs and initializes corresponding
        attributes

        PARAMETERS
        ----------
        frameElementType : str
            Type of the argument
        frame : str
            Frame of the argument
        _id : str
            Id of the argument
        """
        self.__frame_element_type = frameElementType
        self.__frame = frame
        self.__id = _id

    def __init__(self, frameElementOrType: str,
                 frame: str = None,
                 id: str = None):
        if frame is None:
            self.constructor1(frameElementOrType)
        else:
            self.constructor2(frameElementOrType, frame, id)

    cpdef str getFrameElementType(self):
        """
        Accessor for frameElementType.

        RETURNS
        -------
        str
            frameElementType.
        """
        return self.__frame_element_type

    cpdef str getFrame(self):
        """
        Accessor for frame.

        RETURNS
        -------
        str
            frame.
        """
        return self.__frame

    cpdef str getId(self):
        """
        Accessor for id.

        RETURNS
        -------
        str
            id.
        """
        return self.__id

    def __str__(self)-> str:
        """
        __str__ converts an Argument to a string. If the frameElementType is "NONE" returns only "NONE", otherwise
        it returns frameElement string which is in the form of frameElementType$id

        RETURNS
        -------
        str
            string form of argument
        """
        if self.__frame_element_type == "NONE":
            return self.__frame_element_type
        else:
            return self.__frame_element_type + "$" + self.__frame + "$" + self.__id

    cpdef setId(self, str _id):
        self.__id = _id
