#!/usr/bin/python
import sys
import re


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

    def reset(self):
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

    def generate_assembly(self, program):
        program = self.pass1(program)
        symbols = self.pass2(program)
        return self.pass3(program), symbols

    def pass1(self, program):
        """process pseudo operations"""
        i = 0
        for lin in program:
            flds = [l for l in re.split('[\r\t\n ]', lin) if l]
            if flds:
                if flds[0] == ';':
                    program[i] = '\n'

                elif flds[0] == 'nop':
                    program[i] = '\tand	r0,r0,r0\n'

                elif flds[0] == 'hcf':
                    program[i] = '\thcf	r0,r0,r0\n'

                if len(flds) > 1:
                    parts = str(flds[1]).split(',')
                    if flds[0] == 'not':
                        program[i] = f'\txor	{parts[0]},-1\n'

                    elif flds[0] == 'neg':
                        program[i] = f'\txor	{parts[0]},-1\n'
                        program.insert(i + 1, "\tadd	" + parts[0] + ",1\n")

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
                        if str(parts[1]).isdigit():
                            if (int(parts[1]) < 256) and (int(parts[1]) >= -128):
                                program[i] = f'\tldr	{flds[1]}\n'

                            else:
                                program[i] = f'\tldr	{parts[0]},{str((int(parts[1]) >> 8) & 0xff)}\n'
                                program.insert(i + 1, f'\tldc	{parts[0]},{str(int(parts[1]) & 0xff)}\n')

                        else:
                            program[i] = f'\tldc0	{flds[1]}\n'
                            program.insert(i + 1, f'\tldc1	{flds[1]}\n')

                    elif flds[0] == 'ldb' and len(parts) == 2:
                        if parts[1] not in self.lookup:
                            program[i] = f'\tldc0	at,{parts[1]}\n'
                            program.insert(i + 1, f'\tldc1	at,{parts[1]}\n')
                            program.insert(i + 2, f'\tldb	{parts[0]},r0,at\n')

                        else:
                            program[i] = f'\tldb	{parts[0]},r0,{parts[1]}\n'

                    elif flds[0] == 'stb' and len(parts) == 2:
                        if parts[1] not in self.lookup:
                            program[i] = f'\tldc0	at,{parts[1]}\n'
                            program.insert(i + 1, f'\tldc1	at,{parts[1]}\n')
                            program.insert(i + 2, f'\tstb	r0,{parts[0]},at\n')

                        else:
                            program[i] = f'\tstb	r0,{parts[0]},{parts[1]}\n'

                    elif flds[0] == 'ldw' and len(parts) == 2:
                        if parts[1] not in self.lookup:
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
                        if parts[1] not in self.lookup:
                            if not str(parts[1]).isdigit():
                                program[i] = f'\tldc0	at,{parts[1]}\n'
                                program.insert(i + 1, f'\tldc1	at,{parts[1]}\n')
                                program.insert(i + 2, f'\tbez	r0,{parts[0]},at\n')

                        else:
                            program[i] = f'\tbez	r0,{parts[0]},{parts[1]}\n'

                    elif flds[0] == 'bnz' and len(parts) == 2:
                        if parts[1] not in self.lookup:
                            if not str(parts[1]).isdigit():
                                program[i] = f'\tldc0	at,{parts[1]}\n'
                                program.insert(i + 1, f'\tldc1	at,{parts[1]}\n')
                                program.insert(i + 2, f'\tbnz	r0,{parts[0]},at\n')
                        else:
                            program[i] = f'\tbnz	r0,{parts[0]},{parts[1]}\n'

                    if flds[0] == 'lsrm' and len(parts) == 2 and not str(parts[1]).isdigit():
                        program[i] = f'\tlsr	{parts[0]},{parts[0]},r0\n'
                        program.insert(i + 1, f'\tsub	{parts[1]},1\n')
                        program.insert(i + 2, f'\tbnz	{parts[1]},-6\n')

                    elif flds[0] == 'asrm' and len(parts) == 2 and not str(parts[1]).isdigit():
                        program[i] = f'\tasr	{parts[0]},{parts[0]},r0\n'
                        program.insert(i + 1, f'\tsub	{parts[1] },1\n')
                        program.insert(i + 2, f'\tbnz	{parts[1] },-6\n')

                    elif flds[0] == 'lslm' and len(parts) == 2 and not str(parts[1]).isdigit():
                        program[i] = f'\tadd	{parts[0] },{parts[0]},{parts[0]}\n'
                        program.insert(i + 1, f'\tsub	{parts[1]},1\n')
                        program.insert(i + 2, f'\tbnz	{parts[1]},-6\n')
            i += 1

        return program

    def pass2(self, program):
        """determine addresses for labels and add to the lookup dictionary"""
        pc = 0
        symbols_table = []
        for lin in program:
            flds = [l for l in re.split('[\r\t\n ]', lin) if l]
            if not flds:
                continue

            if lin[0] > ' ':
                symb = flds[0]
                self.lookup[symb] = pc
                symbols_table.append(f'{self.to_hex(pc)} {symb}')
                flds2 = ' '.join(flds[1:])
                if flds2:
                    if flds2[0] == '"' and flds2[-1] == '"':
                        flds2 = lin
                        flds2 = flds2[1:-1]
                        flds2 = flds2.replace(r'\t', '\t')
                        flds2 = flds2.replace(r'\n', '\n')
                        flds2 = flds2.replace(r'\r', '\r')

                        while flds2[0] != '"':
                            flds2 = flds2[1:]

                        flds2 = flds2[1:-1] + '\0'
                        while len(flds2) % 2 != 0:
                            flds2 = flds2 + '\0'

                        pc += len(flds2)
                    else:
                        flds = flds[1:]
                        for _ in flds:
                            pc += 2
            else:
                pc += 2

        return symbols_table

    def pass3(self, program):
        """translate assembly code and symbols to machine code"""
        stream = []
        args = sys.argv[1] if sys.argv[1:] else ''
        debug = True if args == 'debug' else False
        pc = 0

        for lin in program:
            flds = [l for l in re.split('[\r\t\n ]', lin) if l]
            if len(lin) == 0:
                continue

            if lin[0] > ' ':
                flds = flds[1:]

            if not flds:
                if not debug:
                    continue
                else:
                    stream.append(lin)

            try:
                flds2 = ' '.join(flds)
                if flds2[0] == '"' and flds2[-1] == '"':
                    flds2 = lin
                    flds2 = flds2[1:-1]
                    flds2 = flds2.replace(r'\t', '\t')
                    flds2 = flds2.replace(r'\n', '\n')
                    flds2 = flds2.replace(r'\r', '\r')

                    while flds2[0] != '"':
                        flds2 = flds2[1:]

                    flds2 = flds2[1:] + '\0'
                    while (len(flds2) % 2) != 0:
                        flds2 = flds2 + '\0'

                    flds3 = ''

                    while True:
                        flds3 += str((int(ord(flds2[0])) << 8) | int(ord(flds2[1]))) + ' '
                        flds2 = flds2[2:]

                        if flds2 == '':
                            break

                    flds3 = [l for l in re.split('[\r\t\n ]', flds3) if l]
                    instruction = self.assemble(flds3)

                    if debug:
                        stream.append('%04x %s    %s' % (pc, self.to_hex(instruction), lin))
                    else:
                        stream.append('%04x %s' % (pc, self.to_hex(instruction)))

                    pc += 2

                    flds3 = flds3[1:]
                    for _ in flds3:
                        instruction = self.assemble(flds3)
                        stream.append('%04x %s' % (pc, self.to_hex(instruction)))
                        pc = pc + 2
                        flds3 = flds3[1:]
                else:
                    if flds[0] not in self.codes:
                        data = self.assemble(flds)

                        if debug:
                            stream.append('%04x %s %s' % (pc, self.to_hex(data), lin))
                        else:
                            stream.append('%04x %s' % (pc, self.to_hex(data)))

                        pc += 2

                        flds = flds[1:]
                        for _ in flds:
                            data = self.assemble(flds)
                            stream.append('%04x %s' % (pc, self.to_hex(data)))
                            pc += 2
                            flds = flds[1:]
                    else:
                        instruction = self.assemble(flds)

                        if debug:
                            stream.append('%04x %s    %s' % (pc, self.to_hex(instruction), lin))
                        else:
                            stream.append('%04x %s' % (pc, self.to_hex(instruction)))

                        pc += 2

            except:
                stream.append(f'**** ????    {lin[:-1]}')

        return stream

    def assemble(self, flds):
        """assemble instruction to machine code"""
        opval = self.codes.get(flds[0])
        symb = self.lookup.get(flds[0])
        if symb is not None:
            return symb
        else:
            if opval is None:
                return int(flds[0], 0)

            parts = str(flds[1]).split(',')
            if len(parts) == 2:
                parts = [0, parts[0], parts[1]]
                if flds[0] == 'ldc0':
                    return opval | 0x0800 | (self.getval(parts[1]) << 8) | ((self.getval(parts[2]) >> 8) & 0xff)
                else:
                    return opval | 0x0800 | (self.getval(parts[1]) << 8) | (self.getval(parts[2]) & 0xff)

            if len(parts) == 3:
                parts = [0, parts[0], parts[1], parts[2]]
                return opval | (self.getval(parts[1]) << 8) | (self.getval(parts[2]) << 5) | (self.getval(parts[3]) << 2)

    def getval(self, s):
        """return numeric value of a symbol or number"""
        return 0 if not s else int(s, 0) if s not in self.lookup else self.lookup[s]

    @staticmethod
    def to_hex(n):
        if hex(n)[0] == '-':
            return hex(n)[3:].rjust(4, '0')
        else:
            return hex(n)[2:].rjust(4, '0')


if __name__ == '__main__':
    import pathlib
    with open(str((pathlib.Path(__file__).parent.parent / 'examples' / 'ninetoone.asm').absolute())) as f:
        x = Assembler()
        print('\n'.join(x.generate_assembly(f.read().split('\n'))))

