from templates.testcase.socket_tools import *

class Test_1:
    @pytest.mark.asyncio
    async def test_a(self):
        await log_socket('aa测试','正在aaaaa...')
        print("wakaka")
        await result_socket('某测试a','success','axxxxx')
        assert 1

    @pytest.mark.asyncio
    async def test_b(self):
        await log_socket('vv测试','正在vvvv...')
        print("wakaka")
        await result_socket('某测试v','success','vxxxxx')
        assert 1

    @pytest.mark.asyncio
    async def test_c(self):
        await log_socket('bb测试','正在bbbbbbb...')
        print("wakaka")
        await result_socket('某测试b','success','bxxxx')
        assert 1
        