import _LeapPython
import Leap, sys, math
import serial
import time
import math

# Scale angles from 0 to 255
# Arduino reads byte-sized values
def convert(angle):
  if(angle < 180):
    return 127 + (angle*127)/45
  if(angle > 180):
    return 127 - ((360 - angle)*127)/45




  
class SampleListener(Leap.Listener):
  
  def onInit(self, controller):
    print "Initialized"
    self.pitch_offset, self.roll_offset = 0, 0
    self.tool_was_present = False

  def onConnect(self, controller):
    print "Connected"

  def onDisconnect(self, controller):
    print "Disconnected"

  def onFrame(self, controller):
        
    frame = controller.frame()
    hands = frame.hands()
    try:
        if len(hands) == 0 and self.tool_was_present:
            # Toggle heli lights off
            ser.write('bbb')
            print('tool disappeared')
            self.tool_was_present = False
          
        if len(hands) > 0:
            hand = hands[0]
            palmRay = hand.palm()
            fingers = hand.fingers()
              
            tool_present = False

            #check if a tool is present
            for hand in hands:
              for finger in hand.fingers():
                if finger.isTool():
                  tool_present = True

            if not self.tool_was_present and tool_present:
              # Toggle heli lights on
              ser.write('bbb')
              print('tool initially found')
              self.tool_was_present = True
              
            if self.tool_was_present and not tool_present:
              # Toggle heli lights off
              ser.write('bbb')
              print('tool disappeared')
              self.tool_was_present = False

                  
            palm = palmRay.position
            normal = hand.normal()
            if normal is not None:
                # pitch (front/back) and roll (left/right)
                pitchAngle = math.atan2(normal.z, normal.y) * 180/math.pi + 180
                rollAngle = math.atan2(normal.x, normal.y) * 180/math.pi + 180

            #Calibration - saves offset when 2 hands are present
            if len(hands) > 1:
                self.pitch_offset = int(convert(pitchAngle) - 127)
                self.roll_offset = int(convert(rollAngle) - 127)     

      
            

            throttle_data = int((((palm.y-30)*255)/300))
            pitch_data = int(255 - (convert(pitchAngle)+self.pitch_offset))
            roll_data = int(convert(rollAngle)) + self.roll_offset

            if throttle_data > 230:
              throttle_data = 230
            if pitch_data > 255:
              pitch_data = 255              
            if roll_data > 255:
              roll_data = 255

            if throttle_data < 0:
              throttle_data = 0
            if pitch_data < 0:
              pitch_data = 0
            if roll_data < 0:
              roll_data = 0
              
            #Map to polynomial scale
            #More control for lower values
            throttle_data = int(((throttle_data/2)**2)/63.25)
            
            #data tag; arduino reads the followng three values as throttle, pitch and roll
            #ensures ardiuno read won't fall out of sync
            ser.write('a')
            ser.write('a')
            ser.write('a')

            #write data to arduino
            ser.write(chr(throttle_data))
            ser.write(chr(pitch_data))
            ser.write(chr(roll_data))
            
            # for debugging
            print throttle_data , pitch_data , roll_data , len(hands), 'pitch_offset:', self.pitch_offset, 'roll_offset:', self.roll_offset
          
        

        #delay before sending new data
        time.sleep(.025)
    except Exception as e:
        print(e)
        
    
    
ser = serial.Serial('COM14',115200)
time.sleep(5)
listener = SampleListener()
controller = Leap.Controller(listener)

# press enter when no hands are present to kill throttle
# while True:
#     val = sys.stdin.readline()
#     ser.write('a')
#     ser.write('a')
#     ser.write('a')
#     ser.write(chr(0))
#     ser.write(chr(127))
#     ser.write(chr(127))
