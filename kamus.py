"""

External Binary Trie

Author: Peb Ruswono Aryan
Description: read external file as dictionary

License : GPL

"""
import struct
import os

BASE_SCHEMA = 'cIII' #current character (char), left branch (uint32), right branch (uint32), value (uint32), limited to ASCII & 2GB filesize


class KamusEksternal:  
    CUR_position = 0
    ROOT_position = 0
    MARKER = 0xFFFFFFFF
    
    def __init__(self, filename, scheme=BASE_SCHEMA):
        if os.path.exists(filename):
            self.handle = open(filename, "rb+")
            
            #read schema
            num = struct.unpack('<B', self.handle.read(1))[0]
            self.schema = self.handle.read(num)
            self.nodesize = struct.calcsize('<'+self.schema)
            
            #read root
            self.ROOT_position = self.handle.tell()
            self.first()
        else:
            self.handle = open(filename, "wb+")
            
            #write schema
            self.schema = scheme
            self.nodesize = struct.calcsize('<'+self.schema)
            self.handle.write(struct.pack('<B', len(self.schema)))
            self.handle.write(self.schema)
            
            #write root
            self.ROOT_position = self.handle.tell()
            self.CUR_position = self.ROOT_position
            self.current = ('`',0,0,self.MARKER)
            self.save()
            
    def close(self):
        self.handle.seek(0, os.SEEK_END)
        self.handle.close()
        
    def has_child(self, c):
        """
        move to child node containing character c, return to current when failed
        """
        self.left()
        while self.current is not None and self.current[0] != c:
            self.right()
        #{ self.current = None | self.current[0] = c }
        
        return self.current
            
    def __getitem__(self,key):
        self.first()
        child = None
        for k in key:
            PARENT_position = self.CUR_position
            child = self.has_child(k)
            if child is None: #not found
                self.handle.seek(PARENT_position)
                self.next()
                break
        #{ child = None | child contains last char in key}
        if child is not None:
            if child[3] == self.MARKER:
                #exist but has not assigned
                return None
            else:
                return child[3]
        else:
            return None
        
    def __setitem__(self, key, value):
        #kasus : ketemu/tidak
        self.first()
        i = 0
        child = None
        for k in key:
            PARENT_position = self.CUR_position
            child = self.has_child(k)
            if child is None: #not found
                self.handle.seek(PARENT_position)
                self.next()
                break
            i += 1
        #{ child = None | child contains last char in key}
        if child is not None:#ketemu
            self.set_value(value)
            self.save()
        else:
            self.insert(key[i:], value)
            
    def findprefix(self, prefix):
        """
        return list of all words startswith prefix
        """
        self.first()
        i = 0
        child = self.current #possible if len(prefix)==0
        for k in prefix:
            PARENT_position = self.CUR_position
            child = self.has_child(k)
            if child is None: #not found
                self.handle.seek(PARENT_position)
                self.next()
                break
            i += 1
        #{ child = None | child contains last char in key}
        result = []
        if self.current[3] != self.MARKER:
            result = [prefix]
        self.left()
        if i==len(prefix):
            return result+self.get_child(prefix[:i])
        else:
            return result
        
            
    def get_child(self, temp):
        stack = []
        result = []
        stack.append((self.CUR_position, temp))
        while len(stack)>0:
            offset,pref = stack.pop()
            #pref = pref.strip()
            self.handle.seek(offset)
            if not self.next(): continue
            if self.current[2] != 0:
                stack.append((self.current[2], pref))
            if self.current[3] != self.MARKER:
                result.append(pref+self.current[0])
            if self.current[1] != 0:
                stack.append((self.current[1], pref+self.current[0]))
        
        return result
            
    def insert(self, key, value):
        """
        insert from current node as parent
        """
        self.handle.seek(0, os.SEEK_END)
        NEXT_position = self.handle.tell()
        
        #find insertion point (parent|sibling)
        if self.current[1] == 0:
            #update parent's left
            self.set_left(NEXT_position)
            self.save()
        else:
            #find last sibling
            PARENT_position = self.CUR_position
            self.left()
            while self.current[2] != 0:
                self.right()
            #{ current is last sibling }
            self.set_right(NEXT_position)
            self.save()
        self.handle.seek(NEXT_position)
        self.CUR_position = self.handle.tell()
        
        for ci in xrange(len(key)):
            #write current
            if ci==len(key)-1:
                self.current = (key[ci], 0, 0, value)
            else:
                self.current = (key[ci], self.CUR_position + self.nodesize, 0, self.MARKER)
            self.handle.write(struct.pack('<'+self.schema, *self.current))
            self.CUR_position = self.handle.tell()
        
    def save(self):
        self.handle.seek(self.CUR_position)
        self.handle.write(struct.pack('<'+self.schema, *self.current))
        
    # modify in-memory-node, saving deferred
    
    def set_char(self, value):
        self.current = (value, self.current[1], self.current[2], self.current[3])
    
    def set_left(self, value):
        self.current = (self.current[0], value, self.current[2], self.current[3])
        
    def set_right(self, value):
        self.current = (self.current[0], self.current[1], value, self.current[3])
        
    def set_value(self, value):
        self.current = (self.current[0], self.current[1], self.current[2], value)
        
    # tree traversal
        
    def left(self):
        """
        (CAR current)
        """
        if self.current[1] != 0:
            self.handle.seek(self.current[1])
            self.next()
        else:
            self.current = None
        return self.current
        
    def right(self):
        """
        (CDR current)
        """
        if self.current[2] != 0:
            self.handle.seek(self.current[2])
            self.next()
        else:
            self.current = None
        return self.current
        
    # read schema updates current (in memory) node and store current offset for later saving
    
    def first(self):
        self.handle.seek(self.ROOT_position)
        self.next()
        
    def next(self):
        self.CUR_position = self.handle.tell()
        buf = self.handle.read(self.nodesize)
        if len(buf)==self.nodesize:
            self.current = struct.unpack('<'+self.schema, buf)
            return True
        else:
            return False
        
if __name__=='__main__':
    k = KamusEksternal('tes.dic')
    k['acuh'] = 2
    k.close()
    k = KamusEksternal('tes.dic')
    print k['a']
    print k['acuh']
    k.close()
    k = KamusEksternal('tes.dic')
    k['a'] = 1
    k['abadi'] = 3
    k.close()
    k = KamusEksternal('tes.dic')
    print k.findprefix('a')
    k.close()
    os.unlink('tes.dic')