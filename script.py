import mdl
import math
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands, symbols ) ==========

  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present

  If vary is found, but frames is not, the entire
  program should exit.

  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.

  jdyrlandweaver
  ==================== """
def first_pass( commands ):

    global num_frames
    global basename

    keylist = []

    for cmd in commands:
      keylist.append(cmd[0])

    for cmd in commands:
      if (cmd[0] == "frames"):
          if "basename" not in keylist:
            basename = "frame"
            print("Basename defaulted to 'frame'")
          num_frames = int(cmd[1])
          print("Frames set to: " + str(num_frames))
              
      if cmd[0] == "basename":
        basename = cmd[1]
        print("Basename set to: " + basename)

      if cmd[0] == "vary":
        if "frames" in keylist:
            pass

        else:
            print("Fatal Script Error -- No frames value set!\n\nProgram Exiting...")
            return False

    return True


"""======== second_pass( commands ) ==========

  In order to set the knobs for animation, we need to keep
  a separate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).

  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.

  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands):
    global num_frames
    klist = []
    knob = ""

    count = 0
    while count < num_frames:
      klist.append({})
      count += 1

    for cmd in commands:
      if cmd[0] == "vary":
        knob = cmd[1]
        if (cmd[2] < -1 or cmd[3] > num_frames or cmd[2] > cmd[3]):
          print("[" + knob + "] Frame Error -- Invalid frame range!\n\nProgram Exiting..." + str(num_frames))
          return
        else:
          start = cmd[2]
          end = cmd[3]
          top = cmd[4]
          bottom = cmd[5]

          calc = ((bottom * 1.0) - top) / (end - start)

          count = start
          while count <= end:
            #print(knob)
            #print("start: " + str(start) + " -- end: " + str(end))
            #print("top: " + str(top) + " -- bottom: " + str(bottom))
            #print("calc: " + str(calc))
            if count == 0:
              klist[count][knob] = math.fabs(calc * count)
            else:
              klist[count][knob] = klist[count - 1][knob] + calc
            count += 1
    #print(klist)
    return klist


def third_pass( commands, symbols ):
    global knoblist
    global basename

    count = 0
    while count < num_frames: #start of outer loop
      #print(symbols)

      color = [255, 255, 255]
      tmp = new_matrix()
      ident( tmp )

      ident(tmp)
      stack = [ [x[:] for x in tmp] ]
      screen = new_screen()
      tmp = []
      step = 0.1
      for command in commands:
          c = command[0]
          args = command[1:]
          #print args

          if c == 'box':
              add_box(tmp,
                      args[0], args[1], args[2],
                      args[3], args[4], args[5])
              matrix_mult( stack[-1], tmp )
              draw_polygons(tmp, screen, color)
              tmp = []
          elif c == 'sphere':
              add_sphere(tmp,
                         args[0], args[1], args[2], args[3], step)
              matrix_mult( stack[-1], tmp )
              draw_polygons(tmp, screen, color)
              tmp = []
          elif c == 'torus':
              add_torus(tmp,
                        args[0], args[1], args[2], args[3], args[4], step)
              matrix_mult( stack[-1], tmp )
              draw_polygons(tmp, screen, color)
              tmp = []
          elif c == 'move':
              val = 1
              if (args[3] != None):
                knob = args[3]
                symbols[knob][1] = knoblist[count][knob]
                val = knoblist[count][knob]
              tmp = make_translate(args[0] * val, args[1] * val, args[2] * val)
              matrix_mult(stack[-1], tmp)
              stack[-1] = [x[:] for x in tmp]
              tmp = []
          elif c == 'scale':
              val = 1
              if (args[3] != None):
                knob = args[3]
                symbols[knob][1] = knoblist[count][knob]
                val = knoblist[count][knob]
              tmp = make_scale(args[0] * val, args[1] * val, args[2] * val)
              matrix_mult(stack[-1], tmp)
              stack[-1] = [x[:] for x in tmp]
              tmp = []
          elif c == 'rotate':
              val = 1
              if (args[2] != None):
                knob = args[2]
                symbols[knob][1] = knoblist[count][knob]
                val = knoblist[count][knob]
              theta = args[1] * (math.pi/180)
              if args[0] == 'x':
                  tmp = make_rotX(theta * val)
              elif args[0] == 'y':
                  tmp = make_rotY(theta * val)
              else:
                  tmp = make_rotZ(theta * val)
              matrix_mult( stack[-1], tmp )
              stack[-1] = [ x[:] for x in tmp]
              tmp = []
          elif c == 'push':
              stack.append([x[:] for x in stack[-1]] )
          elif c == 'pop':
              stack.pop()
          elif c == 'display':
              display(screen)
          #elif c == 'save':

      if (count < 10):
        save_extension(screen, "anim/" + basename + "0" + str(count) + ".png")
        print("Frame saved to: " + basename + "0" + str(count))
      else:
        save_extension(screen, "anim/" + basename + str(count) + ".png")
        print("Frame saved to: " + basename + str(count))

      count += 1
      #print(count)
    #end of outer loop


def run(filename):
    """
    This function runs an mdl script
    """

    global basename
    global num_frames
    global knoblist
    basename = ''
    num_frames = 0
    status = True
   

    p = mdl.parseFile(filename)

    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    status = first_pass(commands)

    if (status == True):
      knoblist = second_pass(commands)
      #print knoblist
      third_pass(commands, symbols)

    make_animation(basename)
 
    
