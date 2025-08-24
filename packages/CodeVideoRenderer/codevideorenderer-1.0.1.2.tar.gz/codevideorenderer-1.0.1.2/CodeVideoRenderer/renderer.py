from manim import *
from contextlib import *
import random, logging, sys, os, re

def CodeVideo(video_name="CodeVideo", interval=0.3, floating_interval=True, floating_camera=True, 
              scale=0.3, paragraph_config={'font':'Consolas'}, **kwargs):

    logging.basicConfig(level=logging.INFO)
    config.output_file = video_name

    # check interval
    min_interval = 0.3
    if interval < min_interval:
        raise ValueError(f"interval is too small, please set a larger value not less than {min_interval}")

    # Camera that smoothly moves to a cursor's position every second without infinite loops.
    class LoopMovingCamera(VGroup):

        def __init__(
            self,
            mob,
            scene,
            move_interval=1,
            move_duration=0.5,
            **kwargs,
        ):
            super().__init__(**kwargs)
            self.mob = mob
            self.scene = scene
            self.move_interval = move_interval
            self.move_duration = move_duration
            self.elapsed_time = 0
            self.is_moving = False  # Indicate whether it is moving
            self.move_progress = 0  # Move progress (0 to 1)
            self.start_pos = None   # Moving start position
            self.target_pos = None  # Moving target position

            self.add_updater(lambda m, dt: self.update_camera_position(dt))

        def update_camera_position(self, dt):
            # If it is moving, handle smooth transition
            if self.is_moving:
                self.move_progress += dt / self.move_duration
                # Calculate current position (interpolation from start to target)
                current_pos = interpolate(
                    self.start_pos,
                    self.target_pos,
                    smooth(self.move_progress)  # Apply smooth transition function
                )
                self.scene.camera.frame.move_to(current_pos)
                
                # Reset status after movement is complete
                if self.move_progress >= 1:
                    self.is_moving = False
                    self.move_progress = 0
                return

            # If not moving, accumulate time to determine whether to start moving
            self.elapsed_time += dt
            if self.elapsed_time >= self.move_interval:
                self.start_pos = self.scene.camera.frame.get_center()  # Record current position
                self.target_pos = self.mob.get_center() + (            # Get target position
                    UP*random.uniform(-0.1,0.1)+LEFT*random.uniform(-0.1,0.1)
                    if floating_camera else 0
                )
                self.is_moving = True                                  # Start moving
                self.elapsed_time -= self.move_interval                # Reset timer

    class code_video(MovingCameraScene):

        # whether the text has chinese characters or punctuation
        def has_chinese(self, text):
            pattern = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uf900-\ufaff]')
            return bool(pattern.search(text))
        
        # no manim output
        @contextmanager
        def _no_manim_output(self):
            manim_logger = logging.getLogger("manim")
            original_manim_level = manim_logger.getEffectiveLevel()
            original_stderr = sys.stderr
            try:
                manim_logger.setLevel(logging.WARNING)
                sys.stderr = open(os.devnull, 'w')
                yield
            finally:
                manim_logger.setLevel(original_manim_level)
                sys.stderr = original_stderr

        def construct(self):
            global code, line_number

            # check arguments
            if {"code_string", "code_file"}.issubset(kwargs):
                raise ValueError("Only one of code_string and code_file can be passed in")
            
            # get code string and check if it contains chinese characters or punctuation
            if "code_string" in kwargs:
                code_strlines = kwargs["code_string"]
                if self.has_chinese(code_strlines):
                    raise ValueError("There are Chinese characters or punctuation in the code, please use English")
            elif "code_file" in kwargs:
                with open(os.path.abspath(kwargs["code_file"]), "r") as f:
                    try:
                        code_strlines = f.read()
                    except UnicodeDecodeError:
                        raise ValueError("There are Chinese characters or punctuation in the code, please use English") from None

            # split each line of code, so that code_strlines can be accessed using code_strlines[line][column]
            code_strlines = code_strlines.split("\n")

            # replace tab with 4 spaces
            if "code_string" in kwargs:
                kwargs["code_string"] = kwargs["code_string"].replace("\t", "    ")
            elif "code_file" in kwargs:
                with open(os.path.abspath(kwargs["code_file"]), "r") as f:
                    kwargs["code_string"] = f.read().replace("\t", "    ")
                    kwargs.pop("code_file")

            # initialize cursor
            cursor_width = 0.0005
            cursor = RoundedRectangle(height=0.35, width=cursor_width, corner_radius=cursor_width/2, 
                                      fill_opacity=1, fill_color=WHITE, color=WHITE).set_z_index(2)
            
            # initialize code block
            code_block = Code(paragraph_config=paragraph_config, **kwargs)
            # window = code_block.submobjects[0] # code window
            line_numbers = code_block.submobjects[1].set_color(GREY) # line numbers
            code = code_block.submobjects[2].set_z_index(2) # code

            # occupy block
            # use '#' to occupy, prevent no volume space
            line_number = len(line_numbers)
            kwargs.pop("code_string") # pop code_string parameter, prevent Code class error
            occupy = Code(
                code_string=line_number*(max([len(code[i]) for i in range(line_number)])*'#' + '\n'),
                paragraph_config=paragraph_config,
                **kwargs
            ).submobjects[2]

            code_line_rectangle = SurroundingRectangle(occupy[0], color="#333333", fill_opacity=1, stroke_width=0).set_z_index(1)
            
            self.camera.frame.scale(scale).move_to(occupy[0][0].get_center())
            self.add(line_numbers[0].set_color(WHITE), code_line_rectangle)
            self.wait()

            #==============================================================================================================
            self.add(cursor)
            cursor.next_to(occupy[0][0], LEFT, buff=-cursor_width) # cursor move to the left of occupy block
        
            # create loop moving camera
            moving_cam = LoopMovingCamera(
                mob=cursor,
                scene=self,
                move_interval=0.1,
                move_duration=0.5
            )
            self.add(moving_cam)
            
            # traverse code lines
            for line in range(len(code)):
                # set line number color
                line_numbers.set_color(GREY)
                line_numbers[line].set_color(WHITE)

                char_num = len(code[line]) # code line character number
                
                print(f"\033[34mRendering line {line+1}/{len(code)}:\033[0m {code_strlines[line].lstrip()}")
                print(f"      0%|          | 0/{char_num}" if char_num != 0 else f"    100%|##########| 0/0", end='')

                # if the line is empty, move the cursor to the left of the occupy block and wait
                if code_strlines[line] == '':
                    cursor.next_to(occupy[line], LEFT, buff=-cursor_width) # cursor move to the left of occupy block
                    self.wait(random.uniform(interval-0.05, interval+0.05) if floating_interval else interval)
                
                code_line_rectangle.set_y(occupy[line].get_y())
                
                self.add(line_numbers[line]) # add line number
                line_y = line_numbers[line].get_y() # line number y coordinate
                
                # traverse code line characters
                is_leading_space = True # whether it is a leading space
                for column in range(char_num):

                    # if it is a leading space, skip
                    if code_strlines[line][column] == ' ' and is_leading_space:
                        pass
                    else:
                        is_leading_space = False

                        char = code[line][column] # code line character
                        occupy_char = occupy[line][column] # occupy block character
                        self.add(char) # add code line character
                        cursor.next_to(occupy_char, RIGHT, buff=0.05) # cursor move to the right of occupy block
                        cursor.set_y(line_y-0.05) # cursor y coordinate in the same line
                        self.wait(random.uniform(interval-0.05, interval+0.05) if floating_interval else interval)

                    # output progress
                    percent = int((column+1)/char_num*100)
                    percent_spaces = (3-len(str(percent)))*' '
                    hashtags = percent//10*'#'
                    number = percent%10 if percent%10 != 0 else ''
                    progress_bar_spaces = (10-percent//10 if percent%10 == 0 else 10-percent//10-1)*' '
                    print(f"\r    {percent_spaces}{percent}%|{hashtags}{number}{progress_bar_spaces}| {column+1}/{char_num}", end='')

                print(f"\n    \033[32mSuccessfully rendered line {line+1}\033[0m\n")

            self.wait()
            logging.info("Combining to Movie file.")
            print()

        def render(self, **kwargs):
            with self._no_manim_output():
                super().render(**kwargs)
            logging.info(f"File ready at '{self.renderer.file_writer.movie_file_path}'")
            print()
            logging.info(f"Rendered {video_name}\nTyping {sum(len(code[line]) for line in range(line_number))} characters")

    return code_video()

