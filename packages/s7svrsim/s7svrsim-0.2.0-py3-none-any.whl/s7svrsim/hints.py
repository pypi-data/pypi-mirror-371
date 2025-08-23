from abc import ABC


class S7DB(ABC):

    def ReadBit(self, dbNumber: int, offset: int, bit: int) -> bool:
        pass

    def WriteBit(self, dbNumber: int, offset: int, bit: int, flag: bool):
        pass

    def ReadByte(self, dbNumber: int, pos :int) -> int:
        pass

    def WriteByte(self, dbNumber: int, pos :int, value: int):
        pass

    def ReadShort(self, dbNumber: int, pos :int) -> int:
        pass

    def WriteShort(self, dbNumber: int, pos :int, value: int):
        pass

    def ReadUInt32(self, dbNumber: int, pos :int) -> int:
        pass

    def WriteUInt32(self, dbNumber: int, pos :int, value: int):
        pass

    def ReadULong(self, dbNumber: int, pos :int) -> int:
        pass

    def WriteULong(self, dbNumber: int, pos :int, value: int):
        pass
    
    def ReadReal(self, dbNumber: int, pos :int) -> float:
        pass

    def WriteReal(self, dbNumber: int, pos :int, value: float):
        pass

    def ReadLReal(self, dbNumber: int, pos :int) -> float:
        pass

    def WriteLReal(self, dbNumber: int, pos :int, value: float):
        pass

    def ReadString(self, dbNumber: int, pos :int) -> str:
        pass

    def WriteString(self, dbNumber: int, pos :int, maxlen: int, value: str):
        pass
    

class S7MB(ABC):

    def ReadBit(self, offset: int, bit: int) -> bool: 
        pass
    def WriteBit(self, offset: int, bit: int, flag: bool): 
        pass

    def ReadByte(self, pos:int ) -> int: 
        pass
    def WriteByte(self, pos:int, value: int):
        pass

    def ReadShort(self, pos:int) -> int:
        pass
    def WriteShort(self, pos: int, value:int):
        pass

    def ReadUInt32(self, pos: int) -> int:
        pass
    def WriteUInt32(self, pos: int, value:int):
        pass

    def ReadULong(self, pos:int) -> int:
        pass
    def WriteULong(self, pos:int, value: int):
        pass

    def ReadReal(self, pos: int) -> float: 
        pass
    def WriteReal(self, pos:int, value: float):
        pass

    def ReadLReal(self, pos:int) -> float:
        pass

    def WriteLReal(self, pos:int,  real:float):
        pass

    def ReadString(self, offset:int) -> str:
        pass

    def WriteString(self, offset:int, maxlen: int, string: str):
        pass


class CancellationToken(ABC):
    IsCancellationRequested: bool
    CanBeCanceled: bool

class Logger(ABC):

    def LogInfo(self, content: str):
        pass
    def LogError(self, content: str):
        pass


class S7Context(ABC):
    DBService: S7DB 
    MB: S7MB
    Logger: Logger
    CancellationToken: CancellationToken