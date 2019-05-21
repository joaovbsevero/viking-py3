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
        program_info, machine_code, run_output = self.memory.compile_assembly(assembly)

        return machine_code, program_info, run_output, symbols
