from psutil import process_iter
processos = []
nomes = []
i = 0
situacaoCpu = 'n'
situacaoRam = 'n'
j = 0
while j < 5:
    for proc in process_iter(['pid', 'name', 'username']):
        if proc.pid != 0 and proc.name != 'Idle' and proc.name() != 'System' and nomes.__contains__(proc.name()) == False:
            useCpu = proc.cpu_percent()
            memoryRam = proc.memory_percent()
            if useCpu > 0:
                nomes.append(proc.name())
                if useCpu > 70 and useCpu < 90:
                    situacaoCpu = 'a'
                elif useCpu >= 90:
                    situacaoCpu = 'e'
                if memoryRam > 75 and memoryRam < 85:
                    situacaoRam = 'a'
                elif memoryRam >= 85:
                    situacaoRam = 'e'

                #processo = {'Nome': proc.name(), 'Pid': proc.pid, 'Cpu': useCpu, 'Ram': proc.memory_percent()}
                processos.append(( proc.pid, proc.name(), useCpu, situacaoCpu, memoryRam, situacaoRam))
    j+=1
def teste(e):
    i=0
    while i < 10:
        atual = i
        i+=1 
        return e[3]
processos.sort(reverse=True ,key=teste)
print(processos)
