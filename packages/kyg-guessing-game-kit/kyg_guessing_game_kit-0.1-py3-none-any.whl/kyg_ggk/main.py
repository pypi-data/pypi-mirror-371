import tkinter as tk
import math
from .fastguess import guesser, fguesser

def main():
    # Create a new window
    window = tk.Tk()

    # Set Window Title
    window.title('KYG G U E S S I N G G A M E KIT')

    # Set the window to start maximized
    window.state('zoomed')

    # Set the background color of the window
    window.config(bg="#f0f0f0")

    # --- Configure the grid layout to be responsive ---
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)
    window.grid_columnconfigure(2, weight=1)
    window.grid_rowconfigure(0, weight=1)
    window.grid_rowconfigure(1, weight=4)
    window.grid_rowconfigure(2, weight=1)
    window.grid_rowconfigure(3, weight=1)
    window.grid_rowconfigure(4, weight=1)

    #Initialize the values
    count = 1
    guess = 1
    maxval = 100
    maxtries = 0

    # --- Functions for Buttons and Game Logic ---
    def end_game():
        """A central function to end the game and reset button states."""
        higher_button.config(state='disabled')
        lower_button.config(state='disabled')
        yes_button.config(state='disabled')
        play_button.config(state='normal') # <-- Re-enable Play button

    def yes():
        nonlocal count, guess, maxtries
        if count <= maxtries:
            result_text = (f"************** I won the bet **************\n"
                            f"Number \"{guess}\" Guessed in \"{count}\" tries \n"
                            f"Thank you for Playing \n"
                            f"Want to Play Again -> Click on Play Button")
        else:
            result_text = "You Won the bet, I couldn't guess in time!"
        update_result(result_text)
        end_game() # <-- End the game and reset buttons

    def high():
        nonlocal count, guess, maxval, maxtries
        count += 1
        if count > maxtries:
            update_result(f"I ran out of tries! You win!\nYour number was not {guess}.\nClick PLAY to start again.")
            end_game()
            return
        guess = fguesser('h', maxval)
        result_text = (f"Guesses Left : {maxtries - count + 1}\n"
                       f"Is it {guess}?")
        update_result(result_text)

    def low():
        nonlocal count, guess, maxval, maxtries
        count += 1
        if count > maxtries:
            update_result(f"I ran out of tries! You win!\nYour number was not {guess}.\nClick PLAY to start again.")
            end_game()
            return
        guess = fguesser('l', maxval)
        result_text = (f"Guesses Left : {maxtries - count + 1}\n"
                       f"Is it {guess}?")
        update_result(result_text)

    def update_result(text):
        result.configure(text=text)

    def new_game():
        nonlocal count, guess, maxval
        count = 1
        guess = 1
        maxval = 100
        range_button.config(state='normal')
        number_form.config(state='normal')
        number_form.delete(0, "end")
        number_form.focus() # <-- Set focus to the entry box
        play_button.config(state='disabled') # <-- Disable Play button during setup
        bet_button.config(state='disabled') # <-- Ensure Bet button is disabled
        end_game()
        update_result(text="Please Enter the Maximum Value and click 'SET MAX'")

    def play_game():
        nonlocal maxval, maxtries, guess
        try:
            val = int(number_form.get())
            if val <= 1:
                update_result(text="Maximum value must be greater than 1.")
                return
            maxval = val
            bet_button.config(state='normal')
            range_button.config(state='disabled')
            number_form.config(state='disabled')
            guess = fguesser('init', maxval)
            maxtries = math.ceil(math.log2(maxval))
            bet_text = (f"I shall guess within {maxtries} tries. \nYou want to bet?\n\n"
                        f"Click the \"BET\" button to start the Game")
            update_result(text=bet_text)
        except ValueError:
            update_result(text="Invalid input. Please enter a number.")

    def bet():
        nonlocal guess, count, maxtries
        higher_button.config(state='normal')
        lower_button.config(state='normal')
        yes_button.config(state='normal')
        bet_button.config(state='disabled')
        result_text = (f"Guesses Left : {maxtries - count + 1}\n"
                        f"Is it {guess}?")
        update_result(result_text)

    # --- WIDGETS with new colors ---
    title = tk.Label(window,text="co-Kreate Your Genius - GUESSING GAME ",font=("Arial",30,"bold"),fg="#000080",bg="#f0f0f0")
    result = tk.Label(window, text= "Click on \"PLAY\" button to start a new game", font=("Arial", 14, "normal"),fg = "#333333", bg="white", justify=tk.LEFT, wraplength=500, relief="sunken", borderwidth=2)
    control_frame = tk.Frame(window, bg="#f0f0f0")
    play_button = tk.Button(control_frame, text="PLAY", font=("Arial", 10, "bold"), fg = "white", bg="#29c70a",command=new_game, width=10)
    range_button = tk.Button(control_frame,text="SET MAX",font=("Arial",10, "bold"), state='disabled', fg="white",bg="#007bff", command=play_game, width=10)
    bet_button=tk.Button(control_frame,text="B E T",font=("Arial",10, "bold"), state='disabled', fg="white",bg="#ffc107", command=bet, width=10)
    number_form = tk.Entry(control_frame,font=("Arial",12), width=10, justify='center')
    number_form.config(state='disabled')
    guess_frame = tk.Frame(window, bg="#f0f0f0")
    higher_button = tk.Button(guess_frame,text="HIGHER",font=("Arial",12, "bold"), state='disabled', fg="white",bg="#17a2b8", command=high, width=12, height=2)
    lower_button = tk.Button(guess_frame,text="LOWER",font=("Arial",12, "bold"), state='disabled', fg="white",bg="#dc3545", command=low, width=12, height=2)
    yes_button = tk.Button(guess_frame,text="YES",font=("Arial",12, "bold"), state='disabled', fg="white",bg="#28a745", command=yes, width=12, height=2)
    exit_button = tk.Button(window,text="Exit",font=("Arial",10, "bold"), fg="White", bg="#6c757d", command=window.destroy, width=10)

    # --- PLACING WIDGETS using grid ---
    title.grid(row=0, column=0, columnspan=3, pady=10)
    result.grid(row=1, column=0, columnspan=3, sticky='nsew', padx=50, pady=20)
    control_frame.grid(row=2, column=0, columnspan=3)
    play_button.pack(side=tk.LEFT, padx=10)
    number_form.pack(side=tk.LEFT, padx=10)
    range_button.pack(side=tk.LEFT, padx=10)
    bet_button.pack(side=tk.LEFT, padx=10)
    guess_frame.grid(row=3, column=0, columnspan=3, pady=20)
    lower_button.pack(side=tk.LEFT, padx=20)
    yes_button.pack(side=tk.LEFT, padx=20)
    higher_button.pack(side=tk.LEFT, padx=20)
    exit_button.grid(row=4, column=1, pady=10)

    window.mainloop()


if __name__ == "__main__":
    main()
