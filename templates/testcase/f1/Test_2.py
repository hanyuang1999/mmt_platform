from templates.testcase.socket_tools import *

class Test_2:
    @pytest.mark.asyncio
    async def test_4(self):
        await log_socket('1','cc测试','正在dfds...')
        print("wakaka")
        await result_socket('1','某测试c','success','bjytjxx')
        assert 1

    @pytest.mark.asyncio
    async def test_5(self):
        await log_socket('1','s测试','正在cvxcvb...')
        print("wakaka")
        await result_socket('1','某测试s','success','bdfx')
        assert 1

    @pytest.mark.asyncio
    async def test_6(self):
        await log_socket('1','vic测试','正在dsfdbb...')
        print("wakaka")
        await result_socket('1','某测试vic','success','m,jx')
        assert 1