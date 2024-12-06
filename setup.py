from cx_Freeze import setup, Executable

# List all packages explicitly (including your modules and external libraries)
packages = [
    "os", "sys", "cv2", "dlib", "numpy", "scipy", "customtkinter", 
    "optuna",
]
setup(
    name="MyApplication",
    version="1.0",
    description="A sample application with all imports",
    options={
        "build_exe": {
            "packages": packages,
            "include_files": [
                ("model.py", "model.py"),
                ("Utils.py", "Utils.py"),
            ]
        }
    },
    executables=[Executable("Husmorph.py", target_name="Husmorph")]
)
