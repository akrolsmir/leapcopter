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
  
  def on_init(self, controller):
    print "Initialized"
    self.pitch_offset, self.roll_offset = 0, 0
    # self.tool_was_present = False

  def on_connect(self, controller):
    print "Connected"

  def on_disconnect(self, controller):
    print "Disconnected"

  def on_frame(self, controller):
    frame = controller.frame()

    # if len(hands) == 0 and self.tool_was_present:
    #     # Toggle heli lights off
    #     ser.write('bbb')
    #     print('tool disappeared')
    #     self.tool_was_present = False
        
    if not frame.hands.empty:
        # Get the first hand
        hand = frame.hands[0]

        height = hand.palm_position.y
        
        # Get the hand's normal vector and direction
        normal = hand.palm_normal
        direction = hand.direction

        pitch = direction.pitch * Leap.RAD_TO_DEG
        roll = normal.roll * Leap.RAD_TO_DEG
          
        # tool_present = False

        #check if a tool is present
        # for hand in hands:
        #   for finger in hand.fingers():
        #     if finger.isTool():
        #       print 'tool'
        #       tool_present = True

        # if not self.tool_was_present and tool_present:
        #   # Toggle heli lights on
        #   ser.write('bbb')
        #   print('tool initially found')
        #   self.tool_was_present = True
          
        # if self.tool_was_present and not tool_present:
        #   # Toggle heli lights off
        #   ser.write('bbb')
        #   print('tool disappeared')
        #   self.tool_was_present = False

        #Calibration - saves offset when 2 hands are present
        # if len(hands) > 1:
        #     self.pitch_offset = int(convert(pitchAngle) - 127)
        #     self.roll_offset = int(convert(rollAngle) - 127)     
        
        throttle_data = int((((height-30)*255)/300))
        pitch_data = int(255 - (convert(pitch)+self.pitch_offset))
        roll_data = int(convert(roll)) + self.roll_offset

        #normalize throttle
        if throttle_data < 0:
          throttle_data = 0
        elif throttle_data > 240:
          throttle_data = 240

        #Map to polynomial scale
        #More control for lower values
        throttle_data = int(((throttle_data/2)**2)/63.25)
        
        #normalize pitch
        if pitch_data > 255:
          pitch_data = 255
        elif 90 < pitch_data and pitch_data < 190: #threshold
          pitch_data = 122
        elif pitch_data < 0:
          pitch_data = 0

        #normalize roll
        if roll_data > 255:
          roll_data = 255
        elif 80 < roll_data and roll_data < 150: # threshhold
          roll_data = 122
        elif roll_data < 0:
          roll_data = 0
          
        
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
        print 'throttle: {0}, pitch: {1}, roll: {2}'.format(throttle_data, pitch_data, roll_data)
        #print 'pitch_offset:', self.pitch_offset, 'roll_offset:', self.roll_offset
       
    #delay before sending new data
    time.sleep(.025)
    
ser = serial.Serial('/dev/tty.usbserial-A900acS7',115200)
time.sleep(2)

def main():  
  # Create a sample listener and controller
  listener = SampleListener()
  controller = Leap.Controller()

  # Have the sample listener receive events from the controller
  controller.add_listener(listener)

  # Keep this process running until Enter is pressed
  print "Press Enter to quit..."
  sys.stdin.readline()

  # Remove the sample listener when done
  controller.remove_listener(listener)


  # press enter when no hands are present to kill throttle
  # while True:
  #     val = sys.stdin.readline()
  #     print val
  #     ser.write('a')
  #     ser.write('a')
  #     ser.write('a')
  #     ser.write(chr(0))
  #     ser.write(chr(127))
  #     ser.write(chr(127))
if __name__ == "__main__":
    main()   
