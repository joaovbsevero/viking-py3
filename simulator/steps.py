

class Assembler:
    def __init__(self):

        self.codes = {
            'and': 0x0000, 'or': 0x1000, 'xor': 0x2000, 'slt': 0x3000,
            'sltu': 0x4000, 'add': 0x5000, 'adc': 0x5001, 'sub': 0x6000,
            'sbc': 0x6001, 'ldr': 0x8000, 'ldc': 0x9000, 'lsr': 0xa000,
            'asr': 0xa001, 'ror': 0xa002, 'ldb': 0x0002, 'stb': 0x1002,
            'ldw': 0x4002, 'stw': 0x5002, 'bez': 0xc000, 'bnz': 0xd000,
            'hcf': 0x0003, 'ldc0': 0x9000, 'ldc1': 0x9000
        }
        self.lookup = {
            'r0': 0, 'r1': 1, 'r2': 2, 'r3': 3,
            'r4': 4, 'r5': 5, 'r6': 6, 'r7': 7,
            'at': 0, 'sr': 5, 'lr': 6, 'sp': 7
        }
        self.reverse_lookup = {

        }

    def pass1(self, program):
        """"process pseudo operations"""

        for i, line in enumerate(program):
            flds = line.split() if line.__contains__(' ') else line.split('\t')
            if flds:
                if flds[0] == ';':
                    program[i] = '\n'

                elif flds[0] == 'nop':
                    program[i] = '\tand	r0,r0,r0\n'

                elif flds[0] == 'hcf':
                    program[i] = '\thcf	r0,r0,r0\n'

                elif len(flds) > 1:
                    parts = flds[1].split(',')

                    if flds[0] == 'not':
                        program[i] = f'\txor	{parts[0]},-1\n'

                    elif flds[0] == 'neg':
                        program[i] = f'\txor	{parts[0]},-1\n'
                        program.insert(i + 1, f'\tadd	{parts[0]},1\n')

                    elif flds[0] == 'mov':
                        program[i] = f'\tand	{parts[0]},{parts[1]},{parts[1]}\n'

                    elif flds[0] == 'lsr':
                        program[i] = f'\tlsr	{parts[0]},{parts[1]},r0\n'

                    elif flds[0] == 'asr':
                        program[i] = f'\tasr	{parts[0]},{parts[1]},r0\n'

                    elif flds[0] == 'ror':
                        program[i] = f'\tror	{parts[0]},{parts[1]},r0\n'

                    elif flds[0] == 'lsl':
                        program[i] = f'\tadd	{parts[0]},{parts[1]},{parts[1]}\n'

                    elif flds[0] == 'rol':
                        program[i] = f'\tadc	{parts[0]},{parts[1]},{parts[1]}\n'

                    elif flds[0] == 'ldi':
                        if parts[1].isdigit():
                            if 256 > int(parts[1]) >= -128:
                                program[i] = f'\tldr	{flds[1]}\n'

                            else:
                                program[i] = f'\tldr	{parts[0]},{(int(parts[1]) >> 8) & 0xff}\n'
                                program.insert(i + 1, f'\tldc	{parts[0]},{int(parts[1]) & 0xff}\n')

                        else:
                            program[i] = f'\tldc0	{flds[1]}\n'
                            program.insert(i + 1, f'\tldc1	{flds[1]}\n')

                    elif flds[0] == 'ldb' and len(parts) == 2:
                        if self.lookup[parts[1]] is None:
                            program[i] = f'\tldc0	at,{parts[1]}\n'
                            program.insert(i + 1, f'\tldc1	at,{parts[1]}\n')
                            program.insert(i + 2, f'\tldb	{parts[0]},r0,at\n')

                        else:
                            program[i] = f'\tldb	{parts[0]},r0,{parts[1]}\n'

                    elif flds[0] == 'stb' and len(parts) == 2:
                        if self.lookup[parts[1]] is None:
                            program[i] = f'\tldc0	at,{parts[1]}\n'
                            program.insert(i + 1, f'\tldc1	at,{parts[1]}\n')
                            program.insert(i + 2, f'\tstb	r0,{parts[0]},at\n')

                        else:
                            program[i] = f'\tstb	r0,{parts[0]},{parts[1]}\n'

                    elif flds[0] == 'ldw' and len(parts) == 2:
                        if self.lookup.get(parts[1]) is None:
                            program[i] = f'\tldc0	at,{parts[1]}\n'
                            program.insert(i + 1, f'\tldc1	at,{parts[1]}\n')
                            program.insert(i + 2, f'\tldw	{parts[0]},r0,at\n')

                        else:
                            program[i] = f'\tldw	{parts[0]},r0,{parts[1]}\n'

                    elif flds[0] == 'stw' and len(parts) == 2:
                        if self.lookup.get(parts[1]) is None:
                            program[i] = f'\tldc0	at,{parts[1]}\n'
                            program.insert(i + 1, f'\tldc1	at,{parts[1]}\n')
                            program.insert(i + 2, f'\tstw	r0,{parts[0]},at\n')

                        else:
                            program[i] = f'\tstw	r0,{parts[0]},{parts[1]}\n'

                    elif flds[0] == 'bez' and len(parts) == 2:
                        if self.lookup.get(parts[1]) is None:
                            if not parts[1].isdigit():
                                program[i] = f'\tldc0	at,{parts[1]}\n'
                                program.insert(i + 1, f'\tldc1	at,{parts[1]}\n')
                                program.insert(i + 2, f'\tbez	r0,{parts[0]},at\n')
                        else:
                            program[i] = f'\tbez	r0,{parts[0]},{parts[1]}\n'

                    elif flds[0] == 'bnz' and len(parts) == 2:
                        if self.lookup[parts[1]] is None:
                            if not parts[1].isdigit():
                                program[i] = f'\tldc0	at,{parts[1]}\n'
                                program.insert(i + 1, f'\tldc1	at,{parts[1]}\n')
                                program.insert(i + 2, f'\tbnz	r0,{parts[0]},at\n')
                        else:
                            program[i] = f'\tbnz	r0,{parts[0]},{parts[1]}\n'

                    elif flds[0] == 'lsrm' and len(parts) == 2 and not parts[1].isdigit():
                        program[i] = f'\tlsr	{parts[0]},{parts[0]},r0\n'
                        program.insert(i + 1, f'\tsub	{parts[1]},1\n')
                        program.insert(i + 2, f'\tbnz	{parts[1]},-6\n')

                    elif flds[0] == 'asrm' and len(parts) == 2 and not parts[1].isdigit():
                        program[i] = f'\tasr	{parts[0]},{parts[0]},r0\n'
                        program.insert(i + 1, f'\tsub	{parts[1]},1\n')
                        program.insert(i + 2, f'\tbnz	{parts[1]},-6\n')

                    elif flds[0] == 'lslm' and len(parts) == 2 and not parts[1].isdigit():
                        program[i] = f'\tadd	{parts[0]},{parts[0]},{+ parts[0]}\n'
                        program.insert(i + 1, f'\tsub	{parts[1]},1\n')
                        program.insert(i + 2, f'\tbnz	{parts[1]},-6\n')

    def pass2(self, program):
        """determine addresses for labels and add to the lookup dictionary"""

        pc = 0
        for line in program:
            flds = line.split() if line.__contains__(' ') else line.split('\t')

            if not flds:
                continue

            if line[0] > ' ':
                symb = flds[0]
                self.lookup[symb] = pc

                # =========== WHAT IN HELL IS 'END' ??? ==========
                # ====== FIX THE TEXTSYM IN DIFFERENT FILES ======
                # textsym.insert(f'{END} {hex(pc)} {symb}')

                flds2 = ' '.join(flds[1:])
                if flds2:
                    if flds2.startswith('"') and flds2.endswith('"'):
                        flds2 = line
                        flds2 = flds2[1:-1]
                        flds2 = flds2.replace(r'\t', '\t')
                        flds2 = flds2.replace(r'\n', '\n')
                        flds2 = flds2.replace(r'\r', '\r')

                        while flds2[0] != '"':
                            flds2 = flds2[1:]

                        flds2 = flds2[1:] + '\0'
                        while (len(flds2) % 2) != 0:
                            flds2 = flds2 + '\0'

                        pc += len(flds2)

                    else:
                        flds = flds[1:]
                        for _ in flds:
                            pc += 2
            else:
                pc += 2

    def pass3(self, program):
        """translate assembly code and symbols to machine code"""
        pc = 0
        code = ''

        for line in program:
            if line == '':
                continue

            flds = line.split() if line.__contains__(' ') else line.split('\t')

            if line[0] > ' ':
                # drop symbol if there is one
                flds = flds[1:]

            if not flds:
                continue

            try:
                flds2 = ' '.join(flds)

                if flds2[0] == '"' and flds2[-1] == '"':
                    flds2 = line
                    flds2 = flds2[1:-1]
                    flds2 = flds2.replace(r'\t', '\t')
                    flds2 = flds2.replace(r'\n', '\t')
                    flds2 = flds2.replace(r'\t', '\t')

                    while flds2[0] != '"':
                        flds2 = flds2[1:]

                    flds2 = flds2[1:] + r'\0'
                    while (len(flds2) % 2) != 0:
                        flds2 = flds2 + r'\0'

                    flds3 = ''
                    while True:
                        flds3 += str((ord(flds2[0]) << 8) | ord(flds2[1])) + ' '
                        flds2 = flds2[2:]
                        if flds2 == '':
                            break

                    flds3 = flds3.split() if flds3.__contains__(' ') else flds3.split('\t')
                    instruction = self.assemble(flds3)
                    code += f'{str(pc)[2:].rjust(4, "0")} {hex(instruction)}'
                    pc += 2
                    flds3 = flds3[1:]

                    while flds3:
                        instruction = self.assemble(flds3)
                        code += f'{str(pc)[2:].rjust(4, "0")} {hex(instruction)}'
                        pc += 2
                        flds3 = flds3[1:]

                else:

                    if self.codes[flds[0]] is None:
                        data = self.assemble(flds)
                        code += f'{str(pc)[2:].rjust(4, "0")} {hex(data)}'
                        pc += 2

                        flds = flds[1:]
                        while flds:
                            data = self.assemble(flds)
                            code += f'{str(pc)[2:].rjust(4, "0")} {hex(data)}'
                            pc += 2
                            flds = flds[1:]
                    else:
                        instruction = self.assemble(flds)
                        code += f'{str(pc)[2:].rjust(4, "0")} {hex(instruction)}'
                        pc += 2
            except:
                code += f'???? {line}'

        return code

    def assemble(self, flds):
        """assemble instruction to machine code"""

        opval = self.codes[flds[0]]
        symb = self.lookup[flds[0]]

        if symb is not None:
            return symb

        else:

            # just a number (prefix can be 0x.. 0o.. 0b..)
            if opval is None:
                return int(flds[0], 0)

            # break opcode fields
            parts = flds[1].split(',')
            if len(parts) == 2:
                parts = [0, parts[0], parts[1]]

                # ldc0 .. ldc1 are special steps of ldc
                if flds[0] == 'ldc0':
                    return opval | 0x0800 | (self.getval(parts[1]) << 8) | ((self.getval(parts[2]) >> 8) & 0xff)

                else:
                    return opval | 0x0800 | (self.getval(parts[1]) << 8) | (self.getval(parts[2]) & 0xff)

            if len(parts) == 3:
                parts = [0, parts[0], parts[1], parts[2]]
                return opval | (self.getval(parts[1]) << 8) | (self.getval(parts[2]) << 5) | (self.getval(parts[3]) << 2)

    def getval(self, s):
        """return numeric value of a symbol or number"""
        if not s:
            # empty symbol - zero
            return 0

        # get value or None if not in lookup
        a = self.lookup[s]
        if a is None:
            # just a number (prefix can be 0x.. 0o.. 0b..)
            return int(s, 0)
        else:
            return a
