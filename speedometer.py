import cv2
import numpy as np
import time
import matplotlib.pyplot as plt
import math

"""
Define some read-only globals for our program
"""
MIN_CONTOUR_AREA = 30000
NUM_FRAMES = 1
WIDTH_THRESHOLD_PERCENTAGE = 0.1

BLUE_COLOR = (255, 0, 0)
GREEN_COLOR = (0, 255, 0)
RED_COLOR = (0, 0, 225)
WHITE_COLOR = (225, 225, 225)

DIRECTION_FROM_LEFT = 'LEFT'
DIRECTION_FROM_RIGHT = 'RIGHT'

def calculate_speed(p1, p2, time):
  diff = abs(p1 - p2)
  return math.trunc(diff / time)

"""
"""
def do_capture():

  is_timing = False
  completed_timing = False
  start_time = -1
  end_time = -1
  direction = ''

  frame_counter = -1

  start_rx = -1
  start_ry = -1

  cap = cv2.VideoCapture(0)

  max_width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  max_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

  x_left_threshold = int(math.floor(max_width * WIDTH_THRESHOLD_PERCENTAGE))
  x_right_threshold = int(max_width - x_left_threshold)
  x_distance = int(max_width - x_left_threshold * 2)

  print('Frame stats:')
  print('\tmax_width=%s' % max_width)
  print('\tx_left_threshold=%s' % x_left_threshold)
  print('\tx_right_threshold=%s' % x_right_threshold)
  print('\tx_distance=%s' % x_distance)

  # Get the current frame
  _, frame = cap.read()
  frame = cv2.flip(frame, 1)

  while(True):

    if cv2.waitKey(1) == 27: 
      break

    if (frame_counter % NUM_FRAMES == 0):
      # Get the next frame
      _, next_frame = cap.read()
      next_frame = cv2.flip(next_frame, 1)

      # Get difference between the frames and do thresholding
      frame_diff = cv2.absdiff(frame, next_frame)
      frame_diff = cv2.cvtColor(frame_diff, cv2.COLOR_BGR2GRAY)
      frame_diff = cv2.blur(frame_diff, (4, 4))
      _, frame_diff = cv2.threshold(frame_diff, 10, 255, cv2.THRESH_BINARY)

      # Find the contours from the thresholded frame_diff
      contours, _ = cv2.findContours(frame_diff, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

      # Loop through the contours to find one larger than MIN_CONTOUR_AREA
      for contour in contours:

        if cv2.contourArea(contour) > MIN_CONTOUR_AREA:
          # Draw boundary lines
          cv2.line(frame, (x_left_threshold, 0), (x_left_threshold, max_height), WHITE_COLOR, 3)
          cv2.line(frame, (x_left_threshold, 0), (x_left_threshold, max_height), WHITE_COLOR, 3)
          cv2.line(frame, (x_right_threshold, 0), (x_right_threshold, max_height), WHITE_COLOR, 3)
          cv2.line(frame, (x_right_threshold, 0), (x_right_threshold, max_height), WHITE_COLOR, 3)

          # Get bounding shapes
          (x, y, w, h) = cv2.boundingRect(contour)
          (rx, ry), radius = cv2.minEnclosingCircle(contour)
          rx = int(rx)
          ry = int(ry)

          # Draw bounding rectangle
          cv2.rectangle(frame, (x, y), (x+w, y+h), GREEN_COLOR, 1)

          # Draw contour radius (blue = previous, green = current) 
          # cv2.circle(frame, (int(start_rx), int(start_ry)), 5, BLUE_COLOR, 1)
          # cv2.circle(frame, (rx, ry), 5, WHITE_COLOR, 1)

          if is_timing:
            if direction == DIRECTION_FROM_LEFT:
              if rx > x_right_threshold:
                print('Crossed the finish line!')
                completed_timing = True
            elif direction == DIRECTION_FROM_RIGHT:
              if rx < x_left_threshold:
                print('Crossed the finish line!')
                completed_timing = True
            else:
              print('BAD STATE - Unknown direction')
              reset_timer_variables()

            if completed_timing:
              print('Timer has completed!')

              end_time = time.time()
              time_diff = end_time - start_time
              speed = math.trunc(x_distance / time_diff)

              cv2.putText(frame, 'Took %ds to cross %dp %d pix/sec' % (time_diff, x_distance, speed), (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, BLUE_COLOR, 3)
              completed_timing = True
            else:
              cv2.putText(frame, 'Cross the finish line on the other side!', (rx, ry), cv2.FONT_HERSHEY_SIMPLEX, 1, GREEN_COLOR, 3)
            
          else:
            if rx < x_left_threshold:
              direction = DIRECTION_FROM_LEFT
            elif rx > x_right_threshold:
              direction = DIRECTION_FROM_RIGHT
            else:
              cv2.putText(frame, 'Move outside of boundary lines to start timer', (rx, ry), cv2.FONT_HERSHEY_SIMPLEX, 1, WHITE_COLOR, 3)

            if len(direction) > 0:
              print('Timer activated! [%s]' % direction)
              is_timing = True
              start_time = time.time()

          break

      # Show frame, and re-assign variables for next loop
      cv2.imshow('video', frame)
      frame = next_frame.copy()

      if completed_timing:
        is_timing = False
        completed_timing = False
        start_time = -1
        end_time = -1
        direction = ''

    frame_counter = (frame_counter + 1) % NUM_FRAMES

    

"""
"""
def main():
  print('Starting video capture...\n')
  do_capture()
  print('Ending video capture...\n')
  cv2.destroyAllWindows()

  

"""
"""
if __name__ == '__main__':
  main()