from templates.testcase.socket_tools import *

class Test_2:
    @pytest.mark.asyncio
    async def test_d(self):
        await log_socket('cc测试','正在dfds...')
        await result_socket('某测试c','success','bjytjxx')
        assert 1

    @pytest.mark.asyncio
    async def test_e(self):
        await log_socket('s测试','正在cvxcvb...')
        await result_socket('某测试s','success','bdfx')
        assert 1

    @pytest.mark.asyncio
    async def test_f(self):
        await log_socket('vic测试','正在dsfdbb...')
        await result_socket('某测试vic','success','m,jx')
        assert 1