#!/usr/bin/env python3

import rospy
import actionlib
import telebot
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from geometry_msgs.msg import Point, Quaternion

# Define the shop and block locations
locations = {
    "Shop1": Point(x=4.359752655029297, y=8.947501182556152, z=0.0),
    "Shop2": Point(x=4.359752655029297, y=8.947501182556152, z=0.0),
    "Block1": Point(x=3.088334083557129, y=-9.654563903808594, z=0.0),
    "Block2": Point(x=3.088334083557129, y=-9.654563903808594, z=0.0),
    "Block3": Point(x=-4.435606956481934, y=-8.467134475708008, z=0.0)
}

def movebase_client(goal):
    client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
    client.wait_for_server()

    # Set the goal location
    move_base_goal = MoveBaseGoal()
    move_base_goal.target_pose.header.frame_id = "map"
    move_base_goal.target_pose.header.stamp = rospy.Time.now()
    move_base_goal.target_pose.pose.position = goal
    move_base_goal.target_pose.pose.orientation = Quaternion(w=1.0)

    # Send the goal and wait for the result
    client.send_goal(move_base_goal)
    wait = client.wait_for_result()
    if not wait:
        rospy.logerr("Action server not available!")
        rospy.signal_shutdown("Action server not available!")
    else:
        return client.get_result()

def handle_telegram_message(message):
    print(message.text)
    
    # Parse the message and extract the shop and block
    lines = message.text.split("\n")
    shop = lines[0].split(" : ")[1]
    block = lines[1].split(" : ")[1]
    
    # Get the location of the shop and block
    shop_location = locations[f"Shop{shop}"]
    block_location = locations[f"Block{block}"]
    
    # Navigate to the shop first
    movebase_client(shop_location)
    
    # Navigate to the block once the shop has been reached
    movebase_client(block_location)

if __name__ == '__main__':
    try:
        # Initialize the ROS node
        rospy.init_node('movebase_client_py')

        # Initialize the Telebot bot
        bot_token = '5875152047:AAFOjC_Z7PJYHMG2B1Rs4fU0TOnNqDP4yJ4'
        bot = telebot.TeleBot(bot_token)
        
        @bot.message_handler(func=lambda message: True)
        def handle_message(message):
            handle_telegram_message(message)

        bot.polling()
        rospy.loginfo("Ready to receive messages.")
        rospy.spin()

    except rospy.ROSInterruptException:
        rospy.loginfo("Navigation test finished.")
