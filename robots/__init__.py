from robots.input_robot.robot import run as input_robot
from robots.content_robot.robot import run as content_robot
from robots.image_robot.robot import run as image_robot
#from robots.image_robot.robot import get_images as image_robot
from robots.video_robot.robot import run as video_robot
import os

__all__ = ['input_robot', 'content_robot', 'image_robot', 'video_robot']

if 'credentials.json' not in os.listdir('.'):
    
    from shutil import copyfile
    
    src = os.path.join(os.path.dirname(__file__), 'credentials.json')
    dst = os.path.join(os.path.dirname(os.path.abspath(__name__)), 'credentials.json')
    copyfile(src=src, dst=dst)
    print(f'You have to set the file "credentials.json" in {dst} to be able to use this module.')
    exit()
else:
    # Implementar rotina para checar o arquivo
    pass