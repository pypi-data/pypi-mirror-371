cdef class FrameElementList(object):

    cdef list __frame_elements

    cpdef updateConnectedId(self, str previousId, str currentId)
    cpdef addPredicate(self, str predicateId)
    cpdef removePredicate(self)
    cpdef bint containsPredicate(self)
    cpdef bint containsPredicateWithId(self, str predicateId)
    cpdef list getFrameElements(self)
    cpdef bint containsFrameElement(self, str argumentType, str frame, str _id)
