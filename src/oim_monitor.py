import asyncio
from datetime import datetime
import platform
import re
from asyncio import subprocess
from decimal import Decimal
from logging import debug, error, info, warning
from sqlite3 import Timestamp
from typing import Any, Dict, List, Optional, Tuple, Union

from src.oim_database import OIM_Database


class OIM_Monitor:
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
        self.database: OIM_Database = OIM_Database()
        ## Ping def
        self.ping_re_pattern_main: re.Pattern = re.compile(r'PING\s(\S+)\s(\S+).+(\d+\spackets\stransmitted),.+(\d+\sreceived)', flags=re.S)
        self.ping_re_pattern_success: re.Pattern = re.compile(r'PING.+ttl=(\d+).+time=([\d.]+\s\S?s)', flags=re.S)
        self.ping_arg_prep: List[str] = ["ping", "", "1"]
        if self.platform == "WINDOWS":
            self.ping_arg_prep[1] = "-n"
        else:
            self.ping_arg_prep[1] = "-c"


    async def _ping(self, destination: str) -> Dict[str, Union[bool, int, str, Decimal]]:
        ping_process: subprocess.Process = await asyncio.create_subprocess_exec(*self.ping_arg_prep, destination, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        timestamp: int = datetime.now().timestamp()
        stdout: bytes
        stderr: bytes
        stdout, stderr = await ping_process.communicate()
        ping_info: List[str] = self.ping_re_pattern_main.findall(stdout.decode())
        return_dict: Dict[str, Union[bool, int, str, Decimal]] = {
                "destination": ping_info[0][0],
                "timestamp": timestamp,
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
            [debug(test) for test in ping_test_results]
            '''for ping_result in ping_test_results:
                self.database.save_ping_result(
                    destination = ping_result["destination"],
                    timestamp = ping_result["timestamp"],
                    ip_str = ping_result["ip_server"],

                )'''
            return True
        except Exception as e:
            error(f"Error: \n{e}")
            return False
        
