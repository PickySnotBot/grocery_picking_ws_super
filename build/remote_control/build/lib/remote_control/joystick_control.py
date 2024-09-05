import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import paho.mqtt.client as mqtt

class JoystickControl(Node):
    def __init__(self):
        super().__init__('joystick_control')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        self.declare_parameter('mqtt_broker', '192.168.1.135')
        self.declare_parameter('mqtt_port', 1883)
        self.declare_parameter('mqtt_topic', 'joystick_data')

        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

        mqtt_broker = self.get_parameter('mqtt_broker').get_parameter_value().string_value
        mqtt_port = self.get_parameter('mqtt_port').get_parameter_value().integer_value
        self.mqtt_client.connect(mqtt_broker, mqtt_port, 60)

        # Start the MQTT loop in a non-blocking way
        self.mqtt_client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        self.get_logger().info(f'Connected to MQTT broker with result code {rc}')
        mqtt_topic = self.get_parameter('mqtt_topic').get_parameter_value().string_value
        client.subscribe(mqtt_topic)

    def on_message(self, client, userdata, msg):
        self.get_logger().info(f'Message received: {msg.topic}')
        buffer = msg.payload

        twist = Twist()

        # Decode the joystick buffer into integers
        leftJoyX = (buffer[0] << 8) | buffer[1]
        leftJoyY = (buffer[2] << 8) | buffer[3]
        leftJoyButton = buffer[4]

        rightJoyX = (buffer[5] << 8) | buffer[6]
        rightJoyY = (buffer[7] << 8) | buffer[8]
        rightJoyButton = buffer[9]

        # Calculate the mapped values for leftJoyX and leftJoyY
        leftJoyX_mapped = 2 * (leftJoyX - 1921) / (4095 - 1921)
        leftJoyY_mapped = 2 * (leftJoyY - 1921) / (4095 - 1921)

        # Calculate the mapped value for rightJoyY
        rightJoyY_mapped = 2 * (rightJoyY - 1933) / (4095 - 1933)

        # Ensure the values are within the -1.0 to 1.0 range
        leftJoyX_mapped = max(-1.0, min(1.0, leftJoyX_mapped)) * 0.2
        leftJoyY_mapped = max(-1.0, min(1.0, leftJoyY_mapped)) * 0.2
        rightJoyY_mapped = max(-1.0, min(1.0, rightJoyY_mapped)) * 0.2

        # Apply deadband
        deadband_threshold = 0.05
        if abs(leftJoyX_mapped) <= deadband_threshold:
            leftJoyX_mapped = 0.0
        if abs(leftJoyY_mapped) <= deadband_threshold:
            leftJoyY_mapped = 0.0
        if abs(rightJoyY_mapped) <= deadband_threshold:
            rightJoyY_mapped = 0.0

        # Update the Twist message
        twist.linear.x = -leftJoyX_mapped
        twist.linear.y = leftJoyY_mapped
        twist.angular.z = -rightJoyY_mapped

        self.publisher_.publish(twist)
        self.get_logger().info(f'Published Twist message: {twist.linear.x , twist.linear.y , twist.angular.z}')

def main(args=None):
    rclpy.init(args=args)
    node = JoystickControl()
    rclpy.spin(node)

    # Clean up on shutdown
    node.mqtt_client.loop_stop()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
