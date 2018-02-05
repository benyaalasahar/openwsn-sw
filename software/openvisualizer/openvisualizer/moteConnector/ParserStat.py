# Copyright (c) 2015, CNRS. 
# All rights reserved. 
#  
# Released under the BSD 3-Clause license as published at the link below.
# https://openwsn.atlassian.net/wiki/display/OW/License

import logging
log = logging.getLogger('ParserStat')
log.setLevel(logging.INFO)
log.addHandler(logging.NullHandler())

import struct

from pydispatch import dispatcher

from ParserException import ParserException
import Parser

from array import array

class ParserStat(Parser.Parser):
    
    HEADER_LENGTH  = 2
    MSPERSLOT      = 15 #ms per slot.
   
    #type of stat message 
     #type of stat message 
    SERTYPE_PKT_TX             = 1
    SERTYPE_PKT_RX             = 2
    SERTYPE_CELL               = 3
    SERTYPE_ACK                = 4
    SERTYPE_PKT_DROPPED        = 5
    SERTYPE_DIO                = 6
    SERTYPE_DAO                = 7
    SERTYPE_NODESTATE          = 8
    SERTYPE_6PCMD              = 9

 
    def __init__(self):
        
        # log
        log.debug('create ParserStat instance')
        
        # initialize parent class
        Parser.Parser.__init__(self,self.HEADER_LENGTH)
        
        self._asn= ['asn_4',           # B
          'asn_2_3',                   # H
          'asn_0_1',                   # H
         ]


       

    
    #======================== public ==========================================
    
    #======================== conversion ==========================================
    
 
 #returns a string with the decimal value of a uint16_t
    def BytesToString(self, bytes):
        str = ''
        i = 0

        #print bytes

        for byte in bytes:
            str = format(eval('{0} + {1} * 256 ** {2}'.format(str, byte, i)))
            #print ('{0}:{1}'.format(i, str)) 
            i = i + 1      

        return(str)

    def BytesToAddr(self, bytes):
        str = ''
        i = 0

        for byte in bytes:
            str = str + '{:02x}'.format(byte) 
            #if (i < len(bytes)-1):
            #    str = str + '-'
            i += 1

        return(str)


    def ByteToL4protocol(self, byte):
       
        IANA = {
        'IANA_IPv6HOPOPT'                     : 0x00,
        'IANA_TCP'                            : 0x06,
        'IANA_UDP'                            : 0x11,
        'IANA_IPv6ROUTE'                      : 0x2b,
        'IANA_ICMPv6'                         : 0x3a,
        'IANA_ICMPv6_ECHO_REQUEST'            :  128,
        'IANA_ICMPv6_ECHO_REPLY'              :  129,
        'IANA_ICMPv6_RS'                      :  133,
        'IANA_ICMPv6_RA'                      :  134,
        'IANA_ICMPv6_RA_PREFIX_INFORMATION'   :    3,
        'IANA_ICMPv6_RPL'                     :  155,
        'IANA_ICMPv6_RPL_DIO'                 : 0x01,
        'IANA_ICMPv6_RPL_DAO'                 : 0x02,
        'IANA_RSVP'                           :   46,
        'IANA_UNDEFINED'                      :  250
        } 

        for key, value in IANA.iteritems():
            if value == byte:
                return(key)
        return("IANA_UNKNOWN")

    def ByteToFrameType(self, byte):
        IEEE154_TYPE = {
        'IEEE154_TYPE_BEACON'                 : 0,
        'IEEE154_TYPE_DATA'                   : 1,
        'IEEE154_TYPE_ACK'                    : 2,
        'IEEE154_TYPE_CMD'                    : 3,
        'IEEE154_TYPE_UNDEFINED'              : 5
        }
 
        for key, value in IEEE154_TYPE.iteritems():
            if value == byte:
                return(key)
        return("FTYPE_UNKNOWN")


    def ByteToUDPPort(self, bytes):
        
        result = eval(self.BytesToString(bytes))        

        WKP = {
        'WKP_TCP_HTTP'                        :    80,
        'WKP_TCP_ECHO'                        :     7,
        'WKP_UDP_COAP'                        :  5683,
        'WKP_UDP_ECHO'                        :     7,
        'WKP_UDP_RINGMASTER'                  : 15000
        }

        for key, value in WKP.iteritems():
            if value == result:
                return(key)
        return("WKP_UNKNOWN")


     #======================== write logs (factroized) ==========================================
  
     #info to write when a packet is dropped

         
 
    #======================== parses and writes the logs  ==========================================
    def parseInput(self,input):
         
         # log
         if log.isEnabledFor(logging.DEBUG):
             log.debug('received stat {0}'.format(input))
        
             
                    
         #headers
         addr = input[0:2]
         asnbytes = input[2:7]  
         (self._asn) = struct.unpack('<BHH',''.join([chr(c) for c in asnbytes])) 
         statType = input[7]

         #depends on the stat-type
         if (statType == self.SERTYPE_PKT_TX):
             log.info('STAT_TX|addr={0}|asn={1}|length={2}|frameType={3}|slotOffset={4}|frequency={5}|l2Dest={6}|txpower={7}|numTxAttempts={8}|L3Src={9}|L3Dest={10}|L4Proto={11}|L4SrcPort={12}|L4DestPort={13}'.format(
             self.BytesToAddr(addr),
             self.BytesToString(asnbytes),
             input[8],
             self.ByteToFrameType(input[9]),
             self.BytesToString(input[10:12]),
             input[12],
             self.BytesToAddr(input[13:21]),
             input[21],
             input[22],
             self.BytesToAddr(input[23:39]),
             self.BytesToAddr(input[39:55]),
             self.ByteToL4protocol(input[55]),
             self.BytesToString(input[56:58]),
             self.BytesToString(input[58:61]),
             message,
             ));
 
 
 
         elif (statType == self.SERTYPE_PKT_RX):
             log.info('STAT_RX|addr={0}|asn={1}|length={2}|frameType={3}|slotOffset={4}|frequency={5}|l2Src={6}|rssi={7}|lqi={8}|crc={9}'.format(
             self.BytesToAddr(addr),
             self.BytesToString(asnbytes),
             input[8],
             self.ByteToFrameType(input[9]),
             self.BytesToString(input[10:12]),
             input[12],
             self.BytesToAddr(input[13:21]),
             input[21],
             input[22],
             input[23],
             message,
             ));
 
 
 
         elif (statType == self.SERTYPE_CELL):
             log.info('STAT_CELL|addr={0}|asn={1}|celltype={3}|shared={4}|slotOffset={5}|channelOffset={6}|neighbor={7}'.format(
                 self.BytesToAddr(addr),
                 self.BytesToString(asnbytes),
                 self.ByteToCellType(input[8]),
                 input[9],
                 input[10],
                 input[1],
                 self.BytesToAddr(input[12:20])
                 ));       
         elif (statType == self.SERTYPE_ACK):
             log.info('STAT_ACK|addr={0}|asn={1}|l2addr={3}'.format(
                 self.BytesToAddr(addr),
                 self.BytesToString(asnbytes),
                 self.BytesToAddr(input[8:16])
                 ));
         elif (statType == self.SERTYPE_PKT_DROPPED):
            log.info('STAT_drop|addr={0}|asn={1}|length={2}|frameType={3}|l2Src={4}|L3Src={11}|L3Dest={12}|L4Proto={13}|L4SrcPort={14}|L4DestPort={15}'.format(
             self.BytesToAddr(addr),
             self.BytesToString(asnbytes),
             input[8],
             input[9],
             input[10],
             self.BytesToAddr(input[11:19]),
             self.BytesToAddr(input[23:39]),
             self.BytesToAddr(input[39:55]),
             self.ByteToL4protocol(input[55]),
             self.BytesToString(input[56:58]),
             self.BytesToString(input[58:61]),
             message
             ));
 
 
 
 
         elif (statType == self.SERTYPE_DIO):
             log.info('STAT_DIO|addr={0}|asn={1}|rplinstanceId={3}|rank={4}|DODAGID={5}'.format(
                 self.BytesToAddr(addr),
                 self.BytesToString(asnbytes),
                 input[8],
                 self.BytesToString(input[9:11]),
                 self.BytesToAddr(input[11:27])               
                 ));
 
         elif (statType == self.SERTYPE_DAO):
             log.info('STAT_DAO|addr={0}|asn={1}|parent={3}|DODAGID={4}'.format(
                 self.BytesToAddr(addr),
                 self.BytesToString(asnbytes),
                 self.BytesToAddr(input[8:16]),
                 self.BytesToAddr(input[16:32])               
                 ));
                 
         elif (statType == self.SERTYPE_NODESTATE):
             
             TicsOn = struct.unpack('<I',''.join([chr(c) for c in input[8:12]]))[0]
             TicsTotal = struct.unpack('<I',''.join([chr(c) for c in input[12:16]]))[0]
             if (TicsTotal > 0):
                 dcr = float(TicsOn) / float(TicsTotal) * 100
             else:
                 dcr = 100                
                 
             log.info('STAT_NODESTATE|addr={0}|asn={1}|DutyCycleRatio={2}|NumDeSync={3}'.format(
                 self.BytesToAddr(addr),
                 self.BytesToString(asnbytes),
                 dcr,
                 input[16]
                 ));
 
         elif (statType == self.SERTYPE_6PCMD):
             log.info('STAT_6PCMD|addr={0}|asn={1}|command={2}|status={3}|neigh={4}'.format(
                 self.BytesToAddr(addr),
                 self.BytesToString(asnbytes),
                 self.ByteToSixtopCode(input[8]),
                 self.BytesToAddr(input[9:17])
                 ));
         
 
         else:
             print('Unknown stat type: type {0} addr {1} asn {2}'.format(
                 statType, 
                 self.BytesToAddr(addr), 
                 self.BytesToString(asnbytes)))
  
        
         return ('error', input)
 
 
 
  #======================== private =========================================
  
   
