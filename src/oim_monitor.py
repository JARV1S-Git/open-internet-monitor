from asyncio import subprocess
from decimal import Decimal
import platform
import asyncio
from typing import Any, Dict, List, Optional, Tuple, Union
import re
from pprint import pprint

class Monitor:
    def __init__(self, *args: Optional[str], default: bool = True) -> None:
        """Initializes a monitor object.
        This class uses pings to test internet connectivity. Any non-keyword arguments will be used as test destinations.

        Args:
            default (bool, optional): If true, uses Google, Cisco, Amazon servers as additional test destinations. Defaults to True.
        """
        ## Set defaults destinations
        if default:
            self.destinations: List[str] = ["google.com", "cisco.com", "amazon.com"]
        else:
            self.destinations: List[str] = []
        ## Add destinations as arguments
        if args:
            self.destinations = self.destinations + list(args)
        ## Check OS
        self.platform: str = platform.system().upper()
        ## Store data
        self.datastore: Dict[Any] = {}
        ## Ping def
        self.ping_re_pattern_main: re.Pattern = re.compile(r'PING\s(\S+)\s(\S+).+(\d+\spackets\stransmitted),.+(\d+\sreceived)', flags=re.S)
        self.ping_re_pattern_success: re.Pattern = re.compile(r'PING.+ttl=(\d+).+time=([\d.]+\s\S?s)', flags=re.S)
        self.ping_arg_prep: List[str] = ["ping", "", "1"]
        if self.platform == "WINDOWS":
            self.ping_arg_prep[1] = "-n"
        else:
            self.ping_arg_prep[1] = "-c"
        '''
        def _ping_outer(self) -> Callable:
            ping_arguments: List[str] = ["ping", None, "1"]
            if self.platform == "WINDOWS":
                ping_arguments[1] = "-n"
            else:
                ping_arguments[1] = "-c"
            async def _ping_inner(self, destination: str) -> List[Union[bool, int]]:
                process_result: subprocess.Process = await asyncio.create_subprocess_exec(*ping_arguments, destination)
                return 
            return _ping_inner
        self._ping: Callable = _ping_outer()
        '''

    async def _ping(self, destination: str) -> Dict[str, Union[bool, int, str, Decimal]]:
        ping_process: subprocess.Process = await asyncio.create_subprocess_exec(*self.ping_arg_prep, destination, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout: bytes
        stderr: bytes
        stdout, stderr = await ping_process.communicate()
        ping_info: List[str] = self.ping_re_pattern_main.findall(stdout.decode())
        return_dict: Dict[str, Union[bool, int, str, Decimal]] = {
                "destination": ping_info[0][0],
                "ip_server": ping_info[0][1][1:-1],
                "packet_tx": int(ping_info[0][2][0]),
                "packet_rx": int(ping_info[0][3][0])
                }
        if return_dict["packet_rx"] == 1:
            ping_info_more: Tuple[str] = self.ping_re_pattern_success.findall(stdout.decode())[0]
            return_dict["success"] = True
            return_dict["ttl"] = int(ping_info_more[0])
            if("ms" in ping_info_more[1]): return_dict["time"] = Decimal(ping_info_more[1].split(" ")[0])/1000
            else: return_dict["time"] = str(ping_info_more[1])
        else:
            return_dict["success"] = False
        return return_dict

    async def run_test(self) -> bool:
        try:
            ping_test_results: Dict[str, Union[bool, int, str, Decimal]] = await asyncio.gather(*(self._ping(destination) for destination in self.destinations))
            [print(test) for test in ping_test_results]
            return True
        except Exception as e:
            print(f"Error: \n{e}")
        

if __name__ == "__main__":
    test_monitor: Monitor = Monitor("microsoft.com")
    asyncio.run(test_monitor.run_test())
    # with open("output.log") as 