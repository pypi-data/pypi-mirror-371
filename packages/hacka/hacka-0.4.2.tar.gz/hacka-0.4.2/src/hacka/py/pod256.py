#----------------------------------------------------------------------------------------------------------#
#                                   H A C K A P Y  :  P O D
#----------------------------------------------------------------------------------------------------------#
# Pod : Piece Of Data, but limied (max: 3x256 variables)
# And so, efficiently serializable...
#----------------------------------------------------------------------------------------------------------#

from .pod import Pod

class Pod256(Pod):
    def __init__( self, aPod= None ):
        super( Pod256, self ).__init__(aPod)
        self.castChildrenAsPod256()
        #assert self.is256()
    
    # Testing:
    #def is256(self):
    #    averageWord= self.averageWordLenght()
    #    return len()

    # Construction: 
    def castChildrenAsPod256(self):
        self._children= [ Pod256( child )
                         for child in self.children() ]
        return self
    
    # Serializer :
    def dump(self):
        return self.dump_str()

    def dump_str(self):
        # Element to dumps:
        words= self.words()
        integers= self.integers()
        values= self.values()
        children= self.children()

        wordSize= len(words)
        maxWordLen= 0
        for w in words :
            maxWordLen= max( maxWordLen, len(w) )
        intSize= len( integers )
        valuesSize= len( values )
        childrenSize= len( self.children() )

        buffer= f'{wordSize} {maxWordLen} {intSize} {valuesSize} {childrenSize} :'
        if wordSize > 0 :
            buffer+= ' '+ ' '.join( str(i) for i in words )
        if intSize > 0 :
            buffer+= ' '+ ' '.join( str(i) for i in integers )
        if valuesSize > 0 :
            buffer+= ' '+ ' '.join( str(i) for i in values )
        for c in children :
            buffer+= "\n" + c.dump_str()
        return buffer

    def load(self, buffer):
        return self.load_str(buffer)
    
    def load_str(self, buffer):
        if type(buffer) == str :
            buffer= buffer.splitlines()
        self.loadLines_str( buffer )
        return self
    
    def loadLines_str(self, buffer):
        # current line:
        line= buffer.pop(0)

        # Get meta data (type, name and structure sizes):
        metas, elements= tuple( line.split(' :') )
        metas= [ int(x) for x in metas.split(' ') ]
        wordSize, maxWordLen, intSize, valuesSize, childrenSize= tuple( metas )
        elements= elements.split(" ")[1:]

        assert( len(elements) == wordSize + intSize + valuesSize )

        # Get words:
        self._words= [ w for w in elements[:wordSize] ]
        wiSize= wordSize+intSize
        self._integers= [ int(i) for i in elements[wordSize:wiSize] ]
        self._values= [ float(f) for f in elements[wiSize:] ]
        
        # load children
        self.clear()
        for iChild in range(childrenSize) :
            child= Pod256()
            buffer= child.loadLines_str(buffer)
            self._children.append( child )

        return buffer
