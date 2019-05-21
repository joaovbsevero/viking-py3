from assemble16 import Assembler
from run16 import Memory


class Device:
    def __init__(self):
        self.assembler = Assembler()
        self.memory = Memory()

    def generate_output(self, program):
        self.assembler.reset()
        self.memory.reset()

        assembly, symbols = self.assembler.generate_assembly(program)
        if not self.memory.check(assembly):
            program_info, machine_code = self.memory.load(assembly)
            output = self.memory.do_steps()

            return machine_code, program_info, output, symbols

        else:
            return [], ['Error'], [], []

    def reset(self):
        self.assembler.reset()
        self.memory.reset()

    def get_steps(self):
        return self.memory.steps
