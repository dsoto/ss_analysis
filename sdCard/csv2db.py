
import csv, os, os.path, sqlite3, sys
from datetime import datetime

class SQLQueries:
    create_circuits_table = '''
CREATE TABLE circuits (
circuitid INTEGER PRIMARY KEY AUTOINCREMENT, 
circuit NUMERIC UNIQUE, 
type TEXT)
'''

    create_logs_table = '''
CREATE TABLE logs (
logid INTEGER PRIMARY KEY AUTOINCREMENT, 
circuitid INTEGER, 
timestamp TIMESTAMP,
watts FLOAT,
volts FLOAT,
amps FLOAT,
watthours_sc20 FLOAT,
watthours_today FLOAT,
powerfactor INTEGER,
frequency FLOAT,
voltamps FLOAT,
status BOOLEAN,
machineid TEXT,
credit FLOAT,
FOREIGN KEY(circuitid) references circuits(circuitid))
'''

def load_file(csv_file, db):
    pass

def load_dir(data_dir, db):
    print "loading database:", db

    db_connection = sqlite3.connect(db)
    db_cursor = db_connection.cursor()

    db_cursor.execute(SQLQueries.create_circuits_table)
    db_cursor.execute(SQLQueries.create_logs_table)

    circuit_ids = {}
    circuit_index = 0
    for root, dirs, files in os.walk(data_dir):
        for f in files:
            if not f.endswith(".log"):
                continue

            print os.path.join(root, f)

            circuit_id = int(f[-6:-4])
            circuit_type = "MAINS" if circuit_id == 0 else "CONSUMER"
            if circuit_id not in circuit_ids:
                db_cursor.execute("INSERT INTO circuits (circuit, type) VALUES(?,?)", 
                                  (circuit_id, circuit_type))
                circuit_index += 1
                circuit_ids[circuit_id] = circuit_index

            idx = circuit_ids[circuit_id]
            log = csv.reader(open(os.path.join(root, f), 'rb'), delimiter=',')
            header = log.next()

            for row in log:
                timestamp = datetime.strptime(row[0], "%Y%m%d%H%M%S").isoformat(' ')
                watts = float(row[1])
                volts = float(row[2])
                amps = float(row[3])
                wh_sc20 = float(row[4])
                wh_today = float(row[5])
                power_factor = int(row[12])
                frequency = float(row[14])
                volt_amps = float(row[15])
                status = 1 if int(row[16]) == 0 else 1
                machine_id = row[18]
                credit = 0.0 if circuit_type == "MAINS" else float(row[20])

                db_cursor.execute("INSERT INTO logs (circuitid, timestamp, watts, volts, amps, watthours_sc20, watthours_today, powerfactor, frequency, voltamps, status, machineid, credit) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", (idx, timestamp, watts, volts, amps, wh_sc20, wh_today, power_factor, frequency, volt_amps, status, machine_id, credit))
                                                
    db_connection.commit()
    db_cursor.close()

    print "done."

if __name__ == "__main__":
    args = sys.argv[1:]
    print args
    load_dir(args[0], args[1])
