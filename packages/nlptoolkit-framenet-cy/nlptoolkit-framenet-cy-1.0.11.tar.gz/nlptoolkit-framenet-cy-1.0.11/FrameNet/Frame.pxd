cdef class Frame:

    cdef str __name
    cdef list __lexical_units
    cdef list __frame_elements

    cpdef addLexicalUnit(self, str lexicalUnit)
    cpdef addFrameElement(self, str frameElement)
    cpdef bint lexicalUnitExists(self, str synSetId)
    cpdef str getLexicalUnit(self, int index)
    cpdef str getFrameElement(self, int index)
    cpdef int lexicalUnitSize(self)
    cpdef int frameElementSize(self)
    cpdef str getName(self)
