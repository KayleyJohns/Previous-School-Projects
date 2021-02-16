#HTML-to-CSV Converter, takes html file and converts it into csv file

import sys
import re
import io

def main():
    table = []
    first_table = [0]
    table_count = 1
    counter = 0;
    
    
    #handle error of no file is specified
    if(len(sys.argv) < 1):
        sys.stderr.write("Error: Please specifiy a file")
        sys.exit()
        
    #html_file = sys.stdin.read()
    html_file = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8').read()
    
    #Handle error if file is not working properly
    if(html_file == None):
        sys.stderr.write("Error: Something went wrong trying to open the file provided")
        sys.exit()
        
    html_file = html_file.replace("\n","")
    html_file= re.split(r">",html_file)
    
    #file is empty
    if(html_file[0] == ""):
        sys.stderr.write("Error: There is nothing inside this file")
        sys.exit()
    
    
    #Create a multi dimetional list holding the table number and the position of where each table ends
    for str in range(len(html_file)):
        if(html_file[str] == "</table"):
            table_info = [table_count, str]
            table.append(table_info)
            table_count += 1
    
    #Print out each table using printData function
    for tab in range(table_count-1):
        print("TABLE {}:".format(table[tab][0]))
        if(table_count == 1):
            printData(table[tab], html_file, first_table, counter)
            sys.exit()
        elif(tab == 0):
            printData(table[tab], html_file, first_table, counter)
            counter += 1
        else:
            printData(table[tab], html_file, table[tab-1], counter)
        print("\n")

    
def printData(tab,html_file,prev,counter): 
    #Goes through the html list and prints out data in csv format with the help of regular expressions
    count = 0
    new_count = 0
    
    if(counter == 0): #if we are looking at the first table then start from zero
        for str in range(tab[1]):
            val = re.search(r"(\s)*<(\s)*tr(\s)*", html_file[str])
            
            #error if there is a comma in data
            if("," in html_file[str] and "<td" not in html_file[str]):
                sys.stderr.write("Error: Invalid data point")
                
            
            #if the list value is not <tr> and is the first header row
            if(val is not None and count == 0):
                str += 1
                val4 = re.search(r"(<(\s)*/tr(\s)*)", html_file[str])

                while(val4 == None): #go through the list until it reaches /tr
                    
                    val1 = re.search(r"^((\s)*)(</td|</th)$", html_file[str])
                    val2 = re.search(r"^([a-zA-Z0-9 :!@#$%^&*()?+.é-]*[0-9]*\.?[0-9]*)(</td(\s)*|</th(\s)*)$", html_file[str])
                    val4 = re.search(r"(\s)*<(\s)*/tr(\s)*", html_file[str])
                    val5 = re.search(r"<(\s)*tr(\s)*|<(\s)*th(\s)*| <(\s)*table(\s)*|<(\s)*/table(\s)*|<(\s)*/br(\s)*|<(\s)*br(\s)*|<(\s)*td(\s)*|<(\s)*tr(\s)*", html_file[str])

                    if(val1 is not None): #if there is nothing to print print comma else p
                        val5 = re.search(r"(<(\s)*/tr(\s)*)", html_file[str+1])
                        if(val5 is not None):
                            print("",end = "")
                        else:
                            print("",end = ",")
                            count += 1
                    elif(val1 == None and val2 == None and val4 == None and val5 == None):
                        print("{}> {}>".format(html_file[str],html_file[str +1]), end = ",")
                        new_count += 1
                        str += 1
                    elif(val2 is not None): #else print the value
                        val5 = re.search(r"(<(\s)*/tr(\s)*)", html_file[str+1])
                        if(val5 is not None):
                            line = re.sub(r'(\s)+', ' ', val2.group(1)).strip()
                            print(line,end = "")
                        else:
                            line = re.sub(r'\s+', ' ', val2.group(1)).strip()
                            print(line,end = ",")
                        count += 1
                        
                    str += 1
                print(" ")

            else:
                new_count = 0
                if(val is not None and new_count == 0): #if str is not tr and is not the header row
                    str += 1
                    val4 = re.search(r"(<(\s)*/tr(\s)*)", html_file[str])
                    while(val4 == None): #go through the list while not equal to /tr
                        val1 = re.search(r"^((\s)*)(</td|</th)$", html_file[str])
                        val2 = re.search(r"^([a-zA-Z0-9 :!@#$%^&*()?+.é-]*[0-9]*\.?[0-9]*)(</td(\s)*|</th(\s)*)$", html_file[str])
                        val4 = re.search(r"<(\s)*/tr(\s)*", html_file[str])
                        val5 = re.search(r"<(\s)*tr(\s)*|<(\s)*th(\s)*| <(\s)*table(\s)*|<(\s)*/table(\s)*|<(\s)*/br(\s)*|<(\s)*br(\s)*|<(\s)*td(\s)*|<(\s)*tr(\s)*", html_file[str])
                
                        if(val1 is not None): #if it has nothing print a comma 
                            val5 = re.search(r"(<(\s)*/tr(\s)*)", html_file[str+1])
                            if(val5 is not None):
                                print("",end = "")
                            else:
                                print("",end = ",")
                            new_count += 1
                        elif(val1 == None and val2 == None and val4 == None and val5 == None):
                            print("{}> {}>".format(html_file[str],html_file[str +1]), end = ",")
                            new_count += 1
                            str += 1
                        elif(val2 is not None): #else print the value
                            val5 = re.search(r"(<(\s)*/tr(\s)*)", html_file[str+1])
                            if(val5 is not None):
                                line = re.sub(r'\s+', ' ', val2.group(1)).strip()
                                print(line,end = "")
                            else:
                                line = re.sub(r'\s+', ' ', val2.group(1)).strip()
                                print(line,end = ",")
                            new_count += 1
                
                        str += 1
                        
                    #while the row is not equal to the amount of columns as the header print commas
                    while(new_count != count):
                        print(",",end="")
                        new_count += 1
                        str +=1
                    print(" ")
    else: 
        #repeat all of the same steps as before but for all of the other tables using the list to go from the index of the last /table until the next table
        for str in range(prev[1],tab[1]):
            val = re.search(r"(\s)*<(\s)*tr(\s)*", html_file[str])
            #error if there is a comma in data
            if("," in html_file[str] and "<td" not in html_file[str]):
                sys.stderr.write("Error: Invalid data point")
        
            if(val is not None and count == 0):
                str += 1
                val4 = re.search(r"(<(\s)*/tr(\s)*)", html_file[str])
                while(val4 == None):
                    val1 = re.search(r"^((\s)*)(</td|</th)$", html_file[str])
                    val2 = re.search(r"^([a-zA-Z0-9 :!@#$%^&*()?+.é-]*[0-9]*\.?[0-9]*)(</td(\s)*|</th(\s)*)$", html_file[str])
                    val4 = re.search(r"(\s)*<(\s)*/tr(\s)*", html_file[str])
                    val5 = re.search(r"<(\s)*tr(\s)*|<(\s)*th(\s)*| <(\s)*table(\s)*|<(\s)*/table(\s)*|<(\s)*/br(\s)*|<(\s)*br(\s)*|<(\s)*td(\s)*|<(\s)*tr(\s)*", html_file[str])

                    if(val1 is not None):
                        val5 = re.search(r"(<(\s)*/tr(\s)*)", html_file[str+1])
                        if(val5 is not None):
                            print("",end = "")
                        else:
                            print("",end = ",")
                            count += 1
                    elif(val1 == None and val2 == None and val4 == None and val5 == None):
                        print("{}> {}>".format(html_file[str],html_file[str +1]), end = ",")
                        new_count += 1
                        str += 1
                    elif(val2 is not None):
                        val5 = re.search(r"(<(\s)*/tr(\s)*)", html_file[str+1])
                        if(val5 is not None):
                            line = re.sub(r'\s+', ' ', val2.group(1)).strip()
                            print(line,end = "")
                        else:
                            line = re.sub(r'\s+', ' ', val2.group(1)).strip()
                            print(line,end = ",")
                        count += 1
                        
                    str += 1
                print(" ")

            else:
                new_count = 0
                if(val is not None and new_count == 0):
                    str += 1
                    val4 = re.search(r"(<(\s)*/tr(\s)*)", html_file[str])
                    while(val4 == None):
                        val1 = re.search(r"^((\s)*)(</td|</th)$", html_file[str])
                        val2 = re.search(r"^([a-zA-Z0-9 :!@#$%^&*()?+.é-]*[0-9]*\.?[0-9]*)(</td(\s)*|</th(\s)*)$", html_file[str])
                        val4 = re.search(r"<(\s)*/tr(\s)*", html_file[str])
                        val5 = re.search(r"<(\s)*tr(\s)*|<(\s)*th(\s)*| <(\s)*table(\s)*|<(\s)*/table(\s)*|<(\s)*/br(\s)*|<(\s)*br(\s)*|<(\s)*td(\s)*|<(\s)*tr(\s)*", html_file[str])
                
                        if(val1 is not None):
                            val5 = re.search(r"(<(\s)*/tr(\s)*)", html_file[str+1])
                            if(val5 is not None):
                                print("",end = "")
                            else:
                                print("",end = ",")
                            new_count += 1
                        elif(val1 == None and val2 == None and val4 == None and val5 == None):
                            print("{}> {}>".format(html_file[str],html_file[str +1]), end = ",")
                            new_count += 1
                            str += 1
                        elif(val2 is not None):
                            val5 = re.search(r"(<(\s)*/tr(\s)*)", html_file[str+1])
                            if(val5 is not None):
                                line = re.sub(r'\s+', ' ', val2.group(1)).strip()
                                print(line,end = "")
                            else:
                                line = re.sub(r'\s+', ' ', val2.group(1)).strip()
                                print(line,end = ",")
                            new_count += 1
                
                        str += 1
                    
                    while(new_count < count):
                        print(",",end="")
                        new_count += 1
                        str +=1
                    print(" ") 
    
if __name__ == '__main__':
    main()

