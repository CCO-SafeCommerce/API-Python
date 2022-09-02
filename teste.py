lista = [10, 25, 30, 45, 50, 60, 70, 80, 90, 100, 75, 65, 55, 40, 35, 20, 15, 5, 0]

for i in range(len(lista)):
  for j in range(len(lista)):
    if lista[i] <= lista[j]:
      salvar = lista[i]
      lista[i] = lista[j]
      lista[j] = salvar

print(lista)