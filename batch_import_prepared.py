import csv
import glob

directory = "D:\dolthub-hospital\dolthub-hospital\procedures"
with open("procedures.ps1", "w") as ps:
    command_str = """cmd /c 'dolt sql < """
    for path in glob.iglob(f"{directory}/*.csv"):
        print(path)
        # filename= "hospitals\\batch_1.csv"
        filename = path
        sqlFile = filename[:-4] + ".sql"
        ps.write(command_str + sqlFile + "'\n")
        openFile = open(filename, "r")
        csvFile = csv.reader(openFile)
        # table = filename.split('.')[0].split('_')[2]
        # this writes to wrong place
        table = filename.split(".")[0]
        # try to take directory
        table = directory.split("\\")[-1]
        header = next(csvFile)
        headers = map((lambda x: "`" + x + "`"), header)
        headers = map((lambda x: "" + x + ""), header)
        qs = map((lambda x: "?"), header)
        insert = (
            f'PREPARE stmt1 FROM "'
            + f"INSERT INTO {table} ("
            + ", ".join(headers)
            + f") VALUES ("
            + ", ".join(qs)
            + f') ;";'
        )
        with open(sqlFile, "w") as f:
            f.write(insert + "\n")
            # f.write("VALUES\n")
            rows = list(csvFile)
            for i, row in enumerate(rows):
                if i == len(rows) - 1:
                    values = map(
                        (lambda x: '"' + x + '"' if len(x) > 0 else ""), row
                    )
                    f.write("EXECUTE stmt1  USING (" + ", ".join(values) + ");")
                else:
                    values = map(
                        (lambda x: '"' + x + '"' if len(x) > 0 else ""), row
                    )
                    f.write("EXECUTE stmt1 USING (" + ", ".join(values) + ");\n")
            f.write("\nDEALLOCATE PREPARE stmt1;")
            f.close()
            openFile.close()
"""
cmd /c 'dolt sql < D:\dolthub-hospital\dolthub-hospital\procedures\bolivar_medical_center_1457321036.sql'
"""
