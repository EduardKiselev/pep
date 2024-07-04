files = [
    ('dog.txt', 'dog_reformated.txt'),
    ('cat.txt', 'cat_reformated.txt'),
    ]

for input_f, output_f in files:
    with open(input_f, 'r') as file, open(output_f, 'w') as output:
        for line in file.readlines():
           # print(line)
            name, data = line.split('/')
            data = data.split()
            data.insert(2, data[2])
            if name == 'Vitamin A, IU': name = 'Vitamin A'
            if input_f == 'cat.txt' and name == 'Protein': data[-2] = str(30)
            if input_f == 'cat.txt' and name == 'Arginine': data[-2] = str(1.11)
            data.insert(0,name+'/')
            data = ' '.join(data)
           # print(data)       
            print(data,file=output)