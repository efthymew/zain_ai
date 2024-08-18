from melee import Button, Controller


def clamp(n, min=0.0, max=1.0): 
    if n < min: 
        return min
    elif n > max: 
        return max
    else: 
        return n 
    
def float_to_bool(number, prob_threshold):
    number = clamp(number)
    if number >= prob_threshold:
        return True
    return False

def apply_deadzone(number, threshold):
    number = clamp(number)
    if abs(number) < threshold:
        return 0.0
    return number

def neutralize_stick(number, threshold):
    number = clamp(number)
    upper = 0.5 + threshold
    lower = 0.5 - threshold
    if number <= upper and number >= lower:
        number = 0.5
    return number


def update_button(controller: Controller, button_type: Button, array_button_value, button_threshold):
    curr_state = controller.current

    # only update on deltas
    if curr_state.button[button_type] and not float_to_bool(array_button_value, button_threshold):
        # release button
        controller.release_button(button_type)

    if not curr_state.button[button_type] and float_to_bool(array_button_value, button_threshold):
        # push button
        controller.press_button(button_type)

def send_input_to_controller(array, controller: Controller, button_threshold=0.6, stick_deadzone=0.1, trigger_deadzone=0.1):
    index = 0
    for button in Button:
        if index >= 12:
            break
        if button == Button.BUTTON_START:
            index += 1
            continue
        update_button(controller, button, array[index], button_threshold)
        index += 1

    control_x, control_y = array[12], array[13]
    c_x, c_y = array[14], array[15]
    l_analog, r_analog = array[16], array[17]

    if controller.current.button[Button.BUTTON_L]:
        # update analog if flag for l is true
        value = apply_deadzone(l_analog, 0.1)
        controller.press_shoulder(Button.BUTTON_L, value)
    
    if controller.current.button[Button.BUTTON_R]:
        # update analog if flag for r is true
        value = apply_deadzone(r_analog, 0.1)
        controller.press_shoulder(Button.BUTTON_R, value)

    controller.tilt_analog(Button.BUTTON_MAIN, neutralize_stick(control_x, 0.1), neutralize_stick(control_y, 0.1))\
    
    controller.tilt_analog(Button.BUTTON_C, neutralize_stick(c_x, 0.1), neutralize_stick(c_y, 0.1))