from . import cli, pod_manager

TOOL_NAME = "Python Pod Manager"
MAX_OUTPUT_LINE_LEN = 90


if __name__ == "__main__":
    try:
        # Calculate for great success
        tool_name_len = len(TOOL_NAME)
        odd_flag = tool_name_len & 1 ^ MAX_OUTPUT_LINE_LEN & 1
        decor_len = int((MAX_OUTPUT_LINE_LEN - 4 - tool_name_len) / 2)

        # Decorate the output and run
        print("─" * MAX_OUTPUT_LINE_LEN)
        print(f".{':' * decor_len} {TOOL_NAME} {':' * (decor_len + odd_flag)}.")
        print("─" * MAX_OUTPUT_LINE_LEN)
        main()
    finally:
        print("─" * MAX_OUTPUT_LINE_LEN)
