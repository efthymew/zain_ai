
import melee
from button_helper import send_input_to_controller

inputs = [[0.0 for i in range(18)] for j in range(10)]

console = melee.Console(path="C:/Users/Graham/AppData/Roaming/Slippi Launcher/netplay/")

controller = melee.Controller(console=console, port=1)
controller_human = melee.Controller(console=console,
                                    port=2,
                                    type=melee.ControllerType.GCN_ADAPTER)

console.run()
console.connect()

controller.connect()
controller_human.connect()

send_input_to_controller(inputs[0], controller)