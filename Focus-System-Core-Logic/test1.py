import pygame
pygame.mixer.init()
pygame.mixer.music.load(r"C:\Users\Acer\Desktop\college-project\focus_system\alert1.wav")
pygame.mixer.music.play()
while pygame.mixer.music.get_busy():
    pass
