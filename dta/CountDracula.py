'''
Created on Jul 22, 2011

@author: varun
'''

import psycopg2, datetime
from datetime import date, time, timedelta, datetime

class CountDracula():
    '''
    classdocs
    '''


    def __init__(self, host, database, username, pw):
        '''
        Constructor
        '''
        
        self._host = host
        self._database = database
        self._username = username
        self._pw = pw
        self._conn2db = psycopg2.connect("host = "+self._host + " dbname="+self._database+ " user="+self._username + " password = "+self._pw )
        self._cur2db = self._conn2db.cursor()
        
        
    def mapNodesFromDTA(self, dtaNodesList, tolerance):
        dtaNodes2countDraculaNodes_dict = {}  #Dictionary by dta node id: Key = dta_node_id, value = CD_node_id
        #counter = 0
        
        
        for dtanodeid in dtaNodesList:
            dtanode = dtaNodesList[dtanodeid]
            dta_node_x = dtanode.getX()
            dta_node_y = dtanode.getY()
            self._cur2db.execute("SELECT int_id from nodes WHERE  sqrt((long_x - %s)^2 + (lat_y - %s)^2) < %s ;",(dta_node_x,dta_node_y,tolerance))
            answer =  self._cur2db.fetchone()
            
            #------ASSUMING there is a single match !!!!------ 
            if answer:
                dtaNodes2countDraculaNodes_dict[dtanode.getId()] = int(answer[0])
                #counter = counter+1
            else:
                dtaNodes2countDraculaNodes_dict[dtanode.getId()] = -1
        

        #print "\n\n Matches found = "
        #print counter
        return dtaNodes2countDraculaNodes_dict
        
        
    def getTurningCounts(self, atNode, fromNode, toNode,fromangle, toangle, starttime, period, number):
        
        
           
        counts = []
        self._cur2db.execute("SELECT street1 from (    ((SELECT DISTINCT street1 from intersection_ids where int_id = %s) UNION (SELECT DISTINCT  street2 from intersection_ids where int_id = %s)) UNION ALL ((SELECT DISTINCT  street1 from intersection_ids where int_id = %s)UNION(SELECT DISTINCT  street2 from intersection_ids where int_id = %s))    ) Street GROUP BY street1 HAVING count(street1) > 1",
                       (atNode,atNode,fromNode,fromNode))
        fromstreet =   self._cur2db.fetchone()

        self._cur2db.execute("SELECT street1 from (    ((SELECT DISTINCT  street1 from intersection_ids where int_id = %s) UNION (SELECT DISTINCT  street2 from intersection_ids where int_id = %s)) UNION ALL ((SELECT DISTINCT  street1 from intersection_ids where int_id = %s)UNION(SELECT DISTINCT  street2 from intersection_ids where int_id = %s))    ) Street GROUP BY street1 HAVING count(street1) > 1",
                       (atNode,atNode,toNode,toNode))
        tostreet =   self._cur2db.fetchone()
        
        if fromstreet == None or tostreet== None:
            return []
        
        if fromstreet != tostreet:
            intstreet = tostreet
        else:
            self._cur2db.execute("SELECT street1 from ((SELECT DISTINCT street1 from intersection_ids where int_id = %s) UNION (SELECT DISTINCT  street2 from intersection_ids where int_id = %s)) STREET where street1 <> %s",
                           (atNode,atNode,fromstreet))
            intstreet =   self._cur2db.fetchone()
            
## TODO 
        
        if (fromangle > 0.785398163) and (fromangle <= 2.35619449):       #fromangle is between pi/4 and 3pi/4 -> SB
            fromdir = "SB"
        elif (fromangle > 2.35619449) and (fromangle <= 3.92699082):        #fromangle is between 3pi/4 and 5pi/4 -> WB
            fromdir = "WB"
        elif (fromangle > 3.92699082) and (fromangle <= 5.49778714):        #fromangle is between 5pi/4 and 7pi/4 -> NB
            fromdir = "NB"
        else: 
            fromdir = "EB"
#------------------------------------------------------------------------------ 
        if (toangle > 0.785398163) and (toangle <= 2.35619449):       #toangle is between pi/4 and 3pi/4 -> SB
            todir = "SB"
        elif (toangle > 2.35619449) and (toangle <= 3.92699082):        #toangle is between 3pi/4 and 5pi/4 -> WB
            todir = "WB"
        elif (toangle > 3.92699082) and (toangle <= 5.49778714):        #toangle is between 5pi/4 and 7pi/4 -> NB
            todir = "NB"
        else: 
            todir = "EB"
            
        counttime = starttime
        for i in range(0,number):
            
            self._cur2db.execute("SELECT AVG(count) from counts_turns where fromstreet = %s AND fromdir = %s AND tostreet = %s  AND todir = %s AND intstreet = %s AND period = %s  GROUP BY starttime HAVING  starttime::time = %s",
                           (fromstreet, fromdir, tostreet, todir, intstreet, period, counttime))
            
            count =  self._cur2db.fetchone()
            if not count == None: 
                counts.extend(count)
            
            counttime = (datetime.combine(date(2000,1,1),starttime) + period).time()
        
        return counts
        
        
        
        
        
        
        