import csv
import glob

# for each table
for t in ['procedures','payers','prices',]:
    # define folder where file is located
    directory = 'D:\dolthub-hospital\dolthub-hospital\\'+t
    # name powershell script for prices or procedures
    ps_script_name = t+'.ps1'
    with open(ps_script_name, 'w') as ps:
        # ps.write('''D:''')
        ps.write('''Set-Location D:\dolthub-hospital\hospital-price-transparency-v2\n''')
        command_str='''cmd /c 'dolt sql < '''
        for path in glob.iglob(f'{directory}/*.csv'):
            print(path)
            # filename= "hospitals\\batch_1.csv"
            filename= path
            # generate name of sql file from csv file
            sqlFile = filename[:-4] + '.sql'
            # create short file name
            shortfilename=filename.split('\\')[-1]
            # write commands to powershell script
            ps.write(command_str+sqlFile+ "'\n")
            # write command to commit after each run
            ps.write('''cmd /c 'dolt commit -am "insert ignore '''+t+" "+shortfilename[:-4]+ '''"'\n''')
            openFile = open(filename, 'r')
            csvFile = csv.reader(openFile)
            # table = filename.split('.')[0].split('_')[2]
            # this writes to wrong place
            table = filename.split('.')[0]
            # try to take directory
            table = directory.split('\\')[-1]
            header = next(csvFile)
            headers = map((lambda x: '`'+x+'`'), header)
            insert = f'INSERT IGNORE INTO {table} (' + ", ".join(headers) + ")"
            with open(sqlFile, 'w') as f:
                f.write(insert + '\n')
                f.write("VALUES\n")
                rows = list(csvFile)
                for i, row in enumerate(rows):
                    if i == len(rows)-1:
                        values = map((lambda x: '"'+str(x).replace('"','""')+'"'), row)
                        # print(values)
                        f.write("("+ ", ".join(values) +");")
                    else:
                        values = map((lambda x: '"'+str(x).replace('"','""')+'"'), row)
                        f.write("("+ ", ".join(values) +"),\n")
                f.close()
                openFile.close()
        # ps.close()
        

'''
cmd /c 'dolt sql < D:\dolthub-hospital\dolthub-hospital\procedures\bolivar_medical_center_1457321036.sql'
'''
    