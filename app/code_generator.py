import random
import string

def generate_unique_string():
    letters = string.ascii_uppercase
    numbers = string.digits

    random_chars = random.sample(letters, 3) + random.sample(numbers, 3)

    random.shuffle(random_chars)

    unique_string = ''.join(random_chars)

    return unique_string

# Example usage
if __name__ == "__main__":
    while True:
        generated_string = generate_unique_string()
        print("Generated String:", generated_string)
        char = input()
        if char == " ":
            break