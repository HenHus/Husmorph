import eel

# Initialize Eel with the folder containing your web files
eel.init('web')

# Expose a Python function to JavaScript
@eel.expose
def greet(name):
    print(f"Hello, {name}!")
    return f"Hello, {name} from Python!"

# Start the application, opening the specified HTML file in a browser window
eel.start('test.html', size=(800, 600))
