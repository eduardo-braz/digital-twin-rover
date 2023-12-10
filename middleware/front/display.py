import gi
gi.require_version('Gtk', '3.0')
gi.require_version('WebKit2', '4.0')
from gi.repository import Gtk, Gdk, WebKit2, GLib
from math import pi
from RoverClass import Rover
import CapturaJoystick.MessageBatteryCharge as BatteryCharge
import multiprocessing

rover = Rover()
batteryRaspberry = BatteryCharge.MessageBatteryCharge("Raspberry", -1)
batteryWheels = BatteryCharge.MessageBatteryCharge("Wheels", -1)
batteryArm = BatteryCharge.MessageBatteryCharge("Arm", -1)
batteryCamera = BatteryCharge.MessageBatteryCharge("Camera", -1)

batteryQueue = {
    "battery_cam": multiprocessing.Queue(),
    "battery_arm": multiprocessing.Queue(),
    "battery_movement": multiprocessing.Queue(),
    "battery_raspberry": multiprocessing.Queue()
}

armQueue = {
    "base_value": multiprocessing.Queue(),
    "ext1_value": multiprocessing.Queue(),
    "ext2_value": multiprocessing.Queue(),
    "gripper_close_value": multiprocessing.Queue()
}

arduinoQueue = {
    "velocity_wheels": multiprocessing.Queue(),
    "angle_front": multiprocessing.Queue(),
    "angle_back": multiprocessing.Queue()
 }

class Window(Gtk.Window):
    global rover
    global batteryRaspberry
    global batteryWheels
    global batteryArm
    global batteryCamera
    global queues
    def __init__(self):
        print(f'Log: Display. Baterias: Raspberry {batteryRaspberry.value} Arduino: {batteryWheels.value} Arm: {batteryArm.value} Camera: {batteryCamera.value}')
        Gtk.Window.__init__(self, title="Painel de controle do Rover")
        self.set_default_size(525, 730)
        self.set_position(Gtk.WindowPosition.NONE)
        self.move(0, 0)

        vbox = Gtk.VBox()
        vbox.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1, 1, 1, 1))

        # Adiciona todos os elementos à caixa
        label = Gtk.Label()
        label.set_markup("<span font='Arial 24' foreground='black'>---------------- Camera ----------------</span>")
        label.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(label, False, False, 0)

        page_cam = WebKit2.WebView()
        page_cam.load_uri("http://192.168.2.100:81/stream")
        page_cam.set_size_request(320, 240)
        vbox.pack_start(page_cam, False, False, 0)

        # Label para exibição bateria da camera
        self.battery_cam_label = Gtk.Label()
        self.battery_cam_label.set_halign(Gtk.Align.CENTER)
        self.battery_cam_label.set_use_markup(True)
        vbox.pack_start(self.battery_cam_label, False, False, 0)
        vbox.pack_start(Gtk.Label(), False, False, 5)

        # Label movimentação / rodas
        moviment_label = Gtk.Label()
        moviment_label.set_markup("<span font='Arial 24' foreground='black'>----------------- Rodas -----------------</span>")
        moviment_label.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(moviment_label, False, False, 0)
        vbox.pack_start(Gtk.Label(), False, False, 0)

        # Box para labels Rodas
        moviment_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        moviment_box.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(moviment_box, False, False, 0)

        # Labels Rodas
        self.velocity_label = Gtk.Label()
        self.angle_front_label = Gtk.Label()
        self.angle_back_label = Gtk.Label()

        self.velocity_label.set_use_markup(True)
        self.angle_front_label.set_use_markup(True)
        self.angle_back_label.set_use_markup(True)

        moviment_box.pack_start(self.velocity_label, False, False, 10)
        moviment_box.pack_start(self.angle_front_label, False, False, 10)
        moviment_box.pack_start(self.angle_back_label, False, False, 10)
        vbox.pack_start(Gtk.Label(), False, False, 0)

        # Label para exibição bateria arm
        self.battery_moviment_label = Gtk.Label()
        self.battery_moviment_label.set_halign(Gtk.Align.CENTER)
        self.battery_moviment_label.set_use_markup(True)
        vbox.pack_start(self.battery_moviment_label, False, False, 0)
        vbox.pack_start(Gtk.Label(), False, False, 5)

        # Label arm / braço robótico
        arm_label = Gtk.Label()
        arm_label.set_markup("<span font='Arial 24' foreground='black'>----------- Braço robótico -----------</span>")
        arm_label.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(arm_label, False, False, 0)
        vbox.pack_start(Gtk.Label(), False, False, 0)

        arm_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        arm_box.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(arm_box, False, False, 0)

        # Labels Arm
        self.base_label = Gtk.Label()
        self.ext1_label = Gtk.Label()
        self.ext2_label = Gtk.Label()
        self.gripper_label = Gtk.Label()

        self.base_label.set_use_markup(True)
        self.ext1_label.set_use_markup(True)
        self.ext2_label.set_use_markup(True)
        self.gripper_label.set_use_markup(True)

        arm_box.pack_start(self.base_label, False, False, 10)
        arm_box.pack_start(self.ext1_label, False, False, 10)
        arm_box.pack_start(self.ext2_label, False, False, 10)
        arm_box.pack_start(self.gripper_label, False, False, 10)

        self.update_arm_values()
        vbox.pack_start(Gtk.Label(), False, False, 0)

        # Label para exibição bateria arm
        self.battery_arm_label = Gtk.Label()
        self.battery_arm_label.set_halign(Gtk.Align.CENTER)
        self.battery_arm_label.set_use_markup(True)
        vbox.pack_start(self.battery_arm_label, False, False, 0)
        vbox.pack_start(Gtk.Label(), False, False, 5)

        # Label arm / braço robótico
        rasp_label = Gtk.Label()
        rasp_label.set_markup("<span font='Arial 24' foreground='black'>----------- Raspberry -----------</span>")
        rasp_label.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(rasp_label, False, False, 0)
        vbox.pack_start(Gtk.Label(), False, False, 0)

        # Label para exibição bateria arm
        self.battery_raspberry_label = Gtk.Label()
        self.battery_raspberry_label.set_halign(Gtk.Align.CENTER)
        self.battery_raspberry_label.set_use_markup(True)
        vbox.pack_start(self.battery_raspberry_label, False, False, 0)
        self.update_battery_label()

        ################################################################
        self.add(vbox)

        #### Atualiza labels
        self.timeout_id_battery = GLib.timeout_add(1000, self.update_battery_label)
        self.timeout_id_moviment = GLib.timeout_add(1000, self.update_moviment_values)
        self.timeout_id_arm = GLib.timeout_add(1000, self.update_arm_values)

    def update_battery_label(self):
        values = {
            "battery_cam": -1,
            "battery_arm": -1,
            "battery_movement": -1,
            "battery_raspberry": -1
        }

        for key in batteryQueue:
            try:
                values[key] = batteryQueue[key].get_nowait()
                print(f"Log: Display. Valor recebido em {key}: ", values[key])
            except Exception as e:
                pass

        battery_cam = values['battery_cam'] if values['battery_cam'] != -1 else batteryCamera.value
        battery_arm = values['battery_arm'] if values['battery_arm'] != -1 else batteryArm.value
        battery_movement = values['battery_movement'] if values['battery_movement'] != -1 else batteryWheels.value
        battery_raspberry = values['battery_raspberry'] if values['battery_raspberry'] != -1 else batteryRaspberry.value

        batteryCamera.value = battery_cam if battery_cam != batteryCamera.value else batteryCamera.value
        batteryArm.value = battery_arm if battery_arm != batteryArm.value else batteryArm.value
        batteryWheels.value = battery_movement if battery_movement != batteryWheels.value else batteryWheels.value
        batteryRaspberry.value = battery_raspberry if battery_raspberry != batteryRaspberry.value else batteryRaspberry.value

        self.battery_cam_label.set_markup("<span font='Arial 12' foreground='{}'><b>Bateria: {}%</b></span>"
                                          .format(self.battery_color(battery_cam), battery_cam))
        self.battery_arm_label.set_markup("<span font='Arial 12' foreground='{}'><b>Bateria: {}%</b></span>"
                                          .format(self.battery_color(battery_arm), battery_arm))
        self.battery_moviment_label.set_markup("<span font='Arial 12' foreground='{}'><b>Bateria: {}%</b></span>"
                                               .format(self.battery_color(battery_movement), battery_movement))
        self.battery_raspberry_label.set_markup("<span font='Arial 12' foreground='{}'><b>Bateria: {}%</b></span>"
                                                .format(self.battery_color(battery_raspberry), battery_raspberry))
        return True

    def battery_color(self, battery):
        if battery > 30:
            color = "green"
        else:
            color = "red"
        return color

    def update_moviment_values(self):
        values = {
            "velocity_wheels": -1,
            "angle_front": -1,
            "angle_back": -1
        }

        for key in arduinoQueue:
            try:
                values[key] = arduinoQueue[key].get_nowait()
                print(f"Log: Display. Valor recebido em {key}: ", values[key])
            except Exception as e:
                pass

        velocity_wheels = values['velocity_wheels'] if values['velocity_wheels'] != -1 else rover.wheels.speed
        angle_front = values['angle_front'] if values['angle_front'] != -1 else rover.wheels.frontAngle
        angle_back = values['angle_back'] if values['angle_back'] != -1 else rover.wheels.backAngle

        rover.wheels.speed = velocity_wheels if velocity_wheels != rover.wheels.speed else rover.wheels.speed
        rover.wheels.frontAngle = angle_front if angle_front != rover.wheels.frontAngle else rover.wheels.frontAngle
        rover.wheels.backAngle = angle_back if angle_back != rover.wheels.backAngle else rover.wheels.backAngle

        if rover.wheels.speed < rover.wheels.speedMin:
            velocity_wheels = 0
        else:
            velocity_wheels = self.RPM_to_ms(abs(rover.wheels.speed))

        self.velocity_label.set_label("<span font='Arial 11'><b>Velocidade: {:.2f}m/s</b></span>".format(velocity_wheels))
        self.angle_front_label.set_label("<span font='Arial 11'><b>Ângulo frontal: {:.0f}º</b></span>".format(angle_front))
        self.angle_back_label.set_label("<span font='Arial 11'><b>Ângulo traseira: {:.0f}º</b></span>".format(angle_back))
        return True

    def RPM_to_ms(self, rpm):
        return 0.0325 * (pi / 30) * self.map_value(rpm, 0, 255, 0, 200)

    def map_value(self, value, from_min, from_max, to_min, to_max):
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min

    def update_arm_values(self):
        values = {
            "base_value": -1,
            "ext1_value": -1,
            "ext2_value": -1,
            "gripper_close_value": -1
        }

        for key in armQueue:
            try:
                values[key] = armQueue[key].get_nowait()
                print(f"Log: Display. Valor recebido em {key}: ", values[key])
            except Exception as e:
                pass

        base_value = values['base_value'] if values['base_value'] != -1 else rover.arm.base
        ext1_value = values['ext1_value'] if values['ext1_value'] != -1 else rover.arm.ext1
        ext2_value = values['ext2_value'] if values['ext2_value'] != -1 else rover.arm.ext2
        gripper_close_value = values['gripper_close_value'] if values['gripper_close_value'] != -1 else rover.arm.gripperClosed

        rover.arm.base = base_value if base_value != rover.arm.base else rover.arm.base
        rover.arm.ext1 = ext1_value if ext1_value != rover.arm.ext1 else rover.arm.ext1
        rover.arm.ext2 = ext2_value if ext2_value != rover.arm.ext2 else rover.arm.ext2
        rover.arm.gripperClosed = gripper_close_value if gripper_close_value != rover.arm.gripperClosed else rover.arm.gripperClosed

        if gripper_close_value:
            gripper_status = "Fechado"
        else:
            gripper_status = "Aberto"

        self.base_label.set_label("<span font='Arial 11'><b>Ângulo base: {}º</b></span>".format(base_value))
        self.ext1_label.set_label("<span font='Arial 11'><b>Ângulo ext1: {}º</b></span>".format(ext1_value))
        self.ext2_label.set_label("<span font='Arial 11'><b>Ângulo ext2: {}º</b></span>".format(ext2_value))
        self.gripper_label.set_label("<span font='Arial 11'><b>Gripper: {}</b></span>".format(gripper_status))
        return True

def main_window(roverClass, batRaspberry, batWheels, batArm, batCamera):
    global rover
    global batteryRaspberry
    global batteryWheels
    global batteryArm
    global batteryCamera
    rover = roverClass
    batteryRaspberry = batRaspberry
    batteryWheels = batWheels
    batteryArm = batArm
    batteryCamera = batCamera
    print(f"Log: Display. Velocidade: {rover.wheels.speed}")
    print(f"Log: Display. Bateria Raspberry: {batteryRaspberry.value}")
    main_window = Window()
    main_window.connect("destroy", Gtk.main_quit)
    main_window.show_all()
    Gtk.main()

def main_window(battery_queue, arm_queue, arduino_queue):
    global rover
    global batteryRaspberry
    global batteryWheels
    global batteryArm
    global batteryCamera
    global batteryQueue
    global armQueue
    global arduinoQueue

    batteryQueue = battery_queue
    armQueue = arm_queue
    arduinoQueue = arduino_queue

    main_window = Window()
    main_window.connect("destroy", Gtk.main_quit)
    main_window.show_all()
    Gtk.main()
