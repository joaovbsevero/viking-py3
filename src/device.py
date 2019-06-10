from assemble16 import Assembler
from run16 import CPU


class Device:
    def __init__(self):
        self.assembler = Assembler()
        self.cpu = CPU()

    def reset(self):
        self.assembler.reset()
        self.cpu.reset()

    def generate_output(self, program):
        self.assembler.reset()
        self.cpu.reset()
        steps_response = 'Error'

        assembly_code, symbols = self.assembler.generate_assembly(program)

        if not self.cpu.check(assembly_code):
            program_info, machine_code = self.cpu.load(assembly_code)
            steps_response = self.cpu.do_steps()
        else:
            return [steps_response, 0, 0, 0, 0]

        return [steps_response, self.cpu.steps, symbols, program_info, machine_code]
