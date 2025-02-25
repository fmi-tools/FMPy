import pytest
from os.path import dirname, join, isfile
import fmpy
from fmpy import platform, supported_platforms, simulate_fmu
from fmpy.util import add_remoting, download_file, has_wsl, has_wine64


pytest.skip(
    reason="Comment out to run remoting test",
    allow_module_level=True
)

@pytest.mark.skipif(platform != 'win64', reason="Windows 32-bit is only supported on Windows 64-bit")
def test_remoting_win32_on_win64_cs():

    filename = download_file(
        'https://github.com/modelica/fmi-cross-check/raw/master/fmus/2.0/cs/win32/FMUSDK/2.0.4/vanDerPol/vanDerPol.fmu',
        checksum='6a782ae3b3298081f9c620a17dedd54370622bd2bb78f42cb027243323a1b805')

    assert 'win64' not in supported_platforms(filename)

    simulate_fmu(filename, fmi_type='CoSimulation', remote_platform='win32')

    add_remoting(filename, host_platform='win64', remote_platform='win32')

    assert 'win64' in supported_platforms(filename)

    simulate_fmu(filename, fmi_type='CoSimulation', remote_platform=None)

@pytest.mark.skipif(platform != 'win64', reason="Windows 32-bit is only supported on Windows 64-bit")
def test_remoting_win32_on_win64_me():

    filename = download_file(
        'https://github.com/modelica/fmi-cross-check/raw/master/fmus/2.0/me/win32/MapleSim/2021.1/CoupledClutches/CoupledClutches.fmu',
        checksum='2a22c800285bcda810d9fe59234ee72c29e0fea86bb6ab7d6eb5b703f0afbe4e')

    assert 'win64' not in supported_platforms(filename)

    simulate_fmu(filename, fmi_type='ModelExchange', remote_platform='win32', fmi_call_logger=None)

    add_remoting(filename, 'win64', 'win32')

    assert 'win64' in supported_platforms(filename)

    simulate_fmu(filename, fmi_type='ModelExchange', remote_platform=None)

@pytest.mark.skipif(not has_wsl(), reason="Requires Windows 64-bit and WSL")
def test_remoting_linux64_on_win64():

    if not isfile(join(dirname(fmpy.__file__), 'remoting', 'linux64', 'server_tcp')):
        return  # Linux binary is missing

    filename = download_file(
        'https://github.com/modelica/fmi-cross-check/raw/master/fmus/2.0/cs/linux64/MapleSim/2021.1/Rectifier/Rectifier.fmu',
        checksum='b9238cd6bb684f1cf5b240ca140ed5b3f75719cacf81df5ff0cae74c2e31e52e')

    assert 'win64' not in supported_platforms(filename)

    simulate_fmu(filename, remote_platform='linux64')

    add_remoting(filename, host_platform='win64', remote_platform='linux64')

    assert 'win64' in supported_platforms(filename)

    simulate_fmu(filename, remote_platform=None)

@pytest.mark.skipif(not has_wine64(), reason="Requires Linux 64-bit and wine 64-bit")
def test_remoting_win64_on_linux64_cs():

    filename = download_file(
        'https://github.com/modelica/fmi-cross-check/raw/master/fmus/2.0/cs/win64/Dymola/2019FD01/DFFREG/DFFREG.fmu',
        checksum='b4baf75e189fc7078b76c3d9f23f6476ec103d93f60168df4e82fa4dc053a93c')

    assert 'linux64' not in supported_platforms(filename)

    simulate_fmu(filename, remote_platform='win64', stop_time=5, output_interval=0.01)

    add_remoting(filename, host_platform='linux64', remote_platform='win64')

    assert 'win64' in supported_platforms(filename)

    simulate_fmu(filename, remote_platform=None)
