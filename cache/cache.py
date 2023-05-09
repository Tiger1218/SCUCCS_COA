# Copyright (C) 2022-2023 Ziqin Li, Sichuan University
# This code is licensed under MIT license.
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated  documentation files (the "Software")
# to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
    This module aims to simulate how three diffrent kinds of cache works
            where they are impleted in the following class:
        SetAssociativeCache,
        FullyAssociativeCache,
        DirectMappedCache
"""

import sys
import logging
from typing import Tuple, List, Optional, Any, Union
from random import randint

Addr = int
Status = int
Number = Union[int, float, complex]

FAILURE: Status = 1
SUCCESS: Status = 0

BLOCK_SIZE = 8

class CacheBlock:
    """A class representing a cache block.

    Attributes:
        data (List[Addr]): A list of data stored in the block.
        tag (int): The tag of the block.

    Methods:
        __init__(self):
            Initializes the cache block.

        access(self, tag: int, offset: int) -> Tuple[Status, int]:
            Accesses the cache block by tag and offset and returns the data if the tag matches.

        __getitem__(self, key: Addr):
            Returns the data at the specified key.

        change(self, key: Addr, value: int):
            Changes the data at the specified key to the given value.

    """

    data: List[Addr] = []
    tag: int

    def __init__(self):
        self.data = [0] * BLOCK_SIZE
        self.tag = -1

    def access(self, tag: int, offset: int) -> Tuple[Status, int]:
        """Accesses the cache block by tag and offset and returns the data if the tag matches.

        Args:
            tag (int): The tag of the block to access.
            offset (int): The offset of the data in the block.

        Returns:
            Tuple[Status, int]: A tuple containing the status of the access
                            (SUCCESS or FAILURE) and the data if found.

        Raises:
            None
        """
        if tag != self.tag:
            return (FAILURE, -1)
        return (SUCCESS, self.data[offset])

    def __getitem__(self, key: Addr):
        return self.data[key]

    def change(self, key: Addr, value: int):
        """Changes the data at the specified key to the given value.

        Args:
            key (Addr): The key of the data to change.
            value (int): The new value to set the data to.

        Returns:
            None

        Raises:
            None
        """
        self.data[key] = value

class BaseCache:
    """Base Class for Cache"""
    def __getitem__(self, addr: Addr):
        pass

class Cache(BaseCache):
    """
        Cache class that
    """
    hits: int
    misses: int
    logger: logging.Logger
    def __init__(self):
        self.hits = 0
        self.misses = 0

    def __getitem__(self, addr: Addr):
        return self.access(addr)

    def statics(self) -> None:
        self.logger.info("Totally Hits %d , Misses %d, hit rate = %.2f",
                         self.hits,
                         self.misses,
                         self.hits / (self.hits + self.misses))

    def calculate(self, hit_time: Number, miss_time: Number) -> Number:
        self.logger.info("Average hit time = %.2f", (self.hits * hit_time +
                                self.misses * (miss_time + hit_time)) / (self.hits + self.misses))

    def _init_logger(
            self,
            log_level: int,
            log_formatter: str):
        logger: logging.Logger = logging.getLogger()
        logger.setLevel(log_level)
        formatter = logging.Formatter(log_formatter)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        self.logger = logger

    def access(self, addr: Addr):
        return memory[addr]

    def _incmiss(self, addr) -> None:
        self.logger.info("Miss hit %d", addr)
        self.misses += 1
        self.hits -= 1

    def _inchit(self, addr: Addr, data: int) -> None:
        self.logger.info("Hit %d, result = %d", addr, data)
        self.hits += 1

class Memory:
    """
        Simulate the memory
    """
    data: List[int]

    def __init__(self, initram: List[int]) -> None:
        self.data = initram

    def __getitem__(self, key: Addr) -> int:
        return self.data[key]

    def __str__(self) -> str:
        return str(self.data)

class SetAssociativeCache(Cache):
    """A class representing a set-associative cache.

    Attributes:
        set_size (int): The number of blocks in a single set.
        size (int): The total number of blocks in the cache.
        sets (List[Any]): A list of sets, where each set is a list of CacheBlock objects.
        logger (logging.Logger): A logger object used for logging.
        hits (int): The number of cache hits.
        misses (int): The number of cache misses.

    Methods:
        __init__(self, set_size: int, size: int, log_level: Optional[int] = logging.debug,
                 log_formatter: Optional[str] =
                 '%(asctime)s - %(name)s - %(levelname)s - %(message)s') -> None:
            Initializes the set-associative cache.

        access(self, addr: Addr) -> int:
            Accesses the memory address and returns the data.

        statics(self) -> None:
            Prints out the hit rate and the total number of hits and misses.

    """

    set_size: int
    size: int
    sets = List[Any]
    logger: logging.Logger
    hits: int
    misses: int
    way: int

    def __init__(self,
                 set_size: int,
                 size: int,
                 log_level: Optional[int] = logging.INFO,
                 log_formatter: Optional[str] = \
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s') -> None:
        """Initializes the set-associative cache.

        Args:
            set_size (int): The number of blocks in a single set.
            size (int): The total number of blocks in the cache.
            log_level (Optional[int], optional): The log level to pass to the logger.
                                Defaults to logging.debug.
            log_formatter (Optional[str], optional): The log formatter to pass to the logger.
                                Defaults to '%(asctime)s - %(name)s - %(levelname)s - %(message)s'.

        Returns:
            None

        Raises:
            None
        """
        super().__init__()
        self.size = size
        self.set_size = set_size
        self._init_sets()
        self._init_logger(log_level, log_formatter)
        print(self.sets)

    def access(self, addr: Addr) -> int:
        """Accesses the memory address and returns the data.

        Args:
            addr (Addr): The memory address to access.

        Returns:
            int: The data stored at the memory address.

        Raises:
            None
        """
        self.logger.debug("Try to access Address %d", addr)
        status, data = self._search(addr)
        if status == SUCCESS:
            self._inchit(addr, data)
            return data
        self._incmiss(addr)
        return self.access(addr)

    def _init_sets(self) -> None:
        """Initializes the sets in the cache.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.sets = [[CacheBlock() for nonsense in range(self.set_size)]
                        for _ in range(self.size // self.set_size)]

    def _search(self, addr: Addr) -> Tuple[Status, int]:
        """Searches for an address in the cache.

        Args:
            addr (Addr): The memory address to search for.

        Returns:
            Tuple[Status, int]: A tuple containing the status of the search
                    (SUCCESS or FAILURE) and the data if found.

        Raises:
            None
        """
        set_index = addr // BLOCK_SIZE % (self.size // self.set_size)
        tag: int = addr // BLOCK_SIZE // (self.size // self.set_size)
        offset: int = addr % BLOCK_SIZE
        self.logger.debug("set_index = %d, tag = %d, offset = %d", set_index, tag, offset)
        for index in range(self.set_size):
            # print(set_index, index)
            if self.sets[set_index][index].tag == tag:
                return (SUCCESS, self.sets[set_index][index][offset])
        return (FAILURE, -1)

    def _replace(self, addr: Addr) -> int:
        """Replaces a block in the cache with new data.

        Args:
            addr (Addr): The memory address to replace.

        Returns:
            int: SUCCESS if the replace was successful, FAILURE otherwise.

        Raises:
            None
        """
        start_block = addr - addr % BLOCK_SIZE
        set_index = addr // BLOCK_SIZE % (self.size // self.set_size)
        index = self._choose_replace_index(set_index)
        self.sets[set_index][index].tag = addr // BLOCK_SIZE // (self.size // self.set_size)
        self.logger.debug("Replacing block sets[%d][%d] from Memory[%d - %d]",
                         set_index, index, start_block, start_block + BLOCK_SIZE - 1)
        try:
            for i in range(start_block, start_block + BLOCK_SIZE):
                self.sets[set_index][index].change(i % BLOCK_SIZE, memory[i])
        except KeyError as k_e:
            self.logger.error("Replace fails. error msg: %s", k_e)
            return FAILURE
        return SUCCESS

    def _choose_replace_index(self, set_index: int) -> int:
        """Chooses a block in a set to replace.

        Args:
            set_index (int): The index of the set to choose a block from.

        Returns:
            int: The index of the block to replace.

        Raises:
            None
        """
        for index in range(self.set_size):
            # print(index, set_index, len(self.sets))
            if self.sets[set_index][index].tag == -1:
                return index
        return randint(0, self.set_size - 1)

    def _incmiss(self, addr) -> None:
        """Increments the miss count.

        Args:
            addr (Addr): The memory address that was missed.

        Returns:
            None

        Raises:
            None
        """
        self.logger.info("Miss hit %d", addr)
        self.misses += 1
        self.hits -= 1
        self._replace(addr)

    def _inchit(self, addr: Addr, data: int) -> None:
        """Increments the hit count.

        Args:
            addr (Addr): The memory address that was hit.
            data (int): The data stored at the memory address.

        Returns:
            None

        Raises:
            None
        """
        self.logger.info("Hit %d, result = %d", addr, data)
        self.hits += 1

class DirectMappedCache(SetAssociativeCache):
    '''
        DirectMappedCache
        Same as SetAssociativeCache
    '''
    def __init__(self,
                 size: int,
                 log_level: Optional[int] = logging.INFO,
                 log_formatter: Optional[str] = \
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s') -> None:
        super().__init__(set_size=1, size=size, log_level=log_level, log_formatter=log_formatter)

class FullAssociativeCache(SetAssociativeCache):
    '''
        FullAssociativeCache
        Same as SetAssociativeCache
    '''
    def __init__(self,
                 size: int,
                 log_level: Optional[int] = logging.INFO,
                 log_formatter: Optional[str] = \
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s') -> None:
        super().__init__(set_size=size, size=size, log_level=log_level, log_formatter=log_formatter)

memory = Memory(list(range(0xffff)))

if __name__ == '__main__':
    ACCESS_ADDR = [int(addr, 16) for addr in \
                   "0x2C, 0x6D, 0x86, 0x29, 0xA5, 0x82, 0xA7, 0x68, 0x80, 0x2B".split(", ")]
    # ACCESS_ADDR = list(range(1, 100))
    # ACCESS_ADDR = 3 * list(range(0x8, 0x33 + 1))
    cache = SetAssociativeCache(2, 4, log_level=logging.DEBUG)
    # print(Memory)
    for a in ACCESS_ADDR:
        _ = cache[a]
    cache.statics()
    cache.calculate(5, 25)
