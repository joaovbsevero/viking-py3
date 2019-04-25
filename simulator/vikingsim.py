#!/usr/bin/python

from simulator import steps


# from PyQt5 import QtWidgets, QtCore, QtGui


class GuiProgram:
    def __init__(self):
        # Classes
        self.assemb = steps.Assembler()

        # GUI Objects
        self.root = Tk()
        self.menu = Menu(root)
        self.memwindow = Toplevel(self.root)
        self.mem_dump = Listbox(self.memwindow, height=24, width=65, font=('Courier', 11))
        self.mem_dumpscroll = Scrollbar(self.memwindow, command=self.mem_dump.yview)
        self.programmenu = Menu(self.menu)
        self.machine_menu = Menu(self.menu)

        self.topframe = Frame(self.root)
        self.middleframe = Frame(self.root)
        self.bottomframe = Frame(self.root)

        self.asmxscrollbar = Scrollbar(self.middleframe, orient=HORIZONTAL)
        self.asmyscrollbar = Scrollbar(self.middleframe)
        self.textasm = Text(self.middleframe, 
                            wrap=None,
                            xscrollcommand=self.asmxscrollbar.set,
                            yscrollcommand=self.asmyscrollbar.set,
                            height=24,
                            width=44, 
                            font=('Courier', 11))
        
        self.text_dump = Listbox(self.middleframe, height=24, width=26, font=('Courier', 11))
        self.textdumpscroll = Scrollbar(self.middleframe, command=self.text_dump.yview)

        self.textsym = Listbox(self.middleframe, height=24, width=18, font=('Courier', 11))
        self.textsymscroll = Scrollbar(self.middleframe, command=self.textsym.yview)
        
        self.out = Text(self.bottomframe, height=14, width=122, font=('Courier', 10))
        self.outscroll = Scrollbar(self.bottomframe, command=self.out.yview)

        # Variables
        self.end = None
        self.reverse_codes = {
            0x0000: 'and', 0x1000: 'or', 0x2000: 'xor', 0x3000: 'slt',
            0x4000: 'sltu', 0x5000: 'add', 0x5001: 'adc', 0x6000: 'sub',
            0x6001: 'sbc', 0x8000: 'ldr', 0x9000: 'ldc', 0xa000: 'lsr',
            0xa001: 'asr', 0xa002: 'ror', 0x0002: 'ldb', 0x1002: 'stb',
            0x4002: 'ldw', 0x5002: 'stw', 0xc000: 'bez', 0xd000: 'bnz'
        }
        self.context = [
            0x0000, 0x0000, 0x0000, 0x0000,  # r0 - r3
            0x0000, 0x0000, 0x0000, 0xdffe,  # r4 - r7
            0x0000, 0x0000, 0x0000  # pc, stack limit, breakpoint
        ]
        self.reg_names = ['r0 (at) : ',
                          'r1      : ',
                          'r2      : ',
                          'r3      : ',
                          'r4      : ',
                          'r5 (sr) : ',
                          'r6 (lr) : ',
                          'r7 (sp) : ',
                          '\nPC      : ']
        self.carry = 0
        self.memory = []
        self.terminput = []

        self.cycles = 0
        self.cycle_delay = 1
        self.RUNNING = -1
        self.STOPPED = -2
        self.machine = self.STOPPED

        # Do all the necessary before this
        mainloop()

    def check(self, program):
        for line in program:
            flds = line.split() if line.__contains__(' ') else line.split('\t')

            if flds:
                return 1

            for f in flds:
                if f == '****':
                    return 1
        return 0

    def load(self, program):
        self.memory = []

        self.text_dump.delete(0, self.end)
        lines = len(program)

        # load program into self.memory
        for line in program:
            flds = line.split() if line.__contains__(' ') else line.split('\t')
            data = int(flds[1], 16)
            self.memory.append(data)

            if data & 0x0800:
                if data & 0xf000 in self.reverse_codes:
                    self.text_dump.insert(self.end,
                                    f'{line}   {self.reverse_codes[data & 0xf000]} '
                                    f'r{(data & 0x0700) >> 8},{data & 0x00ff}')
                else:
                    self.text_dump.insert(self.end, f'{line}   ???')

            else:
                if (data & 0xf003) in self.reverse_codes:
                    self.text_dump.insert(self.end, f'{line}    {self.reverse_codes[data & 0xf003]} r{(data & 0x0700) >> 8},'
                    f'r{(data & 0x00e0) >> 5},r{(data & 0x001c) >> 2}')

                else:
                    self.text_dump.insert(self.end, f'{line}   ???')

        self.out.insert(self.end, f' done. Program size: {str(len(self.memory) * 2)} bytes (code + data).\n')
        self.out.see(self.end)

        # set the stack limit to the self.end of program section
        self.context[9] = (len(self.memory) * 2) + 2

        # reset breakpoint
        self.context[10] = self.context[9]

        # fill the resto of self.memory with zeroes
        self.memory.extend([0 for _ in range(lines, 2872)])

        self.reset()

    def loaderror(self, program):
        self.memory = []

        self.text_dump.delete(0, self.end)

        # load program into self.memory
        for line in program:
            flds = line.split() if line.__contains__(' ') else line.split('\t')

            try:
                data = int(flds[1], 16)
                if data & 0x0800:
                    if (data & 0xf000) in self.reverse_codes:
                        self.text_dump.insert(
                            self.end,
                            f'{line}   {self.reverse_codes[data & 0xf000]} r{(data & 0x0700) >> 8},{(data & 0x00ff)}'
                        )

                    else:
                        self.text_dump.insert(self.end, f'{line}   ???')

                else:
                    if (data & 0xf003) in self.reverse_codes:
                        self.text_dump.insert(
                            self.end, f'{line}   {self.reverse_codes[data & 0xf003]} '
                            f'r{(data & 0x0700) >> 8},r{(data & 0x00e0) >> 5},r{(data & 0x001c) >> 2}'
                        )

                    else:
                        self.text_dump.insert(self.end, line + '   ???')
            except:
                self.text_dump.insert(self.end, line)

        self.out.insert(self.end, ' program has errors.\n')
        self.out.see(self.end)
        self.reset()

    def assembler(self):
        self.out.insert(self.end, '\nAssembling...')
        self.out.see(self.end)
        source_program = str(self.textasm['1.0', 'self.end'])
        self.textsym.delete(0, self.end)
        program = source_program.splitlines()

        self.assemb.pass1(program)
        self.assemb.pass2(program)
        code = self.assemb.pass3(program).splitlines()

        self.loaderror(code) if self.check(code) else self.load(code)

    def cycle(self):

        pc = self.context[8]

        # fetch an instruction from self.memory
        instruction = self.memory[pc >> 1]

        # predecode the instruction (extract opcode fields)
        opc = (instruction & 0xf000) >> 12
        imm = (instruction & 0x0800) >> 11
        rst = (instruction & 0x0700) >> 8
        rs1 = (instruction & 0x00e0) >> 5
        rs2 = (instruction & 0x001c) >> 2
        op2 = instruction & 0x0003
        immediate = instruction & 0x00ff

        # it's halt and catch fire, halt the simulator
        if instruction == 0x0003:
            return 0

        # decode and execute
        if imm == 0:
            if self.context[rs1] > 0x7fff:
                rs1 = self.context[rs1] - 0x10000
            else:
                rs1 = self.context[rs1]

            if self.context[rs2] > 0x7fff:
                rs2 = self.context[rs2] - 0x10000
            else:
                rs2 = self.context[rs2]

        else:
            if self.context[rst] > 0x7fff:
                rs1 = self.context[rst] - 0x10000
            else:
                rs1 = self.context[rst]

            if immediate > 0x7f:
                immediate -= 0x100
            rs2 = immediate

        if opc == 10:
            if op2 == 0:
                self.context[rst] = (rs1 & 0xffff) >> 1

            elif op2 == 1:
                self.context[rst] = rs1 >> 1

            elif op2 == 2:
                self.context[rst] = (self.carry << 15) & ((rs1 & 0xffff) >> 1)

            else:
                self.out.insert(self.end, ('\nInvalid shift instruction at %04x.\n' % self.context[8]))
                self.out.see(self.end)

            self.carry = rs1 & 1

        elif imm == 1 or (imm == 0 and (op2 == 0 or op2 == 1)):
            if opc == 0:
                if imm == 1:
                    rs2 &= 0xff
                self.context[rst] = rs1 & rs2

            elif opc == 1:
                if imm == 1:
                    rs2 &= 0xff
                self.context[rst] = rs1 | rs2

            elif opc == 2:
                self.context[rst] = rs1 ^ rs2

            elif opc == 3:
                if rs1 < rs2:
                    self.context[rst] = 1
                else:
                    self.context[rst] = 0

            elif opc == 4:
                if (rs1 & 0xffff) < (rs2 & 0xffff):
                    self.context[rst] = 1
                else:
                    self.context[rst] = 0

            elif opc == 5:
                if imm == 0 and op2 == 1:
                    self.context[rst] = (rs1 & 0xffff) + (rs2 & 0xffff) + self.carry

                else:
                    self.context[rst] = (rs1 & 0xffff) + (rs2 & 0xffff)

                self.carry = (self.context[rst] & 0x10000) >> 16

            elif opc == 6:
                if imm == 0 and op2 == 1:
                    self.context[rst] = (rs1 & 0xffff) - (rs2 & 0xffff) - self.carry

                else:
                    self.context[rst] = (rs1 & 0xffff) - (rs2 & 0xffff)

                self.carry = (self.context[rst] & 0x10000) >> 16

            elif opc == 8:
                self.context[rst] = rs2

            elif opc == 9:
                self.context[rst] = (self.context[rst] << 8) | (rs2 & 0xff)

            elif opc == 12:
                if imm == 1:
                    if rs1 == 0:
                        pc += rs2
                else:
                    if rs1 == 0:
                        pc = rs2 - 2

            elif opc == 13:
                if imm == 1:
                    if rs1 != 0:
                        pc += rs2
                else:
                    if rs1 != 0:
                        pc = rs2 - 2
            else:
                self.out.insert(self.end, ('\nInvalid computation / branch instruction at %04x.\n' % self.context[8]))
                self.out.see(self.end)

        elif imm == 0 and op2 == 2:
            if opc == 0:
                if rs2 & 0x1:
                    byte = self.memory[(rs2 & 0xffff) >> 1] & 0xff
                else:
                    byte = self.memory[(rs2 & 0xffff) >> 1] >> 8

                if byte > 0x7f:
                    self.context[rst] = byte - 0x100
                else:
                    self.context[rst] = byte

            elif opc == 1:
                if rs2 & 0x1:
                    self.memory[(rs2 & 0xffff) >> 1] = (self.memory[(rs2 & 0xffff) >> 1] & 0xff00) | (rs1 & 0xff)
                else:
                    self.memory[(rs2 & 0xffff) >> 1] = (self.memory[(rs2 & 0xffff) >> 1] & 0x00ff) | ((rs1 & 0xff) << 8)

            elif opc == 4:
                if (rs2 & 0xffff) == 0xf004:  # emulate an input character device (address: 61444)
                    if len(self.terminput) == 0:
                        self.terminput = askstring('Input', 'string val:') + r'\0'

                    result = ord(self.terminput[0])
                    self.terminput = self.terminput[1:]
                    self.context[rst] = result

                elif (rs2 & 0xffff) == 0xf006:  # emulate an input integer device (address: 61446)
                    result = askstring('Input', 'int val:')
                    if result:
                        self.context[rst] = int(result)

                else:
                    self.context[rst] = self.memory[(rs2 & 0xffff) >> 1]

            elif opc == 5:
                if (rs2 & 0xffff) == 0xf000:  # emulate an output character device (address: 61440)
                    self.out.insert(self.end, chr(rs1 & 0xff))
                    self.out.see(self.end)

                elif (rs2 & 0xffff) == 0xf002:  # emulate an output integer device (address: 61442)
                    self.out.insert(self.end, str(rs1))
                    self.out.see(self.end)

                else:
                    self.memory[(rs2 & 0xffff) >> 1] = rs1

            else:
                self.out.insert(self.end, ('\nInvalid load/store instruction at %04x.\n' % self.context[8]))
                self.out.see(self.end)

        else:
            self.out.insert(self.end, ('\nInvalid instruction at %04x.\n' % self.context[8]))
            self.out.see(self.end)

        # increment the program counter
        pc += 2
        self.context[8] = pc

        # fix the stored word to the matching hardware size
        self.context[rst] &= 0xffff

        self.cycles += 1

        # update register labels
        self.refresh_regs()

        return 1

    def newprogram(self):
        self.textasm.delete('1.0', self.end)
        self.textasm.delete('1.0', self.end)

    def openprogram(self):
        name = askopenfilename()
        if name:
            program = open(name, 'r')
            if program:
                program.seek(0)
                self.textasm.delete('1.0', self.end)
                for lin in program:
                    self.textasm.insert(self.end, lin)
                program.close()

    def openadditionalprogram(self):
        name = askopenfilename()
        if name:
            program = open(name, 'r')
            if program:
                program.seek(0)
                self.textasm.insert(self.end, '\n')
                for lin in program:
                    self.textasm.insert(self.end, lin)
                program.close()

    def saveprogram(self):
        name = asksaveasfilename()
        if name:
            program = open(name, 'w')
            if program:
                program.write(self.textasm.get('1.0', 'self.end'))
                program.close()

    def reset(self):
        # clear GPRs
        self.context = [0] * 8

        # set the stack pointer to the last self.memory position
        self.context[7] = len(self.memory) * 2 - 2

        # set pc to zero
        self.context[8] = 0

        # reset breakpoint
        self.machine = self.STOPPED

        self.cycles = 0
        self.refresh_regs()
        self.text_dump.focus()
        self.text_dump.activate(0)
        self.text_dump.see(0)

    def run(self):
        if len(self.memory) > 0:
            if self.machine == self.STOPPED:
                self.machine = self.RUNNING
                self.run_step()
        else:
            showerror('Error', 'No program in self.memory.')

    def run_step(self):
        if self.cycle():
            self.text_dump.focus()
            self.text_dump.activate(self.context[8] >> 1)
            self.text_dump.see(self.context[8] >> 1)

            if self.context[8] == self.context[10]:
                self.out.insert(self.end, ('\nBreakpoint at %04x.\n' % self.context[8]))
                self.out.see(self.end)

            else:
                if self.context[7] < self.context[9]:
                    self.out.insert(self.end, ('\nStack overflow detected at %04x.\n' % self.context[8]))
                    self.out.see(self.end)

                else:
                    if self.machine != self.STOPPED:
                        self.root.after(self.cycle_delay, self.run_step)
        else:
            self.out.insert(self.end, ('\nProgram halted at %04x.\n' % self.context[8]))
            self.out.see(self.end)

    def stop(self):
        self.machine = self.STOPPED

    def step(self):
        if len(self.memory) > 0:
            self.stop()

            if self.cycle():
                self.text_dump.focus()
                self.text_dump.activate(self.context[8] >> 1)
                self.text_dump.see(self.context[8] >> 1)

                if self.context[7] < self.context[9]:
                    self.out.insert(self.end, ('\nStack overflow detected at %04x.\n' % self.context[8]))
                    self.out.see(self.end)
            else:
                self.out.insert(self.end, ('\nProgram halted at %04x.\n' % self.context[8]))
                self.out.see(self.end)
        else:
            showerror('Error', 'No program in self.memory.')

    def refresh_regs(self):
        for i in range(9):
            self.root.reg_label[i].set(self.reg_names[i] + hex(self.context[i]))

        self.root.cycle.set(f'Cycle: {str(self.cycles)}\n')

    def set_breakpoint(self):
        result = askstring('Set breakpoint', 'Program address (hex):')
        if result:
            self.context[10] = int(result, 16)

    def set_cycledelay(self):
        result = askstring('Set machine cycle delay', 'Delay (ms):')
        if result > 0:
            self.cycle_delay = int(result)

    def clear_term(self):
        self.out.delete('1.0', self.end)

    def memdump(self):
        k = 0
        while k < len(self.memory) * 2:
            dump_line = str(hex(k)) + ': '

            l = 0
            while l < 8:
                dump_line = dump_line + hex(self.memory[k / 2 + l]) + ' '
                l += 1

            dump_line += '|'
            l = 0
            while l < 8:
                ch1 = self.memory[k / 2 + l] >> 8
                ch2 = self.memory[k / 2 + l] & 0xff
                if (ch1 >= 32) and (ch1 <= 126):
                    dump_line += chr(ch1)
                else:
                    dump_line += '.'

                if (ch2 >= 32) and (ch2 <= 126):
                    dump_line += chr(ch2)
                else:
                    dump_line += '.'
                l += 1

            dump_line += '|'
            self.mem_dump.insert(self.end, dump_line)
            k += 16

    def build_gui(self):

        self.root.geometry('1000x692+30+30')
        self.root.resizable(0, 0)
        self.root.config(menu=self.menu)

        self.memwindow.title('Memory dump')
        self.memwindow.geometry('600x652+50+50')
        self.memwindow.resizable(0, 0)

        self.mem_dump.configure(yscrollcommand=self.mem_dumpscroll.set)
        self.mem_dump.pack(side=LEFT, fill=BOTH)
        self.mem_dumpscroll.pack(side=LEFT, fill=Y)

        self.menu.add_cascade(label='Program', menu=self.programmenu)

        self.programmenu.add_command(label='New', command=self.newprogram)
        self.programmenu.add_command(label='Load', command=self.openprogram)
        self.programmenu.add_command(label='Load additional file', command=self.openadditionalprogram)
        self.programmenu.add_command(label='Save as', command=self.saveprogram)
        self.programmenu.add_separator()
        self.programmenu.add_command(label='Assemble', command=self.assembler)
        self.programmenu.add_separator()
        self.programmenu.add_command(label='Exit', command=self.root.quit)

        self.menu.add_cascade(label='Machine', menu=self.machine_menu)
        self.machine_menu.add_command(label='Reset', command=self.reset)
        self.machine_menu.add_command(label='Stop', command=self.stop)
        self.machine_menu.add_command(label='Run', command=self.run)
        self.machine_menu.add_command(label='Step', command=self.step)
        self.machine_menu.add_separator()
        self.machine_menu.add_command(label='Set breakpoint', command=self.set_breakpoint)
        self.machine_menu.add_command(label='Set machine cycle delay', command=self.set_cycledelay)
        self.machine_menu.add_command(label='Clear terminal', command=self.clear_term)
        self.machine_menu.add_command(label='Memory dump', command=self.memdump)

        self.topframe.pack()
        self.middleframe.pack()
        self.bottomframe.pack()

        Label(self.topframe, text='Program:', width=46, font=('Courier', 11, 'bold'), anchor=W) \
            .pack(side=LEFT)
        Label(self.topframe, text='Object code / disassembly:', width=28, font=('Courier', 11, 'bold'), anchor=W) \
            .pack(side=LEFT)
        Label(self.topframe, text='Symbol table:', width=22, font=('Courier', 11, 'bold'), anchor=W) \
            .pack(side=LEFT)
        Label(self.topframe, text='Registers:', width=16, font=('Courier', 11, 'bold'), anchor=W) \
            .pack(side=LEFT)

        self.asmxscrollbar.pack(side=BOTTOM, fill=X)
        self.textasm.pack(side=LEFT, fill=BOTH)
        self.asmyscrollbar.pack(side=LEFT, fill=Y)
        self.asmxscrollbar.config(command=self.textasm.xview)
        self.asmyscrollbar.config(command=self.textasm.yview)

        self.text_dump.configure(yscrollcommand=self.textdumpscroll.set)
        self.text_dump.pack(side=LEFT, fill=BOTH)
        self.textdumpscroll.pack(side=LEFT, fill=Y)

        self.textsym.configure(yscrollcommand=self.textsymscroll.set)
        self.textsym.pack(side=LEFT, fill=BOTH)
        self.textsymscroll.pack(side=LEFT, fill=Y)

        self.root.reg_label = []
        for _ in range(9):
            self.root.reg_label.append(StringVar())

        for j in range(9):
            Label(self.middleframe, textvariable=self.root.reg_label[j], width=25, font=('Courier', 11)).pack()

        Label(self.middleframe, text='\nControl:\n', width=25, font=('Courier', 11, 'bold')).pack()

        self.root.cycle = StringVar()
        Label(self.middleframe, textvariable=self.root.cycle, width=25, font=('Courier', 11)).pack()

        self.refresh_regs()

        Button(self.middleframe, text='Reset', width=14, command=self.reset).pack()
        Button(self.middleframe, text='Stop', width=14, command=self.stop).pack()
        Button(self.middleframe, text='Run', width=14, command=self.run).pack()
        Button(self.middleframe, text='Step', width=14, command=self.step).pack()

        self.out.configure(yscrollcommand=self.outscroll.set)
        self.out.pack(side=LEFT, fill=BOTH)
        self.outscroll.pack(side=LEFT, fill=Y)
