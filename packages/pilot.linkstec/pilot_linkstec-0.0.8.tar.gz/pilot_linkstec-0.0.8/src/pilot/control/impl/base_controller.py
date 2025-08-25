from concurrent.futures import ThreadPoolExecutor


from pilot.control.control_interface import ControlInterface
from pilot.unit.impl.base_unit import BaseUnit
from pilot.config.config_reader import ConfigReader


class BaseController(ControlInterface):

    def __init__(self):
        pass


    def _init_unit(self):
        return BaseUnit()

    def run(self,configfile: str = None):
        import time
        config_dto = ConfigReader(configfile).get_dto()
        def worker():
            unit = self._init_unit()
            unit.config_dto = config_dto
            unit.run()
        with ThreadPoolExecutor(max_workers=config_dto.threads) as executor:
            futures = []
            for _ in range(config_dto.threads):
                futures.append(executor.submit(worker))
                time.sleep(0.2)
            for future in futures:
                future.result()
