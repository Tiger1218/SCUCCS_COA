import pytest
from cache import DirectMappedCache, SetAssociativeCache, FullAssociativeCache, Memory

@pytest.fixture()
def init_memory():
    MEMORY = Memory(list(range(0xffffffff)))

@pytest.mark.parametrize('ACCESS_ADDR', 'HIT_RATE', )
def test_DirectMappedCache():
    pass
@pytest.mark.skip
def test_FullAssociativeCache():
    pass

def