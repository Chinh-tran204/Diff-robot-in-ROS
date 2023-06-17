#!/usr/bin/env python
# license removed for brevity
import rospy
from std_msgs.msg import Float64
import RPi.GPIO as GPIO
import smbus
import time


address = 0x48
bus=smbus.SMBus(1)
cmd=0x40

Z_pin = 24

# CHan ket noi keypad
touch_pin_1 = 17
touch_pin_2 = 27
touch_pin_3 = 22
touch_pin_4 = 23

GPIO.setmode(GPIO.BCM)
GPIO.setup(Z_pin,GPIO.IN,GPIO.PUD_UP)
GPIO.setup(touch_pin_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(touch_pin_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)


#tao bien tam cho xe
car_movement = ["standStill","Mid"]
direction = None
side = None

touch_val = [0,0,0,0]

#Tao bien tam chua van toc xe
vel = 0
increment = 2



# Ham doc gia tri analog
def analogRead(chn):
    bus.write_byte(address,cmd+chn)
    value = bus.read_byte(address)
    return value

# Ham Lay gia tri joystick
def readValue():
    val_Z = GPIO.input(Z_pin)
    val_Y = analogRead(0)
    val_X = analogRead(2)
    joyStichVal = [val_X, val_Y, val_Z]
    return joyStichVal

#Ham lay gia tri nut cam ung
def keypadControll(car_dir):   
    touch_val[0]=GPIO.input(touch_pin_1)
    touch_val[1]=GPIO.input(touch_pin_2)
    touch_val[2]=GPIO.input(touch_pin_3)
    touch_val[3]=GPIO.input(touch_pin_4)
    joint_vel = [0,0]
    global vel
    
    if touch_val[0]:
        vel = vel + increment
    elif touch_val[1]:
        vel = vel - increment
    elif touch_val[2]:
        vel = 0
        
    #set up gioi han toc d*
        
    if vel >= 25:
        vel = 25
    elif vel <= 0:
        vel = 0

    #Set up toc do va huong cho xe
    if car_dir[0] == "standStill" and car_dir[1] == "Mid":
        joint_vel = [0,0]
    if car_dir[0] == "Forward":
        joint_vel = [-vel, vel]
    elif car_dir[0] == "Backward":
        joint_vel = [vel, -vel]
    if car_dir[1] == "Right":
        joint_vel[1] = joint_vel[1]*1.755 
    elif car_dir[1] == "Left":
        joint_vel[0] = joint_vel[0]*1.755
    
    if touch_val[3]:
        joint_vel = [-5,-5]
        

    return joint_vel

#Ham suy set truong hop dieu khien
def carDirSetup(joyStickVal):
    x_val = joyStickVal[0]*10
    y_val = joyStickVal[1]*10
    global direction
    global side
    #suy xet di chuyen cua xe
    if 1900<=x_val<=2150 and 1250<=y_val<=1350:
        direction = "standStill"
        side = "Mid"
    else: 
        if y_val > 1350:
            direction = "Backward"
        if y_val < 1250:
            direction = "Forward"
        if 1900<= x_val <= 2150:
            side = "Mid"
        if x_val > 2150:
            side = "Left"
        if x_val < 1900:
            side = "Right"
    car_movement[0] = direction
    car_movement[1] = side
    print("Dir: huong: %s, trai/phai: %s"%(car_movement[0],car_movement[1]))
    return car_movement





# Ham publish
def talker():
    

    pub1 = rospy.Publisher('/my_diffbot/joint1_velocity_controller/command', Float64, queue_size=10)
    pub2 = rospy.Publisher('/my_diffbot/joint2_velocity_controller/command', Float64, queue_size=10)
    rospy.init_node('joystick', anonymous=True)
    rate = rospy.Rate(60) # 10hz
    
    
    while not rospy.is_shutdown():
        #Lay gia tri joystick
        joyStichValue = readValue()
        #Tu gia tri joy set up huong di chuyen cua xe
        carDirection = carDirSetup(joyStichValue)
        # Dua vao gia tri cua nut bam hieu chinh toc do cua xe
        jointVelocity = keypadControll(carDirection)
        #In ra gia tri de test
        print("Velocity: Rvel: %d, Lvel: %d"%(jointVelocity[0],jointVelocity[1]))

        #Publish gia tri
        rospy.loginfo(jointVelocity[1])
        rospy.loginfo(jointVelocity[0])
        pub1.publish(jointVelocity[1])
        pub2.publish(jointVelocity[0])
        rate.sleep()


if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass

