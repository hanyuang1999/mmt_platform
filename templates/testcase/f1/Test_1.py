from templates.testcase.socket_tools import *

class Test_1:
    @pytest.mark.asyncio
    async def test_1(self):
        await log_socket('1','aa测试','正在aaaaa...')
        print("wakaka")
        await result_socket('1','某测试a','success','axxxxx')
        assert 1

    @pytest.mark.asyncio
    async def test_2(self):
        await log_socket('1','vv测试','正在vvvv...')
        print("wakaka")
        await result_socket('1','某测试v','success','vxxxxx')
        assert 1

    @pytest.mark.asyncio
    async def test_3(self):
        await log_socket('1','bb测试','正在bbbbbbb...')
        print("wakaka")
        await result_socket('1','某测试b','success','bxxxx')
        assert 1
        