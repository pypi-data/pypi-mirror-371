import turtle
import random
import time

def run_snake_game():
    """
    The main function to run the classic Snake game.
    """
    # Set up the screen
    screen = turtle.Screen()
    screen.title("Python Snake Game")
    screen.bgcolor("black")
    screen.setup(width=600, height=600)
    screen.tracer(0)  # Turns off the screen updates

    # Snake head
    head = turtle.Turtle()
    head.speed(0)
    head.shape("square")
    head.color("green")
    head.penup()
    head.goto(0, 0)
    head.direction = "stop"

    # Snake food
    food = turtle.Turtle()
    food.speed(0)
    food.shape("circle")
    food.color("red")
    food.penup()
    food.goto(0, 100)

    segments = []
    score = 0

    # Score display
    pen = turtle.Turtle()
    pen.speed(0)
    pen.shape("square")
    pen.color("white")
    pen.penup()
    pen.hideturtle()
    pen.goto(0, 260)
    pen.write("Score: 0", align="center", font=("Courier", 24, "normal"))

    # Functions
    def go_up():
        if head.direction != "down":
            head.direction = "up"

    def go_down():
        if head.direction != "up":
            head.direction = "down"

    def go_left():
        if head.direction != "right":
            head.direction = "left"

    def go_right():
        if head.direction != "left":
            head.direction = "right"

    def move():
        if head.direction == "up":
            y = head.ycor()
            head.sety(y + 20)
        if head.direction == "down":
            y = head.ycor()
            head.sety(y - 20)
        if head.direction == "left":
            x = head.xcor()
            head.setx(x - 20)
        if head.direction == "right":
            x = head.xcor()
            head.setx(x + 20)

    def game_over():
        nonlocal score
        # Clear the previous score
        pen.clear()

        # Write "GAME OVER"
        pen.goto(0, 50)
        pen.write("GAME OVER", align="center", font=("Courier", 48, "bold"))

        # Write the final score
        pen.goto(0, -50)
        pen.write("Final Score: {}".format(score), align="center", font=("Courier", 24, "normal"))

        # Update the screen to show the text
        screen.update()

        # Wait and then close the window
        time.sleep(3)
        screen.bye()

    # Keyboard bindings
    screen.listen()
    screen.onkey(go_up, "Up")
    screen.onkey(go_down, "Down")
    screen.onkey(go_left, "Left")
    screen.onkey(go_right, "Right")

    # Main game loop
    while True:
        screen.update()

        # Check for a collision with the border
        if head.xcor() > 290 or head.xcor() < -290 or head.ycor() > 290 or head.ycor() < -290:
            game_over()
            break  # Exit the loop

        # Check for a collision with the food
        if head.distance(food) < 20:
            x = random.randint(-290, 290)
            y = random.randint(-290, 290)
            food.goto(x, y)

            # Add a new segment
            new_segment = turtle.Turtle()
            new_segment.speed(0)
            new_segment.shape("square")
            new_segment.color("grey")
            new_segment.penup()
            segments.append(new_segment)

            # Increase the score
            score += 10
            pen.clear()
            pen.write("Score: {}".format(score), align="center", font=("Courier", 24, "normal"))

        # Move the end segments first in reverse order
        for index in range(len(segments) - 1, 0, -1):
            x = segments[index - 1].xcor()
            y = segments[index - 1].ycor()
            segments[index].goto(x, y)

        # Move segment 0 to where the head is
        if len(segments) > 0:
            x = head.xcor()
            y = head.ycor()
            segments[0].goto(x, y)

        move()

        # Check for head collision with the body segments
        for segment in segments:
            if segment.distance(head) < 20:
                game_over()
                break # Exit the loop
        else: # This 'else' belongs to the 'for' loop
            time.sleep(0.1)
            continue
        break # This break belongs to the 'for' loop

# run_snake_game()