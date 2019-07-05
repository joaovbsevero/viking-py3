from assemble16 import Assembler
from run16 import CPU


class Device:
    def __init__(self):
        self.assembler = Assembler()
        self.cpu = CPU()
        self.response = None
        self.steps = None
        self.symbols = None
        self.program_info = None
        self.codes = None

    def reset(self):
        self.assembler.reset()
        self.cpu.reset()
        self.response = None
        self.steps = None
        self.symbols = None
        self.program_info = None
        self.codes = None

    def generate_output(self, program):
        self.assembler.reset()
        self.cpu.reset()
        self.response = 'Error'

        assembly_code, self.symbols = self.assembler.generate_assembly(program)

        if not self.cpu.check(assembly_code):
            self.program_info, self.codes = self.cpu.load(assembly_code)
            self.response = self.cpu.do_steps()
            self.steps = self.cpu.steps
        else:
            return [self.response, 0, 0, 0, 0]

        return [self.response, self.cpu.steps, self.symbols, self.program_info, self.codes]

    def get_output(self):
        if self.steps is not None:
            return [self.response, self.cpu.steps, self.symbols, self.program_info, self.codes]
        else:
            return [self.response, 0, 0, 0, 0]
