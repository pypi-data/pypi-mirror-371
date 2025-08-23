from FrameNet.FrameElement cimport FrameElement


cdef class FrameElementList(object):

    def __init__(self, frameElementList: str):
        """
        Constructor of frame element list from a string. The frame elements for a word is a concatenated list of
        frame element separated via '#' character.
        :param frameElementList: String consisting of frame elements separated with '#' character.
        """
        cdef str item
        self.__frame_elements = []
        items = frameElementList.split('#')
        for item in items:
            self.__frame_elements.append(FrameElement(item))

    def __str__(self) -> str:
        """
        Overloaded toString method to convert a frame element list to a string. Concatenates the string forms of all
        frame element with '#' character.
        :return: String form of the frame element list.
        """
        cdef int i
        cdef str result
        if len(self.__frame_elements) == 0:
            return "NONE"
        else:
            result = self.__frame_elements[0].__str__()
            for i in range(1, len(self.__frame_elements)):
                result += "#" + self.__frame_elements[i].__str__()
            return result

    cpdef updateConnectedId(self, str previousId, str currentId):
        """
        Replaces id's of predicates, which have previousId as synset id, with currentId.
        :param previousId: Previous id of the synset.
        :param currentId: Replacement id.
        """
        cdef FrameElement frame_element
        for frame_element in self.__frame_elements:
            if frame_element.getId() == previousId:
                frame_element.setId(currentId)

    cpdef addPredicate(self, str predicateId):
        """
        Adds a predicate argument to the frame element list of this word.
        :param predicateId: Synset id of this predicate.
        """
        if len(self.__frame_elements) != 0 and self.__frame_elements[0].getFrameElementType() == "NONE":
            self.__frame_elements.pop(0)
        self.__frame_elements.append(FrameElement("PREDICATE", "NONE", predicateId))

    cpdef removePredicate(self):
        """
        Removes the predicate with the given predicate id.
        """
        cdef FrameElement frame_element
        for frame_element in self.__frame_elements:
            if frame_element.getFrameElementType() == "PREDICATE":
                self.__frame_elements.remove(frame_element)
                break

    cpdef bint containsPredicate(self):
        """
        Checks if one of the frame elements is a predicate.
        :return: True, if one of the frame elements is predicate; false otherwise.
        """
        cdef FrameElement frame_element
        for frame_element in self.__frame_elements:
            if frame_element.getFrameElementType() == "PREDICATE":
                return True
        return False

    cpdef bint containsPredicateWithId(self, str predicateId):
        """
        Checks if one of the frame element is a predicate with the given id.
        :param predicateId: Synset id to check.
        :return: True, if one of the frame element is predicate; false otherwise.
        """
        cdef FrameElement frame_element
        for frame_element in self.__frame_elements:
            if frame_element.getFrameElementType() == "PREDICATE" and frame_element.getId() == predicateId:
                return True
        return False

    cpdef list getFrameElements(self):
        """
        Returns the frame elements as an array list of strings.
        :return: Frame elements as an array list of strings.
        """
        cdef FrameElement frame_element
        cdef list result
        result = []
        for frame_element in self.__frame_elements:
            result.append(frame_element.__str__())
        return result

    cpdef bint containsFrameElement(self,
                             str frameElementType,
                             str frame,
                             str _id):
        """
        Checks if the given argument with the given type and id exists or not.
        :param frameElementType: Type of the frame element to search for.
        :param frame: Name of the frame to search for
        :param _id: Id of the frame element to search for.
        :return: True if the frame element exists, false otherwise.
        """
        cdef FrameElement frame_element
        for frame_element in self.__frame_elements:
            if frame_element.getFrameElementType() == frameElementType and frame_element.getFrame() == frame and frame_element.getId() == _id:
                return True
        return False
