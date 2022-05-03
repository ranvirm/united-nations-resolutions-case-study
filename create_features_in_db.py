import pandas as pd
import sqlite3

# db connect
conn = sqlite3.connect('quantium.sqlite')
cur = conn.cursor()

# add conflict duration to conflicts tbl
cur.execute(
    '''
    ALTER TABLE conflicts ADD COLUMN duration int;
    '''
)
conn.commit()
cur.execute(
    '''
    update conflicts set duration = conflicts.end - conflicts.start where conflicts.end is not null;
    '''
)
conn.commit()
conn.close()
