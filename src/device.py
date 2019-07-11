from assemble16 import Assembler
from run16 import CPU


class Device:
    def __init__(self):
        self.assembler = Assembler()
        self.cpu = CPU()
        self.steps = None
        self.symbols = None
        self.program_info = None
        self.codes = None

    def reset(self):
        self.assembler.reset()
        self.cpu.reset()
        self.steps = None
        self.symbols = None
        self.program_info = None
        self.codes = None

    def generate_symbols(self, program):
        self.assembler.reset()
        self.cpu.reset()

        assembly_code, self.symbols = self.assembler.generate_assembly(program)

        if not self.cpu.check(assembly_code):
            self.program_info, self.codes = self.cpu.load(assembly_code)
        else:
            return None, None, None

        return self.symbols, self.program_info, self.codes

    def get_step(self):
        step, result = self.cpu.do_step()

        if not result:
            return step, None

        if self.cpu.context[7] < self.cpu.context[9]:
            return step, result

        return step, result
