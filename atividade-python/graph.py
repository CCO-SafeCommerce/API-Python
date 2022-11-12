import psutil
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def showCPU():
    xar = []
    yarCpu1 = []
    yarCpu2 = []
    yarCpu3 = []

    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)

    def animateCPU(i):
        CPU1 = psutil.cpu_percent(interval=1)
        CPU2 = CPU1 + 10
        CPU3 = CPU2 + 5

        current_time = datetime.now()
        current_time_str = current_time.strftime("%H:%M:%S")

        xar.append(str(current_time_str))
        yarCpu1.append(int(CPU1))
        yarCpu2.append(int(CPU2))
        yarCpu3.append(int(CPU3))

        if len(xar) > 5:
            xar.remove(xar[0])
            yarCpu1.remove(yarCpu1[0])
            yarCpu2.remove(yarCpu2[0])
            yarCpu3.remove(yarCpu3[0])

        plt.clf()

        plt.title('Uso das CPU´s\n')
        plt.xlabel('\nTempo')
        plt.ylabel('Porcentagem')
        plt.ylim(0, 100)

        plt.plot(xar, yarCpu1)
        plt.plot(xar, yarCpu2)
        plt.plot(xar, yarCpu3)

    ani = animation.FuncAnimation(fig, animateCPU, interval=1000)
    plt.show()

def showMEMO():
    xar = []
    yarMemo1 = []
    yarMemo2 = []
    yarMemo3 = []

    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)

    def animateCPU(i):
        Memo1 = psutil.virtual_memory().percent
        Memo2 = Memo1 + 15
        Memo3 = Memo2 + 10

        current_time = datetime.now()
        current_time_str = current_time.strftime("%H:%M:%S")

        xar.append(str(current_time_str))
        yarMemo1.append(int(Memo1))
        yarMemo2.append(int(Memo2))
        yarMemo3.append(int(Memo3))

        if len(xar) > 5:
            xar.remove(xar[0])
            yarMemo1.remove(yarMemo1[0])
            yarMemo2.remove(yarMemo2[0])
            yarMemo3.remove(yarMemo3[0])

        plt.clf()

        plt.title('Uso da memória RAM\n')
        plt.xlabel('\nTempo')
        plt.ylabel('Porcentagem')
        plt.ylim(0, 100)

        plt.plot(xar, yarMemo1)
        plt.plot(xar, yarMemo2)
        plt.plot(xar, yarMemo3)

    ani = animation.FuncAnimation(fig, animateCPU, interval=1000)
    plt.show()

def showDISK():
    xar = []
    yarDisco1 = []
    yarDisco2 = []
    yarDisco3 = []

    fig = plt.figure()
    ax1 = fig.add_subplot(1,1,1)

    def animateCPU(i):
        Disco1 = psutil.disk_usage('/').percent
        Disco2 = Disco1 - 5
        Disco3 = Disco2 * 3

        current_time = datetime.now()
        current_time_str = current_time.strftime("%H:%M:%S")

        xar.append(str(current_time_str))
        yarDisco1.append(int(Disco1))
        yarDisco2.append(int(Disco2))
        yarDisco3.append(int(Disco3))

        if len(xar) > 5:
            xar.remove(xar[0])
            yarDisco1.remove(yarDisco1[0])
            yarDisco2.remove(yarDisco2[0])
            yarDisco3.remove(yarDisco3[0])

        plt.clf()

        plt.title('Armazenamento do disco\n')
        plt.xlabel('\nTempo')
        plt.ylabel('Porcentagem')
        plt.ylim(0, 100)

        plt.plot(xar, yarDisco1)
        plt.plot(xar, yarDisco2)
        plt.plot(xar, yarDisco3)

    ani = animation.FuncAnimation(fig, animateCPU, interval=1000)
    plt.show()
