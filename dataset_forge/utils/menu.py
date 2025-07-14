from .printing import print_header, print_error, print_prompt


def show_menu(title, options, header_color, char="#"):
    print_header(title, char=char, color=header_color)
    for key, value in options.items():
        if key.lower() == "0":
            print(
                f"\033[38;2;249;226;175m[ {key} ]  \033[38;2;205;214;244m{value[0]}\033[0m"
            )
        else:
            print(
                f"\033[38;2;137;180;250m[ {key} ]  \033[38;2;205;214;244m{value[0]}\033[0m"
            )
    while True:
        print_prompt("\nEnter your choice: ")
        choice = input().strip()
        if choice in options:
            return choice
        else:
            print_error("Invalid choice. Please try again.")
