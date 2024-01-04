# Abre el archivo en modo de lectura
with open('qtable.txt', 'r') as file:
    # Lee todas las líneas del archivo
    lines = file.readlines()

    # Inicializa el contador de ceros
    count_zeros = 0

    # Recorre cada línea del archivo
    for line in lines:
        # Divide la línea en valores individuales
        values = line.split()

        # Convierte cada valor a punto flotante y verifica si es 0.0
        for value in values:
            if float(value) == 0.0:
                count_zeros += 1

# Muestra el resultado por pantalla
print(f"El número de valores 0.0 en el archivo qtable.txt es: {count_zeros}")
