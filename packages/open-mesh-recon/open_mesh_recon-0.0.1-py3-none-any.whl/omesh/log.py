class PyLog:
    def info(self, message: str):
        print(f" --- INFO ---: {message}")

    def warning(self, message: str):
        print(f" --- WARNING ---: {message}")

    def error(self, message: str):
        print(f" --- ERROR ---: {message}")
        exit()

    def succeed(self, message: str):
        print(f" --- SUCCESSFUL ---: {message}")

if __name__ == "__main__":
    print("Note: This file is not a runable file that has output. Just use the 'PyLog' class in another script or run the 'main.py' script and be careful the folder 'input_images' should exist including just images.")