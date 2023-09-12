import asyncio
import time
import sys
# POSIX shared memory
from ctypes import (Union, Structure, c_uint, c_ulong, c_int, 
                    c_long, c_float, c_double, c_longlong, c_char, c_void_p, c_size_t,
                    sizeof)


from numpy import byte
import sysv_ipc

class VAL(Union):
    '''Pollux Shmem value'''
    _fields_ = [("bVal", c_int),
                ("iVal", c_long),
                ("fVal", c_float),
                ("dVal", c_double),
                ("llVal", c_longlong)]

CHARARR_32 = c_char * 32
class ShVal(Structure):
    '''Pollux Shmem struct'''
    _fields_ = [("type", c_uint), # INT = 0, FLOAT = 1, BOOL = 2, LONG_LONG = 3, DOUBLE = 4
                ("access", c_uint),
                ("tag", CHARARR_32),
                ("val", VAL),
                ("count", c_ulong),
                ("stamp", c_ulong),
               ]

def type_to_val(sh_val):
    '''Switch on the shared memory type union'''
    val = None
    var_type = sh_val.type
    if var_type == 0:
        val = sh_val.val.iVal
    elif var_type == 1:
        val = sh_val.val.fVal
    elif var_type == 2:
        val = sh_val.val.bVal
    elif var_type == 3:
        val = sh_val.val.llVal
    elif var_type == 4:
        val = sh_val.val.dVal
    else:
        print("Weird variable type")
    #print(f"SHM variable {sh_val.tag} with value {val}, ts {sh_val.stamp},type {sh_val.type} received")
    return val

def set_val(sh_val,value):
    '''Switch on the shared memory type union'''
    var_type = sh_val.type
    if var_type == 0:
        sh_val.val.iVal = value
    elif var_type == 1:
        sh_val.val.fVal = value
    elif var_type == 2:
        sh_val.val.bVal = value
    elif var_type == 3:
        sh_val.val.llVal = value
    elif var_type == 4:
        sh_val.val.dVal = value
    else:
        print("Weird variable type")
        return
    # Set new stamp and increment count
    sh_val.stamp = int(time.time())
    sh_val.count = sh_val.count + 1

class ShmReader():
    def __init__(self):
        self.status = {}
    
    async def print_status(self,var):
        try:
            while True:
                print(var)
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            return "print_status has been cancelled!"

    async def periodic_reader(self, memory_key, interval=1):
        '''Coroutine to read pollux shared-memory structures periodically (infinite loop)'''
        print(f"Shared-memory reader: key: {memory_key} - interval: {interval}s")
        try:
            memory = sysv_ipc.SharedMemory(memory_key)               
        except sysv_ipc.ExistentialError:
            print(f"The shared memory segment with key {memory_key} does not exist.")
        else:
            try:
                while True:
                    num_of_structs = int.from_bytes(memory.read(byte_count=sizeof(c_longlong)),
                                                    byteorder='little')

                    for num in range(0, num_of_structs):
                        memory_value = memory.read(sizeof(ShVal), sizeof(c_long)+sizeof(ShVal)*num)
                        shared_buffer = bytearray(memory_value)
                        shared = ShVal.from_buffer(shared_buffer)
                        val = type_to_val(shared)
                        self.status.update({str(shared.tag, "ISO-8859-1"): val})

                #memory.detach()
                    await asyncio.sleep(interval)
                    
            except asyncio.CancelledError:
                return "Shared-memory reader has been cancelled!"

    def update_shm_key(self, memory_key, tag, value):
        try:
            memory = sysv_ipc.SharedMemory(memory_key)               
        except sysv_ipc.ExistentialError:
            print(f"The shared memory segment with key {memory_key} does not exist")
        else:   
            num_of_structs = int.from_bytes(memory.read(byte_count=sizeof(c_longlong)),
                                                    byteorder='little')
            for num in range(0, num_of_structs):
                memory_value = memory.read(sizeof(ShVal), sizeof(c_long)+sizeof(ShVal)*num)
                shared_buffer = bytearray(memory_value)
                shared = ShVal.from_buffer(shared_buffer)
                if str(shared.tag, "ISO-8859-1") == tag:
                    set_val(shared,value)
                    memory.write(shared,sizeof(c_long)+sizeof(ShVal)*num)
                    memory.detach()
                    return
                else:
                    continue

            memory.detach()
            print(f"There in no variable with tag {tag} defined in shared memory id {memory_key}")

    
    def create_shm(self, memory_key,data):
        memory = sysv_ipc.SharedMemory(memory_key, flags=sysv_ipc.IPC_CREAT, mode=644, size=(len(data)*sizeof(ShVal)+sizeof(c_longlong)))
        nofdata =  c_ulong(len(data))
        memory.write(nofdata,0)
        i = 0
        for item in data:
            shm_val = ShVal()
            shm_val.tag = str.encode(item)
            shm_val.type = data[item]
            memory.write(shm_val,sizeof(c_ulong)+sizeof(ShVal) * i)
            i = i + 1
            print(f"Added {item} to shared memory")
        print(f"Shared memory created with {len(data)} elements")
