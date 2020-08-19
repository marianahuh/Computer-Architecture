"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

SP = 7

# greater gtf == > flag, ltf == < flag, etf == = flag
ltf = 0b100
gtf = 0b010
etf = 0b001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.running = True
        self.flags = 0b00000001
        self.branch_table = {
            HLT: self.HLT_op,
            LDI: self.LDI_op,
            PRN: self.PRN_op,
            ADD: self.ADD_op,
            MUL: self.MUL_op,
            PUSH: self.PUSH_op,
            POP: self.POP_op,
            CALL: self.CALL_op,
            RET: self.RET_op,
            CMP: self.CMP_op,
            JMP: self.JMP_op,
            JEQ: self.JEQ_op,
            JNE: self.JNE_op
        }
    # accept the address to read and return the value stored there

    def ram_read(self, MAR):
        return self.ram[MAR]
    # accept a value to write, and the address to write it to

    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""
        address = 0
        with open(sys.argv[1]) as file:
            for line in file:
                # Ignore comments
                comment_split = line.split("#")
                num = comment_split[0].strip()
                if num == "":
                    continue  # Ignore blank lines
                instruction = int(num, 2)  # Base 10, but ls-8 is base 2
                self.ram[address] = instruction
                address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # multiply the values in two registers together and store the result in reg_a
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        # Compare the values in two registers
        elif op == "CMP":
            # if reg_a is less than reg_b,
            if self.reg[reg_a] < self.reg[reg_b]:
                # set the Less-than L flag to 1, otherwise set it to 0
                self.flags = ltf
            # If reg_a is greater than reg_b,
            elif self.reg[reg_a] > self.reg[reg_b]:
                # set the Greater-than G flag to 1, otherwise set it to 0
                self.flags = gtf
            # otherwise, set the Equal E flag to 1, otherwise set it to 0
            else:
                self.flags = etf
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    # halt the cpu and exit the emulator

    def HLT_op(self, oper_a, oper_b):
        self.running = False

    # set the value of a register to an integer
    def LDI_op(self, oper_a, oper_b):
        self.reg[oper_a] = oper_b
        self.pc += 3

    # print numeric value stored in the given reg and to the console the decimal
    # int val stored in the given register
    def PRN_op(self, oper_a, oper_b):
        print(self.reg[oper_a])
        self.pc += 2

    # add the value in two registers and store the result in reg A handled by ALU
    def ADD_op(self, oper_a, oper_b):
        self.alu('ADD', oper_a, oper_b)
        self.pc += 3

    # multiply - handled by ALU
    def MUL_op(self, oper_a, oper_b):
        self.alu('MUL', oper_a, oper_b)
        self.pc += 3

    # push the value in the given register on the stack
    def PUSH_op(self, oper_a, oper_b):
        self.push(self.reg[oper_a])
        self.pc += 2

    # pop the value at the top of the stack into the given register
    def POP_op(self, oper_a, oper_b):
        self.reg[oper_a] = self.pop()
        self.pc += 2

    # calls a subroutine at the address stored in the register
    def CALL_op(self, oper_a, oper_b):
        self.reg[SP] -= 1
        self.ram[self.reg[SP]] = self.pc + 2
        update_reg = self.ram[self.pc + 1]
        self.pc = self.reg[update_reg]

    # return from the subroutine. Pop the value from the top of the stack and
    # store it in the PC
    def RET_op(self, oper_a, oper_b):
        self.pc = self.ram[self.reg[SP]]
        self.reg[SP] += 1

    # handled by ALU
    def CMP_op(self, oper_a, oper_b):
        self.alu('CMP', oper_a, oper_b)
        self.pc += 3

    # jump to the address stored in the given register
    def JMP_op(self, oper_a, oper_b):
        # set the PC to the address stored in the given register
        self.pc = self.reg[oper_a]

    def JEQ_op(self, oper_a, oper_b):
        # if equal flag is set (true),
        if self.flags & etf:
            # jump to the address stored in the given register
            self.pc = self.reg[oper_a]
        else:
            self.pc += 2

    def JNE_op(self, oper_a, oper_b):
        # if E flag is false,
        if not self.flags & etf:
            # jump to the address stored in the given register
            self.pc = self.reg[oper_a]
        else:
            self.pc += 2

    # push the value in the given register on the stack
    def push(self, value):
        # decrement the SP
        self.reg[SP] -= 1
        # copy the value in the given register to the address pointed to by SP
        self.ram_write(value, self.reg[7])

    # pop the value at the top of the stack into the given register
    def pop(self):
        # copy the value from the address pointed to by SP to the given register
        value = self.ram_read(self.reg[7])
        # increment SP
        self.reg[SP] += 1
        return value

    def run(self):
        """Run the CPU."""
        while self.running:
            IR = self.ram_read(self.pc)
            oper_a = self.ram_read(self.pc + 1)
            oper_b = self.ram_read(self.pc + 2)
            if int(bin(IR), 2) in self.branch_table:
                self.branch_table[IR](oper_a, oper_b)
            else:
                raise Exception(
                    f'Invalid {IR}, not in branch table \t {list(self.branch_table.keys())}')
