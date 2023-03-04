try:
    import time # pip install times
    import argparse #pip install argparse
    import keyboard # pip install keyboard
except ImportError as error:
    print(error)
    exit()

class Performances:
    """
    A class used to determine some statistics about the simulation

    Attributes
    ----------
        start : float
            a float to store the starting time
        stop : float
            a float to store the ending time
        elapsed : float
            a float to store the elapsed time
        cycles : int
            an int to store the number of machine cycles

    Methods
    -------
        timerStart()
            store the starting time in start attribute
        
        timerStop()
            store the ending time in stop attribute and store the elsapsed time in elapsed attribute

        cycleUpdate()
            updates the number of machine cycles used for each instruction

            Parameters
            ----------
            inst: int
                inst
    """
    def __init__(self):
        self.cycles = 1

    def cycleUpdate(self, inst):
        if inst in [3, 4, 15, 16, 17]:
            self.cycles += 2
        else:
            self.cycles += 1
    
    def timerStart(self):
        self.start = time.perf_counter()

    def timerStop(self):
        self.stop = time.perf_counter()
        self.elapsed = self.stop - self.start

class Cache:
    """
    A class used to represent a cache memory (under development)

    """
    def __init__(self, nbSets, blockLines, blockSize, nbAddr, memory):
        self.wordsNb = blockSize*8/nbAddr
        self.setsNb = nbSets
        self.linesNb = blockLines
        self.wordSize = nbAddr
        self.memory = memory
        self.sets = []

        for i in range(0, self.setsNb):
            self.sets.append()

    def readCache(self, addr):
        pass

    def writeCache(self, addr, data):
        pass

    def writeThrough(self, addr, data):
        pass

class DataMemory:
    """
    A class used to represent a memory area to store data

    Attributes
    ----------
        memorySlots : int table
            array that represents a memory area in which data are stored

        num_data_mem_cells : int
            size of the memory area

    Methods
    -------
        readDataMemory(addr)
            reads the memory area at the indicated address

            Parameters
            ----------
            addr: int
                data address

        writeDataMemory(addr, value)
            writes a data to the indicated address

            Parameters
            ----------
            addr: int
                data address

            value : int
                data to store in memory

        showDataMemory()
            show all elements of the memory area

        twoComplement(nb)
            calculate the two's complement of the input parameter

            Parameters
            ----------
            nb: int
                nb to process

            Returns
            -------
            nb: int
                the two's complement of nb
    """
    def __init__(self, num_data_mem_cells):
        self.memorySlots = []
        self.num_data_mem_cells = num_data_mem_cells

        for i in range(0, self.num_data_mem_cells):
            self.memorySlots.append(0)
    
    def readDataMemory(self, addr):
        return self.memorySlots[addr]
    
    def writeDataMemory(self, addr, value):
        self.memorySlots[addr] = value

    def showDataMemory(self):
        print("DATA MEMORY : ")
        pc = 0
        for i in self.memorySlots:
            if len('{:b}'.format(i)) > 17:
                print("\nOverflow on SLOT" + str(pc) + " ! (32 bits signed)")
                exit()
            else:
                print("%04x" % self.twosComplement(i) + " ", end='')
            pc+=1
        print("\n")

    def twosComplement(self, nb):
        if nb>>15:
            nb=((nb) & 0xFFFF)
        return nb

class VirtualMachine:
    """
    A class used to represent a memory area to store data

    Attributes
    ----------
        running : bool
            determine if the virtual machine is running or not

        num_regs : int
            the number of registers to use

        regs : int table
            table containing the registers

        address : int table
            table containing all the addresses

        program : string table
            table containing all the instructions in machine language

        pc : int
            increments with each instruction performed

        inputFile: string
            name of the file where the program is located in machine language

        step_by_step: bool
            defines the operation of the virtual machine (automatic or manual)


    Methods
    -------
        run()
            represents the main program to be followed by calling the corresponding methods

        loadAddrInst()
            load the program in machine language in the "program" attribute

        initRegs(init_regs_file)
            initialize registers to the values of the initialization file

            Parameter
            ---------

            init_regs_file : string
                name of the initialization file

        decode(instr)
            decodes the instruction in machine language to extract the register value and the associated command
            
            Parameter
            -----------
                instr : int
                    value of the instruction to decode

        eval()
            displays the decoded command with the updated register value 

        showRegs()
            displays the value of the registers at each instruction execution. Checks if there is no overflow.  

        showStatistics()
            displays the statistics at the end of the simulation

        loadInFile()
            loads a report of the simulation into a file
    """
    def __init__(self, inputFile, root, num_regs, num_data_mem_cells, init_regs_file, step_by_step = False):
        self.running = True
        self.num_regs = num_regs
        self.regs = []
        self.address = []
        self.program = []
        self.pc = 0
        self.inputFile = inputFile
        self.step_by_step = step_by_step

        if root == None:
            self.outputFile = "vm_" + time.strftime("%Y_%m_%d-%H_%M_%S") + ".txt"
        else:
            self.outputFile = str(root) + "/vm_" + time.strftime("%Y_%m_%d-%H_%M_%S") + ".txt"

        self.dataMemory = DataMemory(num_data_mem_cells)
        self.performances = Performances()

        self.loadAddrInst()
        self.initRegs(init_regs_file)
    
    def run(self):
        self.performances.timerStart()
        while(self.running):
            self.currentInst = self.program[self.pc]
            self.currentAddr = self.address[self.pc]

            print("Next instruction =>")
            print("PC : " + str(self.pc) + ", inst : " + self.currentInst + ", Machine cycle : " + str(self.performances.cycles))

            self.currentInst = int(self.currentInst, 16)

            self.decode(self.currentInst)
            self.eval()
            self.showRegs()

            self.dataMemory.showDataMemory()

            self.pc += 1

            if(self.step_by_step):
                keyboard.wait('right')

        self.performances.timerStop()

        self.showStatistics()
        self.loadInFile()

    def loadAddrInst(self):
        file = open(self.inputFile, "r")
        lines = file.readlines()
        cnt = 0
        for line in lines:
            parsed = line.split(" ")
            self.address.append(parsed[0])

            if len(lines) != cnt+1:
                self.program.append(parsed[1][:-1])
            else:
                self.program.append(parsed[1])
            cnt += 1

    def initRegs(self, init_regs_file):
        if(init_regs_file is not None):
            file = open(init_regs_file, "r")
            lines = file.readlines()
            if(len(lines) != self.num_regs):
                print("You have declared " + str(self.num_regs) +" registers but you initialized " + str(len(lines)) + " !")
                print("Please check the -r, -ri options or your register initialization file")
                exit()
            for line in lines:
                self.regs.append(int(line))
        else:  
            for i in range(0, self.num_regs):
                self.regs.append(0)
        
    def decode(self, instr):
        self.instrNum = (instr & 0xF8000000) >> 27

        if self.instrNum == 15:
            self.imm      = (instr & 0x4000000) >> 26
            self.reg1     = (instr & 0x3FFFFE0) >>  5
            self.reg2     = (instr & 0x1F)

        elif self.instrNum == 16 or self.instrNum == 17:
            self.reg1     = (instr & 0x7C00000) >>  22
            self.reg2     = (instr & 0x3FFFFF)

        elif self.instrNum == 18:
            self.reg1     = (instr & 0x7FFFFFF)

        else:
            self.reg1     = (instr & 0x7C00000) >>  22
            self.imm      = (instr & 0x200000) >> 21
            self.reg2     = (instr & 0x1FFFE0) >>  5
            self.reg3     = (instr & 0x1F)

    def eval(self):
        print("Command : ", end='')

        if self.instrNum == 1:
            if(self.imm):
                print("add " + "r" + str(self.reg1) + ", r" + str(self.reg2) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] + self.regs[self.reg2]
            else:
                print("add " + "r" + str(self.reg1) + ", " + str(self.twosComplement(self.reg2)) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] + self.reg2

        elif self.instrNum == 2:
            if(self.imm):
                print("sub " + "r" + str(self.reg1) + ", r" + str(self.reg2) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] - self.regs[self.reg2]
            else:
                print("sub " + "r" + str(self.reg1) + ", " + str(self.twosComplement(self.reg2)) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] - self.reg2
        
        elif self.instrNum == 3:
            if(self.imm):
                print("mul " + "r" + str(self.reg1) + ", r" + str(self.reg2) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] * self.regs[self.reg2]
            else:
                print("mult " + "r" + str(self.reg1) + ", " + str(self.twosComplement(self.reg2)) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] * self.reg2
        
        elif self.instrNum == 4:
            if(self.imm):
                print("div " + "r" + str(self.reg1) + ", r" + str(self.reg2) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] // self.regs[self.reg2]
            else:
                print("div " + "r" + str(self.reg1) + ", " + str(self.twosComplement(self.reg2)) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] // self.reg2

        elif self.instrNum == 5:
            if(self.imm):
                print("and " + "r" + str(self.reg1) + ", r" + str(self.reg2) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] and self.regs[self.reg2]
            else:
                print("and " + "r" + str(self.reg1) + ", " + str(self.twosComplement(self.reg2)) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] and self.reg2

        elif self.instrNum == 6:
            if(self.imm):
                print("or " + "r" + str(self.reg1) + ", r" + str(self.reg2) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] or self.regs[self.reg2]
            else:
                print("or " + "r" + str(self.reg1) + ", " + str(self.twosComplement(self.reg2)) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] or self.reg2

        elif self.instrNum == 7:
            if(self.imm):
                print("xor " + "r" + str(self.reg1) + ", r" + str(self.reg2) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] ^ self.regs[self.reg2]
            else:
                print("xor " + "r" + str(self.reg1) + ", " + str(self.twosComplement(self.reg2)) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] ^ self.reg2

        elif self.instrNum == 8:
            if(self.imm):
                print("shl " + "r" + str(self.reg1) + ", r" + str(self.reg2) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] << self.regs[self.reg2]
            else:
                print("shl " + "r" + str(self.reg1) + ", " + str(self.twosComplement(self.reg2)) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] << self.reg2

        elif self.instrNum == 9:
            if(self.imm):
                print("shr " + "r" + str(self.reg1) + ", r" + str(self.reg2) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] >> self.regs[self.reg2]
            else:
                print("shr " + "r" + str(self.reg1) + ", " + str(self.twosComplement(self.reg2)) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.regs[self.reg1] >> self.reg2

        elif self.instrNum == 10:
            if(self.imm):
                print("slt " + "r" + str(self.reg1) + ", r" + str(self.reg2) + ", r" + str(self.reg3))
                if self.regs[self.reg1] <= self.regs[self.reg2]:
                    self.regs[self.reg3] = 1
                else:
                    self.regs[self.reg3] = 0
            else:
                print("slt " + "r" + str(self.reg1) + ", " + str(self.twosComplement(self.reg2)) + ", r" + str(self.reg3))
                if self.regs[self.reg1] <= self.reg2:
                    self.regs[self.reg3] = 1
                else:
                    self.regs[self.reg3] = 0
        
        elif self.instrNum == 11:
            if(self.imm):
                print("sle " + "r" + str(self.reg1) + ", r" + str(self.reg2) + ", r" + str(self.reg3))
                if self.regs[self.reg1] <= self.regs[self.reg2]:
                    self.regs[self.reg3] = 1
                else:
                    self.regs[self.reg3] = 0
            else:
                print("sle " + "r" + str(self.reg1) + ", " + str(self.twosComplement(self.reg2)) + ", r" + str(self.reg3))
                if self.regs[self.reg1] <= self.reg2:
                    self.regs[self.reg3] = 1
                else:
                    self.regs[self.reg3] = 0
        
        elif self.instrNum == 12:
            if(self.imm):
                print("seq " + "r" + str(self.reg1) + ", r" + str(self.reg2) + ", r" + str(self.reg3))
                if self.regs[self.reg1] == self.regs[self.reg2]:
                    self.regs[self.reg3] = 1
                else:
                    self.regs[self.reg3] = 0
            else:
                print("seq " + "r" + str(self.reg1) + ", " + str(self.twosComplement(self.reg2)) + ", r" + str(self.reg3))
                if self.regs[self.reg1] == self.reg2:
                    self.regs[self.reg3] = 1
                else:
                    self.regs[self.reg3] = 0

        elif self.instrNum == 13: #load
            if(self.imm):
                print("load " + "r" + str(self.reg1) + ", r" + str(self.reg2) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.dataMemory.readDataMemory(self.regs[self.reg1] + self.regs[self.reg2])
            else:
                print("load " + "r" + str(self.reg1) + ", " + str(self.twosComplement(self.reg2)) + ", r" + str(self.reg3))
                self.regs[self.reg3] = self.dataMemory.readDataMemory(self.regs[self.reg1] + self.reg2)

        elif self.instrNum == 14: #store
            if(self.imm):
                print("store " + "r" + str(self.reg1) + ", r" + str(self.reg2) + ", r" + str(self.reg3))
                self.dataMemory.writeDataMemory(self.regs[self.reg1] + self.regs[self.reg2] ,self.regs[self.reg3])
            else:
                print("store " + "r" + str(self.reg1) + ", " + str(self.twosComplement(self.reg2)) + ", r" + str(self.reg3))
                self.dataMemory.writeDataMemory(self.regs[self.reg1] + self.reg2 ,self.regs[self.reg3])

        elif self.instrNum == 15: #jmp
            if(self.imm):
                print("jmp " + "r" + str(self.reg1) + ", r" + str(self.reg2))
                self.regs[self.reg2] = self.pc + 1
                self.pc = self.regs[self.reg1] - 1
            else:
                print("jmp " + str(self.twosComplement(self.reg1)) + ", r" + str(self.reg2))
                self.regs[self.reg2] = self.pc + 1
                self.pc = self.reg1 - 1

        elif self.instrNum == 16: #braz
            print("braz " + "r" + str(self.reg1) + ", " + str(hex(self.reg2)))
            if self.regs[self.reg1] == 0:
                self.pc = self.reg2 - 1
            else:
                pass

        elif self.instrNum == 17: #branz
            print("branz " + "r" + str(self.reg1) + ", " + str(hex(self.twosComplement(self.reg2))))
            if self.regs[self.reg1] != 0:
                self.pc = self.reg2 - 1
            else:
                pass

        elif self.instrNum == 18: #scall
            print("scall " + str(self.reg1))
            if int(self.reg1) == 0:
                self.regs[1] = int(input("Enter a value for r1 : "))
            else:
                print("r1 = " + str(self.regs[1]) + "(10) ," + str(hex(self.regs[1])) + ("(16)"))

        elif self.instrNum == 0: #stop
            print("stop")
            self.running = False

        else:
            print("Undefinied command")
            exit()

        print("")
        self.regs[0] = 0
        self.performances.cycleUpdate(self.instrNum)

    def showRegs(self):
        print("REGISTERS : ")
        pc = 0
        for i in self.regs:
            if len('{:b}'.format(i)) > 17:
                print("\nOverflow on R" + str(pc) + " ! (32 bits signed)")
                exit()
            else:
                print("%04x" % self.twosComplement(i) + " ", end='')
            pc+=1
        print("\n")

    def twosComplement(self, nb):
        if nb>>15:
            nb=((nb) & 0xFFFF)
        return nb

    def showStatistics(self):
        print("Some statistics :")
        print("Simulation duration : " + str(round(self.performances.elapsed, 3)) + " second(s)")
        print("Number of machine cycle(s) : " + str(self.performances.cycles))
        print("Instruction processing frequency : " + str(round(self.performances.cycles/self.performances.elapsed, 3)) + " Hz")
        print("\n")

    def loadInFile(self):
        open(self.outputFile, "w").close()
        file = open(self.outputFile, "a")

        file.write("Simulation duration : " + str(round(self.performances.elapsed, 3)) + " second(s)\n")
        file.write("Number of machine cycle(s) : " + str(self.performances.cycles) + "\n")
        file.write("Instruction processing frequency : " + str(round(self.performances.cycles/self.performances.elapsed, 3)) + " Hz\n")
        file.write("Options setup : " + str(self.num_regs) + " registers, " + str(self.dataMemory.num_data_mem_cells) + " memory slots\n\n")
        index = 1
        for i in self.regs:
            if index-1 <10:
                file.write("R" + str(index-1) + "  : 0x%04x" % self.twosComplement(i) + " / ")
            else:
                file.write("R" + str(index-1) + " : 0x%04x" % self.twosComplement(i) + " / ")
            if not(index % 8) and index != 0:
                file.write("\n")
            index += 1

        file.write("\n")

        index = 1
        for i in self.dataMemory.memorySlots:
            if index-1 < 10:
                file.write("SLOT" + str(index-1) + "  : 0x%04x" % self.twosComplement(i) + " / ")
            else:
                file.write("SLOT" + str(index-1) + " : 0x%04x" % self.twosComplement(i) + " / ")
            if not(index % 7) and index != 0:
                file.write("\n")
            index += 1

        file.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This program simulates the instruction set of the input machine code, corresponding to the initial assembly program.", epilog="Program realized in the microprocessor course by Mallory LEHUAULT-PARC", formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-i", "--input_file", help=".bin input file", required=True)
    parser.add_argument("-o", "--output_root", help="output directory (make sure it already exist)")
    parser.add_argument("-r", "--nb_registers", help="number of registers available", required=True)
    parser.add_argument("-m", "--memory_size", help="number of memory slots available", required=True)
    parser.add_argument("-ri", "--registers_init_file", help=".txt file to init registers value")
    parser.add_argument("-s", "--step_by_step", help="(True) press RIGHT KEY to simulate the next instruction")

    args = parser.parse_args()

    vm = VirtualMachine(args.input_file, args.output_root, int(args.nb_registers, 10), int(args.memory_size, 10), args.registers_init_file, args.step_by_step)
    vm.run()