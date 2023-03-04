try:
    import argparse #pip install argparse
    import time # pip install times
except ImportError as error:
    print(error)
    exit()

class Performances:
    """
    A class used to determine some statistics about the translate

    Attributes
    ----------
        start : float
            a float to store the starting time
        stop : float
            a float to store the ending time
        elapsed : float
            a float to store the elapsed time

    Methods
    -------
        timerStart()
            store the starting time in start attribute
        
        timerStop()
            store the ending time in stop attribute and store the elsapsed time in elapsed attribute
    """
    def __init__(self):
        self.start = None
        self.stop = None
        self.elapsed = None
    
    def timerStart(self):
        self.start = time.perf_counter()

    def timerStop(self):
        self.stop = time.perf_counter()
        self.elapsed = self.stop - self.start

class Assembler:
    """
    A class that is used to pre-process the assembly program before it is converted to machine language

    Attributes
    ----------
        inputFile: string
            The file name of the assembler program

        outputFile: string
            the name of the file in which to save the translated assembly program

        instructionManager: object
            python object used to translate the assembly program

        performance: object
            python object used to measure the performance of the translation

        labels: dictionary
            dictionary used to store the labels found in the assembler program

        lines: string table
            table used to store each line of the assembler program before translation

    Methods
    -------
        run()
            represents the main program to be followed by calling the corresponding methods and displays the results of the translation

        openFile(asm_file)
            opens the file corresponding to the assembly program

            Parameters
            ----------
            asm_file: string
                the name of the assembler file in which the program to be translated is located

        lookForLabelsAndInstrcutions()
            slices the assembly program to extract labels and instructions and removes unwanted elements

        loadInFile(data)
            saves in a binary file the result of the conversion of the assembly program into machine language

            Parameters
            ----------
            data: int table
                table in which all machine instructions are grouped
    """
    def __init__(self, inputFile, outputFile):
        self.inputFile = inputFile
        self.outputFile = outputFile
        self.instructionsManager = None
        self.performances = Performances()
        self.labels = {}
        self.lines = []
    
    def run(self):
        print("Starting conversion!")
        self.performances.timerStart()
        print(" - Reading file...")
        self.openFile(self.inputFile)
        print(" - Parsing file...")
        self.lookForLabelsAndInstrs()
        print(" - Converting program...")
        self.instructionsManager = Instruction(self.labels, self.lines)
        self.instructionsManager.encode()
        print(" - Saving machine code...")
        self.loadInFile(self.instructionsManager.machineCode)
        self.performances.timerStop()
        print("Done !\n")

        print("Some statistics :")
        print("Number of instructions : ", len(self.lines))
        print("Number of labels : ", len(self.labels))
        print("Traduction duration : " + str(round(self.performances.elapsed, 3)) + " second(s)")
        print("Instruction translanting frequency : " + str(round(len(self.lines)/self.performances.elapsed, 3)) + " Hz")
        print("")

    def openFile(self, asm_file):
        file = open(asm_file, 'r')
        self.inputFile = file.readlines()
        file.close()

    def lookForLabelsAndInstrs(self):
        pc = 0
        for line in self.inputFile:
            parsing_for_labels = []
            for i in line:
                if i == "#" or i == "\n" or i == ";":
                    break
                elif i == " " or i == "\t":
                    continue
                else:
                    parsing_for_labels.append(i)

            to_check = "".join(parsing_for_labels)

            if to_check != "":
                if ":" in to_check:
                    index = to_check.rfind(":")
                    raw = to_check[index+1:]
                    self.labels[to_check[:index]] = pc
                    if raw != "":
                        self.lines.append(raw)
                        pc+=1
                    else:
                        continue
                else:
                    self.lines.append(to_check)
                    pc+=1
    
    def loadInFile(self, data):
        index = 0
        open(self.outputFile, "w").close()
        file = open(self.outputFile, "a")
        for i in data:
            file.write("0x%08x" % index + " " + "0x%08x" % i)
            if(int(index) != len(data)-1):
                file.write("\n")
            else:
                pass
            index += 1
        file.close()

class Instruction:
    """
    A class used to translate the pre-processed assembly program into machine language 

    Attributes
    ----------
        labels : dictionary
            the dictionary where the labels located in the assembler program are stored

        cmd: string table
            the table where are stored all the lines of the assembler program

        machineCode: int table
            table used to store the calculated machine instructions 

        instructions: dictionary
            dictionary used to link an assembly command to its associated instruction number (stop : 0, add : 1 ...)

    Methods
    -------
        instCheck(inst)
            analyzes the current assembly instruction to determine if it is valid or not

            Parameters
            ----------
            inst: string
                current instruction
        
        encode()
            translates the set of instructions into machine language and stores them in the machineCode attribute
    """
    def __init__(self, labels, cmd):
        self.labels = labels
        self.cmd = cmd
        self.machineCode = []
        instruction_set = [    "stop", "add", "sub", "mul", "div", 
                                    "and", "or", "xor", "shl", "shr", 
                                    "slt", "sle", "seq", "load", "store",
                                    "jmp", "braz", "branz", "scall"    ]
        self.instructions = {}

        for k in range(0, len(instruction_set)):
            self.instructions[instruction_set[k]] = k

    def instCheck(self, inst):
        if self.instructions.get(inst) is not None:
            return inst
        else:
            print("Undefined instruction : ", inst)
            exit()
    
    def encode(self):
        for sample in self.cmd:
            r = []
            reg_nb = []
            line_splited = sample.split(",")
            if "jmp" in line_splited[0]:
                inst = "jmp"
                for key in self.labels:
                    if key in line_splited[0]:
                        cmd = 0
                        break
                    else:
                        cmd = 1
            else:
                inst = line_splited[0].rsplit("r", 1)[0]
            instr = 0
            if inst == "stop":
                instr += self.instructions.get(Instruction.instCheck(self, inst))<<27
            elif inst == "braz" or inst == "branz":
                instr += self.instructions.get(Instruction.instCheck(self, inst))<<27
                instr += int(line_splited[0].rsplit("r", 1)[1])<<22
                instr += int(self.labels.get(line_splited[1]))
            elif "scall" in inst:
                n = int(inst[5:])
                instr += self.instructions.get(Instruction.instCheck(self, inst[:5]))<<27
                instr += n
            elif inst == "jmp":
                if cmd == 1:
                    try:
                        reg_nb.append(int(line_splited[0].split("p")[1][1:]))
                    except ValueError:
                        reg_nb.append(int(line_splited[0].split("p")[1]) & (2**16 - 1))
                        cmd = 0
                else:
                    label = line_splited[0][3:]
                    reg_nb.append(self.labels.get(label))
                reg_nb.append(int(line_splited[1][1:]))
                instr += self.instructions.get(Instruction.instCheck(self, inst))<<27
                instr += cmd<<26
                instr += reg_nb[0]<<5
                instr += reg_nb[1]
            else :
                r.append("r"+line_splited[0].rsplit("r", 1)[1])
                r.append(line_splited[1])
                r.append(line_splited[2])
                reg_nb.append(int(r[0][1:]))
                if "r" in r[1]:
                    reg_nb.append(int(r[1][1:]))
                    cmd = 1
                else:
                    nb = int(r[1])
                    nb = nb & (2**16 - 1)
                    reg_nb.append(nb)
                    cmd = 0
                reg_nb.append(int(r[2][1:]))
                instr += self.instructions.get(Instruction.instCheck(self, inst))<<27
                instr += int(reg_nb[0])<<22
                instr += cmd<<21
                instr += reg_nb[1]<<5
                instr += reg_nb[2]
            self.machineCode.append(instr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This program transforms your assembly code into a machine language that can be simulated by the corresponding instruction set simulator.", epilog="Program realized in the microprocessor course by Mallory LEHUAULT-PARC",formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-i", "--input_file", help=".asm input file", required=True)
    parser.add_argument("-o", "--output_file", help=".bin output file", required=True)

    args = parser.parse_args()

    assembler = Assembler(args.input_file, args.output_file)
    assembler.run()