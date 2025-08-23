import xml.etree.ElementTree

import pkg_resources

cdef class FrameNet:

    def __init__(self):
        """
        A constructor of FrameNet class which reads all frame files inside the files2.txt file. For each filename inside
        that file, the constructor creates a FrameNet.Frame and puts in inside the frames array.
        """
        self.__frames = []
        root = xml.etree.ElementTree.parse(pkg_resources.resource_filename(__name__, 'data/framenet.xml')).getroot()
        for frame_node in root:
            frame = Frame(frame_node.attrib["NAME"])
            for child_node in frame_node:
                if child_node.tag == "LEXICAL_UNITS":
                    for lexical_unit in child_node:
                        frame.addLexicalUnit(lexical_unit.text)
                elif child_node.tag == "FRAME_ELEMENTS":
                    for frame_element in child_node:
                        frame.addFrameElement(frame_element.text)
            self.__frames.append(frame)

    cpdef bint lexicalUnitExists(self, str synSetId):
        """
        Checks if the given lexical unit exists in any frame in the frame set.
        :param synSetId: Id of the lexical unit
        :return: True if any frame contains the given lexical unit, false otherwise.
        """
        cdef Frame frame
        for frame in self.__frames:
            if frame.lexicalUnitExists(synSetId):
                return True
        return False

    cpdef list getFrames(self, str synSetId):
        """
        Returns an array of frames that contain the given lexical unit in their lexical units
        :param synSetId: Id of the lexical unit.
        :return: An array of frames that contains the given lexical unit.
        """
        cdef list result
        cdef Frame frame
        result = []
        for frame in self.__frames:
            if frame.lexicalUnitExists(synSetId):
                result.append(frame)
        return result

    cpdef int size(self):
        """
        Returns number of frames in the frame set.
        :return: Number of frames in the frame set.
        """
        return len(self.__frames)

    cpdef Frame getFrame(self, int index):
        """
        Returns the element at the specified position in the frame list.
        :param index: index of the element to return
        :return: The element at the specified position in the frame list.
        """
        return self.__frames[index]
