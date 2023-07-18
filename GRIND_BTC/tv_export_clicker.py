import pyautogui
import keyboard


from time import sleep

def move_mouse_to_coordinates(x, y):
  pyautogui.moveTo(x, y)

def print_mouse_coordinates():
    while(1):
        x, y = pyautogui.position()
        print(f"X: {x} Y: {y}")
        sleep(1)

sleep(2)
move_mouse_to_coordinates(1347, 125)
pyautogui.click()
sleep(1)
move_mouse_to_coordinates(1446, 320)
pyautogui.click()
sleep(1)
move_mouse_to_coordinates(941, 611)
sleep(1)
pyautogui.click()

def on_key_press(event):
    if event.name == 'esc':
        print("ESC key pressed. Exporting TV Data...")
        
        sleep(0.5)
        move_mouse_to_coordinates(1347, 125)
        pyautogui.click()
        sleep(0.5)
        move_mouse_to_coordinates(1446, 320)
        pyautogui.click()
        sleep(0.5)
        #vmove_mouse_to_coordinates(941, 611)
        # sleep(1)
        # pyautogui.click()
        # sleep(1)
        move_mouse_to_coordinates(939, 587)
        sleep(0.5)
        pyautogui.click()
                

keyboard.on_press(on_key_press)

