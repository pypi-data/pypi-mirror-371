from base64 import b64encode
from xxhash import xxh3_64_intdigest
from io import BytesIO
from .stream import BinStream
from json import (
    loads as json_loads,
    dumps as json_dumps
)


class RST:
    __slots__ = ('entries', 'version', 'hash_bits', 'has_trenc', 'count', 'hashtable')

    def __init__(self, entries = dict(), version = 5, hash_bits = 38, has_trenc=False, count = 0, hashtable = dict()):
        self.entries = entries
        self.version = version
        self.hash_bits = hash_bits
        self.has_trenc = has_trenc
        self.count = count
        self.hashtable = hashtable

    def __json__(self):
        return {key: getattr(self, key) for key in self.__slots__}

    def stream(self, path, mode, raw=None):
        if raw != None:
            if raw == True:  # the bool True value
                return BinStream(BytesIO())
            else:
                return BinStream(BytesIO(raw))
        return BinStream(open(path, mode))

    def read(self, path, raw=None):
        # Credits https://github.com/CommunityDragon/CDTB/blob/master/cdtb/rstfile.py
        with self.stream(path, 'rb', raw) as f:
            magic, = f.read_s(3)
            self.version, = f.read_u8()
            if magic != "RST":
                raise Exception(f'pyRitoFile: invalid magic for RST file "{magic}"')
            
            if self.version != 5:
                raise Exception(f'pyRitoFile: unsupported RST version "{self.version}"')
            

            hash_mask = (1 << self.hash_bits) - 1
            self.count, = f.read_ul()
            entries = []

            # what is this bro ;-;
            for _ in range(self.count):
                v, = f.read_ull()
                entries.append((v >> self.hash_bits, v & hash_mask))
            
            data = f.stream.read()
            for offset, b_hash in entries:
                end = data.find(b"\0", offset)
                d = data[offset:end]
                self.entries[b_hash] = d.decode('utf-8', 'replace')
            
            print()

    def write(self, path, raw=None):
        with self.stream(path, 'wb', raw) as bs:
            bs.write_s("RST")
            bs.write_u8(self.version)
            bs.write_ul(len(self.entries))
            
            entries_order = []
            for b_hash_str, text in self.entries.items():
                try:
                    hash_int = int(b_hash_str)
                except:
                    hash_int = xxh3_64_intdigest(b_hash_str.lower()) & ((1 << self.hash_bits) - 1)
                
                entries_order.append((hash_int, text))
            
            data_block = bytearray()
            current_offset = 0
            entries_with_offsets = []
            
            for hash_int, text in entries_order:
                text_bytes = text.encode('utf-8', 'replace') + b'\x00'
                entries_with_offsets.append((hash_int, current_offset))
                data_block.extend(text_bytes)

                current_offset += len(text_bytes)
            
            hash_mask = (1 << self.hash_bits) - 1
            for hash_int, offset in entries_with_offsets:
                combined = (offset << self.hash_bits) | (hash_int & hash_mask)
                bs.write_ull(combined)
            
            bs.stream.write(data_block)

    def read_json(self, path, raw=None):
        if raw:
            self.entries = json_loads(raw)
        else:
            self.entries = json_loads(open(path, 'r', encoding='utf-8').read())

    def write_json(self, path, raw=None):
        result = json_dumps(self.entries, indent=4, ensure_ascii=False)
        if raw:
            return result

        with open(path, 'w', encoding='utf-8') as f:
            f.write(result)
    
    def un_hash(self):
        new_entries = {}
        for h, value in self.entries.items():
            if h in self.hashtable:
                new_entries[self.hashtable[h]] = value
            else:
                new_entries[int(h)] = value
        
        self.entries = new_entries