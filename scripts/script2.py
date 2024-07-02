with open('cat.txt','r') as file, open('cat_new.txt','w') as output:
    for line in file.readlines():
        print(line)
        name,data = line.split('/')
        data = data.split()
        data.insert(2,data[2])
        data.insert(0,name+'/')
        data = ' '.join(data)
        print(data)       
        print(data,file=output)