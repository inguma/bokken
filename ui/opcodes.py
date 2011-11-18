##      opcodes.py
#       -*- coding: utf-8 -*
#
#       Copyright 2011 David Martínez Moreno <ender@debian.org>
#       This software is not affiliated in any way with Facebook, my current employer.
#
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       at your option) any later version.
#
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

instructions = {
    "ADD <dst>, <src>":"Adds <src> to <dst>.\n<dst> may be a register or memory.\n<src> may be a register, memory or immediate value.",
    "CALL <loc>":"Call a function and return to the next instruction when finished.\n<loc> may be a relative offset from the current location, a register or memory addr.",
    "CMP <dst>, <src>":"Compare <src> with <dst>.\nSimilar to SUB instruction but does not modify the <dst> operand\nwith the result of the subtraction.",
    "DEC <dst>":"Subtract 1 from <dst>.\n<dst> may be a register or memory.",
    "DIV <divisor>":"Divide the EDX:EAX registers (64‐bit combo) by <divisor>.\n<divisor> may be a register or memory.",
    "INC <dst>":"Add 1 to <dst>.\n<dst> may be a register or memory.",
    "JE <loc>":"Jump if Equal (ZF=1) to <loc>.",
    "JGE <loc>":"Jump if Greater or Equal (SF=OF) to <loc>.",
    "JG <loc>":"Jump if Greater (ZF=0 and SF=OF) to <loc>.",
    "JLE <loc>":"Jump is Less or Equal (SF<>OF) to <loc>.",
    "JMP <loc>":"Jump to <loc>. Unconditional.",
    "JNE <loc>":"Jump if Not Equal (ZF=0) to <loc>.",
    "JNZ <loc>":"Jump if Not Zero (ZF=0) to <loc>.",
    "JZ <loc>":"Jump if Zero (ZF=1) to <loc>.",
    "LEA <dst>, <src>":"Load Effective Address.\nGets a pointer to the memory expression <src> and stores it in <dst>.",
    "MOV <dst>, <src>":"Move data from <src> to <dst>.\n<src> may be an immediate value, register, or a memory address.\n<dst> may be either a memory address or a register.\nBoth <src> and <dst> may not be memory addresses.",
    "MUL <src>":"Multiply the EDX:EAX registers (64‐bit combo) by <src>.\n<src> may be a register or memory.",
    "POP <dst>":"Take a 32‐bit value from the stack and store it in <dst>.\nESP is incremented by 4.\n<dst> may be a register, including segment registers, or memory.",
    "PUSH <value>":"Adds a 32‐bit value to the top of the stack.\nDecrements ESP by 4.\n<value> may be a register, segment register, memory or immediate value.",
    "ROL <dst>, <count>":"Bitwise Rotate Left the value in <dst> by <count> bits.\n<dst> may be a register or memory address.\n<count> may be immediate or CL register.",
    "ROR <dst>, <count>":"Bitwise Rotate Right the value in <dst> by <count> bits.\n<dst> may be a register or memory address.\n<count> may be immediate or CL register.",
    "SHL <dst>, <count>":"Bitwise Shift Left the value in <dst> by <count> bits.\nZero bits added to the least significant bits.\n<dst> may be reg. or mem. <count> is imm. or CL.",
    "SHR <dst>, <count>":"Bitwise Shift Right the value in <dst> by <count> bits.\nZero bits added to the least significant bits.\n<dst> may be reg. or mem. <count> is imm. or CL.",
    "SUB <dst>, <src>":"Subtract <src> from <dst>.\n<src> may be immediate, memory or a register.\n<dst> may be memory or a register.\n(src = dst)‐>ZF=1, (src > dst)‐>CF=1, (src < dst)‐>CF=0 and ZF=0",
    "TEST <dst>, <src>":"Performs a logical OR operation but does not modify the value in the <dst> operand.\n(src = dst)‐>ZF=1, (src <> dst)‐>ZF=0.",
    "XCHG <dst, <src>":"Exchange the contents of <src> and <dst>.\nOperands may be register or memory.\nBoth operands may not be memory.",
    "XOR <dst>, <src>":"Bitwise XOR the value in <src> with the value in <dst>, storing the result in <dst>.\n<dst> may be reg or mem and <src> may be reg, mem or imm."
}
